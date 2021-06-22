from django.contrib import admin
import os

from django.contrib.auth.models import Permission
from .models import WorkspaceModel, AccountModel, BusinessModel, UserModel
from common.mixins import AdminViewPermissionMixin


@admin.register(WorkspaceModel)
class WorkspaceAdmin(AdminViewPermissionMixin, admin.ModelAdmin):
    list_display = ('uuid', 'created', 'name', )
    list_filter = ('created', )
    search_fields = ('uuid', 'name', )
    list_per_page = 100


@admin.register(AccountModel)
class AccountAdmin(AdminViewPermissionMixin, admin.ModelAdmin):
    list_display = ('uuid', 'auth_id', 'username', 'email', 'date_joined', )
    list_filter = ('date_joined', 'last_login', )
    search_fields = ('uuid', 'auth_id', 'username', )
    list_per_page = 100
    ordering = ('date_joined',)
    fieldsets = (
        (None, {'fields': ('auth_id', 'username', 'email', 'password')}),
        ('Status fields', {'fields': ('is_staff', 'is_superuser', 'is_active')}),
        ('Dates', {'fields': ('date_joined', 'last_login')}),
        ('Permissions', {'fields': ('groups', 'user_permissions', 'workspaces')}),
    )


@admin.register(BusinessModel)
class BusinessAdmin(AdminViewPermissionMixin, admin.ModelAdmin):
    list_display = ('uuid', 'created', 'organization_name', )
    list_filter = ('created',)
    search_fields = ('uuid', 'organization_name', )
    list_per_page = 100


@admin.register(UserModel)
class UserAdmin(AdminViewPermissionMixin, admin.ModelAdmin):
    list_display = ('uuid', 'created', 'business', 'first_name')
    list_filter = ('created', )
    search_fields = ('uuid', 'business__organization_name', )
    list_per_page = 100


# Register authentication and authorization models
# admin.site.register(Group)
admin.site.register(Permission)