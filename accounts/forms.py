from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import WorkspaceModel, AccountModel, BusinessModel, UserModel
from common.mixins import PasswordConfirmFormMixin, AccountRegisterFormMixin
from common.base import BASE_FORM_ATTRS


class WorkspaceAdminCreationForm(forms.ModelForm):
    class Meta:
        model = WorkspaceModel
        fields = '__all__'

    def save(self, commit=True):
        workspace_ = super().save(commit=False)
        creation_data = dict(
            name=workspace_.name,
            business=workspace_.business, )
        workspace = self.Meta.model.objects.create(**creation_data)

        return workspace


class AccountAdminChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = AccountModel
        fields = '__all__'

    def clean_password(self):
        return self.initial["password"]


class AccountAdminCreation(PasswordConfirmFormMixin, forms.ModelForm):
    business_id = forms.CharField(min_length=8, max_length=8, help_text='Required length: 8')

    class Meta:
        model = AccountModel
        fields = ('username', 'email', 'is_staff', )

    def save(self, commit=True):
        user_ = super().save(commit=False)
        creation_data = dict(
            business_id=self.cleaned_data['business_id'],
            username=user_.username,
            email=user_.email, )
        if user_.is_staff:
            user = self.Meta.model.objects.create_superuser(
                **creation_data,
                password=self.cleaned_data['password'], )
        else:
            user = self.Meta.model.objects.create_user(**creation_data,
                                                       password=self.cleaned_data['password'], )
        return user


class UsernameLoginForm(forms.Form):
    business_id = forms.CharField(min_length=8, max_length=8, label='Business Id',
                                  widget=forms.TextInput(
                                      attrs={**BASE_FORM_ATTRS,
                                             'placeholder': 'Business ID'}
                                  ))
    username = forms.CharField(max_length=150, label='Username', widget=forms.TextInput(
        attrs={**BASE_FORM_ATTRS,
               'placeholder': 'Username'}
    ))
    password = forms.CharField(max_length=128, label='Password', widget=forms.PasswordInput(
        attrs={**BASE_FORM_ATTRS,
               'placeholder': 'Password'}
    ))


class EmailLoginForm(forms.Form):
    email = forms.EmailField(max_length=150, label='Email Address', widget=forms.EmailInput(
        attrs={**BASE_FORM_ATTRS,
               'placeholder': 'Email Address'}
    ))
    password = forms.CharField(max_length=128, label='Password', widget=forms.PasswordInput(
        attrs={**BASE_FORM_ATTRS,
               'placeholder': 'Password'}
    ))


class BusinessAccountRegisterForm(PasswordConfirmFormMixin, AccountRegisterFormMixin):
    organization_name = forms.CharField(max_length=150, widget=forms.TextInput(
        attrs={**BASE_FORM_ATTRS,
               'placeholder': 'Organization Name'},
    ))


class UserAccountRegisterForm(PasswordConfirmFormMixin, AccountRegisterFormMixin):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(
        attrs={**BASE_FORM_ATTRS,
               'placeholder': 'First Name'},
    ))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(
        attrs={**BASE_FORM_ATTRS,
               'placeholder': 'Last Name'},
    ))
