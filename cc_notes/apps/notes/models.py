from django.db import models
from django.urls import reverse

from taggit.managers import TaggableManager
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
import uuid,os
from django.contrib.contenttypes.fields import GenericRelation

from comments.models import Comment
from users.models import User


class Archive(models.Model):
    name = models.CharField(verbose_name="归档名", max_length=32)
    created = models.DateTimeField('创建日期', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="archives", related_query_name="archive")
    isPublic = models.BooleanField('是否公开', default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'archives'
        ordering = ['-created']
        verbose_name = '归档'
        verbose_name_plural = verbose_name


CATEGORY_CHOICES = (
    ('随笔', '随笔'),
    ('日记', '日记'),
    ('心情', '心情'),
    ('小说', '小说'),
)

BODY_CHOICES = (
    ('0', '富文本'),
    ('1', 'markdown'),
)


class Article(models.Model):
    title = models.CharField('标题', max_length=64)
    body = models.TextField(verbose_name='正文')
    markdownText = models.TextField(verbose_name="markdown文本", blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="articles", related_query_name="article")
    avatar = ProcessedImageField(verbose_name='配图', upload_to='articles/%Y/%m/%d/',
                                 blank=True, null=True, format='JPEG',
                                 options={'quality': 60})
    bodyType = models.CharField(choices=BODY_CHOICES, default='0',
                                max_length=1, verbose_name='文本类型')
    archive = models.ForeignKey(Archive, on_delete=models.CASCADE, related_name="articles",
                                related_query_name="article", null=True, blank=True)
    created = models.DateTimeField('创建日期', auto_now_add=True)
    updated = models.DateTimeField('修改日期', auto_now=True)
    total_views = models.PositiveIntegerField('浏览量', default=0)
    category = models.CharField(choices=CATEGORY_CHOICES, default='随笔',
                                max_length=2, verbose_name='文章类别')
    tags = TaggableManager('标签', blank=True)
    supports = models.PositiveIntegerField('点赞量', default=0)
    isPublic = models.BooleanField('是否公开', default=False)
    isStar = models.BooleanField('星标', default=False)
    isDraft = models.BooleanField('草稿', default=False)
    description = models.CharField(verbose_name='简介', blank=True, null=True, max_length=1024)
    comments = GenericRelation(Comment, related_query_name='article', verbose_name='评论')
    collectors = models.ManyToManyField(User, related_name='collections', verbose_name='收藏者',
                                        blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'tb_articles'
        ordering = ['-updated']
        verbose_name = '文章'
        verbose_name_plural = verbose_name
