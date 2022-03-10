from django.urls import path
from .views import *
from rest_framework.urlpatterns import format_suffix_patterns


app_label = 'notes'

urlpatterns = [
    # articles 视图集
    path('', ArticleViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('<int:pk>/', ArticleViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('avatar/<int:article_id>/', RefreshArticleAvatarView.as_view(), name='article_avatar_refresh'),
    # path('', ArticlesListView.as_view(), name='article-list'),
    # path('<int:pk>/', ArticleView.as_view(), name='article-detail'),

    # archives 视图集
    path('archives/', ArchiveViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('archives/<int:pk>/', ArchiveViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),

    # archives条件查询
    path('archives-belong/<int:pk>/', ArchivesBelongsView.as_view(), name='archive-belong'),
    path('archives-add/<int:article_id>/<int:archive_id>/', add_article_to_archive, name='add-article-archive'),
    path('archives-add/<int:article_id>/', add_article_to_archive, name='remove-article-archive'),

    # articles 条件查询
    path('recommend/', RecommendArticlesView.as_view(),name='article-recommend'),
    path('search/', SearchArticlesView.as_view(),name='article-search'),
    path('category/', category_count, name='category_count'),

    # article 细化改写
    path('up/<int:article_id>/<int:user_id>/', article_up, name='article-up'),
    path('total-views/<int:pk>/', article_views_up, name='article-views-up'),
    path('collections/<int:article_id>/<int:user_id>/', CollectionView.as_view(), name='collection-add'),
    path('check/collects/<int:article_id>/<int:user_id>/', is_collected, name='check-collect'),
    path('checkup/<int:article_id>/<int:user_id>/', check_article_up, name='check-up'),
    path('title/<int:pk>/', article_title, name='article-previous'),
]

urlpatterns = format_suffix_patterns(urlpatterns)