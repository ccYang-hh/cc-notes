from django.shortcuts import render,get_object_or_404
from django.db.models import Count
from django.contrib.auth import logout
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.views import TokenObtainPairView
from django_redis import get_redis_connection
import jwt

from cc_notes.configs.dev import SIMPLE_JWT
from .serializers import EmailRegisterSerializer, MobileRegisterSerializer, \
    UserSerializer, MyTokenObtainPairSerializer, AccountSerializer, SimpleUserSerializer, AvatarSerializer
from .models import User, FollowUser
from .utils import time_converter
# Create your views here.


class UserPagination(PageNumberPagination):
    page_size = 6
    page_query_param = 'page'
    max_page_size = 10
    page_size_query_param = 'page_size'


# 注册功能视图集
class RegisterView(generics.CreateAPIView):
    def get_serializer_class(self):
        query_dict = self.request.query_params
        if 'mode' in query_dict and 'mobile' in query_dict.get('mode'):
            return MobileRegisterSerializer
        return EmailRegisterSerializer


# 自定义jwt登录
class CustomTokenLoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# 解析token令牌
@api_view(['POST'])
def decode_token(request):
    token = request.data['token']
    data = jwt.decode(
        token,
        SIMPLE_JWT['SIGNING_KEY'],
        algorithms=[SIMPLE_JWT['ALGORITHM']],
    )
    # 拼接图片url字段
    avatar = get_object_or_404(User, id=data['user_id']).avatar
    return Response({
        'token_type': data['token_type'],
        'user_id': data['user_id'],
        'username': data['username'],
        'expire': time_converter(data['exp']),
        'avatar': str(f'http://www.yhiscoding.cn{avatar.url}')
    })


class UserListView(generics.ListAPIView):

    def get_serializer_class(self):
        query_dict = self.request.query_params
        mode = query_dict.get('mode')
        if mode == "complex":
            return AccountSerializer
        else:
            return UserSerializer

    def get_queryset(self):
        query_dict = self.request.query_params
        if not query_dict:
            return User.objects.all().prefetch_related('articles')
        else:
            px = query_dict.get('px')
            nums = query_dict.get('nums')
            if nums:
                nums = int(nums)
            else:
                nums = 4
            if px:
                if px == "articles":
                    return User.objects.all().prefetch_related('articles').annotate(
                                                article_count=Count('article')).order_by('-article_count')[:nums]
                elif px == "fans":
                    return User.objects.all().prefetch_related('articles').annotate(
                        fans_count=Count('fans')).order_by('-fans_count')[:nums]
            else:
                return User.objects.all().prefetch_related('articles')


# 注销功能视图
class logoutView(APIView):
    """
    注意！JWT的注销无法做到像session一样在服务端删除，token存储在客户端，无法直接控制
    目前有两种方法来实现JWT的合理注销：
        1）设置合理的token过期时间，并且在注销时删除客户端的token存储
           缺点：该方案不够安全，因为别有用心的用户仍有可能在注销前备份token
        2）设置一个token黑名单，用户提交注销操作后，将该token放进黑名单，过期后删除。
    """
    def get(self, request):
        if request.user.is_anonymous:
            return Response({'message': 'anonymous'})
        else:
            username = request.user.username
            logout(request)
            return Response({
                'message': 'OK',
                'username': username
            })


# 用户信息验证
@api_view(['POST'])
def check_user_info(request, format=None):
    mode = request.data['mode']
    value = request.data['value']
    if mode == 'username':
        check_count = User.objects.filter(username__exact=value).count()
    elif mode == 'mobile':
        check_count = User.objects.filter(mobile__exact=value).count()
    elif mode == 'email':
        check_count = User.objects.filter(email__exact=value).count()
    else:
        check_count = 0
    data = {
        'value': value,
        'count': check_count
    }
    return Response(data)


# account
class AccountView(generics.RetrieveUpdateAPIView):

    def get_object(self):
        user_id = self.kwargs['user_id']
        return get_object_or_404(User, id=user_id)

    def get_serializer_class(self):
        mode = self.request.query_params.get("mode")
        if mode == "simple":
            return SimpleUserSerializer
        return AccountSerializer


@api_view()
def check_follow(request, user_id, follow_id):
    c_user = get_object_or_404(User, id=user_id)
    follow_user = get_object_or_404(User, id=follow_id)
    if FollowUser.objects.filter(user_from=c_user, user_to=follow_user).exists():
        return Response({
            "code": 201,
            "message": "已关注"
        })
    return Response({
        "code": 200,
        "message": "未关注"
    })


@api_view()
@permission_classes([IsAuthenticated,])
def follow_user(request, user_id, follow_id):
    if user_id == follow_id:
        return Response({
            "code": 0,
        })
    c_user = get_object_or_404(User, id=user_id)
    follow_user = get_object_or_404(User, id=follow_id)
    if FollowUser.objects.filter(user_from=c_user, user_to=follow_user).exists():
        item = get_object_or_404(FollowUser, user_from=c_user,user_to=follow_user)
        item.delete()
        return Response({
            "code": 201,
            "results": {
                "user_id": follow_id,
                "follows": follow_user.fans.count()
            }
        })
    FollowUser.objects.create(user_from=c_user,user_to=follow_user)
    return Response({
        "code": 200,
        "results": {
            "user_id": follow_id,
            "follows": follow_user.fans.count()
        }
    })


class FollowList(generics.ListAPIView):
    serializer_class = UserSerializer
    pagination_class = UserPagination
    # permission_classes = [IsAuthenticated,]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        return user.follows.all()


class FansList(generics.ListAPIView):
    serializer_class = UserSerializer
    pagination_class = UserPagination
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        return user.fans.all()


class RefreshAvatarView(generics.UpdateAPIView):
    serializer_class = AvatarSerializer
    permission_classes = [IsAuthenticated,]

    def get_object(self):
        user_id = self.kwargs['user_id']
        return get_object_or_404(User, id=user_id)


class RecentFollowsView(generics.ListAPIView):
    serializer_class = SimpleUserSerializer
    pagination_class = UserPagination

    def get_queryset(self):
        recent_users = []
        user_id = self.kwargs['user_id']
        recent_follows = FollowUser.objects.filter(user_to_id=user_id).order_by('-created')
        for recent in recent_follows:
            recent_users.append(recent.user_from)
        return recent_users


@api_view()
def get_user_articles_count(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return Response({
        "code": 200,
        "count": user.articles.count()
    })
