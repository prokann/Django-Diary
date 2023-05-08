from django.db import models


class Telegram(models.Model):
    username = models.CharField(max_length=25, default='SOME STRING')
    chat_id = models.CharField(max_length=40)



