# Generated by Django 3.1.2 on 2022-02-14 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0002_auto_20220214_1931'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='bodyType',
            field=models.CharField(choices=[('0', '富文本'), ('1', 'markdown')], default='0', max_length=1, verbose_name='文本类型'),
        ),
        migrations.AlterField(
            model_name='article',
            name='category',
            field=models.CharField(choices=[('随笔', '随笔'), ('日记', '日记'), ('心情', '心情'), ('小说', '小说')], default='随笔', max_length=2, verbose_name='文章类别'),
        ),
    ]