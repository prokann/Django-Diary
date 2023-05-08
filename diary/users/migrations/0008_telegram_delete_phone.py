# Generated by Django 4.1.1 on 2023-04-21 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_delete_goal'),
    ]

    operations = [
        migrations.CreateModel(
            name='Telegram',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(default='SOME STRING', max_length=25)),
                ('chat_id', models.CharField(max_length=40)),
            ],
        ),
        migrations.DeleteModel(
            name='Phone',
        ),
    ]
