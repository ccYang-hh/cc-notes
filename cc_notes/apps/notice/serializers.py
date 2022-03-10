from rest_framework import serializers
from notifications.models import Notification

from users.serializers import SimpleUserSerializer
from notes.models import Article
from comments.models import Comment
from feeds.models import Feed,Feeling


class SimpleArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('id', 'title')


class SimpleCommentSerializer(serializers.ModelSerializer):
    body = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'body')

    def get_body(self, instance):
        return instance.body[:16]


class ArticleNoticeSerializer(serializers.ModelSerializer):
    actor = SimpleUserSerializer()
    target = SimpleArticleSerializer()
    action_object = SimpleCommentSerializer()

    class Meta:
        model = Notification
        fields = ('id', 'unread', 'actor', 'verb', 'target', 'action_object', 'timestamp',
                  'recipient_id', 'deleted')


class SimpleFeedSerializer(serializers.ModelSerializer):
    body = serializers.SerializerMethodField()

    class Meta:
        model = Feed
        fields = ('id', 'body')

    def get_body(self, instance):
        return instance.body[:16]


class SimpleFeelingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Feeling
        fields = ('id', 'content')


class FeedNoticeSerializer(serializers.ModelSerializer):
    actor = SimpleUserSerializer()
    target = SimpleFeedSerializer()
    action_object = SimpleFeelingSerializer()

    class Meta:
        model = Notification
        fields = ('id', 'unread', 'actor', 'verb', 'target', 'action_object', 'timestamp',
                  'recipient_id', 'deleted')
