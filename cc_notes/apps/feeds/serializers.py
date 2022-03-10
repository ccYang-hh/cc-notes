from rest_framework import serializers
from django.shortcuts import get_object_or_404
from notifications.signals import notify

from cc_notes.utils.serializers import Base64ImageField
from .models import FeedImages, Feed, Feeling
from users.serializers import SimpleUserSerializer
from users.models import User


class FeedImageSerializer(serializers.ModelSerializer):
    feed = serializers.PrimaryKeyRelatedField(read_only=True)
    feed_id = serializers.CharField(write_only=True)
    #image = serializers.ImageField(max_length=None, use_url=True)
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = FeedImages
        fields = ['id', 'image', 'created', 'feed', 'feed_id']

    def create(self, validated_data):
        print(validated_data)
        feed_id = validated_data['feed_id']
        del validated_data['feed_id']
        feed_image = FeedImages(**validated_data)
        feed = Feed.objects.get(id=feed_id)
        feed_image.feed = feed
        feed_image.save()
        return feed_image


class FeelingSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    feed = serializers.PrimaryKeyRelatedField(read_only=True)
    feed_id = serializers.CharField(write_only=True)
    user_id = serializers.CharField(write_only=True)

    class Meta:
        model = Feeling
        fields = ['id', 'user', 'feed', 'content', 'created', 'feed_id', 'user_id']

    def create(self, validated_data):
        request = self.context['request']
        feed_id = validated_data['feed_id']
        user_id = validated_data['user_id']
        del validated_data['feed_id']
        del validated_data['user_id']
        feeling = Feeling(**validated_data)
        user = get_object_or_404(User, id=user_id)
        feed = get_object_or_404(Feed, id=feed_id)
        feeling.user = user
        feeling.feed = feed
        feeling.save()
        notify.send(
            request.user,
            recipient=feed.author,
            verb='回复了你',
            target=feed,
            action_object=feeling,
        )
        return feeling


class SimpleFeedImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = FeedImages
        fields = ['id', 'image', 'created']


class FeedSerializer(serializers.ModelSerializer):
    author = SimpleUserSerializer(read_only=True)
    supports = serializers.IntegerField(read_only=True)
    total_views = serializers.IntegerField(read_only=True)
    images = SimpleFeedImageSerializer(many=True,read_only=True)

    class Meta:
        model = Feed
        fields = ['id', 'body', 'created', 'total_views', 'author', 'images', 'supports']

    def create(self, validated_data):
        request = self.context['request']
        feed = Feed(**validated_data)
        feed.author = request.user
        feed.save()
        return feed


class SimpleFeedSerializer(serializers.ModelSerializer):
    author = SimpleUserSerializer(read_only=True)
    body = serializers.SerializerMethodField()

    class Meta:
        model = Feed
        fields = ['id', 'body', 'created', 'author']

    def get_body(self, instance):
        return instance.body[:10]