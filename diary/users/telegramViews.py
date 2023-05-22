import time
import telebot
from django.contrib.auth.models import User
from .models import Telegram
from entries.models import Goal, GoalExec
import threading
from decouple import config


bot = telebot.TeleBot(config('TOKEN'))


def notificate():
    new_time, current_time = False, True
    while True:
        if new_time == current_time:
            current_time = time.strftime('%A:%H:%M')
        else:
            current_time = time.strftime('%A:%H:%M')
            day = current_time.split(':')[0].lower()
            hour = int(current_time.split(':')[1])
            min = int(current_time.split(':')[2])
            goals = Goal.objects.all()

            for goal in goals:
                if goal.continuing and goal.notifications:
                    if hour == goal.notification_hour and min == goal.notification_minutes \
                            and Telegram.objects.filter(username=goal.username).exists():

                        if 'monday' == day and goal.monday or \
                                'tuesday' == day and goal.tuesday or \
                                'wednesday' == day and goal.wednesday or \
                                'thursday' == day and goal.thursday or \
                                'friday' == day and goal.friday or \
                                'saturday' == day and goal.saturday or \
                                'sunday' == day and goal.sunday:

                            bot.send_message(Telegram.objects.get(username=goal.username).chat_id,
                                         f"It's already {str(hour).zfill(2)}:{str(min).zfill(2)}, it's time "
                                         f"to fulfill the goal - {goal.goal_name}")

            new_time = time.strftime('%A:%H:%M')


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "Hello! Write your nickname in Your Day so that we can synchronize your account "
                                      "and in the future we can remind you about the completion of your tasks. There "
                                      "will be no ads, we promise :)")


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'This bot was created so that you receive messages about your goals at the time '
                                      'you choose on the site.\nIf you want to change it or remove the message '
                                      'altogether, go [here](https://www.google.com) and click "Edit goal" near goal'
                                      'you need.') #link!!


@bot.message_handler(content_types=['text'])
def save_chat_id(message):
    if not Telegram.objects.filter(chat_id=message.chat.id).exists():
        if User.objects.filter(username=message.text).exists():
            if Telegram.objects.filter(username=message.text).exists():
                Telegram.objects.filter(username=message.text).update(chat_id=message.chat.id)
            else:
                Telegram(username=message.text, chat_id=message.chat.id).save()

            bot.send_message(message.chat.id, "Super! We'll send a message when it's time to remind you about things.")
        else:
            bot.send_message(message.chat.id, 'You have entered a nickname that does not exist. Write again.')
    else:
        bot.send_message(message.chat.id, 'You will receive a message at the time you indicated on the website.')


notificate_thread = threading.Thread(target=notificate)
notificate_thread.start()

