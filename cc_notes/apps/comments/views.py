from rest_framework.views import APIView
from rest_framework import generics,status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django_redis import get_redis_connection

from .serializers import CommentSerializer
from .models import Comment
from notes.models import Article

# Create your views here.


class CommentPagination(PageNumberPagination):
    page_size = 6
    page_query_param = 'page'
    max_page_size = 10
    page_size_query_param = 'page_size'


class CommentItemView(APIView):
    # permission_classes = [IsAuthenticated, ]

    def get(self, request, comment_id, format=None):
        comment = get_object_or_404(Comment, id=comment_id)
        serializer = CommentSerializer(comment, context={'request': request})
        return Response(serializer.data)


class ArticleCommentsRootView(APIView):

    def get(self, request, article_id, format=None):
        article = get_object_or_404(Article, id=article_id)
        comments = Comment.objects.filter(article=article, parent=None)
        count = Comment.objects.filter(article=article).count()
        serializer = CommentSerializer(comments, many=True, context={'request':request})
        return Response({
            'root': serializer.data,
            'count': count
        })


class ArticleCommentsChildrenView(APIView):

    def __init__(self):
        super(ArticleCommentsChildrenView,self).__init__()
        self.children = []

    def children_mapper(self, root, request):
        if root and root['children'] != []:
            for child_id in list(root['children']):
                child = get_object_or_404(Comment, id=child_id)
                self.children.append(child)
                child_serializer = CommentSerializer(child, context={'request': request})
                self.children_mapper(dict(child_serializer.data), request)

    def get(self, request, parent_comment_id, format=None):
        parent = get_object_or_404(Comment, id=parent_comment_id)
        parent_serializer = CommentSerializer(parent, context={'request': request})
        self.children_mapper(dict(parent_serializer.data), request)
        serializer = CommentSerializer(self.children, many=True, context={'request': request})
        return Response(serializer.data)


class CommentsListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    pagination_class = CommentPagination
    permission_classes = [IsAdminUser,]

    def get_queryset(self):
        return Comment.objects.filter(parent=None)


class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    pagination_class = CommentPagination
    permission_classes = [IsAuthenticated, ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={**kwargs, 'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CommentDelView(APIView):

    def get(self, request, comment_id, format=None):
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user != comment.user:
            return Response({
                'message': '非评论用户！'
            }, status=status.HTTP_400_BAD_REQUEST)
        comment.delete()
        return Response({'message': 'OK'})


@api_view()
def comment_up(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user
    redis_conn = get_redis_connection('session')
    flag = redis_conn.get('lik_cm_%d_user_%d' % (comment_id, user.id))
    if flag is None:
        # 如果没有点赞
        comment.likes += 1
        comment.save()
        redis_conn.set('lik_cmt_%d_user_%d' % (comment_id, user.id), '1')
        return Response({'message': 'OK', 'likes': comment.likes})
    else:
        # 如果已经点赞,取消点赞
        comment.likes -= 1
        comment.save()
        redis_conn.delete('lik_cmt_%d_user_%d' % (comment_id, user.id))
        return Response({'message': 'enable', 'likes': comment.likes})


@api_view()
def check_comment_up(request, comment_id):
    redis_conn = get_redis_connection('session')
    comment = get_object_or_404(Comment, id=comment_id)
    flag = redis_conn.get('lik_cmt_%d_user_%d' % (comment_id, request.user.id))
    if flag is None:
        return Response({'message': 'no', 'likes': comment.likes})
    else:
        return Response({'message': 'yes', 'likes': comment.likes})


@api_view()
def get_article_comments_count(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    return Response({
        "count": article.comments.count(),
        "code": 200,
    })

