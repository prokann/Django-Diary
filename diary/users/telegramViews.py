from entries.models import Goal, GoalExec
# from entries.views import make_list
import time
import telebot
from django.contrib.auth.models import User
from .models import Telegram
from entries.models import Goal, GoalExec
import threading


bot = telebot.TeleBot('')


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
                                     f'Зараз вже {str(hour).zfill(2)}:{str(min).zfill(2)}, прийшов час виповняти ціль - '
                                     f'{goal.goal_name}')

            new_time = time.strftime('%A:%H:%M')


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "Привіт! Напиши свій нік у Твій День, щоб ми синхронізували твій аккаунт і в "
                                      "подальшому змогли тобі нагадувати про виконання твоїх справ. Реклами не буде, "
                                      "обіцяємо :)")


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'Цей бот створено, щоб Вам приходили повідомлення про Ваші цілі у час, який Ви '
                                      'обрали на сайті.\nЯкщо хочете його змінити чи прибрати повідомлення взагалі, '
                                      'зайдіть на сторінку Твій День: налаштування.')


@bot.message_handler(content_types=['text'])
def save_chat_id(message):
    if not Telegram.objects.filter(chat_id=message.chat.id).exists():
        if User.objects.filter(username=message.text).exists():
            if Telegram.objects.filter(username=message.text).exists():
                Telegram.objects.filter(username=message.text).update(chat_id=message.chat.id)
            else:
                Telegram(username=message.text, chat_id=message.chat.id).save()

            bot.send_message(message.chat.id, 'Супер! Ми надішлемо повідомлення, коли прийде час нагадати про справи.')
        else:
            bot.send_message(message.chat.id, 'Ви ввели неіснуючий нікнейм. Напишіть ще раз.')
    else:
        bot.send_message(message.chat.id, 'Вам прийде повідомлення у час, який Ви вказали на сайті.')


notificate_thread = threading.Thread(target=notificate)
notificate_thread.start()

