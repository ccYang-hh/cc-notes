"""
Django settings for cc_notes project.

Generated by 'django-admin startproject' using Django 3.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os,sys
from pathlib import Path
import django_redis
import datetime
import rest_framework_simplejwt
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xp8xmqedk0n6)7=-0p^2g=sz5f86*x)=$psr_$v&0l1#1t!hfc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'simpleui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',  # 跨域
    'taggit',  # 标签
    'imagekit',
    'notifications', # 消息通知

    'users',
    'tools',
    'notes',
    'comments',
    'feeds',
    'notice',
    'events'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cc_notes.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'dist')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cc_notes.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cc_notes',
        'USER': 'cc_notes',
        'PASSWORD': 'Cc0727..',
        'HOST': '47.117.1.196',
        'PORT': 3306,
        'CONN_MAX_AGE': 300,  # 最大连接时间300s
        'OPTIONS': {
            # 解决emoji表情存储数据报错问题
            'charset': 'utf8mb4'
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'dist/static'),
    os.path.join(BASE_DIR,'static')
]
STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = ['users.utils.WithMobileModelBackend']

# 日志系统配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {                     # 日志信息显示的格式
        'verbose': {
            'format': '[ %(asctime)s ] [ %(levelname)s ] %(module)s %(lineno)d : %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '[ %(asctime)s ] %(module)s %(lineno)d : %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'filters': {  # 对日志进行过滤
        'require_debug_true':{  # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'handlers': {        # 日志处理方法
        'console': {     # 向终端输出日志
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true'],
            'formatter': 'simple'
        },
        'file': {        # 向文件输出日志
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR.parent, 'logs/cc_notes.log'),
            'filters': ['require_debug_true'],
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {         # 日志器，日志系统入口
        'django': {      # 定义一个叫做django的日志器
            'handlers': ['console', 'file'],  # 该日志器有两个handler，可以同时向终端与文件输出日志（多线程）
            'propagate': True,    # 是否继续向下层传递日志消息
            'level': 'INFO',      # 日志器接受的最低日志级别
        }
    },
}

# DRF配置项
REST_FRAMEWORK = {
    # 异常处理，使用我们自定义的异常处理
    'EXCEPTION_HANDLER': 'cc_notes.utils.exceptions.exception_handler',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        # 'rest_framework.authentication.TokenAuthentication',
        #'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    # 日期显示格式
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",
    'DATE_FORMAT': "%Y-%m-%d",
    #'DATE_INPUT_FORMATS': "%Y-%m-%d",
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=7),
    # 刷新access令牌时一并刷新refresh令牌并返回
    'ROTATE_REFRESH_TOKENS': True,
    # 加密算法
    'ALGORITHM': 'HS512',
    # 签名
    'SIGNING_KEY': SECRET_KEY,
    'UPDATE_LAST_LOGIN': True,
}

# 配置redis缓存
CACHES = {
  'default': {
     'BACKEND': 'django_redis.cache.RedisCache',
     # 如果redis在其它主机，这里需要将host更改为该主机ip
     'LOCATION': 'redis://47.117.1.196:6379/0',
     "OPTIONS": {
         "CLIENT_CLASS": "django_redis.client.DefaultClient",

         "PASSWORD": "aa5dvC5is6@CbpCJwIWg",
     }
  },
  'session': {
     'BACKEND': 'django_redis.cache.RedisCache',
     'LOCATION': 'redis://47.117.1.196:6379/1',
     "OPTIONS": {
         "CLIENT_CLASS": "django_redis.client.DefaultClient",

         "PASSWORD": "aa5dvC5is6@CbpCJwIWg",
     }
  },
  'verify_codes': {
     'BACKEND': 'django_redis.cache.RedisCache',
     'LOCATION': 'redis://47.117.1.196:6379/2',
     "OPTIONS": {
         "CLIENT_CLASS": "django_redis.client.DefaultClient",

         "PASSWORD": "aa5dvC5is6@CbpCJwIWg",
     }
 }
}

CSRF_USE_SESSIONS = False
CSRF_COOKIE_HTTPONLY = False

# 配置session引擎 ：基于缓存的session
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# 配置session使用缓存的哪一个配置：使用default配置，即使用redis的1号数据库
SESSION_CACHE_ALIAS = "session"

# 允许所有来源访问本站资源
CORS_ORIGIN_ALLOW_ALL = True
# 跨域访问白名单
CORS_ORIGIN_WHITELIST = [
    'http://127.0.0.1:8080',
    'http://localhost:8080',
    'https://127.0.0.1:8080',
    'https://localhost:8080',  # 凡是出现在白名单中的域名，都可以访问后端接口
]
# 跨域时允许携带cookie
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
)
CORS_ALLOW_HEADERS = (
    'XMLHttpRequest',
    'X_FILENAME',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'accept',
)

# email后端支持
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# SMTP服务器
EMAIL_HOST = 'smtp.sina.com'
# 邮箱名
EMAIL_HOST_USER = 'cc19990727@sina.com'
# 邮箱密码
EMAIL_HOST_PASSWORD = '183ffd7198d9c6fc'
# 发送邮件的端口
EMAIL_PORT = 465
# 是否使用 TLS
#EMAIL_USE_TLS = True
EMAIL_USE_SSL = True
#EMAIL_PORT = 465

EMAIL_FROM = 'CC笔记'
# 默认的发件人
DEFAULT_FROM_EMAIL = 'cc19990727@sina.com'
