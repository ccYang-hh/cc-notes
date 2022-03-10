from django.urls import path
from .views import (
    RegisterView,
    logoutView,
    UserListView,
    check_user_info,
    CustomTokenLoginView,
    decode_token,
    AccountView,
    follow_user,
    check_follow,
    FollowList,
    FansList,
    RefreshAvatarView,
    RecentFollowsView,
    get_user_articles_count
)
from rest_framework.urlpatterns import format_suffix_patterns
# from rest_framework_jwt.views import obtain_jwt_token

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

app_label = 'users'

urlpatterns = [
    path('', UserListView.as_view(),name='user-list'),
    path('register/', RegisterView.as_view(), name='register'),
    # path('login/', obtain_jwt_token, name='login'),
    path('logout/', logoutView.as_view(),name='logout'),
    path('check/', check_user_info, name='check-user'),
    path('token/', CustomTokenLoginView.as_view(), name='token_obtain_pair'),
    path('token/decode/', decode_token, name='token_decode'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('<int:user_id>/', AccountView.as_view(), name='account_info'),
    path('follows/<int:user_id>/<int:follow_id>/', follow_user, name='user_follow'),
    path('follows-check/<int:user_id>/<int:follow_id>/', check_follow, name='user_follow_check'),

    path('follows/<int:user_id>/', FollowList.as_view(), name='follow_list'),
    path('follows-recent/<int:user_id>/', RecentFollowsView.as_view(), name='recent_follows'),
    path('fans/<int:user_id>/', FansList.as_view(), name='fans_list'),
    path('avatar/<int:user_id>/', RefreshAvatarView.as_view(), name='avatar_refresh'),

    path('articles-count/<int:user_id>/', get_user_articles_count, name='articles_count'),
]

urlpatterns = format_suffix_patterns(urlpatterns)