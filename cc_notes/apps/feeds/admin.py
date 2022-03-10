from django.contrib import admin
from .models import Feed, FeedImages, Feeling

# Register your models here.
admin.site.register(Feed)
admin.site.register(FeedImages)
admin.site.register(Feeling)