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

_raw_hosts = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1', 'http://http://10.211.0.249.nip.io:8080')
ALLOWED_HOSTS = [h.strip() for h in _raw_hosts.split(',') if h.strip()]
# Ajout automatique du domaine nip.io correspondant à une IP publique si fourni
PUBLIC_IP = os.environ.get('PUBLIC_IP')
if PUBLIC_IP:
    nip_host = f"{PUBLIC_IP}.nip.io"
    if nip_host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(nip_host)


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
    'core.middleware.ForceHTTPSMiddleware',  # Redirection HTTPS optionnelle
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
                'core.context_processors.socialapps_flags',
            ],
        },
    },
]

WSGI_APPLICATION = 'delais_paiements.wsgi.application'


# --- CONFIGURATION DE LA BASE DE DONNÉES (via variables d'environnement) ---
# Fallback intelligent :
#  - Dans Docker : host par défaut = 'db' (service docker-compose)
#  - Hors Docker : host par défaut = '127.0.0.1' et si port mappé externe 3307 utilisé, on peut définir DB_PORT=3307 dans .env
IN_DOCKER = os.environ.get('RUNNING_IN_DOCKER') == '1' or os.path.exists('/.dockerenv')

# Hôte par défaut : nom de service Docker dans le conteneur, loopback hors Docker
DEFAULT_DB_HOST = 'db' if IN_DOCKER else '127.0.0.1'

# On lit d'abord la variable d'environnement éventuelle
DB_HOST = os.environ.get('DB_HOST', DEFAULT_DB_HOST)

# Si on N'EST PAS dans Docker mais que l'utilisateur a laissé 'db' (nom de service compose),
# on effectue un fallback automatique pour éviter l'erreur de résolution locale.
if not IN_DOCKER and DB_HOST in {'db', 'mysql', 'mariadb'}:
    DB_HOST = '127.0.0.1'

# Port : 3306 par défaut (le port interne). On laisse la possibilité de le surcharger.
# (Si vous mappez le conteneur sur 3307 en local, définissez DB_PORT=3307 dans le .env)
DB_PORT = os.environ.get('DB_PORT', '3306')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'delais'),
        'USER': os.environ.get('DB_USER', 'IBK'),
        'PASSWORD': os.environ.get('DB_PASS', 'Masteribk2019++'),
        'HOST': DB_HOST,
        'PORT': DB_PORT,
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
# Le répertoire où `collectstatic` placera tous les fichiers statiques pour la production.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CONFIGURATION DJANGO-ALLAUTH ---
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# URLs de redirection
LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Configuration de base allauth (API récente sans paramètres dépréciés)
# Ancien: ACCOUNT_AUTHENTICATION_METHOD, remplacé par ACCOUNT_LOGIN_METHODS
ACCOUNT_LOGIN_METHODS = {'username', 'email'}
# Champs d'inscription (suffixe * = requis)
ACCOUNT_SIGNUP_FIELDS = ['username*', 'email*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_USERNAME_MIN_LENGTH = 3
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_UNIQUE_EMAIL = True
# Rate limiting (remplace LOGIN_ATTEMPTS_LIMIT/TIMEOUT) : 5 tentatives sur 5 min
ACCOUNT_RATE_LIMITS = { 'login_failed': '5/5m' }

# Configuration des formulaires
ACCOUNT_FORMS = {
    'login': 'core.forms.CustomLoginForm'
}


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

# --- Sécurité / reverse proxy ---
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = False  # Mettre True si derrière HTTPS
CSRF_COOKIE_SECURE = False     # Idem
X_FRAME_OPTIONS = 'SAMEORIGIN'
REFERRER_POLICY = 'strict-origin-when-cross-origin'
CSRF_TRUSTED_ORIGINS = [f"http://{h}" for h in ALLOWED_HOSTS if h] + [f"https://{h}" for h in ALLOWED_HOSTS if h]

# Activer la redirection HTTPS si variable d'environnement FORCE_HTTPS=1
FORCE_HTTPS = os.environ.get('FORCE_HTTPS') == '1'

