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
from settings.common import DEBUG
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


class SetCSRFTokenView(View):
    def get(self, request):
        """Void view to set a csrftoken Cookie"""
        token = get_token(request)
        response = HttpResponse()
        response.set_cookie('csrftoken', value=token)
        # response = HttpResponse(
        #    content=json.dumps({'csrftoken': token}),
        #    content_type='application/json')
        return response

class CheckActiveSession(View):
    def get(self, request):
        return HttpResponse(
            content=json.dumps({'success': request.user.is_authenticated}),
            content_type='application/json')


urlpatterns=[
    re_path(r'^favicon\.png$', RedirectView.as_view(
        url='/static/assets/img/favicon.png')),
    path('admin/', admin.site.urls),

    # view that sets a new CRFToken to Agent client
    path('set-csrftoken/', SetCSRFTokenView.as_view(), name='set-csrftoken'),
    # view that checks if current session is active
    path('check-session/', CheckActiveSession.as_view(), name='check-session'),

    # API
    path('api/v%s/' % settings.SCALADE_VERSION[0], include('api.urls')),
    path('api-auth/', include('rest_framework.urls')) if settings.DEBUG else []
]

# serve media files in Development
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
