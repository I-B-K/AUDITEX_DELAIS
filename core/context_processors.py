# core/context_processors.py
from core.models import UserProfile
from django.apps import apps
from django.contrib.sites.models import Site

def pending_registrations_count(request):
    """Expose le nombre d'inscriptions en attente dans le contexte global (superuser seulement)."""
    try:
        if request.user.is_authenticated and request.user.is_superuser:
            return { 'pending_registrations_count': UserProfile.objects.filter(statut='EN_ATTENTE').count() }
    except Exception:
        # En cas de migration incomplète ou autre, on évite de casser le rendu.
        return {}
    return {}


def socialapps_flags(request):
    """Indique si le provider Google est configuré (évite erreurs template)."""
    flags = { 'GOOGLE_SOCIALAPP_CONFIGURED': False }
    try:
        SocialApp = apps.get_model('socialaccount', 'SocialApp')
        if SocialApp:
            site = Site.objects.get_current(request)
            if site:
                flags['GOOGLE_SOCIALAPP_CONFIGURED'] = SocialApp.objects.filter(provider='google', sites=site).exists()
    except Exception:
        pass
    return flags
