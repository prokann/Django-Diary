from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, RemoveUser
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# from .models import Telegram
from entries.models import Goal, GoalExec
from django.http import HttpResponse
from .telegramViews import bot


def telegram(request):
    # bot.polling()
    return HttpResponse('gf')


def unhide_div(request): #new_goal
    return render(request, 'users/home.html', {'unhide': True, 'dict_days': {'monday': False, 'tuesday': False,
                                                                             'wednesday': False, 'thursday': False,
                                                                             'friday': False, 'saturday': False,
                                                                             'sunday': False}})


def edit_goal(request):
    goal_id = request.GET.get("goal_id")
    if goal_id:
        el = Goal.objects.get(goal_id=int(goal_id))
        return render(request, 'users/home.html', {'goal': el.goal_name, 'hour_category': el.notification_hour,
                                                   'minutes_category': el.notification_minutes, 'goal_id': int(goal_id),
                                                   'dict_days': {'monday': el.monday, 'tuesday': el.tuesday,
                                                                 'wednesday': el.wednesday, 'thursday': el.thursday,
                                                                 'friday': el.friday, 'saturday': el.saturday,
                                                                 'sunday': el.sunday}})


def add_goal(request):
    if request.method == 'POST':
        try:
            goal_id = request.POST['goal_id']
            item = Goal.objects.get(goal_id=goal_id)
            if item.username != f'{request.user}':
                return HttpResponse('Щось пішло не так. Спробуйте ще раз.')
        except Exception as e:
            goal_id = False

        goal = request.POST.get('goal').capitalize()
        hour = request.POST.get('hour_category')
        minutes = request.POST.get('minutes_category')
        days = request.POST.getlist('option')

        try:
            hour, minutes = int(hour) - 1, int(minutes) - 1
        except Exception as e:
            messages.error(request, f"Ви заповнили не всі поля. Тому повідомлення на ціль {goal} приходити не будуть.")
            hour, minutes = 25, 25

        if goal and goal_id:
            element = Goal(goal_id=goal_id, username=request.user.username, goal_name=goal,
                           notification_hour=hour, notification_minutes=minutes)
        elif goal:
            element = Goal(username=request.user.username, goal_name=goal, notification_hour=hour,
                           notification_minutes=minutes)
        element.save()

        def make_true(day):
            Goal.objects.filter(goal_id=element.goal_id).update(**{day: True})

        if days[0] == 'every_day':
            make_true('monday'), make_true('tuesday'), make_true('wednesday'), make_true('thursday'), make_true(
                'friday'), make_true('saturday'), make_true('sunday')
        else:
            days = request.POST.getlist('days[]')
            if len(days) > 0:
                for day in days:
                    make_true(day)
            else:
                messages.error(request,
                                   f"Ви не вказали дні. Тому повідомлення на ціль {goal} приходити не будуть.")

    return home(request)


def notify_off(request):
    goal_id = request.GET.get("goal_id")
    try:
        Goal.objects.filter(goal_id=int(goal_id)).update(monday=False, tuesday=False, wednesday=False, thursday=False,
                                                         friday=False, saturday=False, sunday=False)
    except Exception as e:
        pass
    #and notificate
    return home(request)


def notify_on(request):
    return home(request)


def close_goal(request):
    return home(request)


def delete_goal(request):
    return home(request)


def return_list(set):
    count = 0
    scroll = []
    for i in range(len(set)):
        scroll.append(*set[count])
        count += 1
    return scroll


def home(request):
    goals = Goal.objects.filter(username=request.user)

    return render(request, 'users/home.html', {'goals': goals,
                                               'days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                                                        'saturday', 'sunday']})


def register_user(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Hi, {username}! Your account was created successfully.')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required()
def profile(request):
    # phone = Phone.objects.filter(username=request.user).values_list('phone_number')
    # context = {"phone_number": return_list(phone)}
    # return render(request, 'users/profile.html', context)
    return render(request, 'users/profile.html')


def edit_email(request):
    if request.method == 'POST':
        email = request.POST['email']

        User.objects.filter(username=request.user).update(email=email)
    return render(request, 'users/profile.html')


def remove_user(request):

    if request.method == 'GET':
        form = RemoveUser(request.GET)
        rem = User.objects.get(username=request.user)
        if rem is not None:
            rem.delete()
            messages.success(request, f'Bye, {request.user}. Your account was deleted.')
            return render(request, 'users/home.html')
        else:
            pass
               # Send some error messgae
    else:
        form = RemoveUser()
    context = {'form': form}
    return render(request, 'users/home.html', context)
