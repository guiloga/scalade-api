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
import json

import settings


class GetCSRFTokenView(View):
    def get(self, request):
        token = get_token(request)
        response = HttpResponse(
            content=json.dumps({'csrftoken': token}),
            content_type='application/json')
        return response


urlpatterns=[
    re_path(r'^favicon\.png$', RedirectView.as_view(
        url='/static/assets/img/favicon.png')),
    path('admin/', admin.site.urls),
    # path('', RedirectView.as_view(pattern_name='accounts:login', permanent=False)),
    path('logout/', auth_views.LogoutView.as_view(),
         name='logout'),

    # view that gets a new CRFToken to Agent client
    path('get-csrftoken/', GetCSRFTokenView.as_view(), name='get-csrftoken'),

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
