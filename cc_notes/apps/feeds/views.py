from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from django_redis import get_redis_connection
from django.shortcuts import get_object_or_404

from .models import Feeling, Feed, FeedImages
from users.models import User
from .serializers import FeedSerializer, FeedImageSerializer, FeelingSerializer, SimpleFeedSerializer


class FeedPagination(PageNumberPagination):
    page_size = 6
    page_query_param = 'page'
    max_page_size = 10
    page_size_query_param = 'page_size'


class FeedViewSet(viewsets.ModelViewSet):
    serializer_class = FeedSerializer
    pagination_class = FeedPagination

    def get_queryset(self):
        query_dict = self.request.query_params
        user_id = query_dict.get('user')
        if user_id:
            mode = query_dict.get('mode')
            user = get_object_or_404(User, id=user_id)
            if mode == "only":
                return user.feeds.all()
            elif mode == "exclude":
                return Feed.objects.exclude(author=user)
            else:
                return user.feeds.all()
        return Feed.objects.all()


class FeedImagesViewSet(viewsets.ModelViewSet):
    serializer_class = FeedImageSerializer
    pagination_class = FeedPagination

    def get_queryset(self):
        return FeedImages.objects.all()


class FeelingsListView(generics.ListCreateAPIView):
    serializer_class = FeelingSerializer
    pagination_class = FeedPagination

    def get_queryset(self):
        query_dict = self.request.query_params
        feed_id = query_dict.get('feed')
        if feed_id:
            feed = get_object_or_404(Feed, id=feed_id)
            feelings = feed.feelings.all()
            return feelings
        else:
            return Feeling.objects.all()

    def get(self, request, *args, **kwargs):
        query_dict = self.request.query_params
        feed_id = query_dict.get('feed')
        if feed_id:
            feed = get_object_or_404(Feed, id=feed_id)
            feelings = feed.feelings.all()
            mode = query_dict.get('mode')
            if mode == 'sorted':
                ups = feelings.filter(content='0').count()
                hearts = feelings.filter(content='1').count()
                smile = feelings.filter(content='2').count()
                Ooo = feelings.filter(content='3').count()
                sweat = feelings.filter(content='4').count()
                angry = feelings.filter(content='5').count()
                return Response({
                    "ups": ups,
                    "hearts": hearts,
                    "smile": smile,
                    "Ooo": Ooo,
                    "sweat": sweat,
                    "angry": angry
                })
            else:
                return super(FeelingsListView, self).get(request, *args, **kwargs)
        else:
            return super(FeelingsListView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        feed_id = request.data['feed_id']
        if Feeling.objects.filter(user_id=user_id, feed_id=feed_id):
            return Response({"code": -1})
        return self.create(request, *args, **kwargs)


class RecentFeedsView(generics.ListAPIView):
    serializer_class = SimpleFeedSerializer
    pagination_class = FeedPagination

    def get_queryset(self):
        return Feed.objects.order_by('-created')
