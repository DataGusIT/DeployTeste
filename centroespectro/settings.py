# settings.py
import os
import dj_database_url  # Importe o dj-database-url
from pathlib import Path
from django.contrib.messages import constants as messages

from dotenv import load_dotenv
load_dotenv()

# ... (outras configurações como BASE_DIR)
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# CONFIGURAÇÕES DE SEGURANÇA (MUITO IMPORTANTE)
# =============================================================================

# NUNCA deixe a SECRET_KEY no código. Leia de uma variável de ambiente.
# O Render irá injetar essa variável para nós.
SECRET_KEY = os.environ.get('SECRET_KEY')

# O DEBUG deve ser False em produção.
# Lemos de uma variável de ambiente. Se não existir, o padrão é 'False'.
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# O Render nos dará o nome do host. Adicionamos ele à lista de hosts permitidos.
ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Em desenvolvimento, você pode adicionar 'localhost' e outros:
# if not RENDER_EXTERNAL_HOSTNAME:
#     ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])


# =============================================================================
# CONFIGURAÇÕES DE APLICAÇÕES E MIDDLEWARE
# =============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',  # Adicionado para WhiteNoise
    'django.contrib.staticfiles',
    'core',
    # Apps do Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    # Provedor do Google
    'allauth.socialaccount.providers.google',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Adicione o middleware do WhiteNoise logo após o SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# ... (ROOT_URLCONF, TEMPLATES, WSGI_APPLICATION continuam iguais)
ROOT_URLCONF = 'centroespectro.urls'
WSGI_APPLICATION = 'centroespectro.wsgi.application'

# ... (TEMPLATES e outras configurações)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# =============================================================================
# CONFIGURAÇÕES DE BANCO DE DADOS (USANDO dj-database-url)
# =============================================================================

DATABASES = {
    'default': dj_database_url.config(
        # O Render fornecerá a variável DATABASE_URL.
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600 # Melhora a performance mantendo conexões abertas
    )
}

# ... (AUTH_PASSWORD_VALIDATORS, I18N continuam iguais)
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# =============================================================================
# CONFIGURAÇÕES DE ARQUIVOS ESTÁTICOS (COM WHITENOISE)
# =============================================================================

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Adicione essa linha para que o WhiteNoise armazene os arquivos de forma eficiente
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ... (DEFAULT_AUTO_FIELD continua igual)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


MESSAGE_TAGS = {
    messages.DEBUG: 'info',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}


# Adicione este bloco no final do settings.py
AUTHENTICATION_BACKENDS = [
    # Necessário para logar no admin com username
    'django.contrib.auth.backends.ModelBackend',

    # Backend de autenticação do allauth
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

LOGIN_REDIRECT_URL = '/'  # Redireciona para a home após o login
LOGOUT_REDIRECT_URL = '/login/' # Redireciona para a página de login após o logout

# Configurações específicas do Allauth
ACCOUNT_EMAIL_VERIFICATION = 'optional' # ou 'mandatory'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'username_email' # Permite login com user ou email
SOCIALACCOUNT_QUERY_EMAIL = True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        # As chaves virão das variáveis de ambiente, não do banco
        'APP': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
            'secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
            'key': ''
        }
    }
}