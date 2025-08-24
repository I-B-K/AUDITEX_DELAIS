# delais_paiements/settings.py
import os
from pathlib import Path
import pymysql
pymysql.install_as_MySQLdb()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-remplacez-moi-avec-une-vraie-cle-secrete')

# SECURITY WARNING: don't run with debug turned on in production!
# La valeur 'False' en production est gérée via le .env
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites', # Requis par allauth

    # Applications tierces
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google', # Pour l'authentification Google

    # Votre application
    'core',
]

# Requis par django-allauth
SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware', # Ajouté pour allauth
]

ROOT_URLCONF = 'delais_paiements.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # Indique à Django où trouver les templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.pending_registrations_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'delais_paiements.wsgi.application'


# --- CONFIGURATION DE LA BASE DE DONNÉES (via variables d'environnement) ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'delais'),
        'USER': os.environ.get('DB_USER', 'IBK'),
        'PASSWORD': os.environ.get('DB_PASS', 'Masteribk2019++'),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# Internationalization
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Casablanca'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CONFIGURATION DJANGO-ALLAUTH ---
# --- CONFIGURATION DJANGO-ALLAUTH (MISE À JOUR) ---
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_ON_GET = True # Permet la déconnexion via une requête GET

# NOUVELLES CONFIGURATIONS RECOMMANDÉES
ACCOUNT_LOGIN_METHOD = 'email' # 'username' | 'email' | 'username_email'
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'none' # Mettez 'mandatory' en production si vous voulez la vérification par email


# Configuration du fournisseur Google
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
            'prompt': 'select_account',
        }
    }
}
# Pour utiliser le formulaire de connexion personnalisé
ACCOUNT_FORMS = {'login': 'core.forms.CustomLoginForm'}

