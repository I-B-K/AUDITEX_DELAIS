# core/admin.py
from django.contrib import admin
from .models import Client, Declaration, Facture

class FactureInline(admin.TabularInline):
    """Permet d'éditer les factures directement depuis la page de déclaration."""
    model = Facture
    extra = 0 # N'affiche pas de champ de facture vide par défaut dans l'admin

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('raison_sociale', 'numero_if', 'numero_ice')
    search_fields = ('raison_sociale', 'numero_if')

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