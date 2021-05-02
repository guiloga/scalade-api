from django.contrib import admin

from streams.models import StreamModel, FunctionTypeModel, FunctionInstanceModel, VariableModel


@admin.register(StreamModel)
class StreamAdmin(admin.ModelAdmin):
    pass


@admin.register(FunctionTypeModel)
class FunctionTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(FunctionInstanceModel)
class FunctionInstanceAdmin(admin.ModelAdmin):
    pass


@admin.register(VariableModel)
class VariableAdmin(admin.ModelAdmin):
    pass
