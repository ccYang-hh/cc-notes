from django.urls import path
from .views import *
from rest_framework.urlpatterns import format_suffix_patterns

app_label = 'comments'

urlpatterns = [
    path('', CommentsListView.as_view(), name='comment-list'),
    path('<int:comment_id>/', CommentItemView.as_view(), name='comment-detail'),
    # 发布文章评论
    path('post-article/<int:article_id>/<int:parent_comment_id>/',
         CommentCreateView.as_view(), name='article-comment-reply'),
    path('post-article/<int:article_id>/', CommentCreateView.as_view(), name='article-comment-post'),
    # 获取根评论
    path('article-root/<int:article_id>/', ArticleCommentsRootView.as_view(), name='article-root-comments'),
    # 获取子评论
    path('article-children/<int:parent_comment_id>/',
         ArticleCommentsChildrenView.as_view(), name='article-children-comments'),
    # 删除评论
    path('delete/<int:comment_id>/', CommentDelView.as_view(), name="comment-del"),
    # 点赞评论
    path('up/<int:comment_id>/', comment_up, name='comment-up'),
    path('check-up/<int:comment_id>/', check_comment_up, name='comment-check-up'),

    path('article-count/<int:article_id>/', get_article_comments_count, name='article-comments-count')
]

urlpatterns = format_suffix_patterns(urlpatterns)