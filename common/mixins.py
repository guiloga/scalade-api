import os
from .utils import DecoratorShipper as drs
from .base import BASE_FORM_ATTRS
from django import forms


class BaseHeadersMixin:
    @drs.base_headers
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    @drs.base_headers
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)

    @drs.base_headers
    def put(self, *args, **kwargs):
        return super().put(*args, **kwargs)

    @drs.base_headers
    def patch(self, *args, **kwargs):
        return super().patch(*args, **kwargs)

    @drs.base_headers
    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)


class BaseAPIMixin:
    def create(self, *args, **kwargs):
        # TODO: Subclass and implement this method
        pass

    def retrieve(self, *args, **kwargs):
        # TODO: Subclass and implement this method
        pass

    def update(self, *args, **kwargs):
        # TODO: Subclass and implement this method
        pass

    def delete(self, *args, **kwargs):
        # TODO: Subclass and implement this method
        pass


class AdminAddFormMixin:
    def get_form(self, request, obj=None, **kwargs):
        action = self.parse_action_from_request(request)
        if action == 'add':
            kwargs['form'] = self.add_form

        return super().get_form(request, obj, **kwargs)

    @staticmethod
    def parse_action_from_request(request) -> str:
        return os.path.basename(
            request.path[:-1] if request.path[-1] == '/' else request.path)


class PasswordConfirmFormMixin(forms.Form):
    password = forms.CharField(max_length=128, help_text='Password', widget=forms.PasswordInput(
        attrs={**BASE_FORM_ATTRS,
               'placeholder': 'Password'}
    ))
    password_confirm = forms.CharField(max_length=128, help_text='Password Confirmation',
                                       widget=forms.PasswordInput(
                                                attrs={**BASE_FORM_ATTRS,
                                                       'placeholder': 'Password Confirmation'}
                                            ))

    def clean_password_confirmation(self):
        p1 = self.cleaned_data.get('password')
        p2 = self.cleaned_data.get('password_confirm')
        if p1 and p2 and p1 == p2:
            return p1
        else:
            raise forms.ValidationError('Passwords don\'t match.')


class AccountRegisterFormMixin(forms.Form):
    username = forms.CharField(max_length=150, label='Username', widget=forms.TextInput(
        attrs={**BASE_FORM_ATTRS,
               'placeholder': 'Username'}
    ))
    email = forms.EmailField(max_length=150, label='Email Address', widget=forms.EmailInput(
        attrs={**BASE_FORM_ATTRS,
               'placeholder': 'Email Address'}
    ))
