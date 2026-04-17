from django.urls import path

from .views import (
    ChangePasswordView,
    LoginTwoFactorView,
    LoginView,
    LogoutView,
    ProfileView,
    SignupView,
    TwoFactorConfirmView,
    TwoFactorDisableView,
    TwoFactorSendOtpView,
    TwoFactorSetupView,
)


urlpatterns = [
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/login/verify-2fa/', LoginTwoFactorView.as_view(), name='login-verify-2fa'),
    path('auth/2fa/setup/', TwoFactorSetupView.as_view(), name='2fa-setup'),
    path('auth/2fa/confirm/', TwoFactorConfirmView.as_view(), name='2fa-confirm'),
    path('auth/2fa/disable/', TwoFactorDisableView.as_view(), name='2fa-disable'),
    path('auth/2fa/send-otp/', TwoFactorSendOtpView.as_view(), name='2fa-send-otp'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('whoami/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]
