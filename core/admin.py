from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html 
from .models import CategoriaFAQ, CategoriaContato, CategoriaFerramenta, FAQ, Contato, Ferramenta, CustomUser, UserDownload, UserSavedFAQ, FotoContato, UserSavedContato

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
# ADMINISTRAÇÃO DE CONTATOS
# =============================================================================

@admin.register(CategoriaContato)
class CategoriaContatoAdmin(admin.ModelAdmin):
    # Adicionamos 'display_icone' também aqui
    list_display = ('nome', 'display_icone')
    search_fields = ('nome',)

    @admin.display(description='Ícone Atual')
    def display_icone(self, obj):
        # Reutilizamos a mesma lógica
        if obj.icone:
            return format_html('<i class="{}" style="font-size: 20px;"></i>', obj.icone)
        return "Nenhum"

class FotoContatoInline(admin.TabularInline):
    model = FotoContato
    extra = 1
    fields = ('imagem', 'legenda', 'ordem')

@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'cidade', 'estado', 'telefone', 'email')
    list_filter = ('categoria', 'estado', 'atendimento_presencial', 'atendimento_online')
    search_fields = ('nome', 'descricao', 'cidade', 'rua', 'bairro', 'cep', 'email')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'imagem', 'categoria')
        }),
        ('Endereço', {
            'fields': ('rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep'),
            'classes': ('collapse',)  # Seção recolhível para economizar espaço
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
    
    inlines = [FotoContatoInline]

# Se você quiser registrar o modelo FotoContato separadamente também
@admin.register(FotoContato)
class FotoContatoAdmin(admin.ModelAdmin):
    list_display = ('contato', 'legenda', 'ordem')
    list_filter = ('contato',)
    search_fields = ('contato__nome', 'legenda')
    ordering = ('contato', 'ordem')

@admin.register(UserSavedContato)
class UserSavedContatoAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_contato_nome', 'get_categoria', 'data_salva')
    list_filter = ('data_salva', 'contato__categoria')
    search_fields = ('user__username', 'user__email', 'contato__nome')
    readonly_fields = ('data_salva',)
    date_hierarchy = 'data_salva'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'contato')
        }),
        ('Informações de Data', {
            'fields': ('data_salva',),
            'classes': ('collapse',)
        }),
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

