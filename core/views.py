from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, RelatorioDesempenhoForm
from django.db.models import Q
from .models import (
    FAQ, CategoriaFAQ, CategoriaContato, CategoriaFerramenta, 
    Contato, Ferramenta, CustomUser, UserDownload, UserSavedFAQ, UserSavedContato, Aluno, RelatorioDesempenho, Turma
)

from collections import defaultdict
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
import json
import logging
from django.db.models import Q, Count 
from collections import OrderedDict

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def is_admin(user):
    """Função auxiliar para verificar se o usuário é admin"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

# NOVA FUNÇÃO AUXILIAR
def is_professor(user):
    """Função auxiliar para verificar se o usuário é professor"""
    # CORREÇÃO: Acessamos o campo através da relação 'customuser'
    # Adicionamos um 'hasattr' por segurança, para o caso do admin (superuser) não ter o perfil customuser criado.
    return user.is_authenticated and hasattr(user, 'customuser') and user.customuser.is_professor

# =============================================================================
# NOVAS VIEWS: ÁREA DO PROFESSOR
# =============================================================================

@login_required
@user_passes_test(is_professor, login_url='/login/', redirect_field_name=None)
def area_professor(request):
    """
    Carrega a página principal da área do professor, incluindo os
    controles de filtro e a lista inicial de alunos.
    """
    alunos_list = Aluno.objects.select_related('turma').all().order_by('nome_completo')

    paginator = Paginator(alunos_list, 10)
    page_number = request.GET.get('page')
    alunos_page_obj = paginator.get_page(page_number)
    
    # Adicionando último relatório (sua lógica original, mas aplicada à página atual)
    for aluno in alunos_page_obj:
        aluno.ultimo_relatorio = RelatorioDesempenho.objects.filter(aluno=aluno).first()

    # Buscando dados para os filtros
    turmas = Turma.objects.all().order_by('nome')
    niveis_autismo = Aluno.NIVEL_AUTISMO_CHOICES

    context = {
        'title': 'Área do Professor',
        'alunos_page': alunos_page_obj,
        'turmas': turmas,
        'niveis_autismo': niveis_autismo,
    }
    return render(request, 'core/auth/area_professor.html', context)


@login_required
@user_passes_test(is_professor, login_url='/login/', redirect_field_name=None)
def filtrar_alunos_api(request):
    """
    Endpoint de API que retorna a lista de alunos filtrada em HTML.
    Esta view é chamada via AJAX pelo JavaScript da página.
    """
    # 1. Obter parâmetros da requisição GET
    search_term = request.GET.get('search', '')
    turma_id = request.GET.get('turma', '')
    nivel = request.GET.get('nivel', '')
    
    # 2. Construir a query base
    alunos_list = Aluno.objects.select_related('turma').all().order_by('nome_completo')
    
    # 3. Aplicar filtros se eles existirem
    if search_term:
        alunos_list = alunos_list.filter(nome_completo__icontains=search_term)
    
    if turma_id and turma_id != 'todos':
        alunos_list = alunos_list.filter(turma_id=turma_id)
        
    if nivel and nivel != 'todos':
        alunos_list = alunos_list.filter(nivel_autismo=nivel)
        
    # 4. Paginar os resultados filtrados
    paginator = Paginator(alunos_list, 10)
    page_number = request.GET.get('page', 1) # Sempre vai para a página 1 em uma nova filtragem
    alunos_page_obj = paginator.get_page(page_number)

    # Adicionando último relatório (lógica original)
    for aluno in alunos_page_obj:
        aluno.ultimo_relatorio = RelatorioDesempenho.objects.filter(aluno=aluno).first()

    context = {
        'alunos_page': alunos_page_obj
    }
    
    # 5. Renderizar APENAS a lista de alunos e a paginação
    return render(request, 'core/auth/_lista_alunos_parcial.html', context)

@login_required
@user_passes_test(is_professor, login_url='/login/', redirect_field_name=None)
def detalhes_aluno(request, aluno_id):
    """Exibe todos os relatórios de um aluno específico."""
    # MODIFICADO: Usamos select_related aqui também
    aluno = get_object_or_404(Aluno.objects.select_related('turma'), id=aluno_id)
    relatorios = RelatorioDesempenho.objects.filter(aluno=aluno).select_related('professor')
    
    context = {
        'title': f'Relatórios de {aluno.nome_completo}',
        'aluno': aluno,
        'relatorios': relatorios
    }
    return render(request, 'core/auth/detalhes_aluno.html', context)


@login_required
@user_passes_test(is_professor, login_url='/login/', redirect_field_name=None)
def adicionar_relatorio(request, aluno_id):
    """Formulário para adicionar um novo relatório para um aluno."""
    aluno = get_object_or_404(Aluno, id=aluno_id)
    
    if request.method == 'POST':
        form = RelatorioDesempenhoForm(request.POST)
        if form.is_valid():
            relatorio = form.save(commit=False)
            relatorio.aluno = aluno
            relatorio.professor = request.user.customuser # Associa o CustomUser do professor logado
            relatorio.save()
            messages.success(request, f'Relatório para {aluno.nome_completo} salvo com sucesso!')
            return redirect('detalhes_aluno', aluno_id=aluno.id)
    else:
        form = RelatorioDesempenhoForm()
        
    context = {
        'title': f'Adicionar Relatório para {aluno.nome_completo}',
        'form': form,
        'aluno': aluno
    }
    return render(request, 'core/auth/adicionar_relatorio.html', context)

@login_required
@user_passes_test(is_professor, login_url='/login/', redirect_field_name=None)
def ferramentas_professor(request):
    """
    Lista TODAS as ferramentas para a área do professor com paginação aninhada.
    - Paginação principal para CATEGORIAS (3 por página).
    - Paginação secundária para FERRAMENTAS dentro de cada categoria (3 por página).
    """
    # 1. PAGINAÇÃO PRINCIPAL (CATEGORIAS)
    categorias_com_ferramentas = CategoriaFerramenta.objects.annotate(
        num_ferramentas=Count('ferramentas')
    ).filter(num_ferramentas__gt=0).order_by('nome')
    
    main_paginator = Paginator(categorias_com_ferramentas, 3)  # 3 categorias por página
    main_page_number = request.GET.get('page')
    main_page_obj = main_paginator.get_page(main_page_number)
    categorias_na_pagina = main_page_obj.object_list

    # 2. BUSCAR TODAS AS FERRAMENTAS PARA AS CATEGORIAS DA PÁGINA ATUAL
    # CORREÇÃO: Usando 'categoria__in' ao invés de 'tipo__in'
    todas_ferramentas_da_pagina = Ferramenta.objects.filter(
        categoria__in=categorias_na_pagina
    ).order_by('nome')
    
    ferramentas_agrupadas = defaultdict(list)
    for ferramenta in todas_ferramentas_da_pagina:
        # CORREÇÃO: Agrupando por 'ferramenta.categoria' ao invés de 'ferramenta.tipo'
        ferramentas_agrupadas[ferramenta.categoria].append(ferramenta)

    # 3. CRIAR PAGINADORES ANINHADOS PARA CADA CATEGORIA
    dados_pagina_atual = OrderedDict()
    for categoria in categorias_na_pagina:
        lista_de_ferramentas = ferramentas_agrupadas.get(categoria, [])
        ferramenta_paginator = Paginator(lista_de_ferramentas, 3)  # 3 ferramentas por página
        
        # Cria um nome de parâmetro de URL único para este paginador
        query_param_name = f"cat_fer_{categoria.id}_page"
        ferramenta_page_number = request.GET.get(query_param_name)
        ferramenta_page_obj = ferramenta_paginator.get_page(ferramenta_page_number)
        
        dados_pagina_atual[categoria] = {
            'ferramentas_page_obj': ferramenta_page_obj,
            'query_param_name': query_param_name
        }

    # 4. PREPARAR O CONTEXTO FINAL
    context = {
        'title': 'Ferramentas do Professor',
        'ferramentas_por_categoria_paginada': dados_pagina_atual,
        'page_obj': main_page_obj,  # Paginador principal
        'sem_ferramentas': not categorias_com_ferramentas.exists()
    }
    
    return render(request, 'core/auth/ferramentas_professor.html', context)


# =============================================================================
# VIEWS PÚBLICAS - PÁGINAS PRINCIPAIS
# =============================================================================

def index(request):
    """Página inicial do sistema"""
    return render(request, 'core/index.html', {'title': 'Início'})

def sobre(request):
    """Página sobre o sistema"""
    return render(request, 'core/sobre.html', {'title': 'Sobre'})

def privacy(request):
    """Página de política de privacidade"""
    return render(request, 'core/privacy.html', {'title': 'Privacy Policy'})

def newsletter_signup(request):
    """Cadastro de newsletter"""
    if request.method == "POST":
        email = request.POST.get('email')
        # Aqui você pode adicionar lógica para salvar o e-mail na sua lista de newsletter
        return HttpResponse(f"Obrigado por se inscrever! Seu e-mail: {email}")
    return redirect('index')

# =============================================================================
# VIEWS DE FERRAMENTAS
# =============================================================================

def ferramentas(request):
    """Lista todas as ferramentas PÚBLICAS organizadas por categoria."""
    # MODIFICADO: Adicionamos .filter(apenas_para_professores=False) para
    # buscar apenas as ferramentas que NÃO são exclusivas para professores.
    categorias_com_ferramentas = CategoriaFerramenta.objects.annotate(
        num_ferramentas=Count('ferramentas')
    ).filter(
        num_ferramentas__gt=0, 
        ferramentas__apenas_para_professores=False # <-- Filtro principal
    ).prefetch_related('ferramentas').distinct()
    
    context = {
        'title': 'Ferramentas',
        'categorias_com_ferramentas': categorias_com_ferramentas,
    }
    
    return render(request, 'core/ferramentas.html', context)


def detalhes_ferramenta(request, id):
    """Exibe detalhes de uma ferramenta específica"""
    ferramenta = Ferramenta.objects.get(id=id)
    return render(request, 'core/detalhes_ferramenta.html', {
        'title': ferramenta.nome,
        'ferramenta': ferramenta
    })

@login_required
def register_download(request, ferramenta_id):
    """Registra o download de uma ferramenta pelo usuário"""
    if request.method == 'POST':
        ferramenta = get_object_or_404(Ferramenta, id=ferramenta_id)
        # Criar o registro de download
        download = UserDownload(user=request.user, ferramenta=ferramenta)
        download.save()
        messages.success(request, f'Download de {ferramenta.nome} registrado!')
        return redirect('detalhes_ferramenta', id=ferramenta_id)
    
    return redirect('ferramentas')


# =============================================================================
# VIEWS DE FAQ/DÚVIDAS
# =============================================================================

def duvidas(request):
    """
    Lista FAQs com paginação aninhada:
    - Paginação principal para TODAS as CATEGORIAS (3 por página).
    - Paginação secundária para DÚVIDAS dentro de cada categoria (4 por página).
    """
    # 1. CAPTURAR TERMO DE PESQUISA
    termo_pesquisa = request.POST.get('termo', request.GET.get('termo', ''))

    # 2. PAGINAÇÃO PRINCIPAL (CATEGORIAS)
    # CORREÇÃO: Paginamos TODAS as categorias, sem filtrar as vazias.
    todas_categorias = CategoriaFAQ.objects.all().order_by('nome')

    main_paginator = Paginator(todas_categorias, 3)
    main_page_number = request.GET.get('page')
    main_page_obj = main_paginator.get_page(main_page_number)
    categorias_na_pagina = main_page_obj.object_list

    # 3. BUSCAR TODAS AS FAQS PARA AS CATEGORIAS DA PÁGINA ATUAL
    faqs_da_pagina = FAQ.objects.filter(
        categoria__in=categorias_na_pagina
    ).select_related('categoria').order_by('pergunta')
    
    if termo_pesquisa:
        faqs_da_pagina = faqs_da_pagina.filter(
            Q(pergunta__icontains=termo_pesquisa) | 
            Q(resposta__icontains=termo_pesquisa)
        )
    
    faqs_agrupadas = defaultdict(list)
    for faq in faqs_da_pagina:
        faqs_agrupadas[faq.categoria].append(faq)

    # 4. CRIAR PAGINADORES ANINHADOS PARA CADA CATEGORIA
    dados_pagina_atual = OrderedDict()
    for categoria in categorias_na_pagina:
        lista_de_faqs = faqs_agrupadas.get(categoria, [])
        
        faq_paginator = Paginator(lista_de_faqs, 4) # 4 dúvidas por página
        query_param_name = f"faq_cat_{categoria.id}_page"
        faq_page_number = request.GET.get(query_param_name)
        faq_page_obj = faq_paginator.get_page(faq_page_number)
        
        dados_pagina_atual[categoria] = {
            'faqs_page_obj': faq_page_obj,
            'query_param_name': query_param_name
        }

    # 5. OBTER IDS DAS FAQS SALVAS PELO USUÁRIO
    faqs_salvas_ids = []
    if request.user.is_authenticated:
        faqs_salvas_ids = list(UserSavedFAQ.objects.filter(
            user=request.user
        ).values_list('faq_id', flat=True))

    # 6. PREPARAR O CONTEXTO FINAL
    context = {
        'faqs_por_categoria_paginada': dados_pagina_atual,
        'page_obj': main_page_obj,
        'termo_pesquisa': termo_pesquisa,
        'faqs_salvas_ids': faqs_salvas_ids,
    }
    
    return render(request, 'core/duvidas.html', context)

def pesquisar_faqs(request):
    """View para buscar FAQs - redirect para duvidas com termo de pesquisa"""
    if request.method == 'POST':
        termo = request.POST.get('termo', '')
        return redirect(f'/duvidas/?termo={termo}')
    return redirect('duvidas')

@login_required
@require_POST
@csrf_protect
def salvar_faq(request, faq_id):
    """View para salvar uma FAQ no perfil do usuário"""
    try:
        # Busca a FAQ
        faq = get_object_or_404(FAQ, id=faq_id)
        
        # Busca o CustomUser de forma mais robusta
        try:
            # Primeiro tenta por username
            user = CustomUser.objects.get(username=request.user.username)
        except CustomUser.DoesNotExist:
            try:
                # Se não encontrar, tenta por email (se ambos modelos tiverem)
                if hasattr(request.user, 'email') and request.user.email:
                    user = CustomUser.objects.get(email=request.user.email)
                else:
                    raise CustomUser.DoesNotExist
            except CustomUser.DoesNotExist:
                return JsonResponse({
                    'success': False, 
                    'message': 'Usuário não encontrado no sistema. Faça login novamente.'
                })
        
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False, 
                'message': 'Usuário não autenticado corretamente.'
            })
        
        # Verifica se já não está salva
        faq_salva, created = UserSavedFAQ.objects.get_or_create(
            user=user, 
            faq=faq
        )
        
        if created:
            return JsonResponse({
                'success': True, 
                'message': 'Dúvida salva com sucesso!',
                'action': 'saved'
            })
        else:
            return JsonResponse({
                'success': True,
                'message': 'Esta dúvida já está salva.',
                'action': 'already_saved'
            })
            
    except FAQ.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'message': 'Dúvida não encontrada.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Erro interno: {str(e)}'
        })

@login_required
@require_POST
@csrf_protect
def remover_faq_salva(request, faq_id):
    """View para remover uma FAQ salva do perfil do usuário"""
    try:
        # Busca a FAQ
        faq = get_object_or_404(FAQ, id=faq_id)
        
        # Busca o CustomUser de forma mais robusta
        try:
            # Primeiro tenta por username
            user = CustomUser.objects.get(username=request.user.username)
        except CustomUser.DoesNotExist:
            try:
                # Se não encontrar, tenta por email (se ambos modelos tiverem)
                if hasattr(request.user, 'email') and request.user.email:
                    user = CustomUser.objects.get(email=request.user.email)
                else:
                    raise CustomUser.DoesNotExist
            except CustomUser.DoesNotExist:
                return JsonResponse({
                    'success': False, 
                    'message': 'Usuário não encontrado no sistema. Faça login novamente.'
                })
        
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False, 
                'message': 'Usuário não autenticado corretamente.'
            })
        
        # Tenta remover a FAQ salva
        faq_salva = UserSavedFAQ.objects.filter(user=user, faq=faq).first()
        
        if faq_salva:
            faq_salva.delete()
            return JsonResponse({
                'success': True, 
                'message': 'Dúvida removida com sucesso!',
                'action': 'removed'
            })
        else:
            return JsonResponse({
                'success': False, 
                'message': 'Dúvida não encontrada nas suas dúvidas salvas.',
                'action': 'not_found'
            })
            
    except FAQ.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'message': 'Dúvida não encontrada.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Erro interno: {str(e)}'
        })

# =============================================================================
# VIEWS DE CONTATOS
# =============================================================================



def contatos(request):
    """
    Lista Contatos com paginação aninhada:
    - Paginação principal para CATEGORIAS (3 por página).
    - Paginação secundária para CONTATOS dentro de cada categoria (3 por página).
    """
    # 1. PAGINAÇÃO PRINCIPAL (CATEGORIAS)
    categorias_com_contatos = CategoriaContato.objects.annotate(
        num_contatos=Count('contatos')
    ).filter(num_contatos__gt=0).order_by('nome')
    
    main_paginator = Paginator(categorias_com_contatos, 3)
    main_page_number = request.GET.get('page')
    main_page_obj = main_paginator.get_page(main_page_number)
    categorias_na_pagina = main_page_obj.object_list

    # 2. BUSCAR TODOS OS CONTATOS PARA AS CATEGORIAS DA PÁGINA ATUAL
    todos_contatos_da_pagina = Contato.objects.filter(
        categoria__in=categorias_na_pagina
    ).order_by('nome')
    
    contatos_agrupados = defaultdict(list)
    for contato in todos_contatos_da_pagina:
        contatos_agrupados[contato.categoria].append(contato)

    # 3. CRIAR PAGINADORES ANINHADOS PARA CADA CATEGORIA
    # Usamos um OrderedDict para manter a ordem da paginação principal.
    dados_pagina_atual = OrderedDict()
    for categoria in categorias_na_pagina:
        lista_de_contatos = contatos_agrupados.get(categoria, [])
        
        # Cria um paginador específico para os contatos desta categoria
        contato_paginator = Paginator(lista_de_contatos, 3) # 3 contatos por página
        
        # Cria um nome de parâmetro de URL único para este paginador
        query_param_name = f"cat_{categoria.id}_page"
        contato_page_number = request.GET.get(query_param_name)
        
        # Pega o objeto da página de contatos para esta categoria
        contato_page_obj = contato_paginator.get_page(contato_page_number)
        
        dados_pagina_atual[categoria] = {
            'contatos_page_obj': contato_page_obj,
            'query_param_name': query_param_name
        }

    # 4. BUSCAR CONTATOS SALVOS PELO USUÁRIO
    contatos_salvos_ids = []
    if request.user.is_authenticated:
        contatos_salvos_ids = list(UserSavedContato.objects.filter(
            user=request.user
        ).values_list('contato_id', flat=True))

    # 5. PREPARAR O CONTEXTO FINAL
    context = {
        'title': 'Contatos',
        'contatos_por_categoria_paginada': dados_pagina_atual,
        'page_obj': main_page_obj,  # Paginador principal
        'contatos_salvos_ids': contatos_salvos_ids,
        'sem_contatos': not categorias_com_contatos.exists()
    }
    
    return render(request, 'core/contatos.html', context)

def detalhes_contato(request, id):
    """Exibe detalhes de um contato específico"""
    contato = Contato.objects.get(pk=id)
    return render(request, 'core/detalhes_contato.html', {'contato': contato})

@login_required
@require_POST
@csrf_protect
def salvar_contato(request, contato_id):
    """View para salvar um contato no perfil do usuário"""
    try:
        # Busca o contato
        contato = get_object_or_404(Contato, id=contato_id)
        
        # Busca o CustomUser de forma mais robusta
        try:
            # Primeiro tenta por username
            user = CustomUser.objects.get(username=request.user.username)
        except CustomUser.DoesNotExist:
            try:
                # Se não encontrar, tenta por email (se ambos modelos tiverem)
                if hasattr(request.user, 'email') and request.user.email:
                    user = CustomUser.objects.get(email=request.user.email)
                else:
                    raise CustomUser.DoesNotExist
            except CustomUser.DoesNotExist:
                return JsonResponse({
                    'success': False, 
                    'message': 'Usuário não encontrado no sistema. Faça login novamente.'
                })
        
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False, 
                'message': 'Usuário não autenticado corretamente.'
            })
        
        # Verifica se já não está salvo
        contato_salvo, created = UserSavedContato.objects.get_or_create(
            user=user, 
            contato=contato
        )
        
        if created:
            return JsonResponse({
                'success': True, 
                'message': 'Contato salvo com sucesso!',
                'action': 'saved'
            })
        else:
            return JsonResponse({
                'success': True,
                'message': 'Este contato já está salvo.',
                'action': 'already_saved'
            })
            
    except Contato.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'message': 'Contato não encontrado.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Erro interno: {str(e)}'
        })

@login_required
@require_POST
@csrf_protect
def remover_contato_salvo(request, contato_id):
    """View para remover um contato salvo do perfil do usuário"""
    try:
        # Busca o contato
        contato = get_object_or_404(Contato, id=contato_id)
        
        # Busca o CustomUser de forma mais robusta
        try:
            # Primeiro tenta por username
            user = CustomUser.objects.get(username=request.user.username)
        except CustomUser.DoesNotExist:
            try:
                # Se não encontrar, tenta por email (se ambos modelos tiverem)
                if hasattr(request.user, 'email') and request.user.email:
                    user = CustomUser.objects.get(email=request.user.email)
                else:
                    raise CustomUser.DoesNotExist
            except CustomUser.DoesNotExist:
                return JsonResponse({
                    'success': False, 
                    'message': 'Usuário não encontrado no sistema. Faça login novamente.'
                })
        
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False, 
                'message': 'Usuário não autenticado corretamente.'
            })
        
        # Tenta remover o contato salvo
        contato_salvo = UserSavedContato.objects.filter(user=user, contato=contato).first()
        
        if contato_salvo:
            contato_salvo.delete()
            return JsonResponse({
                'success': True, 
                'message': 'Contato removido com sucesso!',
                'action': 'removed'
            })
        else:
            return JsonResponse({
                'success': False, 
                'message': 'Contato não encontrado nos seus contatos salvos.',
                'action': 'not_found'
            })
            
    except Contato.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'message': 'Contato não encontrado.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Erro interno: {str(e)}'
        })

# =============================================================================
# VIEWS DE AUTENTICAÇÃO E PERFIL
# =============================================================================

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # MODIFICAÇÃO IMPORTANTE: Para a herança multi-tabela funcionar corretamente,
            # precisamos criar o objeto CustomUser explicitamente após criar o User.
            CustomUser.objects.create(user_ptr_id=user.pk)
            
            username = form.cleaned_data.get('username')
            messages.success(
                request, 
                f'Conta criada com sucesso para {username}! Você foi logado automaticamente.'
            )
            login(request, user)
            return redirect('index')
        else:
            messages.error(
                request, 
                'Por favor, corrija os erros abaixo.'
            )
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'core/auth/register.html', {'form': form})


def login_view(request):
    """Login de usuários"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                if user.is_staff or user.is_superuser:
                    messages.success(request, f'Bem-vindo, {user.first_name}! Acesso administrativo concedido.')
                    return redirect('/admin/')
                else:
                    messages.success(request, f'Bem-vindo, {user.first_name}! Login realizado com sucesso.')
                
                next_url = request.GET.get('next', 'index')
                return redirect(next_url)
            else:
                messages.error(request, 'Nome de usuário ou senha inválidos.')
        else:
            messages.error(request, 'Nome de usuário ou senha inválidos.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'core/auth/login.html', {'form': form})


def logout_view(request):
    """Logout de usuários"""
    logout(request)
    messages.success(request, 'Você saiu com sucesso!')
    return redirect('index')

@login_required
def profile_view(request):
    """Perfil do usuário com histórico de downloads, FAQs salvas e contatos salvos"""
    user = request.user
    custom_user = user.customuser # Acessa o perfil customizado aqui
    
    # Supondo que UserSavedFAQ e UserSavedContato usam a FK para CustomUser
    duvidas_salvas = UserSavedFAQ.objects.filter(
        user=custom_user
    ).select_related('faq', 'faq__categoria').order_by('-data_salva')
    
    contatos_salvos = UserSavedContato.objects.filter(
        user=custom_user
    ).select_related('contato', 'contato__categoria').order_by('-data_salva')

    # Supondo que UserDownload usa a FK para CustomUser
    downloads = UserDownload.objects.filter(user=custom_user).select_related('ferramenta')
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user) # O form edita o User base
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)
    
    return render(request, 'core/auth/profile.html', {
        'form': form,
        'downloads': downloads,
        'duvidas_salvas': duvidas_salvas,
        'contatos_salvos': contatos_salvos,
        'title': 'Meu Perfil'
    })


# =============================================================================
# VIEWS ADMINISTRATIVAS - DASHBOARD
# =============================================================================

@user_passes_test(is_admin)
def admin_dashboard(request):
    """Dashboard administrativo com estatísticas gerais"""
    categorias_faq = CategoriaFAQ.objects.all().count()
    categorias_contato = CategoriaContato.objects.all().count()
    categorias_ferramenta = CategoriaFerramenta.objects.all().count()
    
    ferramentas = Ferramenta.objects.all().count()
    contatos = Contato.objects.all().count()
    faqs = FAQ.objects.all().count()
    usuarios = CustomUser.objects.all().count()
    
    context = {
        'title': 'Dashboard Admin',
        'categorias_faq': categorias_faq,
        'categorias_contato': categorias_contato,
        'categorias_ferramenta': categorias_ferramenta,
        'ferramentas': ferramentas,
        'contatos': contatos,
        'faqs': faqs,
        'usuarios': usuarios
    }
    
    return render(request, 'core/admin/dashboard.html', context)

# =============================================================================
# VIEWS ADMINISTRATIVAS - GESTÃO DE CATEGORIAS FAQ
# =============================================================================

@user_passes_test(is_admin)
def admin_categorias_faq(request):
    """Lista todas as categorias FAQ"""
    categorias = CategoriaFAQ.objects.all()
    return render(request, 'core/admin/categorias_faq.html', {
        'categorias': categorias,
        'title': 'Gestão de Categorias FAQ'
    })

@user_passes_test(is_admin)
def admin_categoria_faq_criar(request):
    """Criar nova categoria FAQ"""
    if request.method == 'POST':
        nome = request.POST.get('nome')
        icone = request.POST.get('icone')
        
        categoria = CategoriaFAQ(nome=nome, icone=icone)
        categoria.save()
        
        messages.success(request, 'Categoria FAQ criada com sucesso!')
        return redirect('admin_categorias_faq')
    
    return render(request, 'core/admin/categoria_form.html', {
        'title': 'Nova Categoria FAQ'
    })

@user_passes_test(is_admin)
def admin_categoria_faq_editar(request, id):
    """Editar categoria FAQ existente"""
    categoria = get_object_or_404(CategoriaFAQ, id=id)
    
    if request.method == 'POST':
        categoria.nome = request.POST.get('nome')
        categoria.icone = request.POST.get('icone')
        categoria.save()
        
        messages.success(request, 'Categoria FAQ atualizada com sucesso!')
        return redirect('admin_categorias_faq')
    
    return render(request, 'core/admin/categoria_form.html', {
        'categoria': categoria,
        'title': 'Editar Categoria FAQ'
    })

@user_passes_test(is_admin)
def admin_categoria_faq_excluir(request, id):
    """Excluir categoria FAQ"""
    categoria = get_object_or_404(CategoriaFAQ, id=id)
    
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoria FAQ excluída com sucesso!')
        return redirect('admin_categorias_faq')
    
    return render(request, 'core/admin/confirmacao_exclusao.html', {
        'objeto': categoria,
        'tipo': 'Categoria FAQ',
        'title': 'Excluir Categoria FAQ'
    })

# =============================================================================
# VIEWS ADMINISTRATIVAS - GESTÃO DE FAQ
# =============================================================================

@user_passes_test(is_admin)
def admin_faqs(request):
    """Lista todas as FAQs"""
    faqs = FAQ.objects.all()
    return render(request, 'core/admin/faqs.html', {
        'faqs': faqs,
        'title': 'Gestão de FAQs'
    })

@user_passes_test(is_admin)
def admin_faq_criar(request):
    """Criar nova FAQ"""
    categorias = CategoriaFAQ.objects.all()
    
    if request.method == 'POST':
        pergunta = request.POST.get('pergunta')
        resposta = request.POST.get('resposta')
        categoria_id = request.POST.get('categoria')
        categoria = get_object_or_404(CategoriaFAQ, id=categoria_id)
        
        faq = FAQ(pergunta=pergunta, resposta=resposta, categoria=categoria)
        faq.save()
        
        messages.success(request, 'FAQ criada com sucesso!')
        return redirect('admin_faqs')
    
    return render(request, 'core/admin/faq_form.html', {
        'categorias': categorias,
        'title': 'Nova FAQ'
    })

@user_passes_test(is_admin)
def admin_faq_editar(request, id):
    """Editar FAQ existente"""
    faq = get_object_or_404(FAQ, id=id)
    categorias = CategoriaFAQ.objects.all()
    
    if request.method == 'POST':
        faq.pergunta = request.POST.get('pergunta')
        faq.resposta = request.POST.get('resposta')
        categoria_id = request.POST.get('categoria')
        faq.categoria = get_object_or_404(CategoriaFAQ, id=categoria_id)
        faq.save()
        
        messages.success(request, 'FAQ atualizada com sucesso!')
        return redirect('admin_faqs')
    
    return render(request, 'core/admin/faq_form.html', {
        'faq': faq,
        'categorias': categorias,
        'title': 'Editar FAQ'
    })

@user_passes_test(is_admin)
def admin_faq_excluir(request, id):
    """Excluir FAQ"""
    faq = get_object_or_404(FAQ, id=id)
    
    if request.method == 'POST':
        faq.delete()
        messages.success(request, 'FAQ excluída com sucesso!')
        return redirect('admin_faqs')
    
    return render(request, 'core/admin/confirmacao_exclusao.html', {
        'objeto': faq,
        'tipo': 'FAQ',
        'title': 'Excluir FAQ'
    })

# =============================================================================
# VIEWS ADMINISTRATIVAS - GESTÃO DE CATEGORIAS CONTATO
# =============================================================================

@user_passes_test(is_admin)
def admin_categorias_contato(request):
    """Lista todas as categorias de contato"""
    categorias = CategoriaContato.objects.all()
    return render(request, 'core/admin/categorias_contato.html', {
        'categorias': categorias,
        'title': 'Gestão de Categorias de Contato'
    })

@user_passes_test(is_admin)
def admin_categoria_contato_criar(request):
    """Criar nova categoria de contato"""
    if request.method == 'POST':
        nome = request.POST.get('nome')
        icone = request.POST.get('icone')
        
        categoria = CategoriaContato(nome=nome, icone=icone)
        categoria.save()
        
        messages.success(request, 'Categoria de Contato criada com sucesso!')
        return redirect('admin_categorias_contato')
    
    return render(request, 'core/admin/categoria_form.html', {
        'title': 'Nova Categoria de Contato'
    })

@user_passes_test(is_admin)
def admin_categoria_contato_editar(request, id):
    """Editar categoria de contato existente"""
    categoria = get_object_or_404(CategoriaContato, id=id)
    
    if request.method == 'POST':
        categoria.nome = request.POST.get('nome')
        categoria.icone = request.POST.get('icone')
        categoria.save()
        
        messages.success(request, 'Categoria de Contato atualizada com sucesso!')
        return redirect('admin_categorias_contato')
    
    return render(request, 'core/admin/categoria_form.html', {
        'categoria': categoria,
        'title': 'Editar Categoria de Contato'
    })

@user_passes_test(is_admin)
def admin_categoria_contato_excluir(request, id):
    """Excluir categoria de contato"""
    categoria = get_object_or_404(CategoriaContato, id=id)
    
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoria de Contato excluída com sucesso!')
        return redirect('admin_categorias_contato')
    
    return render(request, 'core/admin/confirmacao_exclusao.html', {
        'objeto': categoria,
        'tipo': 'Categoria de Contato',
        'title': 'Excluir Categoria de Contato'
    })

# =============================================================================
# VIEWS ADMINISTRATIVAS - GESTÃO DE CONTATOS
# =============================================================================

@user_passes_test(is_admin)
def admin_contatos(request):
    """Lista todos os contatos"""
    contatos = Contato.objects.all()
    return render(request, 'core/admin/contatos.html', {
        'contatos': contatos,
        'title': 'Gestão de Contatos'
    })

@user_passes_test(is_admin)
def admin_contato_criar(request):
    """Criar novo contato"""
    categorias = CategoriaContato.objects.all()
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        
        # Tratamento para upload de imagem
        imagem = request.FILES.get('imagem')
        
        # Campos de endereço
        rua = request.POST.get('rua')
        numero = request.POST.get('numero')
        complemento = request.POST.get('complemento')
        bairro = request.POST.get('bairro')
        cidade = request.POST.get('cidade')
        estado = request.POST.get('estado')
        cep = request.POST.get('cep')
        
        telefone = request.POST.get('telefone')
        horario_funcionamento = request.POST.get('horario_funcionamento')
        categoria_id = request.POST.get('categoria')
        atendimento_presencial = 'atendimento_presencial' in request.POST
        atendimento_online = 'atendimento_online' in request.POST
        
        categoria = get_object_or_404(CategoriaContato, id=categoria_id) if categoria_id else None
        
        contato = Contato(
            nome=nome,
            descricao=descricao,
            imagem=imagem,
            rua=rua,
            numero=numero,
            complemento=complemento,
            bairro=bairro,
            cidade=cidade,
            estado=estado,
            cep=cep,
            telefone=telefone,
            horario_funcionamento=horario_funcionamento,
            categoria=categoria,
            atendimento_presencial=atendimento_presencial,
            atendimento_online=atendimento_online
        )
        contato.save()
        
        messages.success(request, 'Contato criado com sucesso!')
        return redirect('admin_contatos')
    
    return render(request, 'core/admin/contato_form.html', {
        'title': 'Novo Contato',
        'categorias': categorias
    })

@user_passes_test(is_admin)
def admin_contato_editar(request, id):
    """Editar contato existente"""
    contato = get_object_or_404(Contato, id=id)
    categorias = CategoriaContato.objects.all()
    
    if request.method == 'POST':
        contato.nome = request.POST.get('nome')
        contato.descricao = request.POST.get('descricao')
        
        # Tratamento para upload de imagem
        if 'imagem' in request.FILES:
            contato.imagem = request.FILES['imagem']
        
        # Campos de endereço
        contato.rua = request.POST.get('rua')
        contato.numero = request.POST.get('numero')
        contato.complemento = request.POST.get('complemento')
        contato.bairro = request.POST.get('bairro')
        contato.cidade = request.POST.get('cidade')
        contato.estado = request.POST.get('estado')
        contato.cep = request.POST.get('cep')
        
        contato.telefone = request.POST.get('telefone')
        contato.horario_funcionamento = request.POST.get('horario_funcionamento')
        
        categoria_id = request.POST.get('categoria')
        contato.categoria = get_object_or_404(CategoriaContato, id=categoria_id) if categoria_id else None
        
        contato.atendimento_presencial = 'atendimento_presencial' in request.POST
        contato.atendimento_online = 'atendimento_online' in request.POST
        contato.save()
        
        messages.success(request, 'Contato atualizado com sucesso!')
        return redirect('admin_contatos')
    
    return render(request, 'core/admin/contato_form.html', {
        'contato': contato,
        'title': 'Editar Contato',
        'categorias': categorias
    })

@user_passes_test(is_admin)
def admin_contato_excluir(request, id):
    """Excluir contato"""
    contato = get_object_or_404(Contato, id=id)
    
    if request.method == 'POST':
        contato.delete()
        messages.success(request, 'Contato excluído com sucesso!')
        return redirect('admin_contatos')
    
    return render(request, 'core/admin/confirmacao_exclusao.html', {
        'objeto': contato,
        'tipo': 'Contato',
        'title': 'Excluir Contato'
    })

# =============================================================================
# VIEWS ADMINISTRATIVAS - GESTÃO DE CATEGORIAS FERRAMENTA
# =============================================================================

@user_passes_test(is_admin)
def admin_categorias_ferramenta(request):
    """Lista todas as categorias de ferramenta"""
    categorias = CategoriaFerramenta.objects.all()
    return render(request, 'core/admin/categorias_ferramenta.html', {
        'categorias': categorias,
        'title': 'Gestão de Categorias de Ferramenta'
    })

@user_passes_test(is_admin)
def admin_categoria_ferramenta_criar(request):
    """Criar nova categoria de ferramenta"""
    if request.method == 'POST':
        nome = request.POST.get('nome')
        icone = request.POST.get('icone')
        
        categoria = CategoriaFerramenta(nome=nome, icone=icone)
        categoria.save()
        
        messages.success(request, 'Categoria de Ferramenta criada com sucesso!')
        return redirect('admin_categorias_ferramenta')
    
    return render(request, 'core/admin/categoria_form.html', {
        'title': 'Nova Categoria de Ferramenta'
    })

@user_passes_test(is_admin)
def admin_categoria_ferramenta_editar(request, id):
    """Editar categoria de ferramenta existente"""
    categoria = get_object_or_404(CategoriaFerramenta, id=id)
    
    if request.method == 'POST':
        categoria.nome = request.POST.get('nome')
        categoria.icone = request.POST.get('icone')
        categoria.save()
        
        messages.success(request, 'Categoria de Ferramenta atualizada com sucesso!')
        return redirect('admin_categorias_ferramenta')
    
    return render(request, 'core/admin/categoria_form.html', {
        'categoria': categoria,
        'title': 'Editar Categoria de Ferramenta'
    })

@user_passes_test(is_admin)
def admin_categoria_ferramenta_excluir(request, id):
    """Excluir categoria de ferramenta"""
    categoria = get_object_or_404(CategoriaFerramenta, id=id)
    
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoria de Ferramenta excluída com sucesso!')
        return redirect('admin_categorias_ferramenta')
    
    return render(request, 'core/admin/confirmacao_exclusao.html', {
        'objeto': categoria,
        'tipo': 'Categoria de Ferramenta',
        'title': 'Excluir Categoria de Ferramenta'
    })

# =============================================================================
# VIEWS ADMINISTRATIVAS - GESTÃO DE FERRAMENTAS
# =============================================================================

@user_passes_test(is_admin)
def admin_ferramentas(request):
    """Lista todas as ferramentas"""
    ferramentas = Ferramenta.objects.all().select_related('tipo')
    return render(request, 'core/admin/ferramentas.html', {
        'ferramentas': ferramentas,
        'title': 'Gestão de Ferramentas'
    })

@user_passes_test(is_admin)
def admin_ferramenta_criar(request):
    """Criar nova ferramenta"""
    categorias = CategoriaFerramenta.objects.all()
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        icone_classe = request.POST.get('icone_classe')
        tipo_id = request.POST.get('tipo')
        tipo = get_object_or_404(CategoriaFerramenta, id=tipo_id) if tipo_id else None
        eh_gratuita = 'eh_gratuita' in request.POST
        categoria = request.POST.get('categoria')
        
        # Tratamento para upload de arquivo
        arquivo = request.FILES.get('arquivo')
        
        ferramenta = Ferramenta(
            nome=nome,
            descricao=descricao,
            icone_classe=icone_classe,
            tipo=tipo,
            eh_gratuita=eh_gratuita,
            categoria=categoria,
            arquivo=arquivo
        )
        ferramenta.save()
        
        messages.success(request, 'Ferramenta criada com sucesso!')
        return redirect('admin_ferramentas')
    
    return render(request, 'core/admin/ferramenta_form.html', {
        'title': 'Nova Ferramenta',
        'categorias': categorias,
        'opcoes_categoria': dict(Ferramenta._meta.get_field('categoria').choices)
    })

@user_passes_test(is_admin)
def admin_ferramenta_editar(request, id):
    """Editar ferramenta existente"""
    ferramenta = get_object_or_404(Ferramenta, id=id)
    categorias = CategoriaFerramenta.objects.all()
    
    if request.method == 'POST':
        ferramenta.nome = request.POST.get('nome')
        ferramenta.descricao = request.POST.get('descricao')
        ferramenta.icone_classe = request.POST.get('icone_classe')
        
        tipo_id = request.POST.get('tipo')
        ferramenta.tipo = get_object_or_404(CategoriaFerramenta, id=tipo_id) if tipo_id else None
        
        ferramenta.eh_gratuita = 'eh_gratuita' in request.POST
        ferramenta.categoria = request.POST.get('categoria')
        
        # Tratamento para upload de arquivo
        if 'arquivo' in request.FILES:
            ferramenta.arquivo = request.FILES['arquivo']
        
        ferramenta.save()
        
        messages.success(request, 'Ferramenta atualizada com sucesso!')
        return redirect('admin_ferramentas')
    
    return render(request, 'core/admin/ferramenta_form.html', {
        'ferramenta': ferramenta,
        'title': 'Editar Ferramenta',
        'categorias': categorias,
        'opcoes_categoria': dict(Ferramenta._meta.get_field('categoria').choices)
    })

@user_passes_test(is_admin)
def admin_ferramenta_excluir(request, id):
    """Excluir ferramenta"""
    ferramenta = get_object_or_404(Ferramenta, id=id)
    
    if request.method == 'POST':
        ferramenta.delete()
        messages.success(request, 'Ferramenta excluída com sucesso!')
        return redirect('admin_ferramentas')
    
    return render(request, 'core/admin/confirmacao_exclusao.html', {
        'objeto': ferramenta,
        'tipo': 'Ferramenta',
        'title': 'Excluir Ferramenta'
    })

# =============================================================================
# VIEWS IRRELEVANTES ATÉ AGORA - FAZ PARTE DO PERFIL DE USUÁRIO
# =============================================================================

def document_list(request):
    # Lógica para listar documentos
    # Pode ser adaptada conforme seus modelos atuais
    return render(request, 'core/document_list.html', {'documents': []})

