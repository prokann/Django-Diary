# Generated by Django 4.1.1 on 2023-02-01 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='username',
            field=models.CharField(default='SOME STRING', max_length=25),
        ),
    ]
