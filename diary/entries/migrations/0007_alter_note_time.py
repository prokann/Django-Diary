# Generated by Django 4.1.1 on 2023-02-07 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0006_alter_note_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]