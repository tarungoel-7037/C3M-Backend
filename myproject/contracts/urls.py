from django.urls import path

from .views import ContractCreateView,ContractListView

urlpatterns = [
    path('contracts/create/', ContractCreateView.as_view(), name='contract-create'),
    path('contracts/', ContractListView.as_view(), name='list-contracts'),
]
