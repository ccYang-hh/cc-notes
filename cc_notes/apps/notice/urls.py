from django.urls import path
from .views import (
    ArticleNoticeList,
    update_notice_all,
    update_notice
)
from rest_framework.urlpatterns import format_suffix_patterns


app_label = 'notice'

urlpatterns = [
    path('unread/<int:user_id>/', ArticleNoticeList.as_view(), name='notice_unread'),
    path('update-all/<int:user_id>/', update_notice_all, name='notice_update_all'),
    path('update/<int:notice_id>/', update_notice, name='notice_update'),
]

urlpatterns = format_suffix_patterns(urlpatterns)