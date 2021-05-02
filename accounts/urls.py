from django.urls import path
import accounts.views as auth_views

urlpatterns = [
    path('login', auth_views.LoginView.as_view(), name='login'),
    path('register', auth_views.RegisterView.as_view(), name='register'),
    path('recover-password', auth_views.RecoverPasswordView.as_view(), name='recover-password'),
]
