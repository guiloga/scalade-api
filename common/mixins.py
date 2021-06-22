
from django import forms
import os

from .utils import DecoratorShipper as Decorators
from .base import BASE_FORM_ATTRS


class BaseHeadersMixin:
    @Decorators.base_headers
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    @Decorators.base_headers
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)

    @Decorators.base_headers
    def put(self, *args, **kwargs):
        return super().put(*args, **kwargs)

    @Decorators.base_headers
    def patch(self, *args, **kwargs):
        return super().patch(*args, **kwargs)

    @Decorators.base_headers
    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)


class AdminViewPermissionMixin:
    def has_add_permission(self, request) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
    
    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_view_permission(self, request, obj=None) -> bool:
        return True
