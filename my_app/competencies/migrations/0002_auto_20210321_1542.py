# Generated by Django 3.1.4 on 2021-03-21 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competencies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='name',
            field=models.CharField(default='TBC', max_length=200),
        ),
        migrations.AddField(
            model_name='usertask',
            name='name',
            field=models.CharField(default='TBC', max_length=200),
        ),
    ]
