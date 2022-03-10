from django.urls import path
from .views import (
    EventViewSet
)
from rest_framework.urlpatterns import format_suffix_patterns


app_label = 'events'

urlpatterns = [
    path('', EventViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('<int:pk>/', EventViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
]

urlpatterns = format_suffix_patterns(urlpatterns)