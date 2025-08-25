from django.conf import settings
from django.http import HttpResponseRedirect
import os
import logging

logger = logging.getLogger(__name__)


class ForceHTTPSMiddleware:
    """Redirige vers HTTPS si FORCE_HTTPS=1 et que la requête n'est pas déjà sécurisée.

    On se base sur X-Forwarded-Proto défini par le reverse proxy.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, 'FORCE_HTTPS', False)

    def __call__(self, request):
        if self.enabled:
            proto = request.META.get('HTTP_X_FORWARDED_PROTO') or ('https' if request.is_secure() else 'http')
            if proto != 'https':
                # Construire URL HTTPS
                url = request.build_absolute_uri().replace('http://', 'https://', 1)
                return HttpResponseRedirect(url)
        return self.get_response(request)


class HostLoggingMiddleware:
    """Loggue l'en-tête Host reçu et la liste ALLOWED_HOSTS pour diagnostiquer DisallowedHost.

    Optionnellement, si settings.DEBUG et HOST_ALLOW_WILDCARD=1, force l'acceptation de tous les hôtes
    en définissant request.META['HTTP_HOST'] sur une valeur autorisée (hack contrôlé dev seulement).
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.allow_wildcard = settings.DEBUG and os.environ.get('HOST_ALLOW_WILDCARD') == '1'

    def __call__(self, request):
        host = request.META.get('HTTP_HOST')
        logger.warning("[HostLogging] Host reçu=%s ALLOWED_HOSTS=%s wildcard=%s", host, settings.ALLOWED_HOSTS, self.allow_wildcard)
        if self.allow_wildcard and host not in settings.ALLOWED_HOSTS:
            # Injecte un host autorisé existant pour court-circuiter l'exception (debug uniquement)
            if settings.ALLOWED_HOSTS:
                request.META['HTTP_HOST'] = settings.ALLOWED_HOSTS[0]
        return self.get_response(request)
