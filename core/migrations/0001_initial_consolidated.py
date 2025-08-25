from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):
    """Migration initiale consolidée (remplace les migrations 0001 -> 0020 précédentes).

    ATTENTION: Si une base de données existe déjà avec l'historique des anciennes migrations,
    appliquez cette migration avec --fake OU repartez d'une base vide (drop & recreate).
    """

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raison_sociale', models.CharField(max_length=255, unique=True, verbose_name='Raison Sociale')),
                ('numero_if', models.CharField(max_length=20, unique=True, verbose_name="N° d'Identifiant Fiscal (IF)")),
                ('numero_ice', models.CharField(blank=True, null=True, max_length=30, verbose_name="N° d'Identifiant Commun de l'Entreprise (ICE)")),
                ('adresse', models.TextField(blank=True, null=True, verbose_name='Adresse')),
            ],
            options={
                'verbose_name': 'Client',
                'verbose_name_plural': 'Clients',
                'ordering': ['raison_sociale'],
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_notes', models.TextField(blank=True, verbose_name="Notes d'inscription")),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('statut', models.CharField(choices=[('EN_ATTENTE', 'En attente de validation'), ('VALIDE', 'Validé'), ('REJETE', 'Rejeté')], default='EN_ATTENTE', max_length=20, verbose_name="Statut de l'inscription")),
                ('admin_notes', models.TextField(blank=True, help_text="Notes internes sur la validation ou le rejet de l'inscription", verbose_name='Notes administratives')),
                ('validation_date', models.DateTimeField(blank=True, null=True, verbose_name='Date de validation/rejet')),
                ('user', models.OneToOneField(on_delete=models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Profil Utilisateur',
                'verbose_name_plural': 'Profils Utilisateurs',
            },
        ),
        migrations.CreateModel(
            name='Declaration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_declaration', models.CharField(choices=[('TRIMESTRIEL', 'Trimestriel'), ('ANNUEL', 'Annuel')], default='TRIMESTRIEL', max_length=12, verbose_name='Type de Déclaration')),
                ('periode', models.IntegerField(blank=True, choices=[(1, 'Trimestre 1'), (2, 'Trimestre 2'), (3, 'Trimestre 3'), (4, 'Trimestre 4')], null=True, verbose_name='Période')),
                ('annee', models.IntegerField(verbose_name='Année')),
                ("chiffre_affaires_n1", models.DecimalField(decimal_places=2, max_digits=15, verbose_name="Chiffre d'affaires N-1")),
                ('taux_directeur', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Taux Directeur (%)')),
                ('statut', models.CharField(choices=[('DRAFT', 'Brouillon'), ('SUBMITTED', 'Soumis')], default='DRAFT', max_length=10, verbose_name='Statut')),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='declarations', to='core.client', verbose_name='Client')),
                ('collaborateur', models.ForeignKey(null=True, on_delete=models.deletion.SET_NULL, related_name='declarations', to=settings.AUTH_USER_MODEL, verbose_name='Collaborateur')),
            ],
            options={
                'verbose_name': 'Déclaration',
                'verbose_name_plural': 'Déclarations',
                'ordering': ['-annee', '-periode'],
                'unique_together': {('client', 'type_declaration', 'periode', 'annee')},
            },
        ),
        migrations.CreateModel(
            name='Facture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fournisseur_if', models.CharField(blank=True, max_length=20, null=True, verbose_name="N° d'IF")),
                ('fournisseur_ice', models.CharField(blank=True, max_length=30, null=True, verbose_name="N° d'ICE")),
                ('fournisseur_raison_sociale', models.CharField(blank=True, max_length=255, null=True, verbose_name='Nom et prénom ou raison sociale')),
                ('fournisseur_rc', models.CharField(blank=True, max_length=50, null=True, verbose_name='N° RC')),
                ('fournisseur_adresse', models.CharField(blank=True, max_length=255, null=True, verbose_name='Adresse siège social')),
                ('fournisseur_ville_rc', models.CharField(blank=True, max_length=100, null=True, verbose_name='Ville du RC')),
                ('numero_facture', models.CharField(blank=True, max_length=100, null=True, verbose_name='N° de facture')),
                ("date_emission_facture", models.DateField(blank=True, null=True, verbose_name="Date d'émission")),
                ('nature_prestation', models.CharField(blank=True, max_length=255, null=True, verbose_name='Nature des marchandises, travaux ou services')),
                ('montant_ttc', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Montant de la facture TTC')),
                ('date_livraison', models.DateField(blank=True, null=True, verbose_name='Date de livraison/prestation')),
                ('mois_transaction', models.IntegerField(blank=True, null=True, verbose_name='Mois (transaction périodique)')),
                ('annee_transaction', models.IntegerField(blank=True, null=True, verbose_name='Année (transaction périodique)')),
                ('date_constatation_service', models.DateField(blank=True, null=True, verbose_name='Date constatation service (public)')),
                ('date_paiement_prevue', models.DateField(blank=True, null=True, verbose_name='Date prévue pour le paiement')),
                ('date_paiement_convenue', models.DateField(blank=True, null=True, verbose_name='Date convenue pour le paiement')),
                ('delai_paiement_secteur', models.CharField(blank=True, max_length=50, null=True, verbose_name='Délai de paiement secteur')),
                ('date_paiement_prevue_secteur', models.DateField(blank=True, null=True, verbose_name='Date prévue paiement (secteur)')),
                ('montant_non_paye', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Montant non encore payé')),
                ('montant_paye_hors_delai', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Montant payé hors délai')),
                ('date_paiement_hors_delai', models.DateField(blank=True, null=True, verbose_name='Date du paiement hors délai')),
                ('montant_objet_litige', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Montant en Litige')),
                ('date_recours_judiciaire', models.DateField(blank=True, null=True, verbose_name='Date Recours Judiciaire')),
                ('montant_du_apres_jugement', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Montant Dû (Jugement)')),
                ('date_jugement_definitif', models.DateField(blank=True, null=True, verbose_name='Date Jugement Définitif')),
                ('mois_suspension_amende', models.IntegerField(blank=True, null=True, verbose_name='Nombre mois de suspension pénalités')),
                ('mode_paiement', models.CharField(blank=True, choices=[('1', 'Espèces'), ('2', 'Chèque'), ('3', 'Prélèvement'), ('4', 'Virement'), ('5', 'Effets'), ('6', 'Compensation'), ('7', 'Autres')], max_length=2, null=True, verbose_name='Mode de paiement')),
                ('reference_paiement', models.CharField(blank=True, max_length=100, null=True, verbose_name='Références du paiement')),
                ('nombre_mois_retard', models.IntegerField(blank=True, null=True, verbose_name='Nombre mois de retard')),
                ('amende', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Amende')),
                ('declaration', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='factures', to='core.declaration')),
            ],
            options={
                'verbose_name': 'Facture',
                'verbose_name_plural': 'Factures',
            },
        ),
        migrations.CreateModel(
            name='ReleveFacture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mois', models.IntegerField(verbose_name='Mois')),
                ('numero_facture', models.CharField(max_length=100, verbose_name='N° Facture')),
                ('date_facture', models.DateField(verbose_name='Date Facture')),
                ('designation', models.CharField(max_length=255, verbose_name='Désignation des biens et services')),
                ('nom_fournisseur', models.CharField(max_length=255, verbose_name='Nom Fournisseur')),
                ('if_fournisseur', models.CharField(max_length=20, verbose_name='IF Fournisseur')),
                ('ice_fournisseur', models.CharField(max_length=30, verbose_name='ICE Fournisseur')),
                ('montant_ht', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Montant HT')),
                ('code_tva', models.IntegerField(blank=True, null=True, verbose_name='Code TVA')),
                ('montant_tva', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Montant TVA')),
                ('montant_ttc', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Montant TTC')),
                ('mode_paiement', models.CharField(choices=[('1', 'Espèces'), ('2', 'Chèque'), ('3', 'Prélèvement'), ('4', 'Virement'), ('5', 'Effet'), ('6', 'Compensation'), ('7', 'Autre')], max_length=20, verbose_name='Mode Paiement')),
                ('date_paiement', models.DateField(verbose_name='Date Paiement')),
                ('prorata', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Prorata (%)')),
                ('nombre_jours', models.IntegerField(blank=True, null=True, verbose_name='Nombre de jours')),
                ('declaration', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='releves_factures', to='core.declaration')),
            ],
            options={
                'verbose_name': 'Relevé de Facture',
                'verbose_name_plural': 'Relevés de Factures',
                'ordering': ['mois', 'date_facture'],
            },
        ),
        migrations.AddField(
            model_name='client',
            name='collaborateurs',
            field=models.ManyToManyField(blank=True, related_name='clients_assignes', to=settings.AUTH_USER_MODEL, verbose_name='Collaborateurs assignés'),
        ),
    ]
