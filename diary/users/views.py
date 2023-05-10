from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, RemoveUser
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from entries.models import Goal, GoalExec
from entries.views import make_list
from django.http import HttpResponse
from .telegramViews import bot
from datetime import datetime


def telegram(request):
    bot.polling()
    return HttpResponse('Telegram Bot is working :)')


def unhide_div(request): #new_goal
    return render(request, 'users/home.html', {'unhide': True, 'dict_days': {'monday': False, 'tuesday': False,
                                                                             'wednesday': False, 'thursday': False,
                                                                             'friday': False, 'saturday': False,
                                                                             'sunday': False}})


def edit_goal(request):
    goal_id = request.GET.get("goal_id")

    item = Goal.objects.get(goal_id=int(goal_id))
    if item.username != f'{request.user}':
        return HttpResponse('Something went wrong. Try again.')
    return render(request, 'users/home.html', {'goal': item.goal_name, 'hour_category': item.notification_hour,
                                               'minutes_category': item.notification_minutes, 'goal_id': int(goal_id),
                                               'notifications': item.notifications, 'continuing': item.continuing,
                                               'dict_days': {'monday': item.monday, 'tuesday': item.tuesday,
                                                             'wednesday': item.wednesday, 'thursday': item.thursday,
                                                             'friday': item.friday, 'saturday': item.saturday,
                                                             'sunday': item.sunday}})


def add_goal(request):
    if request.method == 'POST':
        try:
            goal_id = request.POST['goal_id']
            item = Goal.objects.get(goal_id=goal_id)
            if item.username != f'{request.user}':
                return HttpResponse('Something went wrong. Try again.')
        except Exception as e:
            goal_id = False

        goal = request.POST.get('goal').capitalize()
        hour = request.POST.get('hour_category')
        minutes = request.POST.get('minutes_category')
        days = request.POST.getlist('option')
        close = request.POST.get('continuing')
        if close:
            continuing, notify = False, False
        else:
            continuing = True
            notify = True if request.POST.get('notifications') != None else False

        try:
            hour, minutes = int(hour) - 1, int(minutes) - 1
        except Exception as e:
            messages.error(request, f"You have not filled in all the fields. Therefore, messages will not come to the"
                                    f" goal {goal}.")
            hour, minutes = 25, 25

        if goal and goal_id:
            element = Goal(goal_id=goal_id, username=request.user.username, goal_name=goal,
                           notification_hour=hour, notification_minutes=minutes, notifications=notify,
                           continuing=continuing)
        elif goal:
            element = Goal(username=request.user.username, goal_name=goal, notification_hour=hour,
                           notification_minutes=minutes, notifications=notify, continuing=continuing)
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
                               f"You didn't specify days. Therefore, messages will not come to the goal {goal}.")

    return home(request, 'True')


def delete_goal(request):
    try:
        goal_id = int(request.GET.get('goal_id'))
        item = Goal.objects.get(goal_id=goal_id)
        if item.username != f'{request.user}':
            return HttpResponse('Something went wrong. Try again.')
        else:
            GoalExec.objects.filter(goal_id=goal_id).delete()
    except Exception as e:
        pass

    return home(request)


def return_list(set):
    count = 0
    scroll = []
    for i in range(len(set)):
        scroll.append(*set[count])
        count += 1
    return scroll


def get_goals(request):
    weekday = datetime.today().strftime('%A').lower()
    today = str(datetime.today()).split(' ')[0]
    ids_user = make_list(Goal.objects.filter(username=request.user).values_list('goal_id'))
    goals_name, goals_today, goals_done, goals_ids = [], [], [], []
    for id in ids_user:
        goal = Goal.objects.get(username=request.user, goal_id=id)
        goals_name.append(goal.goal_name)
        if GoalExec.objects.filter(goal_id=id, time=today):
            goals_done.append(True)
        else:
            goals_done.append(False)
        if getattr(goal, weekday):
            goals_today.append(True)
        else:
            goals_today.append(False)
        goals_ids.append(id)

    goals_exec = zip(goals_name, goals_today, goals_done, goals_ids)
    return goals_exec


def home(request, added_goal=''):
    if request.method == 'POST' and not added_goal:
        today = str(datetime.today()).split(' ')[0]
        need_delete = GoalExec.objects.filter(time=today)
        need_save = request.POST.getlist('days[]')

        for goal_del in need_delete:
            if goal_del:
                GoalExec.objects.get(time=today, goal_id=goal_del.goal_id).delete()
        for goal_sav in need_save:
            if goal_sav:
                GoalExec(time=today, goal_id=goal_sav, approved=True).save()

    goals = Goal.objects.filter(username=request.user)
    try:
        goals_exec = get_goals(request)
    except Exception as e:
        goals_exec = False
    return render(request, 'users/home.html', {'goals': goals, 'goals_exec': goals_exec,
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
