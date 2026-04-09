from django.urls import path

from .views import (
    ContractRoleTypeListView,
    ContractTaskTypeListView,
    ContractTypeListView,
    GroupListView,
)

urlpatterns = [
    path('masters/contract-types/', ContractTypeListView.as_view(), name='masters-contract-types'),
    path('masters/groups/', GroupListView.as_view(), name='masters-groups'),
    path('masters/contract-task-types/', ContractTaskTypeListView.as_view(), name='masters-contract-task-types'),
    path('masters/contract-role-types/', ContractRoleTypeListView.as_view(), name='masters-contract-role-types'),
]

