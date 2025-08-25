from django.conf import settings
from django.http import HttpResponseRedirect


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
