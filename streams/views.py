from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.views.generic import TemplateView
from common.utils import ModelManager


@login_required
def dashboard_view(request):
    ctx = dict()
    ctx['streams_status_counts'] = ModelManager.handle(
        'streams.Stream', 'all').values('status').annotate(total=Count('status'))
    ctx['functions_status_counts'] = ModelManager.handle(
        'streams.FunctionInstance', 'all').values('status').annotate(total=Count('status'))

    return render(request,
                  template_name='streams/dashboard.html',
                  context=ctx, )


class StreamListView(LoginRequiredMixin, TemplateView):
    template_name = 'streams/stream_list.html'


class StreamDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'streams/stream_detail.html'
