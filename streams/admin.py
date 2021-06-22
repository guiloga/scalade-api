from django.contrib import admin

from common.mixins import AdminViewPermissionMixin
from streams.models import FunctionTypeModel, StreamModel, FunctionInstanceModel, VariableModel, \
    FunctionInstanceLogMessageModel


@admin.register(FunctionTypeModel)
class FunctionTypeAdmin(AdminViewPermissionMixin, admin.ModelAdmin):
    list_display = ('uuid', 'created', 'key', 'verbose_name', 'updated')
    list_filter = ('created', 'updated', )
    search_fields = ('uuid', 'key', 'verbose_name', )
    list_per_page = 100


@admin.register(StreamModel)
class StreamAdmin(AdminViewPermissionMixin, admin.ModelAdmin):
    list_display = ('uuid', 'created', 'name', 'updated', 'status', )
    list_filter = ('created', 'updated', 'status', )
    search_fields = ('uuid', 'name', 'workspace', )
    list_per_page = 100


@admin.register(FunctionInstanceModel)
class FunctionInstanceAdmin(AdminViewPermissionMixin, admin.ModelAdmin):
    list_display = ('uuid', 'created', 'function_type', 'stream', 'updated', 'status', )
    list_filter = ('created', 'updated', 'status', )
    search_fields = ('uuid', 'name', 'function_type', 'stream', )
    list_per_page = 100


@admin.register(VariableModel)
class VariableAdmin(AdminViewPermissionMixin, admin.ModelAdmin):
    list_display = ('uuid', 'created', 'iot', 'id_name', 'function_instance', )
    list_filter = ('created', 'iot', )
    search_fields = ('uuid', 'id_name', 'function_instance', )
    list_per_page = 100


@admin.register(FunctionInstanceLogMessageModel)
class FunctionInstanceLogMessageAdmin(AdminViewPermissionMixin, admin.ModelAdmin):
    list_display = ('uuid', 'created', 'function_instance', 'log_level', )
    list_filter = ('created', 'log_level', )
    search_fields = ('uuid', 'function_instance', )
    list_per_page = 100
