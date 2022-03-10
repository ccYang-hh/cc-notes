from django.shortcuts import get_object_or_404
from django.utils.http import urlquote
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from notifications.models import Notification

from .serializers import ArticleNoticeSerializer, FeedNoticeSerializer

from users.models import User


class NoticePagination(PageNumberPagination):
    page_size = 3
    page_query_param = 'page'
    max_page_size = 10
    page_size_query_param = 'page_size'


class ArticleNoticeList(generics.ListAPIView):
    pagination_class = NoticePagination

    def get_serializer_class(self):
        target = urlquote(self.request.query_params['target'])
        if target == "articles":
            return ArticleNoticeSerializer
        elif target == "feeds":
            return FeedNoticeSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        target = self.request.query_params['target']
        if target == "articles":
            return Notification.objects.filter(unread=1, recipient_id=user_id, target_content_type_id=11)
        elif target == "feeds":
            return Notification.objects.filter(unread=1, recipient_id=user_id, target_content_type_id=15)


@api_view()
def update_notice(request, notice_id):
    notice = get_object_or_404(Notification, id=notice_id)
    notice.mark_as_read()
    return Response({
        "code": 200,
        "message": "已标记为已读"
    })


@api_view()
def update_notice_all(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.notifications.mark_all_as_read()
    return Response({
        "code": 200,
        "message": "已全部标记为已读"
    })
