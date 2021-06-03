"""scalade_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.http.response import HttpResponse
from django.middleware.csrf import get_token
from django.views import View
from django.views.generic import RedirectView
from django.urls import path, include, re_path

from .views import LandingView
import settings


class SetCSRFTokenView(View):
    def get(self, request):
        response = HttpResponse()
        token = get_token(request)
        response.set_cookie('csrftoken', value=token)
        return response


urlpatterns = [
    re_path(r'^favicon\.png$', RedirectView.as_view(url='/static/assets/img/favicon.png')),
    path('admin/', admin.site.urls),
    # path('', RedirectView.as_view(pattern_name='accounts:login', permanent=False)),
    path('logout/', auth_views.LogoutView.as_view(),
         name='logout'),

    # void view that sets csrftoken cookie to Agent client
    path('set-csrftoken/', SetCSRFTokenView.as_view(), name='set-csrftoken'),

    # info
    path('', LandingView.as_view(), name='landing'),

    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('app/', include('streams.urls')),

    # API
    path('api/v%s/' % settings.SCALADE_VERSION[0], include('api.urls')),
    path('api-auth/', include('rest_framework.urls'))
]

# serve media files in Development
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

