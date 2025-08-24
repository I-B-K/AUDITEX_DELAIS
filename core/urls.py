# core/urls.py
from django.urls import path
from core import views
from core.views_registration import RegistrationRequestsView, ValidateRegistrationView

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('declaration/<int:pk>/', views.DeclarationDetailView.as_view(), name='declaration_detail'),
    path('declaration/<int:pk>/export/xml/', views.export_declaration_xml, name='export_declaration_xml'),
    
    # NOUVELLES URLs pour les exports
    path('declaration/<int:pk>/export/pdf/', views.export_declaration_pdf, name='export_declaration_pdf'),
    path('declaration/<int:pk>/export/excel/', views.export_declaration_excel, name='export_declaration_excel'),
    
    path('export/template/', views.export_excel_template, name='export_excel_template'),
    
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/add/', views.ClientCreateView.as_view(), name='client_add'),
    path('clients/<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_edit'),
    path('clients/<int:pk>/declarations/', views.ClientDeclarationsView.as_view(), name='client_declarations'),
    path('clients/<int:pk>/assign/', views.ClientCollaboratorAssignView.as_view(), name='client_collaborators_assign'),
    path('collaborators/', views.CollaboratorListView.as_view(), name='collaborator_list'),
    path('collaborators/<int:pk>/assign/clients/', views.CollaboratorClientAssignView.as_view(), name='collaborator_client_assign'),
    
    # URLs pour la gestion des inscriptions
    path('inscriptions/', RegistrationRequestsView.as_view(), name='registration_requests'),
    path('inscriptions/<int:pk>/valider/', ValidateRegistrationView.as_view(), name='validate_registration'),
]
