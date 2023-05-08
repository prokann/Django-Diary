from django.db import models


class Note(models.Model):
    username = models.CharField(max_length=25, default='SOME STRING')
    time = models.DateTimeField(auto_now=True)

    mood = models.CharField(max_length=15)
    note = models.CharField(max_length=1000000)
    need_cups = models.IntegerField(default=10, blank=True, null=True)
    now_cups = models.IntegerField(default=0, blank=True, null=True)
    # image = models.ImageField(upload_to=None, height_field=None, width_field=None, max_length=100, blank=True)


class Lists(models.Model):
    list_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=25, default='SOME STRING')
    list_name = models.CharField(max_length=25, blank=True, null=True)
    time = models.DateTimeField(auto_now=True)


class ListsWork(models.Model):
    list_id = models.IntegerField()
    case_name = models.CharField(max_length=25, default='SOME STRING')
    approved = models.BooleanField(default=False)


class ListsHome(models.Model):
    list_id = models.IntegerField()
    case_name = models.CharField(max_length=25, default='SOME STRING')
    approved = models.BooleanField(default=False)


class ListsRest(models.Model):
    list_id = models.IntegerField()
    case_name = models.CharField(max_length=25, default='SOME STRING')
    approved = models.BooleanField(default=False)


class ListsDevelopment(models.Model):
    list_id = models.IntegerField()
    case_name = models.CharField(max_length=25, default='SOME STRING')
    approved = models.BooleanField(default=False)


class Goal(models.Model):
    goal_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=25, default='SOME STRING')
    goal_name = models.CharField(max_length=25, default='SOME STRING')
    notification_hour = models.IntegerField(blank=True, null=True)
    notification_minutes = models.IntegerField(blank=True, null=True)
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)


class GoalExec(models.Model):
    goal_id = models.IntegerField()
    approved = models.BooleanField(default=False)
    time = models.DateTimeField(auto_now=True)









