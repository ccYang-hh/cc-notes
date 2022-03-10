from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from datetime import datetime

from .models import Event
from .serializers import EventSerializer


class EventViewSet(ModelViewSet):
    serializer_class = EventSerializer

    def get_object(self):
        event_id = self.kwargs['pk']
        event = get_object_or_404(Event, id=event_id)
        return event

    def get_queryset(self):
        query_dict = self.request.query_params
        date_str = query_dict.get('date')
        user_id = query_dict.get('user')
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        events = Event.objects.filter(time=date_obj, creator_id=user_id)
        return events
