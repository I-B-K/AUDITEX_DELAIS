# delais_paiements/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')), # URLs pour la connexion, déconnexion, etc.
    
    # L'URL racine redirige vers la page de connexion si l'utilisateur n'est pas authentifié.
    # Si l'utilisateur est déjà connecté, il sera redirigé vers le tableau de bord par django-allauth.
    path('', RedirectView.as_view(pattern_name='account_login', permanent=False)),
    path('', RedirectView.as_view(url='/dashboard/', permanent=True)),
    
    # Inclure les URLs de votre application 'core'
    path('', include('core.urls')),
]
