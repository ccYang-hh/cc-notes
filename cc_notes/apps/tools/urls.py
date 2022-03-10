from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (
    set_verify_code,
    check_code,
    get_weather,
    get_user_location,
    get_bk_results,
)


app_label = 'tools'

urlpatterns = [
    path('code/', set_verify_code, name="code"),
    path('code/check/', check_code, name='code_check'),
    path('location/', get_user_location, name="user-location"),
    path('weather/', get_weather, name="weather"),

    path('bk-search/<str:keyword>/', get_bk_results, name="bk_search"),
]