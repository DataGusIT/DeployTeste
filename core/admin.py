from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html 
from .models import CategoriaFAQ, CategoriaContato, CategoriaFerramenta, FAQ, Contato, Ferramenta, CustomUser, UserDownload, UserSavedFAQ, FotoContato, UserSavedContato
import uuid
from supabase import create_client, Client
import os
from django import forms

# =============================================================================
# ADMINISTRAÇÃO DE USUÁRIOS
# =============================================================================

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_admin', 'is_staff')
    list_filter = ('is_admin', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('is_admin',)}),
    )

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
    list_display = ('pergunta', 'categoria')
    list_filter = ('categoria',)
    search_fields = ('pergunta', 'resposta')

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
# ADMINISTRAÇÃO DE CONTATOS (SEÇÃO COMPLETAMENTE ATUALIZADA)
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


# --- MUDANÇA 1: ATUALIZANDO O FORMULÁRIO DA GALERIA ---
class FotoContatoInline(admin.TabularInline):
    model = FotoContato
    extra = 1
    # Define os campos que serão exibidos no formulário inline
    fields = ('imagem_upload', 'display_imagem', 'legenda', 'ordem')
    readonly_fields = ('display_imagem',)

    # Este método adiciona dinamicamente nosso campo de upload de arquivo ao formulário
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        # Adiciona o campo de upload que não está no modelo
        form.base_fields['imagem_upload'] = forms.ImageField(label="Upload para Galeria", required=False)
        # Oculta o campo de URL para não poluir a interface, já que será preenchido automaticamente
        if 'imagem_url' in form.base_fields:
            form.base_fields['imagem_url'].widget = forms.HiddenInput()
        return formset

    @admin.display(description='Imagem da Galeria')
    def display_imagem(self, obj):
        # Mostra a imagem atual da galeria
        if obj.imagem_url:
            return format_html('<img src="{}" width="100" />', obj.imagem_url)
        return "Nenhuma imagem."


@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    # Sua configuração existente...
    list_display = ('nome', 'categoria', 'cidade', 'display_imagem')
    list_filter = ('categoria', 'estado', 'atendimento_presencial', 'atendimento_online')
    search_fields = ('nome', 'descricao', 'cidade')
    
    # Vamos manter o campo 'imagem_url' como somente leitura para evitar que editem a URL na mão
    readonly_fields = ('imagem_url', 'display_imagem')
    
    # Adicionando o campo de upload de volta ao fieldset
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'imagem_upload', 'display_imagem', 'categoria')
        }),
        ('Endereço', {
            'fields': ('rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep'),
            'classes': ('collapse',)
        }),
        ('Contato', {
            'fields': ('telefone', 'email', 'site', 'horario_funcionamento')
        }),
        ('Redes Sociais', {
            'fields': ('whatsapp', 'facebook', 'instagram', 'linkedin', 'youtube'),
            'classes': ('collapse',)
        }),
        ('Tipo de Atendimento', {
            'fields': ('atendimento_presencial', 'atendimento_online')
        }),
        ('Informações Adicionais', {
            'fields': ('especialidades', 'convenios', 'observacoes'),
            'classes': ('collapse',)
        }),
    )

    # Adiciona dinamicamente o campo de upload de arquivo ao formulário do admin
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['imagem_upload'] = forms.ImageField(label="Nova Imagem Principal (Substitui a atual)", required=False)
        return form

    @admin.display(description='Imagem Principal')
    def display_imagem(self, obj):
        if obj.imagem_url:
            return format_html('<img src="{}" width="150" />', obj.imagem_url)
        return "Nenhuma imagem."

    # --- MUDANÇA 2: FUNÇÃO AUXILIAR DE UPLOAD (PARA NÃO REPETIR CÓDIGO) ---
    def _upload_to_supabase(self, imagem_file, sub_folder=''):
        """Função auxiliar para fazer upload de um arquivo para o Supabase."""
        try:
            url: str = os.environ.get("SUPABASE_URL")
            key: str = os.environ.get("SUPABASE_KEY")
            supabase: Client = create_client(url, key)
            bucket_name: str = "fotos-contatos"

            file_ext = imagem_file.name.split('.')[-1]
            # Adiciona a subpasta ao caminho, se fornecida
            path_prefix = f"{sub_folder}/" if sub_folder else ""
            path_on_bucket = f"public/{path_prefix}{uuid.uuid4()}.{file_ext}"

            supabase.storage.from_(bucket_name).upload(
                file=imagem_file.read(),
                path=path_on_bucket,
                file_options={"content-type": imagem_file.content_type}
            )
            return supabase.storage.from_(bucket_name).get_public_url(path_on_bucket)
        except Exception as e:
            # Retorna None e a exceção para que a função que chamou possa lidar com o erro
            return None, e

    # Salva a IMAGEM PRINCIPAL
    def save_model(self, request, obj, form, change):
        imagem_file = request.FILES.get('imagem_upload')
        if imagem_file:
            public_url, error = self._upload_to_supabase(imagem_file, sub_folder='main')
            if public_url:
                obj.imagem_url = public_url
            else:
                self.message_user(request, f"Ocorreu um erro ao salvar a imagem principal: {error}", level='error')
        
        super().save_model(request, obj, form, change)

    # --- MUDANÇA 3: SALVA AS IMAGENS DA GALERIA (FOTOCONTATO) ---
    def save_formset(self, request, form, formset, change):
        # Pega as instâncias (objetos FotoContato) do formset, mas não salva ainda
        instances = formset.save(commit=False)

        # Itera sobre cada formulário no formset para verificar se um arquivo foi enviado
        for i, instance in enumerate(instances):
            # A chave do arquivo no request.FILES é construída com o prefixo do formset
            file_upload_key = f'{formset.prefix}-{i}-imagem_upload'
            
            if file_upload_key in request.FILES:
                imagem_file = request.FILES[file_upload_key]
                public_url, error = self._upload_to_supabase(imagem_file, sub_folder='gallery')
                if public_url:
                    instance.imagem_url = public_url
                else:
                    self.message_user(request, f"Erro ao salvar uma imagem da galeria: {error}", level='error')

        # Agora salva as instâncias (modificadas ou não) e lida com as exclusões
        super().save_formset(request, form, formset, change)

    # Adiciona o formulário inline da galeria ao admin do Contato
    inlines = [FotoContatoInline]

# Você pode remover o registro separado do FotoContatoAdmin se não precisar acessá-lo diretamente
# @admin.register(FotoContato) ...

@admin.register(UserSavedContato)
class UserSavedContatoAdmin(admin.ModelAdmin):
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

@admin.register(Ferramenta)
class FerramentaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'eh_gratuita', 'classificacao', 'get_tipo_funcionalidade')
    list_filter = ('categoria', 'eh_gratuita', 'tipo')
    search_fields = ('nome', 'descricao')

    @admin.display(description='Tipo de Funcionalidade')
    def get_tipo_funcionalidade(self, obj):
        return obj.tipo.nome

@admin.register(UserDownload)
class UserDownloadAdmin(admin.ModelAdmin):
    list_display = ('user', 'ferramenta', 'data_download')
    list_filter = ('data_download',)
    search_fields = ('user__username', 'ferramenta__nome')

