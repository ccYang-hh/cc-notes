from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from django.contrib.contenttypes.fields import GenericRelation

from comments.models import Comment
from users.models import User


class Feed(models.Model):
    body = models.TextField(verbose_name='正文')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="feeds", related_query_name="feed")
    created = models.DateTimeField('创建日期', auto_now_add=True)
    total_views = models.PositiveIntegerField('浏览量', default=0)
    supports = models.PositiveIntegerField('点赞量', default=0)
    comments = GenericRelation(Comment, related_name="feed", related_query_name='feed', verbose_name='评论')

    def __str__(self):
        return self.body[:6]

    class Meta:
        db_table = 'feeds'
        ordering = ['-created']
        verbose_name = '动态'
        verbose_name_plural = verbose_name


FEELING_CHOICES = (
    ('0', '点赞'),
    ('1', '爱心'),
    ('2', '大笑'),
    ('3', '惊讶'),
    ('4', '流汗'),
    ('5', '愤怒')
)


class Feeling(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="feelings", related_query_name="feeling")
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE,
                             related_name="feelings", related_query_name="feeling")
    content = models.CharField(choices=FEELING_CHOICES, default='0', max_length=1, verbose_name="态度")
    created = models.DateTimeField('发布日期', auto_now_add=True)

    def __str__(self):
        return self.content

    class Meta:
        db_table = 'feelings'
        verbose_name = '态度'
        verbose_name_plural = verbose_name


class FeedImages(models.Model):
    image = ProcessedImageField(verbose_name='配图', upload_to='feeds/%Y/%m/%d/',
                                blank=True, null=True, format='JPEG',
                                options={'quality': 60})
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="images", related_query_name="image")
    created = models.DateTimeField('创建日期', auto_now_add=True)

    class Meta:
        db_table = 'feed_images'
        ordering = ['-created']
        verbose_name = 'FeedImages'
        verbose_name_plural = verbose_name
