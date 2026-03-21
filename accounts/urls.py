from django.urls import path
from . import views


urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_details, name='profile_details'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path(
        'password-reset/token/',
        views.password_reset_token_redirect,
        name='password_reset_token_redirect',
    ),
]

