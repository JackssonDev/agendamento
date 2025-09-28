"""
Django settings for o seu projeto.
Gerado pelo 'django-admin startproject' usando Django 5.2.6.
"""

from pathlib import Path
import os
import dj_database_url # <--- NOVO: Para configurar o PostgreSQL do Render

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# =================================================================
# VARIÁVEIS DE AMBIENTE (PRODUÇÃO)
# =================================================================

# SECURITY WARNING: keep the secret key used in production secret!
# Carrega a chave do Render. Se não encontrar (local), usa a chave local (segurança baixa)
SECRET_KEY = os.environ.get('SECRET_KEY', 'sua_secret_key_aqui')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG será False no Render e True se a variável de ambiente DEBUG for 'True' (apenas para ambiente de staging/teste)
DEBUG = os.environ.get('DEBUG', 'False') == 'True'


# Permite o acesso do Render (qualquer subdomínio *.onrender.com)
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.onrender.com']


# Application definition

INSTALLED_APPS = [
    # Jazzmin deve ser o PRIMEIRO!
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
    # <--- NOVO: Adiciona Whitenoise para servir arquivos estáticos de forma eficiente
    'whitenoise.middleware.WhiteNoiseMiddleware', 
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


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# =================================================================
# CONFIGURAÇÃO DE BANCO DE DADOS (POSTGRESQL PARA RENDER)
# =================================================================

DATABASES = {
    'default': dj_database_url.config(
        # Render irá preencher a variável DATABASE_URL com a URL do PostgreSQL
        default='sqlite:///{}'.format(BASE_DIR / 'db.sqlite3'),
        conn_max_age=600 # Tempo máximo de conexão (bom para produção)
    )
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# Necessário para o Django encontrar os arquivos estáticos
STATIC_URL = '/static/'

# Diretório onde o collectstatic irá COPIAR todos os arquivos (Jazzmin, Admin, suas apps)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 

# Diretórios onde você guarda arquivos estáticos globais do projeto (opcional)
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# <--- NOVO: Configuração do Whitenoise para produção
# Compacta e gerencia o cache dos arquivos estáticos para performance
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =================================================================
# CONFIGURAÇÕES DE SEGURANÇA (PRODUÇÃO)
# =================================================================

# Redireciona todo tráfego para HTTPS (obrigatório em produção)
SECURE_SSL_REDIRECT = True

# =================================================================
# CONFIGURAÇÕES DO DJANGO JAZZMIN (Sem Alteração)
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
    
    # Tema (Experimente: 'darkly', 'cosmo', 'materia', 'united')
    "theme": "materia",  
    
    # Cores (Use classes do Bootstrap)
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