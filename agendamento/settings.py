"""
Django settings for agendamento project.
"""

from pathlib import Path
import os
import dj_database_url # Para configurar o PostgreSQL do Render

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# =================================================================
# VARIÁVEIS DE AMBIENTE E SEGURANÇA (PRODUÇÃO)
# =================================================================

# Carrega a chave do Render. Se não encontrar (local), usa a chave local.
SECRET_KEY = os.environ.get('SECRET_KEY', 'sua_secret_key_aqui_para_uso_local_apenas') 

# DEBUG será False no Render e True se a variável de ambiente DEBUG for 'True'.
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Permite o acesso do Render
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.onrender.com']


# === NOVAS CONFIGURAÇÕES DE SEGURANÇA PARA HTTPS (DEBUG=False) ===

SECURE_SSL_REDIRECT = True 
SECURE_HSTS_SECONDS = 31536000 
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True 
CSRF_COOKIE_SECURE = True 
SESSION_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True


INSTALLED_APPS = [
    'jazzmin', 
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Suas Apps
    'agendamentos',
    # 'sua_outra_app', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Para servir estáticos em produção
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'agendamento.urls' 

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'agendamento.wsgi.application'

# =================================================================
# CONFIGURAÇÃO DE BANCO DE DADOS (POSTGRESQL PARA RENDER)
# =================================================================

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///{}'.format(BASE_DIR / 'db.sqlite3'),
        conn_max_age=600
    )
}

# =================================================================
# VALIDAÇÃO DE SENHA E I18N
# =================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True

# =================================================================
# CONFIGURAÇÃO DE ARQUIVOS (STATIC E MEDIA)
# =================================================================

# Configuração de Mídia (Upload de Imagens)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configuração de Estáticos (CSS, JS)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Whitenoise para produção
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =================================================================
# CONFIGURAÇÕES DO DJANGO JAZZMIN
# =================================================================

JAZZMIN_SETTINGS = {
    "site_title": "PetCare Agendamento",
    "site_header": "PetCare Admin",
    "welcome_sign": "Bem-vindo(a) à administração do PetCare",
    "index_title": "Painel de Controle",
    
    # Customização de Ícones (Font Awesome 5+)
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "agendamentos.agendamento": "fas fa-calendar-check",
        "agendamentos.servico": "fas fa-paw",
        "agendamentos.pet": "fas fa-dog",
        "agendamentos.perfilusuario": "fas fa-address-card",
    },
    
    # Ordenação do Menu Lateral
    "order_with_respect_to": ["agendamentos", "auth"],
    
    # ==================== UI Tweaks (Visual) ====================
    "show_sidebar": True,
    "navigation_expanded": True,
    
    "theme": "materia",  
    
    "navbar_classes": "navbar-dark bg-info",
    "sidebar_classes": "sidebar-light-primary", 
    "body_classes": "hold-transition sidebar-mini",
    
    "search_model": "agendamentos.agendamento",
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "sidebar_fixed": True,
    "sidebar_hoverable": False,
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme_classes": [],
    "dark_mode_vars": {},
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}