# core/urls.py
from django.urls import path
from .views import (
    DashboardView,
    DeclarationDetailView,
    ClientListView,
    ClientCreateView,
    ClientUpdateView,
    CollaboratorListView,
    ClientDeclarationsView,
    export_declaration_xml # NOUVELLE VUE
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('declaration/<int:pk>/', DeclarationDetailView.as_view(), name='declaration_detail'),
    
    # NOUVELLE URL pour l'export XML
    path('declaration/<int:pk>/export/xml/', export_declaration_xml, name='export_declaration_xml'),
    
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('clients/add/', ClientCreateView.as_view(), name='client_add'),
    path('clients/<int:pk>/edit/', ClientUpdateView.as_view(), name='client_edit'),
    path('clients/<int:pk>/declarations/', ClientDeclarationsView.as_view(), name='client_declarations'),
    path('collaborators/', CollaboratorListView.as_view(), name='collaborator_list'),
]
