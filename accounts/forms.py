from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import WorkspaceModel, AccountModel
from common.mixins import PasswordConfirmFormMixin


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
