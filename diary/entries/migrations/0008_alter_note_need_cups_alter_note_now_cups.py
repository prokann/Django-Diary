# Generated by Django 4.1.1 on 2023-02-08 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0007_alter_note_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='need_cups',
            field=models.IntegerField(blank=True, default=10),
        ),
        migrations.AlterField(
            model_name='note',
            name='now_cups',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
