from rest_framework import serializers
import re
from django_redis import get_redis_connection
from django.contrib.auth.models import update_last_login
from cc_notes.utils.serializers import Base64ImageField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from taggit.serializers import (TagListSerializerField, TaggitSerializer)

from .models import User
from notes.models import Article


# 用户注册序列化类
class RegisterBaseSerializer(serializers.ModelSerializer):
    passwordCheck = serializers.CharField(label="确认密码", write_only=True)
    code = serializers.IntegerField(label="验证码", write_only=True)
    refresh = serializers.CharField(label="refresh", read_only=True)
    access = serializers.CharField(label="access", read_only=True)

    def create(self, validated_data):
        del validated_data['passwordCheck']
        del validated_data['code']

        user = User(**validated_data)
        user.set_password(validated_data['password']) #加密密码

        user.save()

        # 创建jwt token进行状态保持，并返回给客户端
        # from rest_framework_jwt.settings import api_settings
        # jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 调用jwt的payload_handler函数
        # jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 调用jwt的encode_handler函数
        # # 该函数根据user生成一个payload载荷并返回，该payload包含user_id、user_username、expire_time、email等数据
        # payload = jwt_payload_handler(user)
        # # 该函数根据传入的payload生成jwt
        # token = jwt_encode_handler(payload)

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        user.refresh = refresh
        user.access = access

        return user


class EmailRegisterSerializer(RegisterBaseSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'passwordCheck', 'email',
                  'code', 'refresh', 'access', 'location']
        extra_kwargs = {
            'username': {
                'min_length': 1,
                'max_length': 16,
                'error_messages': {
                    'min_length': '仅允许1-16个字符的用户名',
                    'max_length': '仅允许1-16个字符的用户名'
                }
            },
            'password': {
                'write_only': True,
                'min_length': 6,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许6-20个字符的用户名',
                    'max_length': '仅允许6-20个字符的用户名'
                }
            },
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['passwordCheck']:
            raise serializers.ValidationError('密码不一致！')
        redis_conn = get_redis_connection('verify_codes')
        mail_code = redis_conn.get('mail_%s' % attrs['email'])
        if mail_code is None:
            raise serializers.ValidationError('无效的邮箱验证码！')
        if str(attrs['code']) != bytes.decode(mail_code):
            raise serializers.ValidationError('验证码错误！')
        return attrs


class MobileRegisterSerializer(RegisterBaseSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'passwordCheck', 'mobile',
                  'code', 'refresh', 'access', 'location']
        extra_kwargs = {
            'username': {
                'min_length': 1,
                'max_length': 16,
                'error_messages': {
                    'min_length': '仅允许1-16个字符的用户名',
                    'max_length': '仅允许1-16个字符的用户名'
                }
            },
            'password': {
                'write_only': True,
                'min_length': 6,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许6-20个字符的用户名',
                    'max_length': '仅允许6-20个字符的用户名'
                }
            },
        }

    def validate_mobile(self, value):
        if not re.match(r'1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式有误！')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['passwordCheck']:
            raise serializers.ValidationError('密码不一致！')
        redis_conn = get_redis_connection('verify_codes')
        mobile_code = redis_conn.get('mobile_%s' % attrs['mobile'])
        if mobile_code is None:
            raise serializers.ValidationError('无效的手机验证码！')
        if str(attrs['code']) != bytes.decode(mobile_code):
            raise serializers.ValidationError('验证码错误！')
        return attrs


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    注意：官方实例中推荐重写get_token，这会将额外信息编码进令牌中，之后在后端解码即可；
         如果重写validate，则只是 /token 方法返回的信息多了，但编码中仍不包含额外信息
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['user_id'] = user.pk
        return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'gender', 'avatar', 'email', 'last_login',
                  'date_joined', 'location', 'introduction', 'follows', 'fans']


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar', 'introduction', 'location']


class SimpleArticleSerializer(TaggitSerializer, serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    author = SimpleUserSerializer(read_only=True)
    tags = TagListSerializerField()

    class Meta:
        model = Article
        fields = ['id', 'author', 'avatar', 'title', 'created', 'description', 'isPublic', 'category',
                  'isStar', 'isDraft', 'total_views', 'tags', 'supports']

    def get_description(self, article):
        if article.description:
            return article.description
        else:
            return article.body[:300]


class AccountSerializer(serializers.ModelSerializer):
    articles = SimpleArticleSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'gender', 'avatar', 'email', 'date_joined', 'location', 'introduction',
                  'follows', 'fans', 'articles', 'last_login']

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.mobile = validated_data.get('mobile', instance.mobile)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.location = validated_data.get('location', instance.location)
        instance.introduction = validated_data.get('introduction', instance.introduction)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = User
        fields = ['id', 'avatar']

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance
