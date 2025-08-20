# delais_paiements/asgi.py
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delais_paiements.settings')
application = get_asgi_application()

# --- SEPARATOR ---

# delais_paiements/wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delais_paiements.settings')
application = get_wsgi_application()
