from django.urls import path

from .views import (
    ContractCreateView,
    ContractListView,
    ContractDetailView,
    ObligationCreateView,
    ObligationDeleteView,
    ObligationDetailView,
    ObligationListView,
    ObligationUpdateView,
    ContractDeleteView,
    ContractUpdateView,
)

urlpatterns = [
    path('contracts/create/', ContractCreateView.as_view(), name='contract-create'),
    path('contracts/', ContractListView.as_view(), name='list-contracts'),
    path('contracts/<int:contract_id>/', ContractDetailView.as_view(), name='contract-detail'),
    # path('contracts/<int:contract_id>/delete/', ContractDeleteView.as_view(), name='contract-delete'),
    # path('contracts/<int:contract_id>/update/', ContractUpdateView.as_view(), name='contract-update'),
    path('contracts/<int:contract_id>/obligations/create/', ObligationCreateView.as_view(), name='obligation-create'),
    path('contracts/<int:contract_id>/obligations/', ObligationListView.as_view(), name='obligation-list'),
    path('obligations/<int:obligation_id>/', ObligationDetailView.as_view(), name='obligation-detail'),
    path('obligations/<int:obligation_id>/update/', ObligationUpdateView.as_view(), name='obligation-update'),
    path('obligations/<int:obligation_id>/delete/', ObligationDeleteView.as_view(), name='obligation-delete'),
]
