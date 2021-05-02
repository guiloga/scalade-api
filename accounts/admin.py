from django.contrib import admin
import os

from django.contrib.auth.models import Group, Permission
from .models import WorkspaceModel, AccountModel, BusinessModel, UserModel
from .forms import WorkspaceAdminCreationForm, AccountAdminChangeForm, AccountAdminCreation
from common.mixins import AdminAddFormMixin


@admin.register(WorkspaceModel)
class WorkspaceAdmin(AdminAddFormMixin, admin.ModelAdmin):
    list_display = ('uuid', 'created', 'name', )
    list_filter = ('created', )
    search_fields = ('uuid', 'name', )
    list_per_page = 100
    add_form = WorkspaceAdminCreationForm


@admin.register(AccountModel)
class AccountAdmin(AdminAddFormMixin, admin.ModelAdmin):
    form = AccountAdminChangeForm
    add_form = AccountAdminCreation
    list_display = ('uuid', 'auth_id', 'username', 'email', 'date_joined', )
    list_filter = ('date_joined', 'last_login', )
    search_fields = ('uuid', 'auth_id', 'username', )
    readonly_fields = ('auth_id', 'username')
    list_per_page = 100
    ordering = ('date_joined',)
    fieldsets = (
        (None, {'fields': ('auth_id', 'username', 'email', 'password')}),
        ('Status fields', {'fields': ('is_staff', 'is_superuser', 'is_active')}),
        ('Dates', {'fields': ('date_joined', 'last_login')}),
        ('Permissions', {'fields': ('groups', 'user_permissions', 'workspaces')}),
    )
    add_fieldsets = (
        (None, {
            'fields': ('username', 'business_id', 'email', 'is_staff',
                       'password', 'password_confirm'),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        action = self.parse_action_from_request(request)
        self.readonly_fields = ('auth_id', 'username')
        if action == 'add':
            self.readonly_fields = []
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)


@admin.register(BusinessModel)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'created', 'organization_name', )
    list_filter = ('created',)
    search_fields = ('uuid', 'organization_name', )
    list_per_page = 100


@admin.register(UserModel)
class UserAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'created', 'business', 'first_name')
    list_filter = ('created', )
    search_fields = ('uuid', 'business__organization_name', )
    list_per_page = 100


# Register authentication and authorization models
# admin.site.register(Group)
admin.site.register(Permission)