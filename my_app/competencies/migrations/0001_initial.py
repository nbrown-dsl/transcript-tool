# Generated by Django 3.1.4 on 2021-03-21 15:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Usertask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upvote', models.BooleanField()),
                ('usertasktask', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='competencies.task')),
            ],
            options={
                'ordering': ['-usertasktask'],
            },
        ),
    ]
