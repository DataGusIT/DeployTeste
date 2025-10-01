from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html 
from .models import CategoriaFAQ, CategoriaContato, CategoriaFerramenta, FAQ, Contato, Ferramenta, CustomUser, UserDownload, UserSavedFAQ, FotoContato, UserSavedContato, Aluno, RelatorioDesempenho, Turma
import uuid
from supabase import create_client, Client
import os
from django import forms

# =============================================================================
# FUNÇÃO AUXILIAR DE UPLOAD (REUTILIZÁVEL)
# =============================================================================
# É uma boa prática mover a lógica de upload para uma função que pode ser chamada
# por qualquer painel de administração.
def _upload_to_supabase(file_obj, bucket_name, sub_folder=''):
    """
    Faz o upload de um arquivo para um bucket específico no Supabase.
    Retorna a URL pública e uma mensagem de erro (se houver).
    """
    try:
        url, key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY")
        supabase: Client = create_client(url, key)
        
        file_ext = file_obj.name.split('.')[-1]
        path_prefix = f"{sub_folder}/" if sub_folder else ""
        
        # Cria um nome de arquivo único para evitar conflitos
        path_on_bucket = f"public/{path_prefix}{uuid.uuid4()}.{file_ext}"
        
        # Realiza o upload
        supabase.storage.from_(bucket_name).upload(
            file=file_obj.read(), 
            path=path_on_bucket, 
            file_options={"content-type": file_obj.content_type}
        )
        
        # Retorna a URL pública do arquivo
        return supabase.storage.from_(bucket_name).get_public_url(path_on_bucket), None
    except Exception as e:
        # Em caso de erro, retorna None e a exceção
        return None, e

# =============================================================================
# ADMINISTRAÇÃO DE USUÁRIOS
# =============================================================================

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # MODIFICAÇÃO: Adicionado 'is_professor' para fácil visualização e filtro
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_admin', 'is_professor', 'is_staff')
    list_filter = ('is_admin', 'is_professor', 'is_staff', 'is_active')
    
    # MODIFICAÇÃO: Adicionado 'is_professor' aos campos editáveis
    fieldsets = UserAdmin.fieldsets + (
        ('Funções Customizadas', {'fields': ('is_admin', 'is_professor')}),
    )

# =============================================================================
# NOVA ADMINISTRAÇÃO: ALUNOS E RELATÓRIOS
# =============================================================================
# NOVA ADMINISTRAÇÃO PARA TURMAS
@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

class AlunoAdminForm(forms.ModelForm):
    laudo_upload = forms.FileField(label="Novo Laudo (Substitui o atual)", required=False)

    class Meta:
        model = Aluno
        fields = '__all__'

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    form = AlunoAdminForm  # Usa o formulário personalizado
    list_display = ('nome_completo', 'turma', 'nivel_autismo', 'data_nascimento', 'data_cadastro')
    search_fields = ('nome_completo',)
    list_filter = ('turma', 'nivel_autismo', 'data_cadastro',)
    autocomplete_fields = ['turma']
    readonly_fields = ('laudo_url',) # Deixa o campo de URL apenas para leitura

    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('nome_completo', 'data_nascimento')
        }),
        ('Informações Acadêmicas', {
            'fields': ('turma',)
        }),
        ('Informações de Diagnóstico', {
            # Alterado 'laudo' para os novos campos
            'fields': ('nivel_autismo', 'laudo_upload', 'laudo_url')
        }),
    )

    def save_model(self, request, obj, form, change):
        # Verifica se um novo arquivo de laudo foi enviado
        if 'laudo_upload' in form.cleaned_data and form.cleaned_data['laudo_upload']:
            laudo_file = form.cleaned_data['laudo_upload']
            
            # Chama a função de upload para o bucket 'arquivos-producao'
            public_url, error = _upload_to_supabase(
                laudo_file, 
                bucket_name="arquivos-producao", 
                sub_folder='laudos_alunos'
            )
            
            if public_url:
                obj.laudo_url = public_url # Salva a nova URL no objeto
            else:
                self.message_user(request, f"Ocorreu um erro ao salvar o laudo: {error}", level='error')
        
        super().save_model(request, obj, form, change)

@admin.register(RelatorioDesempenho)
class RelatorioDesempenhoAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'professor', 'titulo', 'data_relatorio')
    list_filter = ('aluno', 'professor', 'data_relatorio')
    search_fields = ('titulo', 'relato', 'aluno__nome_completo', 'professor__username')
    autocomplete_fields = ['aluno', 'professor'] # Facilita a busca

# =============================================================================
# ADMINISTRAÇÃO DE DÚVIDAS/FAQ
# =============================================================================

@admin.register(CategoriaFAQ)
class CategoriaFAQAdmin(admin.ModelAdmin):
    # Adicionamos 'display_icone' para mostrar o ícone na lista
    list_display = ('nome', 'display_icone') 
    search_fields = ('nome',)
    
    @admin.display(description='Ícone Atual')
    def display_icone(self, obj):
        # Renderiza a tag <i> com a classe do ícone escolhido
        if obj.icone:
            return format_html('<i class="{}" style="font-size: 20px;"></i>', obj.icone)
        return "Nenhum"

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('pergunta', 'categoria', 'fonte')
    list_filter = ('categoria',)
    search_fields = ('pergunta', 'resposta', 'fonte')

@admin.register(UserSavedFAQ)
class UserSavedFAQAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_faq_pergunta', 'get_categoria', 'data_salva')
    list_filter = ('data_salva', 'faq__categoria')
    search_fields = ('user__username', 'user__email', 'faq__pergunta')
    readonly_fields = ('data_salva',)
    date_hierarchy = 'data_salva'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'faq')
        }),
        ('Informações de Data', {
            'fields': ('data_salva',),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description='Pergunta da FAQ', ordering='faq__pergunta')
    def get_faq_pergunta(self, obj):
        return obj.faq.pergunta[:50] + "..." if len(obj.faq.pergunta) > 50 else obj.faq.pergunta
    
    @admin.display(description='Categoria', ordering='faq__categoria__nome')
    def get_categoria(self, obj):
        return obj.faq.categoria.nome
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'faq', 'faq__categoria')

# =============================================================================
# ADMINISTRAÇÃO DE CONTATOS (VERSÃO FINAL CORRIGIDA)
# =============================================================================

@admin.register(CategoriaContato)
class CategoriaContatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'display_icone')
    search_fields = ('nome',)

    @admin.display(description='Ícone Atual')
    def display_icone(self, obj):
        if obj.icone:
            return format_html('<i class="{}" style="font-size: 20px;"></i>', obj.icone)
        return "Nenhum"

# Formulário para o modelo FotoContato (Galeria)
class FotoContatoInlineForm(forms.ModelForm):
    imagem_upload = forms.ImageField(label="Upload para Galeria", required=False)

    class Meta:
        model = FotoContato
        fields = '__all__'

# Formulário para o modelo Contato (Principal)
class ContatoAdminForm(forms.ModelForm):
    imagem_upload = forms.ImageField(label="Nova Imagem Principal (Substitui a atual)", required=False)

    class Meta:
        model = Contato
        fields = '__all__'

# Formulário Inline para a galeria de fotos
class FotoContatoInline(admin.TabularInline):
    model = FotoContato
    form = FotoContatoInlineForm # Usa nosso formulário personalizado
    extra = 1
    fields = ('imagem_upload', 'display_imagem', 'legenda', 'ordem')
    readonly_fields = ('display_imagem',)

    # Método para mostrar a imagem (removi a duplicata)
    @admin.display(description='Imagem da Galeria')
    def display_imagem(self, obj):
        if obj.imagem_url:
            return format_html('<img src="{}" width="100" />', obj.imagem_url)
        return "Nenhuma imagem."

@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    form = ContatoAdminForm # Usa nosso formulário personalizado para o Contato
    inlines = [FotoContatoInline] # Mantém o formulário da galeria

    list_display = ('nome', 'categoria', 'cidade', 'display_imagem')
    list_filter = ('categoria', 'estado', 'atendimento_presencial', 'atendimento_online')
    search_fields = ('nome', 'descricao', 'cidade')
    
    readonly_fields = ('imagem_url', 'display_imagem')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'imagem_upload', 'display_imagem', 'imagem_url', 'categoria')
        }),
        ('Endereço', { 'fields': ('rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep'), 'classes': ('collapse',) }),
        ('Contato', { 'fields': ('telefone', 'email', 'site', 'horario_funcionamento') }),
        ('Redes Sociais', { 'fields': ('whatsapp', 'facebook', 'instagram', 'linkedin', 'youtube'), 'classes': ('collapse',) }),
        ('Tipo de Atendimento', { 'fields': ('atendimento_presencial', 'atendimento_online') }),
        ('Informações Adicionais', { 'fields': ('especialidades', 'convenios', 'observacoes'), 'classes': ('collapse',) }),
    )

    # Salva a IMAGEM PRINCIPAL
    def save_model(self, request, obj, form, change):
        if 'imagem_upload' in form.cleaned_data and form.cleaned_data['imagem_upload']:
            imagem_file = form.cleaned_data['imagem_upload']
            # Usa a nova função, especificando o bucket correto
            public_url, error = _upload_to_supabase(imagem_file, bucket_name="fotos-contatos", sub_folder='main')
            if public_url:
                obj.imagem_url = public_url
            else:
                self.message_user(request, f"Ocorreu um erro ao salvar a imagem principal: {error}", level='error')
        super().save_model(request, obj, form, change)

    # Salva as IMAGENS DA GALERIA
    # Salva as IMAGENS DA GALERIA (VERSÃO FINAL E ROBUSTA)
    def save_formset(self, request, form, formset, change):
        # Primeiro, executamos o comportamento padrão do Django para lidar com
        # a criação, atualização e exclusão básica dos objetos.
        # Isso garante que objetos marcados para remoção sejam deletados
        # e que objetos existentes sejam atualizados (exceto a imagem).
        super().save_formset(request, form, formset, change)

        # Agora, iteramos sobre cada formulário no formset para lidar com o UPLOAD.
        # formset.forms contém todos os formulários submetidos (novos e existentes).
        for instance_form in formset.forms:
            # Pulamos formulários que não foram alterados ou estão vazios
            if not instance_form.has_changed() and not instance_form.is_bound:
                continue

            # Verificamos se um novo arquivo foi enviado no campo 'imagem_upload'
            if 'imagem_upload' in instance_form.cleaned_data and instance_form.cleaned_data['imagem_upload']:
                
                # Pegamos o objeto de arquivo do formulário
                imagem_file = instance_form.cleaned_data['imagem_upload']
                
                # O instance_form.instance é o objeto FotoContato (novo ou existente)
                # que o Django já preparou para nós.
                instance = instance_form.instance
                
                # Fazemos o upload para o Supabase
                public_url, error = _upload_to_supabase(
                    imagem_file,
                    bucket_name="fotos-contatos",
                    sub_folder='gallery'
                )

                if public_url:
                    # Se o upload deu certo, definimos a URL da imagem...
                    instance.imagem_url = public_url
                    # ...e salvamos a instância no banco de dados.
                    # Isso é crucial para novos objetos e para atualizar existentes.
                    instance.save()
                else:
                    # Se deu erro, notificamos o administrador
                    self.message_user(request, f"Erro ao salvar uma imagem da galeria: {error}", level='error')

        # Chamamos o método save_m2m no final, que é uma boa prática para formsets.
        formset.save_m2m()

    @admin.display(description='Imagem Principal')
    def display_imagem(self, obj):
        if obj.imagem_url:
            return format_html('<img src="{}" width="150" />', obj.imagem_url)
        return "Nenhuma imagem."

@admin.register(UserSavedContato)
class UserSavedContatoAdmin(admin.ModelAdmin):
    # Código existente está correto e não precisa de alterações
    list_display = ('user', 'get_contato_nome', 'get_categoria', 'data_salva')
    list_filter = ('data_salva', 'contato__categoria')
    search_fields = ('user__username', 'user__email', 'contato__nome')
    readonly_fields = ('data_salva',)
    date_hierarchy = 'data_salva'
    
    fieldsets = (
        (None, { 'fields': ('user', 'contato') }),
        ('Informações de Data', { 'fields': ('data_salva',), 'classes': ('collapse',) }),
    )
    
    @admin.display(description='Nome do Contato', ordering='contato__nome')
    def get_contato_nome(self, obj):
        return obj.contato.nome
    
    @admin.display(description='Categoria', ordering='contato__categoria__nome')
    def get_categoria(self, obj):
        return obj.contato.categoria.nome if obj.contato.categoria else 'Sem categoria'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'contato', 'contato__categoria')


# =============================================================================
# ADMINISTRAÇÃO DE FERRAMENTAS
# =============================================================================

@admin.register(CategoriaFerramenta)
class CategoriaFerramentaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'icone')
    search_fields = ('nome',)

# --- NOVO FORMULÁRIO PARA O MODELO FERRAMENTA ---
class FerramentaAdminForm(forms.ModelForm):
    imagem_capa_upload = forms.ImageField(label="Nova Imagem de Capa (Substitui a atual)", required=False)
    arquivo_pdf_upload = forms.FileField(label="Novo Arquivo PDF (Substitui o atual)", required=False)

    class Meta:
        model = Ferramenta
        fields = '__all__'

@admin.register(Ferramenta)
class FerramentaAdmin(admin.ModelAdmin):
    form = FerramentaAdminForm # Usa o formulário personalizado
    list_display = ('nome', 'categoria', 'autor', 'publico_alvo', 'apenas_para_professores', 'eh_gratuita')
    list_filter = ('categoria', 'apenas_para_professores', 'eh_gratuita', 'publico_alvo')
    search_fields = ('nome', 'descricao', 'autor')
    autocomplete_fields = ['categoria']
    readonly_fields = ('imagem_capa_url', 'arquivo_pdf_url') # Deixa os campos de URL apenas para leitura

    fieldsets = (
        ('Informações Principais', {
            'fields': ('nome', 'categoria', 'descricao', 'autor')
        }),
        ('Arquivos e Imagens', {
            # Alterado para os novos campos de upload e URL
            'fields': ('imagem_capa_upload', 'imagem_capa_url', 'arquivo_pdf_upload', 'arquivo_pdf_url')
        }),
        ('Detalhes Pedagógicos', {
            'fields': ('publico_alvo', 'habilidades_desenvolvidas')
        }),
        ('Configurações e Acesso', {
            'fields': ('apenas_para_professores', 'eh_gratuita', 'classificacao', 'icone_classe')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Verifica se uma nova imagem de capa foi enviada
        if 'imagem_capa_upload' in form.cleaned_data and form.cleaned_data['imagem_capa_upload']:
            capa_file = form.cleaned_data['imagem_capa_upload']
            public_url, error = _upload_to_supabase(
                capa_file, 
                bucket_name="arquivos-producao", 
                sub_folder='ferramentas_capas'
            )
            if public_url:
                obj.imagem_capa_url = public_url
            else:
                self.message_user(request, f"Erro ao salvar a imagem de capa: {error}", level='error')

        # Verifica se um novo arquivo PDF foi enviado
        if 'arquivo_pdf_upload' in form.cleaned_data and form.cleaned_data['arquivo_pdf_upload']:
            pdf_file = form.cleaned_data['arquivo_pdf_upload']
            public_url, error = _upload_to_supabase(
                pdf_file, 
                bucket_name="arquivos-producao", 
                sub_folder='ferramentas_pdfs'
            )
            if public_url:
                obj.arquivo_pdf_url = public_url
            else:
                self.message_user(request, f"Erro ao salvar o arquivo PDF: {error}", level='error')
        
        super().save_model(request, obj, form, change)


@admin.register(UserDownload)
class UserDownloadAdmin(admin.ModelAdmin):
    list_display = ('user', 'ferramenta', 'data_download')
    list_filter = ('data_download',)
    search_fields = ('user__username', 'ferramenta__nome')

