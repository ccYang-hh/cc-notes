from django.db import models
from django.contrib.auth import models as auth_models
from imagekit.models import ProcessedImageField


# Create your models here.

GENDER_CHOICES = (
    ('0', '女'),
    ('1', '男'),
)


class User(auth_models.AbstractUser):
    # 手机短信验证码不需要持久保存
    has_confirmed = models.BooleanField(default=False,verbose_name="验证")
    mobile = models.CharField(max_length=11, verbose_name="手机号",blank=True, null=True)
    gender = models.CharField(choices=GENDER_CHOICES, default='1',
                              max_length=1, verbose_name='性别')
    location = models.CharField(default="", verbose_name="用户位置", max_length=64)
    avatar = ProcessedImageField(verbose_name='头像', upload_to='users/%Y/%m/%d/',
                                 blank=True, null=True, format='JPEG', default='users/default/user.jpg',
                                 options={'quality': 60})
    introduction = models.CharField(verbose_name="个人介绍", max_length=128, default="这个人还没有介绍过自己...")
    follows = models.ManyToManyField("self", symmetrical=False, through='FollowUser', related_name='fans')

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class FollowUser(models.Model):
    user_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_from_set')
    user_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_to_set')
    created = models.DateTimeField('时间', auto_now=True)

    class Meta:
        verbose_name = '关注'
        verbose_name_plural = verbose_name
        ordering = ['-created']

    def __str__(self):
        return '{0} 关注了 {1}'.format(self.user_from,self.user_to)