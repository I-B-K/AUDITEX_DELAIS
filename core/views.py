# core/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse
from django.db import transaction
from django.contrib import messages
from django.http import HttpResponse, Http404
import xml.etree.ElementTree as ET
from xml.dom import minidom
import datetime
import os
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
import openpyxl

from core.models import Client, Declaration, Facture
from core.forms import DeclarationForm, FactureFormSet, ClientForm

# ... (Les vues DashboardView, DeclarationDetailView, etc. restent inchangées) ...

class DashboardView(LoginRequiredMixin, ListView):
    model = Declaration
    template_name = 'core/dashboard.html'
    context_object_name = 'recent_declarations'
    paginate_by = 5

    def get_queryset(self):
        return Declaration.objects.select_related('client').order_by('-annee', '-periode')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_clients'] = Client.objects.count()
        context['total_collaborators'] = User.objects.count()
        context['declarations_submitted_count'] = Declaration.objects.filter(statut='SUBMITTED').count()
        if 'declaration_form' not in context:
            context['declaration_form'] = DeclarationForm()
        return context

    def post(self, request, *args, **kwargs):
        form = DeclarationForm(request.POST)
        if form.is_valid():
            # ... (logique de création de déclaration inchangée) ...
            client = form.cleaned_data['client']
            type_declaration = form.cleaned_data['type_declaration']
            periode = form.cleaned_data.get('periode')
            annee = form.cleaned_data['annee']

            filter_kwargs = {
                'client': client,
                'type_declaration': type_declaration,
                'annee': annee
            }
            if type_declaration == 'TRIMESTRIEL':
                filter_kwargs['periode'] = periode
            
            existing_declaration = Declaration.objects.filter(**filter_kwargs).first()

            if existing_declaration:
                messages.warning(request, f"Une déclaration pour ce client et cette période existe déjà. Vous avez été redirigé vers celle-ci.")
                return redirect('declaration_detail', pk=existing_declaration.pk)

            declaration = form.save(commit=False)
            declaration.collaborateur = request.user
            declaration.save()
            messages.success(request, f"La déclaration pour {declaration.client} a été créée.")
            return redirect('declaration_detail', pk=declaration.pk)
        
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        context['declaration_form'] = form
        messages.error(request, "Veuillez corriger les erreurs dans le formulaire de création.")
        return self.render_to_response(context)


class DeclarationDetailView(LoginRequiredMixin, UpdateView):
    model = Declaration
    template_name = 'core/declaration_detail.html'
    context_object_name = 'declaration'
    fields = ['chiffre_affaires_n1', 'taux_directeur']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'formset' not in kwargs:
            if self.request.POST:
                context['formset'] = FactureFormSet(self.request.POST, instance=self.object)
            else:
                context['formset'] = FactureFormSet(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        # ... (logique de modification de déclaration inchangée) ...
        self.object = self.get_object()
        
        if self.object.statut == 'SUBMITTED':
            messages.error(request, "Cette déclaration est déjà soumise et ne peut plus être modifiée.")
            return redirect('declaration_detail', pk=self.object.pk)

        form = self.get_form()
        formset = FactureFormSet(request.POST, instance=self.object)

        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
            return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        with transaction.atomic():
            self.object = form.save()
            formset.instance = self.object
            formset.save()

        if 'submit_declaration' in self.request.POST:
            self.object.statut = 'SUBMITTED'
            self.object.save()
            messages.success(self.request, "La déclaration a été soumise avec succès.")
        else:
            messages.success(self.request, "Les modifications ont été enregistrées en tant que brouillon.")
        
        return redirect(self.get_success_url())
    
    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def get_success_url(self):
        return reverse('declaration_detail', kwargs={'pk': self.object.pk})


class ClientListView(LoginRequiredMixin, ListView):
    # ... (inchangé)
    model = Client
    template_name = 'core/client_list.html'
    context_object_name = 'clients'
    paginate_by = 10

class ClientCreateView(LoginRequiredMixin, CreateView):
    # ... (inchangé)
    model = Client
    form_class = ClientForm
    template_name = 'core/client_form.html'
    success_url = reverse_lazy('client_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Ajouter un nouveau client"
        return context

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    # ... (inchangé)
    model = Client
    form_class = ClientForm
    template_name = 'core/client_form.html'
    success_url = reverse_lazy('client_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Modifier le client : {self.object.raison_sociale}"
        return context

class ClientDeclarationsView(LoginRequiredMixin, ListView):
    # ... (inchangé)
    model = Declaration
    template_name = 'core/client_declarations.html'
    context_object_name = 'declarations'
    paginate_by = 10

    def get_queryset(self):
        self.client = get_object_or_404(Client, pk=self.kwargs['pk'])
        return Declaration.objects.filter(client=self.client).order_by('-annee', '-periode')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = self.client
        return context

class CollaboratorListView(LoginRequiredMixin, ListView):
    # ... (inchangé)
    model = User
    template_name = 'core/collaborator_list.html'
    context_object_name = 'collaborators'


def export_declaration_xml(request, pk):
    # ... (inchangé)
    declaration = get_object_or_404(Declaration, pk=pk)
    root = ET.Element("DeclarationDelaiPaiement")
    def add_sub_element(parent, tag, value):
        if value is not None:
            child = ET.SubElement(parent, tag)
            if isinstance(value, datetime.date):
                child.text = value.strftime('%Y-%m-%d')
            else:
                child.text = str(value)
    add_sub_element(root, "identifiantFiscal", declaration.client.numero_if)
    add_sub_element(root, "annee", declaration.annee)
    periode = 5 if declaration.type_declaration == 'ANNUEL' else declaration.periode
    add_sub_element(root, "periode", periode)
    add_sub_element(root, "activite", 1)
    add_sub_element(root, "chiffreAffaire", int(declaration.chiffre_affaires_n1))
    liste_factures = ET.SubElement(root, "listeFacturesHorsDelai")
    for facture in declaration.factures.all():
        facture_element = ET.SubElement(liste_factures, "FactureHorsDelai")
        add_sub_element(facture_element, "identifiantFiscal", facture.fournisseur_if)
        add_sub_element(facture_element, "numRC", facture.fournisseur_rc)
        add_sub_element(facture_element, "adresseSiegeSocial", facture.fournisseur_adresse)
        add_sub_element(facture_element, "numFacture", facture.numero_facture)
        add_sub_element(facture_element, "dateEmission", facture.date_emission_facture)
        add_sub_element(facture_element, "natureMarchandise", facture.nature_prestation)
        add_sub_element(facture_element, "dateLivraisonMarchandise", facture.date_livraison)
        add_sub_element(facture_element, "moisTransaction", facture.mois_transaction)
        add_sub_element(facture_element, "anneeTransaction", facture.annee_transaction)
        add_sub_element(facture_element, "dateConstatation", facture.date_constatation_service)
        add_sub_element(facture_element, "datePrevuePaiement", facture.date_paiement_prevue)
        add_sub_element(facture_element, "dateConvenuePaiementFacture", facture.date_paiement_convenue)
        add_sub_element(facture_element, "delaiPaiementSecteurActivite", facture.delai_paiement_secteur)
        add_sub_element(facture_element, "DatePrevueSelonDelaiFixeSecteur", facture.date_paiement_prevue_secteur)
        add_sub_element(facture_element, "montantFactureTtc", facture.montant_ttc)
        add_sub_element(facture_element, "montantNonEncorePaye", facture.montant_non_paye)
        add_sub_element(facture_element, "montantPayeHorsDelai", facture.montant_paye_hors_delai)
        add_sub_element(facture_element, "datePaiementHorsDelai", facture.date_paiement_hors_delai)
        add_sub_element(facture_element, "montantObjetDeLitige", facture.montant_objet_litige)
        add_sub_element(facture_element, "dateRecoursJudiciaire", facture.date_recours_judiciaire)
        add_sub_element(facture_element, "montantApresJugement", facture.montant_du_apres_jugement)
        add_sub_element(facture_element, "dateJugementDefinitif", facture.date_jugement_definitif)
        add_sub_element(facture_element, "modePaiement", facture.mode_paiement)
        add_sub_element(facture_element, "referencePaiement", facture.reference_paiement)
    xml_string = ET.tostring(root, 'utf-8')
    dom = minidom.parseString(xml_string)
    pretty_xml = dom.toprettyxml(indent="  ", encoding="utf-8")
    response = HttpResponse(pretty_xml, content_type='application/xml')
    response['Content-Disposition'] = f'attachment; filename="declaration_{declaration.pk}.xml"'
    return response

def export_excel_template(request):
    # ... (inchangé)
    try:
        file_path = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'excel_templates', 'declaration_template.xlsx')
        
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
                return response
        raise Http404
    except Exception as e:
        return HttpResponse(f"Erreur lors de l'exportation du fichier : {e}", status=500)

# NOUVELLE VUE POUR L'EXPORT PDF
def export_declaration_pdf(request, pk):
    declaration = get_object_or_404(Declaration, pk=pk)
    template_path = 'core/declaration_pdf.html'
    context = {'declaration': declaration}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="declaration_{declaration.pk}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

# NOUVELLE VUE POUR L'EXPORT EXCEL
def export_declaration_excel(request, pk):
    declaration = get_object_or_404(Declaration.objects.prefetch_related('factures'), pk=pk)
    
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Déclaration"
    
    # En-têtes
    headers = [
        "N° d'IF Fournisseur", "Raison Sociale Fournisseur", "N° Facture", "Date Émission", 
        "Montant TTC", "Date Paiement Prévue", "Date Paiement Convenue", "Date Paiement Hors Délai",
        "Montant Non Payé", "Montant Payé Hors Délai", "Nombre mois de retard", "Amende"
    ]
    sheet.append(headers)
    
    # Données
    for facture in declaration.factures.all():
        row = [
            facture.fournisseur_if,
            facture.fournisseur_raison_sociale,
            facture.numero_facture,
            facture.date_emission_facture,
            facture.montant_ttc,
            facture.date_paiement_prevue,
            facture.date_paiement_convenue,
            facture.date_paiement_hors_delai,
            facture.montant_non_paye,
            facture.montant_paye_hors_delai,
            facture.nombre_mois_retard,
            facture.amende,
        ]
        sheet.append(row)
        
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="declaration_{declaration.pk}.xlsx"'
    workbook.save(response)
    
    return response
