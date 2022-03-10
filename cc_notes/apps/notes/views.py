from django.shortcuts import render,get_object_or_404
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.utils.http import urlquote
import markdown
from django_redis import get_redis_connection

from rest_framework.decorators import api_view,throttle_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.pagination import PageNumberPagination

from users.models import User
from .models import Article,Archive
from .serializers import ArticleSerializer, ArchiveSerializer, SimpleArticleSerializer, ArticleAvatarSerializer
from taggit.models import Tag

from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    仅管理员用户可进行修改
    其他用户仅可查看
    """
    def has_permission(self, request, view):
        # 对所有人允许 GET, HEAD, OPTIONS 请求
        if request.method in permissions.SAFE_METHODS:
            return True

        # 仅管理员可进行其他操作
        return request.user.is_superuser


class ArticlePagination(PageNumberPagination):
    page_size = 6
    page_query_param = 'page'
    max_page_size = 10
    page_size_query_param = 'page_size'


class ArticleViewSet(viewsets.ModelViewSet):
    pagination_class = ArticlePagination

    def get_serializer_class(self):
        query_dict = self.request.query_params
        user_id = query_dict.get('user')
        _filter = query_dict.get('filter')
        type_name = query_dict.get('type')
        if user_id:
            return SimpleArticleSerializer
        if _filter:
            return SimpleArticleSerializer
        if type_name:
            return SimpleArticleSerializer
        return ArticleSerializer

    def get_queryset(self):
        query_dict = self.request.query_params  # QueryDict类型，其api参考官网
        if not query_dict:
            return Article.objects.all().select_related('archive')
        else:
            type_name = query_dict.get('type')  # 筛选标签
            if not type_name:
                _filter = query_dict.get('filter')  # 全局查找
                if _filter:
                    articles = Article.objects.filter(isDraft=False, isPublic=True).select_related('archive')
                    if _filter == "all":
                        return articles.order_by('-created')
                    elif _filter == "views":
                        return articles.order_by('-total_views')
                else:
                    user_id = query_dict.get('user')  # 基于用户查找
                    if user_id:
                        user = get_object_or_404(User, id=user_id)
                        mode = query_dict.get('mode')
                        articles = user.articles.all().select_related('archive')
                        if mode:
                            if mode == "star":
                                return articles.filter(isStar=True, isDraft=False)
                            elif mode == "draft":
                                return articles.filter(isDraft=True)
                            elif mode == "private":
                                return articles.filter(isPublic=True, isDraft=False)
                            elif mode == "collect":
                                return user.collections.all()
                        else:
                            return articles.filter(isDraft=False).order_by('-created')
                    else:
                        return Article.objects.filter(isPublic=True, isDraft=False).select_related('archive')
            else:
                if type_name == "所有":
                    return Article.objects.filter(isDraft=False, isPublic=True).select_related('archive')
                articles = Article.objects.filter(category=type_name, isDraft=False, isPublic=True).select_related('archive')
                return articles


class RefreshArticleAvatarView(generics.UpdateAPIView):
    serializer_class = ArticleAvatarSerializer
    permission_classes = [IsAuthenticated, ]

    def get_object(self):
        user_id = self.kwargs['article_id']
        return get_object_or_404(Article, id=user_id)


class ArchiveViewSet(viewsets.ModelViewSet):
    pagination_class = ArticlePagination
    serializer_class = ArchiveSerializer

    def get_queryset(self):
        query_dict = self.request.query_params
        if not query_dict:
            return Archive.objects.order_by('-created')
        else:
            user_id = query_dict.get('user')
            if user_id:
                user = get_object_or_404(User, id=user_id)
                return user.archives.all()
            else:
                return Archive.objects.order_by('-created')


class ArchivesBelongsView(generics.ListAPIView):
    serializer_class = SimpleArticleSerializer
    pagination_class = ArticlePagination

    def get_queryset(self):
        archive = get_object_or_404(Archive, id=self.kwargs['pk'])
        return archive.articles.filter(isDraft=False)


@api_view()
def category_count(request):
    results = [
        {
            "tag": "全部文章",
            "count": Article.objects.filter(isDraft=False, isPublic=True).count()
        },
        {
            "tag": "心情记录",
            "count": Article.objects.filter(isDraft=False, isPublic=True, category="心情").count()
        },
        {
            "tag": "学习随笔",
            "count": Article.objects.filter(isDraft=False, isPublic=True, category="随笔").count()
        },
        {
            "tag": "日常生活",
            "count": Article.objects.filter(isDraft=False, isPublic=True, category="日记").count()
        },
        {
            "tag": "小说创作",
            "count": Article.objects.filter(isDraft=False, isPublic=True, category="小说").count()
        }
    ]
    return Response({
        "code": 200,
        "results": results
    })


@api_view(['GET'])
def add_article_to_archive(request, article_id, archive_id=None):
    article = get_object_or_404(Article, id=article_id)
    if article.archive:
        article.archive.articles.remove(article)
        if archive_id:
            archive = get_object_or_404(Archive, id=archive_id)
            archive.articles.add(article)
    else:
        if archive_id:
            archive = get_object_or_404(Archive, id=archive_id)
            archive.articles.add(article)
    return Response({
        'code': 200,
        'message': 'OK'
    })


class ArticleView(generics.RetrieveUpdateAPIView):
    serializer_class = ArticleSerializer

    def get_object(self):
        article = get_object_or_404(Article, id=self.kwargs.get('pk'))
        return article


class ArticlesListView(generics.ListAPIView):
    pagination_class = ArticlePagination
    #permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        query_dict = self.request.query_params
        user_id = query_dict.get('user')
        if user_id:
            return SimpleArticleSerializer
        return ArticleSerializer

    def get_queryset(self):
        query_dict = self.request.query_params  # QueryDict类型，其api参考官网
        if not query_dict:
            return Article.objects.order_by('-updated')
        else:
            types = query_dict.getlist('type')  # getlist() api 用于获取某个查询参数的列表
            if not types:
                user_id = query_dict.get('user')
                user = get_object_or_404(User, id=user_id)
                mode = query_dict.get('mode')
                articles = user.articles.all()
                if mode:
                    if mode == "star":
                        return articles.filter(isStar=True)
                    elif mode == "draft":
                        return articles.filter(isDraft=True)
                    elif mode == "private":
                        return articles.filter(isPrivate=True)
                else:
                    return articles
            else:
                articles = Article.objects.filter(tags__name__in=types)
                return articles


class SearchArticlesView(generics.ListAPIView):
    serializer_class = ArticleSerializer
    pagination_class = ArticlePagination

    def get_queryset(self):
        search = self.request.query_params['key']
        articles = Article.objects.filter(Q(title__icontains=search) | Q(tags__name__in=search)
                                          | Q(body__icontains=search) | Q(category__iexact=search),
                                          isPublic=True, isDraft=False).distinct()
        return articles


class RecommendArticlesView(generics.ListAPIView):
    # 筛选出浏览量、点赞量、评论量最高的博文
    serializer_class = ArticleSerializer
    pagination_class = ArticlePagination

    def get_queryset(self):
        query_dict = self.request.query_params
        # 不指定type，则按照浏览量筛选
        if not query_dict:
            recommends = Article.objects.order_by('-total_views')
            return recommends
        else:
            filter_type = query_dict.get('type')
            if not filter_type:
                recommends = Article.objects.order_by('-total_views')
                return recommends
            else:
                if filter_type == 'views':
                    recommends = Article.objects.order_by('-total_views')
                    return recommends
                elif filter_type == 'supports':
                    supports = Article.objects.order_by('-supports')
                    return supports
                elif filter_type == 'comments':
                    comments_articles = Article.objects.order_by('-total_views')
                    return comments_articles


@api_view()
def article_up(request, article_id, user_id):
    article = get_object_or_404(Article, id=article_id)
    user = get_object_or_404(User, id=user_id)
    redis_conn = get_redis_connection('session')
    flag = redis_conn.get('spt_art_%d_user_%d' % (article_id,user_id))
    if flag is None:
        # 如果没有点赞
        article.supports += 1
        article.save()
        redis_conn.set('spt_art_%d_user_%d' % (article_id, user_id), '1')
        return Response({'message': 'OK','supports': article.supports})
    else:
        # 如果已经点赞,取消点赞
        article.supports -= 1
        article.save()
        redis_conn.delete('spt_art_%d_user_%d' % (article_id, user_id))
        return Response({'message': 'enable', 'supports': article.supports})


@api_view()
def check_article_up(request, article_id, user_id):
    redis_conn = get_redis_connection('session')
    article = get_object_or_404(Article, id=article_id)
    flag = redis_conn.get('spt_art_%d_user_%d' % (article_id, user_id))
    if flag is None:
        return Response({'message': 'no','supports': article.supports})
    elif flag is not None and article.supports == 0:
        redis_conn.delete('spt_art_%d_user_%d' % (article_id, user_id))
        return Response({'message': 'no', 'supports': article.supports})
    else:
        return Response({'message': 'yes','supports': article.supports})


class ArticleViewsAnonThrottle(AnonRateThrottle):
    rate = '1/minute'


class ArticleViewsUserThrottle(UserRateThrottle):
    rate = '1/minute'


@api_view()
@throttle_classes([ArticleViewsAnonThrottle, ArticleViewsUserThrottle])
def article_views_up(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.total_views += 1
    article.save()
    return Response({'total_views': article.total_views})


class CollectionView(APIView):

    def get(self, request, article_id, user_id):
        user = get_object_or_404(User, id=user_id)
        article = get_object_or_404(Article, id=article_id)
        if article in user.collections.all():
            # 已经收藏则删除该收藏
            user.collections.remove(article)
            return Response({'message': 'redundant'})
        else:
            user.collections.add(article)
            user.save()
            return Response({'message': 'OK'})


@api_view()
def is_collected(request, article_id, user_id):
    user = get_object_or_404(User, id=user_id)
    article = get_object_or_404(Article, id=article_id)
    if article in user.collections.all():
        return Response({'message': 'yes'})
    else:
        return Response({'message': 'no'})


@api_view()
def article_title(request, pk):
    article = get_object_or_404(Article, pk=pk)
    return Response({
        "id": article.id,
        "title": article.title
    })
