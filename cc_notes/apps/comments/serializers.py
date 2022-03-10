from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .models import Comment
from notes.models import Article
from users.serializers import SimpleUserSerializer

from notifications.signals import notify


class SimpleArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('id',)


class SimpleCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'body', 'created_time', 'likes')


class ChildrenCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('id', 'user', 'body', 'created_time', 'likes',
                  'children', 'is_deleted', 'is_deleted_by_staff')


class CommentSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    reply_to = SimpleUserSerializer(read_only=True)
    parent = SimpleCommentSerializer(read_only=True)
    #children = ChildrenCommentSerializer(read_only=True,many=True)
    content_object = SimpleArticleSerializer(read_only=True)
    #is_proxy = serializers.BooleanField(write_only=True, default=False)

    class Meta:
        model = Comment
        fields = ('id', 'user', 'body', 'content_object', 'created_time', 'likes', 'reply_to',
                  'parent', 'children', 'is_deleted', 'is_deleted_by_staff')
        read_only_fields = ('user', 'content_object', 'reply_to', 'parent', 'children',)

    def create(self, validated_data):
        article_id = self.context['article_id']
        request = self.context['request']
        article = get_object_or_404(Article, id=article_id)
        if 'parent_comment_id' in self.context:
            parent_comment_id = self.context['parent_comment_id']
            parent_comment = get_object_or_404(Comment, id=parent_comment_id)
            new_comment = Comment.objects.create(user=request.user, reply_to=parent_comment.user,
                                                 parent=parent_comment, content_object=article, **validated_data)
            new_comment.save()
            notify.send(
                request.user,
                recipient=parent_comment.user,
                verb='回复了你',
                target=article,
                action_object=new_comment,
            )
            return new_comment
        new_comment = Comment.objects.create(user=request.user, reply_to=None,
                                             content_object=article, parent=None, **validated_data)
        new_comment.save()
        author = article.author
        notify.send(
            request.user,
            recipient=author,
            verb='回复了你',
            target=article,
            action_object=new_comment,
        )
        return new_comment


