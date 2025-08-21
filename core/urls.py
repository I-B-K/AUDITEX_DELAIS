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
    export_declaration_xml,
    export_excel_template,
    export_declaration_pdf, # NOUVELLE VUE
    export_declaration_excel # NOUVELLE VUE
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('declaration/<int:pk>/', DeclarationDetailView.as_view(), name='declaration_detail'),
    path('declaration/<int:pk>/export/xml/', export_declaration_xml, name='export_declaration_xml'),
    
    # NOUVELLES URLs pour les exports
    path('declaration/<int:pk>/export/pdf/', export_declaration_pdf, name='export_declaration_pdf'),
    path('declaration/<int:pk>/export/excel/', export_declaration_excel, name='export_declaration_excel'),
    
    path('export/template/', export_excel_template, name='export_excel_template'),
    
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('clients/add/', ClientCreateView.as_view(), name='client_add'),
    path('clients/<int:pk>/edit/', ClientUpdateView.as_view(), name='client_edit'),
    path('clients/<int:pk>/declarations/', ClientDeclarationsView.as_view(), name='client_declarations'),
    path('collaborators/', CollaboratorListView.as_view(), name='collaborator_list'),
]
