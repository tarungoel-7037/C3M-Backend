from django.urls import path

from .views import LawFirmListView

urlpatterns = [
    path('law-firms/', LawFirmListView.as_view(), name='law-firm-list'),
]
