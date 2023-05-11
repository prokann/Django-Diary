from django.shortcuts import render
from django.core import serializers
from django.core.files import File
from .models import Note, Lists, ListsWork, ListsHome, ListsRest, ListsDevelopment
from datetime import datetime
from calendar import HTMLCalendar, month_name, monthrange
from django.http import HttpResponse


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


moods = {'excellent': 'excellent.png',
         'good': 'good.png',
         'normal': 'normal.png',
         'bad': 'bad.png',
         'horrible': 'horrible.png'}


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
            pass

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
    return render(request, 'entries/statistics.html')







