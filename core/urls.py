from django.urls import path
from . import views

# =============================================================================
# ROTAS PRINCIPAIS DO SITE
# =============================================================================

urlpatterns = [
    path('', views.index, name='index'),
    path('sobre/', views.sobre, name='sobre'),
    path('privacy/', views.privacy, name='privacy'),
    path('documentos/', views.document_list, name='document_list'),
]

# =============================================================================
# ROTAS DE FERRAMENTAS
# =============================================================================

urlpatterns += [
    path('ferramentas/', views.ferramentas, name='ferramentas'),
    path('ferramentas/detalhes/<int:id>/', views.detalhes_ferramenta, name='detalhes_ferramenta'),
    path('ferramenta/<int:ferramenta_id>/download/', views.register_download, name='register_download'),
]

# =============================================================================
# ROTAS DE DÚVIDAS/FAQ
# =============================================================================

urlpatterns += [
    path('duvidas/', views.duvidas, name='duvidas'),
    path('pesquisar-faqs/', views.pesquisar_faqs, name='pesquisar_faqs'),
    path('salvar-faq/<int:faq_id>/', views.salvar_faq, name='salvar_faq'),
    path('remover-faq/<int:faq_id>/', views.remover_faq_salva, name='remover_faq_salva'),
]

# =============================================================================
# ROTAS DE CONTATOS
# =============================================================================

urlpatterns += [
    path('contatos/', views.contatos, name='contatos'),
    path('contatos/<int:id>/', views.detalhes_contato, name='detalhes_contato'),
    path('salvar-contato/<int:contato_id>/', views.salvar_contato, name='salvar_contato'),
    path('remover-contato/<int:contato_id>/', views.remover_contato_salvo, name='remover_contato_salvo'),
]

# =============================================================================
# ROTAS DE AUTENTICAÇÃO
# =============================================================================

urlpatterns += [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cadastro/', views.register_view, name='register'),
    path('perfil/', views.profile_view, name='profile'),
]

# =============================================================================
# ROTAS DE NEWSLETTER
# =============================================================================

urlpatterns += [
    path('newsletter/signup/', views.newsletter_signup, name='newsletter_signup'),
]

# =============================================================================
# ROTAS DE ADMINISTRAÇÃO - DASHBOARD
# =============================================================================

urlpatterns += [
    path('administracao/', views.admin_dashboard, name='admin_dashboard'),
]

# =============================================================================
# ROTAS DE ADMINISTRAÇÃO - CATEGORIAS FAQ
# =============================================================================

urlpatterns += [
    path('administracao/categorias-faq/', views.admin_categorias_faq, name='admin_categorias_faq'),
    path('administracao/categorias-faq/criar/', views.admin_categoria_faq_criar, name='admin_categoria_faq_criar'),
    path('administracao/categorias-faq/editar/<int:id>/', views.admin_categoria_faq_editar, name='admin_categoria_faq_editar'),
    path('administracao/categorias-faq/excluir/<int:id>/', views.admin_categoria_faq_excluir, name='admin_categoria_faq_excluir'),
]

# =============================================================================
# ROTAS DE ADMINISTRAÇÃO - FAQs
# =============================================================================

urlpatterns += [
    path('administracao/faqs/', views.admin_faqs, name='admin_faqs'),
    path('administracao/faqs/criar/', views.admin_faq_criar, name='admin_faq_criar'),
    path('administracao/faqs/editar/<int:id>/', views.admin_faq_editar, name='admin_faq_editar'),
    path('administracao/faqs/excluir/<int:id>/', views.admin_faq_excluir, name='admin_faq_excluir'),
]

# =============================================================================
# ROTAS DE ADMINISTRAÇÃO - CATEGORIAS CONTATO
# =============================================================================

urlpatterns += [
    path('administracao/categorias-contato/', views.admin_categorias_contato, name='admin_categorias_contato'),
    path('administracao/categorias-contato/criar/', views.admin_categoria_contato_criar, name='admin_categoria_contato_criar'),
    path('administracao/categorias-contato/editar/<int:id>/', views.admin_categoria_contato_editar, name='admin_categoria_contato_editar'),
    path('administracao/categorias-contato/excluir/<int:id>/', views.admin_categoria_contato_excluir, name='admin_categoria_contato_excluir'),
]

# =============================================================================
# ROTAS DE ADMINISTRAÇÃO - CONTATOS
# =============================================================================

urlpatterns += [
    path('administracao/contatos/', views.admin_contatos, name='admin_contatos'),
    path('administracao/contatos/criar/', views.admin_contato_criar, name='admin_contato_criar'),
    path('administracao/contatos/editar/<int:id>/', views.admin_contato_editar, name='admin_contato_editar'),
    path('administracao/contatos/excluir/<int:id>/', views.admin_contato_excluir, name='admin_contato_excluir'),
]

# =============================================================================
# ROTAS DE ADMINISTRAÇÃO - CATEGORIAS FERRAMENTA
# =============================================================================

urlpatterns += [
    path('administracao/categorias-ferramenta/', views.admin_categorias_ferramenta, name='admin_categorias_ferramenta'),
    path('administracao/categorias-ferramenta/criar/', views.admin_categoria_ferramenta_criar, name='admin_categoria_ferramenta_criar'),
    path('administracao/categorias-ferramenta/editar/<int:id>/', views.admin_categoria_ferramenta_editar, name='admin_categoria_ferramenta_editar'),
    path('administracao/categorias-ferramenta/excluir/<int:id>/', views.admin_categoria_ferramenta_excluir, name='admin_categoria_ferramenta_excluir'),
]

# =============================================================================
# ROTAS DE ADMINISTRAÇÃO - FERRAMENTAS
# =============================================================================

urlpatterns += [
    path('administracao/ferramentas/', views.admin_ferramentas, name='admin_ferramentas'),
    path('administracao/ferramentas/criar/', views.admin_ferramenta_criar, name='admin_ferramenta_criar'),
    path('administracao/ferramentas/editar/<int:id>/', views.admin_ferramenta_editar, name='admin_ferramenta_editar'),
    path('administracao/ferramentas/excluir/<int:id>/', views.admin_ferramenta_excluir, name='admin_ferramenta_excluir'),
]



