from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = "Crée ou met à jour le Site (django.contrib.sites) avec SITE_ID (defaut 1) en utilisant les variables d'env SITE_DOMAIN et SITE_NAME ou des valeurs par défaut."

    def handle(self, *args, **options):
        import os
        from django.contrib.sites.models import Site
        site_id = getattr(settings, 'SITE_ID', 1)
        domain = os.environ.get('SITE_DOMAIN') or 'localhost'
        name = os.environ.get('SITE_NAME') or 'Default'
        site, created = Site.objects.get_or_create(id=site_id, defaults={'domain': domain, 'name': name})
        changed = False
        if site.domain != domain:
            site.domain = domain
            changed = True
        if site.name != name:
            site.name = name
            changed = True
        if changed:
            site.save()
            self.stdout.write(f"SUCCESS: Site mis à jour ({site.domain})")
        elif created:
            self.stdout.write(f"SUCCESS: Site créé ({site.domain})")
        else:
            self.stdout.write("INFO: Site déjà conforme")
