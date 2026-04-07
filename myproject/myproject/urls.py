from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('law_firms.urls')),
    path('api/', include('organisations.urls')),
    path('api/', include('org_users.urls')),
]
