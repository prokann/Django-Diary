# Generated by Django 4.1.1 on 2023-02-22 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0022_goal_goalexec'),
    ]

    operations = [
        migrations.AddField(
            model_name='goalexec',
            name='time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]