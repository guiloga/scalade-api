from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views import View

from accounts.forms import UsernameLoginForm, EmailLoginForm, BusinessAccountRegisterForm, \
    UserAccountRegisterForm
from common.utils import ModelManager
from settings import LOGIN_REDIRECT_URL


def redirect_authenticated_user(func):
    def wrapper(inst, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(LOGIN_REDIRECT_URL)
        else:
            return func(inst, request, *args, **kwargs)
    return wrapper


class LoginView(View):
    username_form = UsernameLoginForm
    email_form = EmailLoginForm
    template = 'accounts/login.html'

    @redirect_authenticated_user
    def get(self, request, *args, **kwargs):
        return self.render_response(request)

    def post(self, request, *args, **kwargs):
        used_form = request.POST.get('used_form', 'username')
        form = (self.email_form(request.POST)
                if used_form == 'email' else self.username_form(request.POST))
        if form.is_valid():
            user = self._authenticate(request, form)
            if user:
                login(request, user)
                redirect_url = request.GET.get('next') or LOGIN_REDIRECT_URL
                return HttpResponseRedirect(redirect_url)
            else:
                return self.render_response(request, username_form=form)
        else:
            return self.render_response(request, username_form=form)

    def _authenticate(self, request, form):
        if form.__class__ == self.email_form:
            email, password = (
                form.cleaned_data['email'],
                form.cleaned_data['password'],)
            user = authenticate(request, email=email, password=password)
        else:
            business_id, username, password = (
                form.cleaned_data['business_id'],
                form.cleaned_data['username'],
                form.cleaned_data['password'],)
            user = authenticate(request, username=f'{business_id}/{username}', password=password)

        return user

    def render_response(self, request, username_form=None, email_form=None):
        return render(
            request,
            template_name=self.template,
            context={'username_form': username_form or self.username_form(),
                     'email_form': email_form or self.email_form()})


class RegisterView(View):
    business_form = BusinessAccountRegisterForm
    user_form = UserAccountRegisterForm
    template = 'accounts/register.html'

    @redirect_authenticated_user
    def get(self, request, *args, **kwargs):
        return self.render_response(request)

    def _register(self, form):
        # TODO: implement this method
        if form.__class__ == self.business_form:
            organization_name = form.cleaned_data['organization_name']
            business = ModelManager.handle('accounts.business',
                                           'create',
                                           organization_name=organization_name)
            account = ModelManager.handle('accounts.account',
                                          'create')

    def render_response(self, request, business_form=None, user_form=None):
        return render(
            request,
            template_name=self.template,
            context={'business_form': business_form or BusinessAccountRegisterForm(),
                     'user_form': user_form or UserAccountRegisterForm})


class RecoverPasswordView(View):
    template = 'accounts/recover-password.html'

    @redirect_authenticated_user
    def get(self, request, *args, **kwargs):
        return render(
            request,
            template_name=self.template,
            context={})


def logout_view(request):
    pass
