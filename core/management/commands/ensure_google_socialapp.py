from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = "Crée/Met à jour automatiquement la SocialApp Google si les variables d'env GOOGLE_CLIENT_ID et GOOGLE_CLIENT_SECRET sont définies."

    def handle(self, *args, **options):
        client_id = getattr(settings, 'environ', {}).get('GOOGLE_CLIENT_ID') if hasattr(settings, 'environ') else None
        # Fallback via os.environ
        import os
        client_id = client_id or os.environ.get('GOOGLE_CLIENT_ID')
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        if not client_id or not client_secret:
            self.stdout.write('WARNING: GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET non définis - skip')
            return
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.models import Site
        site_id = getattr(settings, 'SITE_ID', 1)
        site = Site.objects.filter(id=site_id).first()
        if not site:
            self.stdout.write(f"ERROR: Site id={site_id} introuvable")
            return
        app, created = SocialApp.objects.get_or_create(
            provider='google',
            name='Google OAuth',
            defaults={'client_id': client_id, 'secret': client_secret}
        )
        if not created:
            changed = False
            if app.client_id != client_id:
                app.client_id = client_id
                changed = True
            if app.secret != client_secret:
                app.secret = client_secret
                changed = True
            if changed:
                app.save()
                self.stdout.write('SUCCESS: SocialApp Google mise à jour')
        if site not in app.sites.all():
            app.sites.add(site)
        self.stdout.write('SUCCESS: SocialApp Google OK')
