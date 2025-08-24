# core/context_processors.py
from core.models import UserProfile

def pending_registrations_count(request):
    """Expose le nombre d'inscriptions en attente dans le contexte global (superuser seulement)."""
    try:
        if request.user.is_authenticated and request.user.is_superuser:
            return { 'pending_registrations_count': UserProfile.objects.filter(statut='EN_ATTENTE').count() }
    except Exception:
        # En cas de migration incomplète ou autre, on évite de casser le rendu.
        return {}
    return {}
