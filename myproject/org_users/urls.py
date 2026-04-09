from django.urls import path

from org_users import views

urlpatterns = [
    path('users/<int:organisation_id>/', views.OrganisationUsersView.as_view(), name='organisation-users'),
    path('users/create/', views.AddOrganisationUserView.as_view(), name='add-organisation-user'),
    path('users/<int:id>/update/', views.UpdateOrganisationUserView.as_view(), name='update-organisation-user'),
    path('users/<int:id>/delete/', views.DeleteOrganisationUserView.as_view(), name='delete-organisation-user'),
    path('users/<int:user_id>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/', views.CurrentUserDetailView.as_view(), name='current-user-detail'),
]
