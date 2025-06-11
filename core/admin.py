from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CategoriaFAQ, CategoriaContato, CategoriaFerramenta, FAQ, Contato, Ferramenta, CustomUser, UserDownload, UserSavedFAQ,  FotoContato

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
    list_display = ('nome', 'icone')
    search_fields = ('nome',)

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
    list_display = ('nome', 'icone')
    search_fields = ('nome',)

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