# Generated by Django 3.1.2 on 2022-02-22 07:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0007_auto_20220218_1426'),
    ]

    operations = [
        migrations.DeleteModel(
            name='RichTextNote',
        ),
    ]
