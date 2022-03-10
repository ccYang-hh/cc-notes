from rest_framework import serializers
from .models import Event

from users.serializers import SimpleUserSerializer


class EventSerializer(serializers.ModelSerializer):
    creator = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'time', 'finished', 'creator',]

    def create(self, validated_data):
        event = Event(**validated_data)
        request = self.context['request']
        event.creator = request.user
        # from users.models import User
        # user = User.objects.get(id=2)
        # event.creator = user
        event.save()
        return event

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.time = validated_data.get('time', instance.time)
        instance.finished = validated_data.get('finished', instance.finished)
        instance.save()
        return instance
