# core/forms.py
from django import forms
from django.forms import inlineformset_factory
from core.models import Declaration, Facture, Client
from datetime import date
from allauth.account.forms import LoginForm
import datetime

class CustomLoginForm(LoginForm):
    """Surcharge le formulaire de connexion pour le styliser avec Tailwind."""
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['login'].label = ""
        self.fields['login'].widget.attrs.update({
            'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm',
            'placeholder': 'Adresse e-mail'
        })
        self.fields['password'].label = ""
        self.fields['password'].widget.attrs.update({
            'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm',
            'placeholder': 'Mot de passe'
        })

        if 'remember' in self.fields:
            self.fields['remember'].widget.attrs.update({
                'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'
            })

class DeclarationForm(forms.ModelForm):
    """Formulaire pour créer une nouvelle déclaration."""
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        label="Client",
        empty_label="--- Sélectionnez un client ---",
        widget=forms.Select(attrs={'class': 'mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md'})
    )

    class Meta:
        model = Declaration
        fields = ['client', 'type_declaration', 'periode', 'annee', 'chiffre_affaires_n1', 'taux_directeur']
        labels = {
            'type_declaration': 'Type de Déclaration',
            'periode': 'Période (Trimestre)',
            'chiffre_affaires_n1': "Chiffre d'affaires N-1",
            'taux_directeur': 'Taux Directeur (%)',
        }
        widgets = {
            'type_declaration': forms.Select(attrs={'class': 'mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md'}),
            'periode': forms.Select(attrs={'class': 'mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md'}),
            'annee': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'value': date.today().year
            }),
            'chiffre_affaires_n1': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'placeholder': "Montant en MAD"
            }),
            'taux_directeur': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'placeholder': "Ex: 3.00"
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        type_declaration = cleaned_data.get("type_declaration")
        periode = cleaned_data.get("periode")

        if type_declaration == 'ANNUEL':
            cleaned_data['periode'] = None
        
        if type_declaration == 'TRIMESTRIEL' and not periode:
            self.add_error('periode', "La période est requise pour une déclaration trimestrielle.")
            
        return cleaned_data

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['raison_sociale', 'numero_if', 'numero_ice', 'adresse']
        widgets = {
            'raison_sociale': forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm'}),
            'numero_if': forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm'}),
            'numero_ice': forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm'}),
            'adresse': forms.Textarea(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm', 'rows': 3}),
        }

class FactureForm(forms.ModelForm):
    """Formulaire pour une seule facture, avec tous les champs."""
    
    MONTH_CHOICES = [
        ('', '---'), (1, 'Janvier'), (2, 'Février'), (3, 'Mars'), (4, 'Avril'),
        (5, 'Mai'), (6, 'Juin'), (7, 'Juillet'), (8, 'Août'),
        (9, 'Septembre'), (10, 'Octobre'), (11, 'Novembre'), (12, 'Décembre')
    ]
    current_year = datetime.date.today().year
    YEAR_CHOICES = [('', '---')] + [(year, year) for year in range(current_year - 5, current_year + 6)]

    mois_transaction = forms.TypedChoiceField(
        choices=MONTH_CHOICES, coerce=int, empty_value=None, required=False,
        widget=forms.Select(attrs={'class': 'w-full border-none rounded p-1 bg-transparent focus:ring-0 text-xs'})
    )
    annee_transaction = forms.TypedChoiceField(
        choices=YEAR_CHOICES, coerce=int, empty_value=None, required=False,
        widget=forms.Select(attrs={'class': 'w-full border-none rounded p-1 bg-transparent focus:ring-0 text-xs'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def clean(self):
        cleaned_data = super().clean()
        
        if not self.has_changed():
            return cleaned_data

        # --- Règle 1 : Champs de base requis ---
        required_fields = {
            'fournisseur_if': "N° d'IF", 'fournisseur_ice': "N° d'ICE", 
            'fournisseur_raison_sociale': "Raison Sociale", 'fournisseur_rc': "N° RC",
            'fournisseur_adresse': "Adresse", 'fournisseur_ville_rc': "Ville du RC",
            'numero_facture': "N° Facture", 'date_emission_facture': "Date Émission",
            'nature_prestation': "Nature Prestation", 'montant_ttc': "Montant TTC"
        }
        for field_name, field_label in required_fields.items():
            if not cleaned_data.get(field_name):
                self.add_error(field_name, f"Le champ '{field_label}' est obligatoire.")

        # --- Règle 2 : Validation de la date de livraison/prestation ---
        date_livraison = cleaned_data.get("date_livraison")
        mois_transaction = cleaned_data.get("mois_transaction")
        annee_transaction = cleaned_data.get("annee_transaction")
        date_constatation_service = cleaned_data.get("date_constatation_service")

        option1_filled = bool(date_livraison)
        option2_filled = bool(mois_transaction and annee_transaction)
        option3_filled = bool(date_constatation_service)

        filled_options_count_livraison = sum([option1_filled, option2_filled, option3_filled])

        if filled_options_count_livraison == 0:
            self.add_error(None, forms.ValidationError(
                "Info Livraison : Veuillez remplir soit la 'Date Livraison', soit 'Mois/Année', soit la 'Date Constatation Service'."
            ))
        
        if filled_options_count_livraison > 1:
            self.add_error(None, forms.ValidationError(
                "Info Livraison : Veuillez ne remplir qu'une seule des options suivantes : 'Date Livraison', 'Mois/Année', ou 'Date Constatation Service'."
            ))

        # --- Règle 3 : Validation de la date de paiement ---
        date_paiement_prevue = cleaned_data.get("date_paiement_prevue")
        date_paiement_convenue = cleaned_data.get("date_paiement_convenue")
        delai_paiement_secteur = cleaned_data.get("delai_paiement_secteur")
        date_paiement_prevue_secteur = cleaned_data.get("date_paiement_prevue_secteur")

        option_paie_1_filled = bool(date_paiement_prevue)
        option_paie_2_filled = bool(date_paiement_convenue)
        option_paie_3_filled = bool(delai_paiement_secteur and date_paiement_prevue_secteur)

        filled_options_count_paiement = sum([option_paie_1_filled, option_paie_2_filled, option_paie_3_filled])

        if filled_options_count_paiement == 0:
            self.add_error(None, forms.ValidationError(
                "Info Paiement : Veuillez remplir soit la 'Date Paiement Prévue', soit la 'Date Paiement Convenue', soit 'Délai Secteur' et 'Date Prévue Secteur'."
            ))
        
        if filled_options_count_paiement > 1:
            self.add_error(None, forms.ValidationError(
                "Info Paiement : Veuillez ne remplir qu'une seule des options suivantes : 'Date Paiement Prévue', 'Date Paiement Convenue', ou 'Délai/Date Secteur'."
            ))
            
        # --- Règle 4 : Validation du montant payé / non payé ---
        montant_non_paye = cleaned_data.get("montant_non_paye")
        montant_paye_hors_delai = cleaned_data.get("montant_paye_hors_delai")
        date_paiement_hors_delai = cleaned_data.get("date_paiement_hors_delai")

        option_montant_1_filled = montant_non_paye is not None
        option_montant_2_filled = montant_paye_hors_delai is not None

        if option_montant_1_filled and option_montant_2_filled:
            self.add_error(None, forms.ValidationError(
                "Info Montant : Veuillez ne remplir qu'un seul des deux champs : 'Montant Non Payé' ou 'Montant Payé Hors Délai'."
            ))

        if not option_montant_1_filled and not option_montant_2_filled:
            self.add_error(None, forms.ValidationError(
                "Info Montant : Veuillez remplir soit le 'Montant Non Payé', soit le 'Montant Payé Hors Délai'."
            ))
        
        if montant_paye_hors_delai is not None and not date_paiement_hors_delai:
            self.add_error('date_paiement_hors_delai', "Ce champ est requis avec le 'Montant Payé Hors Délai'.")
        
        if montant_paye_hors_delai is None and date_paiement_hors_delai:
             self.add_error('date_paiement_hors_delai', "Ce champ doit être vide si le 'Montant Payé Hors Délai' est vide.")

        # --- Règle 5 : Validation de la section Litige ---
        montant_objet_litige = cleaned_data.get("montant_objet_litige")
        if montant_objet_litige is not None and montant_objet_litige > 0:
            litige_fields = {
                'date_recours_judiciaire': "Date Recours Judiciaire",
                'montant_du_apres_jugement': "Montant Dû (Jugement)",
                'date_jugement_definitif': "Date Jugement Définitif"
            }
            for field_name, field_label in litige_fields.items():
                if not cleaned_data.get(field_name):
                    self.add_error(field_name, f"Ce champ est requis car un montant est en litige.")

        # --- Règle 6 : Validation du mode et de la référence de paiement ---
        mode_paiement = cleaned_data.get("mode_paiement")
        reference_paiement = cleaned_data.get("reference_paiement")

        if montant_paye_hors_delai is not None:
            if not mode_paiement:
                self.add_error('mode_paiement', forms.ValidationError(
                    "Ce champ est requis lorsque le 'Montant Payé Hors Délai' est renseigné."
                ))
            if not reference_paiement:
                self.add_error('reference_paiement', forms.ValidationError(
                    "Ce champ est requis lorsque le 'Montant Payé Hors Délai' est renseigné."
                ))

        return cleaned_data

    class Meta:
        model = Facture
        exclude = ('declaration',)
        
        input_class = 'w-full border-none rounded p-1 bg-transparent focus:ring-0 text-xs'
        select_class = 'w-full border-none rounded p-1 bg-transparent focus:ring-0 text-xs'
        date_attrs = {'type': 'date', 'class': input_class}
        widgets = {
            'fournisseur_if': forms.TextInput(attrs={'class': input_class}),
            'fournisseur_ice': forms.TextInput(attrs={'class': input_class}),
            'fournisseur_raison_sociale': forms.TextInput(attrs={'class': input_class}),
            'fournisseur_rc': forms.TextInput(attrs={'class': input_class}),
            'fournisseur_adresse': forms.TextInput(attrs={'class': input_class}),
            'fournisseur_ville_rc': forms.TextInput(attrs={'class': input_class}),
            'numero_facture': forms.TextInput(attrs={'class': input_class}),
            'date_emission_facture': forms.DateInput(attrs=date_attrs, format='%Y-%m-%d'),
            'nature_prestation': forms.TextInput(attrs={'class': input_class}),
            'date_livraison': forms.DateInput(attrs=date_attrs, format='%Y-%m-%d'),
            'date_constatation_service': forms.DateInput(attrs=date_attrs, format='%Y-%m-%d'),
            'date_paiement_prevue': forms.DateInput(attrs=date_attrs, format='%Y-%m-%d'),
            'date_paiement_convenue': forms.DateInput(attrs=date_attrs, format='%Y-%m-%d'),
            'delai_paiement_secteur': forms.TextInput(attrs={'class': input_class}),
            'date_paiement_prevue_secteur': forms.DateInput(attrs=date_attrs, format='%Y-%m-%d'),
            'montant_ttc': forms.NumberInput(attrs={'class': f'{input_class} text-right'}),
            'montant_non_paye': forms.NumberInput(attrs={'class': f'{input_class} text-right'}),
            'montant_paye_hors_delai': forms.NumberInput(attrs={'class': f'{input_class} text-right'}),
            'date_paiement_hors_delai': forms.DateInput(attrs=date_attrs, format='%Y-%m-%d'),
            'mode_paiement': forms.Select(attrs={'class': select_class}),
            'reference_paiement': forms.TextInput(attrs={'class': input_class}),
            'montant_objet_litige': forms.NumberInput(attrs={'class': f'{input_class} text-right'}),
            'date_recours_judiciaire': forms.DateInput(attrs=date_attrs, format='%Y-%m-%d'),
            'montant_du_apres_jugement': forms.NumberInput(attrs={'class': f'{input_class} text-right'}),
            'date_jugement_definitif': forms.DateInput(attrs=date_attrs, format='%Y-%m-%d'),
            'mois_suspension_amende': forms.NumberInput(attrs={'class': input_class}),
            'nombre_mois_retard': forms.NumberInput(attrs={'class': f'{input_class} text-center', 'readonly': True}),
            'amende': forms.NumberInput(attrs={'class': f'{input_class} text-right', 'readonly': True}),
        }

class BaseFactureFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        for i, form in enumerate(self.forms):
            if i >= self.initial_form_count() and not form.has_changed():
                form._errors = {}


FactureFormSet = inlineformset_factory(
    Declaration,
    Facture,
    form=FactureForm,
    formset=BaseFactureFormSet,
    extra=0,
    can_delete=True,
    can_delete_extra=True
)
