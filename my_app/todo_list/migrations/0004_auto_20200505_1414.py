# Generated by Django 3.0.5 on 2020-05-05 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo_list', '0003_auto_20200426_0551'),
    ]

    operations = [
        migrations.AddField(
            model_name='list',
            name='className',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='list',
            name='program',
            field=models.CharField(default='', max_length=50),
        ),
    ]
