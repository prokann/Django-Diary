# Generated by Django 4.1.1 on 2023-02-09 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0016_remove_todolist_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='todolist',
            name='time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
