from django.urls import path, include, re_path
from rest_framework import routers
from .views.accounts import WorkspaceViewSet, AccountViewSet, BusinessViewSetMixin, UserViewSetMixin
from .views.auth import SignUpView, SignInView, SignOutView, ResetPasswordView
from .views.runtime import GetFIContext, CreateFILogMessage, UpdateFIStatus, \
    CreateFIOutput
from .views.streams import StreamViewSet, FunctionTypeViewSet, FunctionInstanceViewSet, \
    VariableViewSet

entities_api_router = routers.DefaultRouter()

# --------------------- #
# Entities API Patterns #
# --------------------- #
# Registering Accounts ViewSets
entities_api_router.register(r'workspaces', WorkspaceViewSet, basename='workspaces')
entities_api_router.register(r'accounts', AccountViewSet, basename='accounts')
entities_api_router.register(r'businesses', BusinessViewSetMixin, basename='businesses')
entities_api_router.register(r'users', UserViewSetMixin, basename='users')

# Registering Streams ViewSets
entities_api_router.register(r'streams', StreamViewSet, basename='streams')
entities_api_router.register(r'function-types', FunctionTypeViewSet, basename='function_types')
entities_api_router.register(r'function-instances', FunctionInstanceViewSet, basename='function_instances')
entities_api_router.register(r'variables', VariableViewSet, basename='variables')

entities_api_patterns = [
    path(r'entities/', include((entities_api_router.urls, 'entities-api'))),
]

# --------------------------- #
# Authentication API Patterns #
# --------------------------- #
auth_api_patterns = [
    re_path(r'^auth/signup-(?P<type_>(user|business))/$', SignUpView.as_view()),
    re_path(r'^auth/signin-(?P<type_>(authid|email))/$', SignInView.as_view()),
    path(r'auth/signout/', SignOutView.as_view()),
    path(r'auth/reset-password/', ResetPasswordView.as_view()),
]

# -------------------- #
# Runtime API patterns #
# -------------------- #
runtime_api_patterns = [
    # fi stands for FunctionInstance
    path(r'runtime/fi-context/', GetFIContext.as_view()),
    path(r'runtime/fi-log/', CreateFILogMessage.as_view()),
    path(r'runtime/fi-status/', UpdateFIStatus.as_view()),
    path(r'runtime/fi-output/', CreateFIOutput.as_view()),
]

urlpatterns = entities_api_patterns + auth_api_patterns + runtime_api_patterns
