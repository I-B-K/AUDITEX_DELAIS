# core/admin.py
from django.contrib import admin
from .models import Client, Declaration, Facture

class FactureInline(admin.TabularInline):
    """Permet d'éditer les factures directement depuis la page de déclaration."""
    model = Facture
    extra = 0 # N'affiche pas de champ de facture vide par défaut dans l'admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil'
    fields = ('registration_notes', 'statut', 'admin_notes', 'registration_date', 'validation_date')
    readonly_fields = ('registration_date', 'validation_date')

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

# Annuler l'enregistrement de l'admin User par défaut
admin.site.unregister(User)
# Enregistrer notre UserAdmin personnalisé
admin.site.register(User, UserAdmin)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('raison_sociale', 'numero_if', 'numero_ice')
    search_fields = ('raison_sociale', 'numero_if')
    filter_horizontal = ('collaborateurs',)  # Améliore l'interface pour les ManyToManyFields

@admin.register(Declaration)
class DeclarationAdmin(admin.ModelAdmin):
    list_display = ('client', 'annee', 'periode', 'statut', 'collaborateur', 'date_modification')
    list_filter = ('statut', 'annee', 'client')
    search_fields = ('client__raison_sociale',)
    inlines = [FactureInline]

@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ('numero_facture', 'declaration', 'fournisseur_raison_sociale', 'montant_ttc', 'date_emission_facture')
    search_fields = ('numero_facture', 'fournisseur_raison_sociale')
    list_filter = ('declaration__client',)