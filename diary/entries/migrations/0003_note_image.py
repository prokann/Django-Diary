# Generated by Django 4.1.1 on 2023-02-02 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0002_note_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='image',
            field=models.ImageField(blank=True, upload_to=None),
        ),
    ]
