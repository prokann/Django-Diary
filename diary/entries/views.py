from django.shortcuts import render
from django.core.files import File
from .models import *
from calendar import HTMLCalendar, month_name, monthrange
from django.db.models.functions import ExtractMonth, ExtractYear, TruncDay
from django.db.models import Max
import calendar
from django.db.models import F, Window
import urllib, base64
import plotly.graph_objs as go
from django.http import HttpResponse
from datetime import datetime
from django.contrib import messages


# standard funcs
def check_field(belonging, value):
    try:
        result = belonging(value)
    except Exception as e:
        result = None
    return result


def time_filter(request, queryset_, class_, month_=None, year_=None, day_=None):
    if day_ is None or day_ == '':
        from_date = datetime(year_, month_, 1, 0, 0, 0, 0)
        to_date = datetime(year_, month_, monthrange(year_, month_)[1], 0, 0, 0, 0)
    else:
        from_date = datetime(year_, month_, int(day_), 0, 0, 0, 0)
        to_date = datetime(year_, month_, int(day_), 23, 59, 59, 0)

    queryset_ = class_.objects.filter(username=request.user).filter(time__gte=from_date, time__lte=to_date).\
        values_list(queryset_)
    return make_list(queryset_)


def make_list(queryset_, false=''):
    list_note = []
    if len(queryset_) > 0:
        try:
            for i in range(len(queryset_)):
                list_note.append(*queryset_[i])
        except Exception as e:
            for i in range(len(queryset_)):
                if false:
                    list_note.append(queryset_[i] + (False,))
                else:
                    list_note.append(queryset_[i])

    return list_note


def return_date(month_=datetime.now().month, year_=datetime.now().year):
    calendar_ = HTMLCalendar(firstweekday=0)
    calendar_ = calendar_.formatmonth(year_, month_)
    month_n = month_name[month_]
    return calendar_, month_, month_n, year_


def return_notes_lists(request, day_='', month=''):
    day_ = request.POST.get('new_day')
    month_ = request.POST.get('new_month')
    if not month_:
        month_ = month

    if month_:
        calendar_, month_, month_n, year_ = return_date(int(month_))

    else:
        calendar_, month_, month_n, year_ = return_date()

    # show notes
    id, username, time, mood, note, need_cups, now_cups = time_filter(request, 'id', Note, month_, year_, day_),\
                                                      time_filter(request, 'username', Note, month_, year_, day_), \
                                                      time_filter(request, 'time', Note, month_, year_, day_), \
                                                      time_filter(request, 'mood', Note, month_, year_, day_), \
                                                      time_filter(request, 'note', Note, month_, year_, day_), \
                                                      time_filter(request, 'need_cups', Note, month_, year_, day_),\
                                                      time_filter(request, 'now_cups', Note, month_, year_, day_)
    lenght_notes = [i for i in range(len(time))]
    if lenght_notes:
        notes = zip(id, username, time, mood, note, need_cups, now_cups, lenght_notes)
    else:
        notes = None

    lists = time_filter(request, 'time', Lists, month_, year_, day_)

    # show lists
    if lists:
        id_list, name_list, time_list, wc, wa, hc, ha, rc, ra, dc, da = [], [], [], [], [], [], [], [], [], [], []
        for i in lists:
            el = Lists.objects.get(time=i)

            id_list.append(el.list_id)
            name_list.append(el.list_name)
            time_list.append(i)

            wc.append(ListsWork.objects.filter(list_id=el.list_id).values_list('case_name'))
            wa.append(ListsWork.objects.filter(list_id=el.list_id).values_list('approved'))

            hc.append(ListsHome.objects.filter(list_id=el.list_id).values_list('case_name'))
            ha.append(ListsHome.objects.filter(list_id=el.list_id).values_list('approved'))

            rc.append(ListsRest.objects.filter(list_id=el.list_id).values_list('case_name'))
            ra.append(ListsRest.objects.filter(list_id=el.list_id).values_list('approved'))

            dc.append(ListsDevelopment.objects.filter(list_id=el.list_id).values_list('case_name'))
            da.append(ListsDevelopment.objects.filter(list_id=el.list_id).values_list('approved'))

        lists = zip(id_list, name_list, time_list, wc, wa, hc, ha, rc, ra, dc, da)

    return notes, lists, calendar_, day_, month_n, year_


def all_notes(request):
    notes, lists, calendar_, day_, month_n, year_ = return_notes_lists(request)

    return render(request, 'entries/all_notes.html', {'notes': notes, 'lists': lists,
                                                      'calendar_': calendar_, 'day_': day_,  'month_n': month_n,
                                                      'year_': year_})


moods = {'success': 'success.png',
         'satisfactory': 'satisfactory.png',
         'normal': 'normal.png',
         'bad': 'bad.png',
         'awful': 'awful.png'}


def new_note(request):
    if request.method == 'GET':
        try:
            need_cups = Note.objects.filter(username=request.user).values_list('need_cups').last()[0]
        except Exception as e:
            need_cups = 15

        return render(request, 'entries/new_note.html', {'need_cups': need_cups, 'moods': moods})
    else:
        return render(request, 'entries/new_note.html', {'moods': moods})


# functions with notes
def write_note(request):
    if request.method == 'POST':
        mood = request.POST.get('name_mood')
        if not mood:
            mood = 'normal'
        note = request.POST['note'].strip()

        need_cups = request.POST['need_cups']
        now_cups = request.POST['now_cups']

        need_cups = check_field(int, need_cups)
        now_cups = check_field(int, now_cups)

        try:
            if need_cups is None:
                need_cups = Note.objects.filter(username=request.user).values_list('need_cups').last()[0]
        except Exception as e:
            need_cups = 20

        if now_cups is None:
            now_cups = 0

        try:
            id_note = request.POST['id_note']

            item = Note.objects.get(id=id_note)
            if item.username != f'{request.user}':
                return HttpResponse('Something went wrong. Try again.')

            element = Note(id=id_note, username=request.user.username, mood=mood, note=note, need_cups=need_cups,
                           now_cups=now_cups)
            element.save()
        except Exception as e:
            element = Note(username=request.user.username, mood=mood, note=note, need_cups=need_cups, now_cups=now_cups)
            element.save()
            id_note = element.id
        return render(request, 'entries/new_note.html', {'mood': mood, 'note': note, 'need_cups': need_cups,
                                                 'now_cups': now_cups, 'id_note': id_note, 'moods': moods})


def edit_note(request):
    id_note = request.GET.get("id_note")
    note = Note.objects.get(id=int(id_note))
    if note.username != f'{request.user}':
        return HttpResponse('Something went wrong. Try again.')
    else:
        return render(request, 'entries/new_note.html', {'mood': note.mood, 'note': note.note,
                                                         'need_cups': note.need_cups, 'now_cups': note.now_cups,
                                                         'id_note': id_note, 'moods': moods})


def delete_note(request):
    id_note = request.GET.get("id_note")
    element = Note.objects.get(id=int(id_note))
    try:
        if element.username != f'{request.user}':
            return HttpResponse('Something went wrong. Try again.')
        else:
            element.delete()
    except Exception as e:
        return HttpResponse('Something went wrong. Try again.')

    return all_notes(request)


# functions with lists
def will_did_case(request, id_list=''):
    try:
        month_n = request.GET.get('day_month').split(', ')[1]
        day_ = request.GET.get('day_month').split(', ')[0]
        month_ = list(month_name).index(month_n)
    except Exception as e:
        pass

    def update_false():
        ListsWork.objects.filter(list_id=int(id_list)).update(approved=False)
        ListsHome.objects.filter(list_id=int(id_list)).update(approved=False)
        ListsRest.objects.filter(list_id=int(id_list)).update(approved=False)
        ListsDevelopment.objects.filter(list_id=int(id_list)).update(approved=False)

    cases = request.POST.getlist('boxes[]')
    try:
        # if new note
        if request.POST['categories']:
            ids = request.POST['id_list']
            if not ids:
                ids = id_list
            ids = int(ids)

        update_false()

    # if all notes
    except Exception as e:
        notes, lists, calendar_, day_, month_n, year_ = return_notes_lists(request, day_, month_)
        lists = list(lists)
        ids = time_filter(request, 'list_id', Lists, list(month_name).index(month_n), year_, day_)
        for id_list in ids:
            update_false()

    for list_ in cases:
        category = list_.split(', ')[0]
        case = list_.split(', ')[1:-1]
        case = case[0]
        id_list = int(list_.split(', ')[-1])

        if category == 'work':
            ListsWork.objects.filter(case_name=case, list_id=id_list).update(approved=True)
        elif category == 'home':
            ListsHome.objects.filter(case_name=case, list_id=id_list).update(approved=True)

        elif category == 'rest':
            ListsRest.objects.filter(case_name=case, list_id=id_list).update(approved=True)

        elif category == 'development':
            ListsDevelopment.objects.filter(case_name=case, list_id=id_list).update(approved=True)

    return render(request, 'entries/all_notes.html', {'notes': notes, 'lists': lists, 'calendar_': calendar_,
                                                      'day_': day_, 'month_n': month_n, 'month_': month_,
                                                      'year_': year_})


def save_list(request, id_list=''):
    name_list = None

    try:
        id_list = request.POST['id_list']
        name_list = request.POST['name_list']
    except Exception as e:
        pass
    if not id_list:
        id_list = request.GET.get("id_list")

    if id_list:
        item = Lists.objects.get(list_id=id_list)
        if item.username != f'{request.user}':
            return HttpResponse('Something went wrong. Try again.')
    else:
        id_list = id_list
    try:
        need_cups = Note.objects.filter(username=request.user).values_list('need_cups').last()[0]
    except Exception as e:
        need_cups = 15

    try:
        def save_case():
            if category == 'work':
                element = ListsWork(case_name=case, list_id=new_list.list_id)
            elif category == 'home':
                element = ListsHome(case_name=case, list_id=new_list.list_id)
            elif category == 'rest':
                element = ListsRest(case_name=case, list_id=new_list.list_id)
            elif category == 'development':
                element = ListsDevelopment(case_name=case, list_id=new_list.list_id)
            element.save()

        category = request.POST['categories']
        case = request.POST['case']

        if case:
            try:
                id_list = int(id_list)
                new_list = Lists(list_id=id_list, username=request.user.username, list_name=name_list)
            except Exception as e:
                new_list = Lists(username=request.user.username, list_name=name_list)

            new_list.save()
            id_list = new_list.list_id

            try:
                if ListsWork.objects.filter(list_id=id_list, case_name=case) or ListsHome.objects.filter(
                        list_id=id_list, case_name=case) or ListsRest.objects.filter(list_id=id_list, case_name=case) \
                        or ListsDevelopment.objects.filter(list_id=id_list, case_name=case):
                    pass
                else:
                    save_case()
            except Exception as e:
                save_case()

        will_did_case(request, id_list)
    except Exception as e:
        pass

    def show_cases(class_, column):
        return make_list(class_.objects.filter(list_id=id_list).values_list(column))

    work, work_app = show_cases(ListsWork, 'case_name'), show_cases(ListsWork, 'approved')
    home, home_app = show_cases(ListsHome, 'case_name'), show_cases(ListsHome, 'approved')
    rest, rest_app = show_cases(ListsRest, 'case_name'), show_cases(ListsRest, 'approved')
    development, development_app = show_cases(ListsDevelopment, 'case_name'), show_cases(ListsDevelopment,
                                                                                         'approved')

    work_z, home_z, rest_z, development_z = zip(work, work_app), zip(home, home_app), zip(rest, rest_app), zip(
        development, development_app)

    return render(request, 'entries/new_note.html', {'name_list': name_list, 'work': work_z, 'home': home_z,
                                                         'rest': rest_z, 'development': development_z,
                                                         'need_cups': need_cups, 'id_list': id_list})


def delete_list(request):

    def accept_deleted(class_, id_list):
        try:
            items = class_.objects.filter(list_id=int(id_list))
            items.delete()
        except Exception as e:
            pass

    id_list = request.GET.get("id_list")

    try:
        element = Lists.objects.get(list_id=int(id_list))
        if element.username != f'{request.user}':
            return HttpResponse('Something went wrong. Try again.')

        accept_deleted(ListsWork, id_list)
        accept_deleted(ListsHome, id_list)
        accept_deleted(ListsRest, id_list)
        accept_deleted(ListsDevelopment, id_list)
        element.delete()
    except Exception as e:
        pass

    return all_notes(request)


def delete_case(request):
    category = request.GET.get("cat_case_idl").split(', ')[0]
    case = request.GET.get("cat_case_idl").split(', ')[1:-1]
    case = case[0]
    id_list = int(request.GET.get("cat_case_idl").split(', ')[-1])
    if category == 'work':
        ListsWork.objects.filter(list_id=id_list, case_name=case).delete()

    elif category == 'home':
        ListsHome.objects.filter(list_id=id_list, case_name=case).delete()

    elif category == 'rest':
        ListsRest.objects.filter(list_id=id_list, case_name=case).delete()

    elif category == 'development':
        ListsDevelopment.objects.filter(list_id=id_list, case_name=case).delete()

    # check if list not empty now
    if not ListsWork.objects.filter(list_id=id_list) and not ListsHome.objects.filter(list_id=id_list) and \
            not ListsRest.objects.filter(list_id=id_list) and not ListsDevelopment.objects.filter(list_id=id_list):
        element = Lists.objects.get(list_id=id_list)
        element.delete()
    return save_list(request, id_list)


def download_data(request):
    queryset_ = Note.objects.filter(username=request.user).values_list('time', 'mood', 'note', 'need_cups', 'now_cups')
    values = ['time', 'mood', 'note', 'need_cups', 'now_cups']

    # if notes is empty
    if queryset_:
        f = open('notes.txt', 'w')
        testfile = File(f)
        for set in queryset_:
            i = 0
            for field in set:
                f.write(f'{values[i]}: ')
                f.write(str(field).replace('(', '').replace(')', ''))
                f.write('\n')
                i += 1
            f.write('\n')
        testfile.close()
        f.close()

        file_path = 'notes.txt'
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename="notes.txt"'
            return response
    return all_notes(request)


def statistics(request):
    month_ = request.POST.get('new_month')
    date = datetime.now()
    year_ = date.year
    if not month_:
        month_, month_n = date.month, date.strftime("%B")
    else:
        month_n = calendar.month_name[int(month_)]

    def build_graphic(graph, goal_name=''):
        if not goal_name:
            data = Note.objects.annotate(month=ExtractMonth('time'), year=ExtractYear('time')).\
                filter(month=month_, year=year_).annotate(day=TruncDay('time')).values('day').\
                annotate(last_time=Max('time')).order_by('day', '-last_time')
            days = [day['day'].strftime('%d') for day in data.values('day')]
            fig = go.Figure()

            if graph == 'water':
                data = data.annotate(max_now_cups=Max('now_cups'), max_need_cups=Max('need_cups')) \
                    .order_by('day')

                need = [cup['max_need_cups'] for cup in data]
                drinked = [cup['max_now_cups'] for cup in data]

                fig.add_trace(go.Bar(x=days, y=drinked, name='Amount consumed'))
                fig.add_trace(go.Scatter(x=days, y=need, name='Your daily intake'))
                fig.update_layout(xaxis_title='Day', yaxis_title='Amount', title=f'Water consumption for {month_n} {year_}',
                                  legend=dict(x=0, y=1))

            elif graph == 'mood':
                data = Note.objects.annotate(month=ExtractMonth('time'), year=ExtractYear('time')).\
                    filter(month=month_, year=year_).annotate(day=TruncDay('time')).\
                    annotate(latest_mood=Window(expression=Max('time'),
                                                partition_by=[F('day')], order_by=F('time').desc(),),).\
                    filter(time=F('latest_mood')).values('day', 'mood').order_by('day')

                mood = [m['mood'] for m in data]
                days = [d['day'].strftime('%d') for d in data]
                fig.add_trace(go.Bar(x=days, y=mood, name='Your moods'))
                fig.update_layout(xaxis_title='Day', yaxis_title='Mood', title=f'Mood tracker for {month_n} {year_}',
                                  legend=dict(x=0, y=1))
        else:
            goal = Goal.objects.get(goal_name=goal_n)
            need_to_do = [goal.monday, goal.tuesday, goal.wednesday, goal.thursday, goal.friday, goal.saturday,
                          goal.sunday]

            exec = GoalExec.objects.filter(goal_id=goal.goal_id).values_list('time')
            goal_exec = []
            for day in exec:
                goal_exec.append(*day)
            dates = [date for date in calendar.Calendar().itermonthdates(year_, int(month_)) if date.month == int(month_)]

            days = [day.strftime("%Y-%m-%d") for day in dates]
            need_to_do_days = [need_to_do[datetime.strptime(day, "%Y-%m-%d").date().weekday()] for day in days]

            goal_exec_days = [any(datetime.strptime(item, '%Y-%m-%d').date() == day for item in goal_exec)
                              for day in dates]

            colors = []
            for i in range(len(days)):
                if goal_exec_days[i]:
                    colors.append('green')
                elif need_to_do_days[i]:
                    colors.append('red')
                else:
                    colors.append('gray')

            trace = go.Scatter(x=days, y=[1] * len(days), mode='markers', marker=dict(
                size=25, color=colors, opacity=0.8, line=dict(width=1, color='black')))

            layout = go.Layout(title=f'Goal "{goal_n}" Execution', xaxis=dict(title='Day'), yaxis=dict(
                showticklabels=False, showgrid=False), hovermode='closest')

            fig = go.Figure(data=[trace], layout=layout)

        fig_bytes = fig.to_image(format='png', engine='kaleido')
        image = base64.b64encode(fig_bytes).decode('utf-8')
        url = 'data:image/png;base64,{}'.format(urllib.parse.quote(image))

        return url

    goals = Goal.objects.filter(username=request.user)
    goal_n = request.POST.get('choose_goal')
    if not goal_n:
        goal_n = goals[0].goal_name
    water, mood, goal = build_graphic('water'), build_graphic('mood'), build_graphic('goal', goal_n)

    return render(request, 'entries/statistics.html', {month_: 'month_', 'year_': year_, 'month_n': month_n,
                                                       'water_url': water, 'mood_url': mood, 'goal_url': goal,
                                                       'goals': goals})


def unhide_div(request): #new_goal
    return render(request, 'entries/goals.html', {'unhide': True, 'dict_days': {'monday': False, 'tuesday': False,
                                                                             'wednesday': False, 'thursday': False,
                                                                             'friday': False, 'saturday': False,
                                                                             'sunday': False}})


def edit_goal(request):
    goal_id = request.GET.get("goal_id")

    item = Goal.objects.get(goal_id=int(goal_id))
    if item.username != f'{request.user}':
        return HttpResponse('Something went wrong. Try again.')
    return render(request, 'entriesf/goals.html', {'goal': item.goal_name, 'hour_category': item.notification_hour,
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

    return goals(request, 'True')


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

    return goals(request)


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


def goals(request, added_goal=''):
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
    return render(request, 'entries/goals.html', {'goals': goals, 'goals_exec': goals_exec,
                                               'days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                                                        'saturday', 'sunday']})



