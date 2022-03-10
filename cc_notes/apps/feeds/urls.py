from django.urls import path
from .views import *
from rest_framework.urlpatterns import format_suffix_patterns


app_label = 'feeds'

urlpatterns = [
    # feeds 视图集
    path('', FeedViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('<int:pk>/', FeedViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})),

    # feedImages 视图集
    path('images/', FeedImagesViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('images/<int:pk>/', FeedImagesViewSet.as_view({'get': 'retrieve'})),

    # feelings 视图集
    path('feelings/', FeelingsListView.as_view(), name='feelings'),

    path('recent/', RecentFeedsView.as_view(), name='recent_feeds'),
]

urlpatterns = format_suffix_patterns(urlpatterns)