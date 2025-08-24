# core/models.py
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

class UserProfile(models.Model):
    """Profile utilisateur avec informations supplémentaires."""
    class StatutChoices(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', 'En attente de validation'
        VALIDE = 'VALIDE', 'Validé'
        REJETE = 'REJETE', 'Rejeté'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    registration_notes = models.TextField(verbose_name="Notes d'inscription", blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(
        max_length=20, 
        choices=StatutChoices.choices,
        default=StatutChoices.EN_ATTENTE,
        verbose_name="Statut de l'inscription"
    )
    admin_notes = models.TextField(
        verbose_name="Notes administratives", 
        blank=True,
        help_text="Notes internes sur la validation ou le rejet de l'inscription"
    )
    validation_date = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Date de validation/rejet"
    )

    class Meta:
        verbose_name = "Profil Utilisateur"
        verbose_name_plural = "Profils Utilisateurs"

    def __str__(self):
        return f"Profil de {self.user.username} ({self.get_statut_display()})"

    @property
    def is_pending(self):
        return self.statut == self.StatutChoices.EN_ATTENTE

@receiver(post_save, sender=UserProfile)
def handle_user_profile_save(sender, instance, created, **kwargs):
    """Envoie une notification à l'administrateur quand un nouveau profil est créé."""
    if created:
        # Envoi d'un email aux administrateurs
        admins = User.objects.filter(is_superuser=True)
        admin_emails = [admin.email for admin in admins if admin.email]
        if admin_emails:
            send_mail(
                'Nouvelle demande d\'inscription',
                f'Un nouvel utilisateur ({instance.user.email}) attend la validation de son compte.',
                settings.DEFAULT_FROM_EMAIL,
                admin_emails,
                fail_silently=True,
            )

class DeclarationManager(models.Manager):
    def get_queryset_for_user(self, user):
        # Règle de base : un utilisateur non authentifié ne voit rien.
        if not user or not user.is_authenticated:
            return self.none()
        
        # Les super-utilisateurs voient tout.
        if user.is_superuser:
            return super().get_queryset()
            
        # Les autres utilisateurs ne voient que les déclarations des clients qui leur sont assignés.
        return super().get_queryset().filter(client__collaborateurs=user).distinct()

class ClientManager(models.Manager):
    def get_queryset_for_user(self, user):
        # Règle de base : un utilisateur non authentifié ne voit rien.
        if not user or not user.is_authenticated:
            return self.none()
            
        # Les super-utilisateurs voient tout.
        if user.is_superuser:
            return super().get_queryset()
            
        # Les autres utilisateurs ne voient que les clients qui leur sont assignés.
        return super().get_queryset().filter(collaborateurs=user).distinct()

class Client(models.Model):
    """Représente un client de l'entreprise."""
    raison_sociale = models.CharField(max_length=255, unique=True, verbose_name="Raison Sociale")
    numero_if = models.CharField(max_length=20, unique=True, verbose_name="N° d'Identifiant Fiscal (IF)")
    numero_ice = models.CharField(max_length=30, blank=True, null=True, verbose_name="N° d'Identifiant Commun de l'Entreprise (ICE)")
    adresse = models.TextField(blank=True, null=True, verbose_name="Adresse")
    collaborateurs = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="clients_assignes", verbose_name="Collaborateurs assignés", blank=True)

    objects = models.Manager()  # Garde le manager par défaut non sécurisé pour l'admin
    secure_objects = ClientManager()  # Notre manager sécurisé pour l'application

    def __str__(self):
        return self.raison_sociale

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['raison_sociale']

class Declaration(models.Model):
    """Représente une déclaration de délai de paiement pour un client et une période."""
    # ... (le reste du modèle reste inchangé) ...
    # ... (assurez-vous que les champs et la classe Meta sont ici) ...
    class PeriodeChoices(models.IntegerChoices):
        T1 = 1, 'Trimestre 1'
        T2 = 2, 'Trimestre 2'
        T3 = 3, 'Trimestre 3'
        T4 = 4, 'Trimestre 4'

    class StatutChoices(models.TextChoices):
        DRAFT = 'DRAFT', 'Brouillon'
        SUBMITTED = 'SUBMITTED', 'Soumis'

    class TypeDeclarationChoices(models.TextChoices):
        TRIMESTRIEL = 'TRIMESTRIEL', 'Trimestriel'
        ANNUEL = 'ANNUEL', 'Annuel'

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="declarations", verbose_name="Client")
    collaborateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="declarations", verbose_name="Collaborateur")
    
    type_declaration = models.CharField(max_length=12, choices=TypeDeclarationChoices.choices, default=TypeDeclarationChoices.TRIMESTRIEL, verbose_name="Type de Déclaration")
    periode = models.IntegerField(choices=PeriodeChoices.choices, verbose_name="Période", blank=True, null=True)
    annee = models.IntegerField(verbose_name="Année")
    chiffre_affaires_n1 = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Chiffre d'affaires N-1")
    taux_directeur = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Taux Directeur (%)", blank=True, null=True)
    statut = models.CharField(max_length=10, choices=StatutChoices.choices, default=StatutChoices.DRAFT, verbose_name="Statut")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    objects = models.Manager()  # Manager par défaut
    secure_objects = DeclarationManager()  # Manager sécurisé

    def __str__(self):
        if self.type_declaration == 'ANNUEL':
            return f"Déclaration Annuelle pour {self.client.raison_sociale} - {self.annee}"
        return f"Déclaration pour {self.client.raison_sociale} - T{self.periode} {self.annee}"

    class Meta:
        unique_together = ('client', 'type_declaration', 'periode', 'annee')
        ordering = ['-annee', '-periode']
        verbose_name = "Déclaration"
        verbose_name_plural = "Déclarations"

class Facture(models.Model):
    """Représente une ligne de facture dans une déclaration."""
    declaration = models.ForeignKey(Declaration, on_delete=models.CASCADE, related_name="factures")

    class ModePaiementChoices(models.TextChoices):
        ESPECES = '1', 'Espèces'
        CHEQUE = '2', 'Chèque'
        PRELEVEMENT = '3', 'Prélèvement'
        VIREMENT = '4', 'Virement'
        EFFETS = '5', 'Effets'
        COMPENSATION = '6', 'Compensation'
        AUTRES = '7', 'Autres'

    fournisseur_if = models.CharField(max_length=20, verbose_name="N° d'IF", blank=True, null=True)
    fournisseur_ice = models.CharField(max_length=30, blank=True, null=True, verbose_name="N° d'ICE")
    fournisseur_raison_sociale = models.CharField(max_length=255, verbose_name="Nom et prénom ou raison sociale", blank=True, null=True)
    fournisseur_rc = models.CharField(max_length=50, blank=True, null=True, verbose_name="N° RC")
    fournisseur_adresse = models.CharField(max_length=255, blank=True, null=True, verbose_name="Adresse siège social")
    fournisseur_ville_rc = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ville du RC")
    numero_facture = models.CharField(max_length=100, verbose_name="N° de facture", blank=True, null=True)
    date_emission_facture = models.DateField(verbose_name="Date d'émission", blank=True, null=True)
    nature_prestation = models.CharField(max_length=255, verbose_name="Nature des marchandises, travaux ou services", blank=True, null=True)
    montant_ttc = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Montant de la facture TTC")
    date_livraison = models.DateField(verbose_name="Date de livraison/prestation", blank=True, null=True)
    mois_transaction = models.IntegerField(verbose_name="Mois (transaction périodique)", blank=True, null=True)
    annee_transaction = models.IntegerField(verbose_name="Année (transaction périodique)", blank=True, null=True)
    date_constatation_service = models.DateField(verbose_name="Date constatation service (public)", blank=True, null=True)
    date_paiement_prevue = models.DateField(verbose_name="Date prévue pour le paiement", blank=True, null=True)
    date_paiement_convenue = models.DateField(verbose_name="Date convenue pour le paiement", blank=True, null=True)
    delai_paiement_secteur = models.CharField(max_length=50, blank=True, null=True, verbose_name="Délai de paiement secteur")
    date_paiement_prevue_secteur = models.DateField(verbose_name="Date prévue paiement (secteur)", blank=True, null=True)
    montant_non_paye = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Montant non encore payé", blank=True, null=True)
    montant_paye_hors_delai = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Montant payé hors délai", blank=True, null=True)
    date_paiement_hors_delai = models.DateField(verbose_name="Date du paiement hors délai", blank=True, null=True)
    montant_objet_litige = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Montant en Litige", blank=True, null=True)
    date_recours_judiciaire = models.DateField(verbose_name="Date Recours Judiciaire", blank=True, null=True)
    montant_du_apres_jugement = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Montant Dû (Jugement)", blank=True, null=True)
    date_jugement_definitif = models.DateField(verbose_name="Date Jugement Définitif", blank=True, null=True)
    mois_suspension_amende = models.IntegerField(verbose_name="Nombre mois de suspension pénalités", blank=True, null=True)
    mode_paiement = models.CharField(max_length=2, choices=ModePaiementChoices.choices, blank=True, null=True, verbose_name="Mode de paiement")
    reference_paiement = models.CharField(max_length=100, blank=True, null=True, verbose_name="Références du paiement")
    nombre_mois_retard = models.IntegerField(verbose_name="Nombre mois de retard", blank=True, null=True)
    amende = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Amende", blank=True, null=True)

    def __str__(self):
        return f"Facture {self.numero_facture or 'N/A'}"

    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"

class ReleveFacture(models.Model):
    """Représente une ligne dans le relevé de factures d'une déclaration."""
    declaration = models.ForeignKey(Declaration, on_delete=models.CASCADE, related_name="releves_factures")

    class ModePaiementChoices(models.TextChoices):
        ESPECES = '1', 'Espèces'
        CHEQUE = '2', 'Chèque'
        PRELEVEMENT = '3', 'Prélèvement'
        VIREMENT = '4', 'Virement'
        EFFET = '5', 'Effet'
        COMPENSATION = '6', 'Compensation'
        AUTRE = '7', 'Autre'

    mois = models.IntegerField(verbose_name="Mois")
    numero_facture = models.CharField(max_length=100, verbose_name="N° Facture")
    date_facture = models.DateField(verbose_name="Date Facture")
    designation = models.CharField(max_length=255, verbose_name="Désignation des biens et services")
    nom_fournisseur = models.CharField(max_length=255, verbose_name="Nom Fournisseur")
    if_fournisseur = models.CharField(max_length=20, verbose_name="IF Fournisseur")
    ice_fournisseur = models.CharField(max_length=30, verbose_name="ICE Fournisseur")
    montant_ht = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Montant HT")
    code_tva = models.IntegerField(verbose_name="Code TVA", blank=True, null=True)
    montant_tva = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Montant TVA")
    montant_ttc = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Montant TTC")
    mode_paiement = models.CharField(max_length=20, choices=ModePaiementChoices.choices, verbose_name="Mode Paiement")
    date_paiement = models.DateField(verbose_name="Date Paiement")
    prorata = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Prorata (%)", blank=True, null=True)
    nombre_jours = models.IntegerField(verbose_name="Nombre de jours", blank=True, null=True)

    def __str__(self):
        return f"Relevé Facture {self.numero_facture} pour {self.nom_fournisseur}"

    class Meta:
        verbose_name = "Relevé de Facture"
        verbose_name_plural = "Relevés de Factures"
        ordering = ['mois', 'date_facture']

@receiver(post_save, sender=User)
def setup_new_user(sender, instance, created, **kwargs):
    """Configure les nouveaux utilisateurs."""
    if created:
        # On s'assure que l'utilisateur n'est pas un superutilisateur
        if not instance.is_superuser:
            # Ajoute l'utilisateur au groupe simpl_user
            group, created = Group.objects.get_or_create(name='simpl_user')
            instance.groups.add(group)
            # L'utilisateur reste actif immédiatement (changement : suppression de la désactivation automatique)
            # Si vous souhaitez toujours imposer une validation avant accès, rétablissez la désactivation ici.
            # instance.is_active = False
            # instance.save(update_fields=['is_active'])

            # Crée un profil utilisateur pour le suivi de l'inscription
            UserProfile.objects.create(
                user=instance,
                registration_notes=f"Inscription via Google avec l'email : {instance.email}"
            )
