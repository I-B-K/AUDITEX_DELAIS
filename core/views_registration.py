# core/views_registration.py
from django.views.generic import ListView, UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from .models import UserProfile, Client
from .forms import RegistrationValidationForm

class RegistrationRequestsView(UserPassesTestMixin, ListView):
    model = UserProfile
    template_name = 'core/registration_requests.html'
    context_object_name = 'pending_profiles'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_queryset(self):
        return UserProfile.objects.filter(statut=UserProfile.StatutChoices.EN_ATTENTE)

class ValidateRegistrationView(UserPassesTestMixin, UpdateView):
    model = UserProfile
    form_class = RegistrationValidationForm
    template_name = 'core/validate_registration.html'
    
    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clients'] = Client.objects.all()
        return context

    def form_valid(self, form):
        profile = form.save(commit=False)
        user = profile.user
        action = self.request.POST.get('action')

        if action == 'validate':
            # Activer l'utilisateur
            user.is_active = True
            profile.statut = UserProfile.StatutChoices.VALIDE
            
            # Assigner les clients sélectionnés
            selected_clients = form.cleaned_data['clients']
            for client in selected_clients:
                client.collaborateurs.add(user)
            
            messages.success(self.request, f"L'inscription de {user.email} a été validée.")
        else:
            # Rejeter l'inscription
            profile.statut = UserProfile.StatutChoices.REJETE
            messages.warning(self.request, f"L'inscription de {user.email} a été rejetée.")

        profile.validation_date = timezone.now()
        user.save()
        profile.save()
        
        return redirect('registration_requests')
