from django.urls import path
from streams.views import dashboard_view, StreamListView, StreamDetailView


app_name = 'streams'
urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('streams/', StreamListView.as_view(), name='management'),
    path('streams/uuid', StreamDetailView.as_view(), name='detail'),
    # TODO: builder view
    # TODO: templates view
]
