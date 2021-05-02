from django.views.generic import TemplateView
from accounts.views import redirect_authenticated_user


class LandingView(TemplateView):
    template_name = 'info/landing.html'

    @redirect_authenticated_user
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
