from django.db import models

from users.models import User


class Event(models.Model):
    title = models.CharField(verbose_name="事件名", max_length=64)
    time = models.DateField(verbose_name="事件执行日期")
    finished = models.BooleanField(verbose_name="是否完成", default=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events", related_query_name="event")

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'events'
        verbose_name = '事件'
        verbose_name_plural = verbose_name

