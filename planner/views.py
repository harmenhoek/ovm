from django.shortcuts import render
from planner.custom_functions import MakePlanning, PlanningToArray, ArrayToTable, toSeconds, TableHeaderFooter
from central.models import Planning, ShiftDay, Post, ShiftTime
from datetime import datetime, timedelta, date
import datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
import json
from .forms import ModifyPlanningPlanner, AddPlanningPlanner, AddOccupationPlanner
from django.db.models import F, Q, Subquery, OuterRef, Value, CharField, DateTimeField, Min
import logging
import itertools

def current_shift(dayname=None, timename=None):
    '''
    For a given dayname and timename (as strings, e.g. Zaterdag 1), it returns the shift date, starttime and endttime.
    If no input is given into the func, it finds the date, starttime, endtime, dayname and daytime for the current date
    and time.
    '''

    datenow = datetime.date.today()
    timenow = datetime.datetime.now().time()

    if dayname is None:
        # see if current date is in list
        if ShiftDay.objects.filter(active=True, date=datenow):
            date, dayname = ShiftDay.objects.filter(active=True, date=datenow).values_list('date', 'dayname')[0]
        else:
            date, dayname = ShiftDay.objects.filter(active=True).values_list('date', 'dayname')[0]
    else:
        date = ShiftDay.objects.get(active=True, dayname__iexact=dayname).date

    if timename is None:
        if ShiftTime.objects.filter(active=True, timestart__lt=timenow, timeend__gt=timenow):
            timestart, timeend, timename = ShiftTime.objects.filter(active=True, timestart__lt=timenow, timeend__gt=timenow).values_list('timestart', 'timeend', 'timename')[0]
        else:
            timestart, timeend, timename = ShiftTime.objects.filter(active=True).values_list('timestart', 'timeend', 'timename')[0]
    else:
        timestart, timeend = ShiftTime.objects.filter(active=True, timename__iexact=timename).values_list('timestart', 'timeend')[0]

    return dayname, date, timename, timestart, timeend

def next_shift(dayname_current, timename_current):
    '''
    For a given dayname and timename (e.g. Zaterdag 2) it returns the next shift, e.g.:
        Zaterdag 2 --> Zaterdag 3
        Zondag 1 --> Zondag 2
        Vrijdag 4 --> Zaterdag 1
        Maandag 4 --> Vrijdag 1

    It first finds the next shifttime by doing current shiftname + 1, if there are no results in the database (when
    shiftname=4), it gets the first shiftname in the table, i.e. 1.
    If shiftname = 1, we should find the next day too, so we set new_day=True, and then query the ShiftDay table
    in a similar manner to find the next shiftday. If new_day=False, it returns the input day.
    '''

    new_day = False
    shifttime_next = ShiftTime.objects.filter(timename__gt=timename_current).order_by('id').first()
    if not shifttime_next:
        shifttime_next = ShiftTime.objects.order_by('timename').first()
        new_day = True
    timename_next = shifttime_next.timename

    if new_day:
        shiftday_next = ShiftDay.objects.filter(dayname__gt=dayname_current).order_by('date').first()
        if not shiftday_next:
            shiftday_next = ShiftDay.objects.order_by('date').first()
        dayname_next = shiftday_next.dayname
    else:
        dayname_next = dayname_current

    return dayname_next, timename_next


@staff_member_required
def planner(request, dayname=None):
    '''
    The main planner page. Note that only the general data is loaded here (daynames for the buttons eg), the inner table
    data is loaded in plannertable to enable AJAX.
    It also gets the next shift info, needed for the Shift Wissel href.
    '''
    if dayname is None:
        # see if current date is in list
        if ShiftDay.objects.filter(active=True, date=date.today()):
            daydate = ShiftDay.objects.get(active=True, date=date.today()).date
            dayname = ShiftDay.objects.get(active=True, date=date.today()).dayname
        else:
            daydate = ShiftDay.objects.filter(active=True)[0].date
            dayname = ShiftDay.objects.filter(active=True)[0].dayname
    else:
        daydate = ShiftDay.objects.get(active=True, dayname__iexact=dayname).date

    alldays = ShiftDay.objects.filter(active=True).order_by('date')

    dayname_now, _, timename_now, _, _ = current_shift()
    nextshift_dayname, nextshift_timename = next_shift(dayname_now, timename_now)

    return render(request, 'planner/planner_list.html', {'currentday': dayname, 'alldays': alldays, 'daydate': daydate,
                                                         'nextshift_dayname': nextshift_dayname,
                                                         'nextshift_timename': nextshift_timename,
                                                         })

@staff_member_required
def plannertable(request, dayname, print=None):
    resolution = 15 * 60
    time_start = 7 * 60 * 60
    time_end = 24 * 60 * 60
    headercolspan = 4

    daydate = ShiftDay.objects.get(dayname__iexact=dayname).date

    reference = toSeconds(daydate, datetime.time(0, 0))

    from django.db.models import IntegerField
    from django.db.models.functions import Cast
    # posts = Post.objects.values('pk', 'post_fullname', 'postslug').filter(active=True).order_by('postslug')
    posts = Post.objects.values('pk', 'post_fullname', 'postslug').filter(active=True).annotate(my_integer_field=Cast('postslug', IntegerField())).order_by('my_integer_field', 'postslug')


    html = TableHeaderFooter('thead', time_start=time_start, time_end=time_end, resolution=resolution, colspan=headercolspan)
    html += "<tbody>"

    from itertools import cycle
    row_colors = cycle(['#ffffff', '#ededed'])

    for post in posts:
        # get data
        planning = Planning.objects.filter(removed=False, user=None, date=daydate, post__pk=post['pk']).values()
        occupation = Planning.objects.filter(removed=False, date=daydate, post__pk=post['pk']).exclude(user=None).values()
        if occupation or planning:
            plan = []
            # restructure
            for p in planning:
                plan.append({'id': p['id'], 'start': toSeconds(p['date'], p['starttime'], reference=reference), 'end': toSeconds(p['date'], p['endtime'], reference=reference)})

            occ = []
            for o in occupation:
                occ.append({'id': o['id'], 'start': toSeconds(o['date'], o['starttime'], reference=reference), 'end': toSeconds(o['date'], o['endtime'], reference=reference)})

            import logging
            logging.warning(f">>>>>>>>>>>>>>>>> occ:")
            for temp in occ:
                logging.warning(f"{temp}")

            planning, plannew, occnew = MakePlanning(occ[:], plan[:])  # pass copies  DO NOT DO ANYTHING WITH occnew, it is the non overlap only!
            LUT = plannew + occ
            occTable, plannewTable, finalTable = PlanningToArray(occ, plannew, time_start, time_end, resolution)


            logging.warning(f"0000000000 planning: {planning}")
            logging.warning(f"0000000000 plannew: {plannew}")
            logging.warning(f"0000000000 occnew: {occnew}")

            logging.warning(f">>>>>>>>>>>>>>>>> finalTable:")
            for temp in finalTable:
                logging.warning(f"{temp}")

            html += ArrayToTable(finalTable, post['postslug'], post['pk'], LUT, dayname, next(row_colors))

            # #TEMP
            # cnt += 1
            # if cnt == 1:
            #     return render(request, 'planner/planner_list_table.html', {'html': html})

    html += TableHeaderFooter('tfoot', time_start=time_start, time_end=time_end, resolution=resolution, colspan=headercolspan)
    html += "</tbody>"
    if print:
        return render(request, 'planner/planner_print.html', {'html': html, 'dayname': dayname})
    return render(request, 'planner/planner_list_table.html', {'html': html})


@staff_member_required
def planner_modify(request, pk, start=None, end=None):
    plan_item = get_object_or_404(Planning, pk=pk)

    if request.method == "POST":
        form = ModifyPlanningPlanner(request.POST, instance=plan_item)
        if form.is_valid():
            form.save()
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "planningUpdated": None,
                        "showMessage": f"Planning aangepast."
                    })
                })

    else:
        starttime = datetime.datetime.combine(date.today(), datetime.time(0, 0)) + datetime.timedelta(seconds=start)
        endtime = datetime.datetime.combine(date.today(), datetime.time(0, 0)) + datetime.timedelta(seconds=end)

        form = ModifyPlanningPlanner(instance=plan_item, initial={'starttime': starttime, 'endtime': endtime})

    return render(request, 'central/planningmodify_form.html', {
        'form': form, 'plan_pk': plan_item.pk, 'start': start, 'end': end,
    })


@staff_member_required
def shift_change(request, dayname=None, timename=None):
    '''
    This function returns all the info needed for the next shift change, i.e. for each sector (Noord, Zuid, etc) and
    each post it gives the changes that are happening within a timeframe: who is new, cancelling, changing posts.

    TODO: add people that remain, and thus might need a short break
    '''

    TESTING = False  # sets any date-time preferred to return at least some data

    if TESTING:
        timename = 1

    # get date, starttime and enttime of the selected shift. If no shift is selected, it uses the current datetime to
    # find the current and next timename and dayname.
    dayname, date, timename, timestart, timeend = current_shift(dayname, timename)

    if TESTING:
        date_string = '2023-06-04'
        date = datetime.datetime.strptime(date_string, "%Y-%m-%d")

    # instead of using the exact shifttimes, we search a little around that, since some people might have starting /
    # ending times that are slightly different.
    timestart_search = datetime.datetime.combine(date, timestart) - datetime.timedelta(hours=1)
    timeend_search = datetime.datetime.combine(date, timeend) - datetime.timedelta(hours=3)

    # logging.warning(f"{timestart_search=}")
    # timestart_search = timestart
    # timeend_search = timeend
    # datenow = '2023-06-04'
    # format_string = '%Y-%m-%d %H:%M:%S.%f'
    # date_string = '2023-06-04 10:45:17.004845'
    # datetimenow = datetime.datetime.strptime(date_string, format_string)

    # get all the users that have change, but are already confirmed (so no need to include them in the shiftchange).
    confirmed_users = Planning.objects.filter(
        confirmed=True,
        removed=False,
        endtime__gt=timestart,
        starttime__lt=timestart,  # extra clause to exclude strange (test) cases where a user is confirmed in the future
    )
    confirmed_users_ids = list(confirmed_users.values_list('user_id', flat=True))  # list with confirmed user ids

    # NEW: get all plannings with people that start between times timestart_search and timeend_search, but exclude
    # people that are already confirmed. These might be people that are either already confirmed on their new post, or
    # people that are changing to another post.
    occupation_new = Planning.objects.filter(
        date=date,
        starttime__gt=timestart_search,
        starttime__lt=timeend_search,
        removed=False,
        confirmed=False,
    ).exclude(
        user=None,
    ).exclude(
        Q(user_id__in=confirmed_users_ids)
    ).annotate(
        shift_type=Value('new')
    )

    # CHANGE: get all planning of people that have a change, i.e. plannings that new, but people that are currently
    # already confirmed (on another post, if they stay on the post, the start-end time search doesn't include them).
    # with an annotation we get the current post they are on.
    occupation_change = Planning.objects.filter(
        date=date,
        starttime__gt=timestart_search,
        starttime__lt=timeend_search,
        removed=False,
        confirmed=False,
    ).annotate(
        post_id_old=Subquery(
            Planning.objects.filter(
                user_id=OuterRef('user_id'),
                confirmed=True
            ).values('post__post_fullname')[:1]
        )
    ).filter(
        Q(user_id__in=confirmed_users_ids)
    ).exclude(
        user=None,
    ).annotate(
        shift_type=Value('change')
    )
    occupation_change_userids = list(occupation_change.values_list('user_id', flat=True))  # get list with ids of these people

    # CANCEL: get all planning of people that are canceling, i.e. they have an endtime in the search range, but do not
    # change post (not in occupation_change_userids).
    # with an annotation we get when they have another shift later today, if any.
    occupation_cancel = Planning.objects.filter(
        date=date,
        removed=False,
        endtime__lt=timeend_search,
    ).exclude(
        Q(user_id__in=occupation_change_userids)  # exclude users that move to a different post
    ).annotate(
        shift_type=Value('cancel')
    ).annotate(
        later_today=Subquery(
            Planning.objects.filter(
                user_id=OuterRef('user_id'),
                confirmed=False,
                date=date,
                starttime__gt=timeend_search
            ).values('starttime')[:1],
        )
    )

    # CHANGE REV: get the same planning as change, but now the reverse. Same as cancel plannings, but now the ones that
    # are in occupation_change_userids.
    # with an annotation we get the new post.
    occupation_changerev = Planning.objects.filter(
        # confirmed=True,
        date=date,
        removed=False,
        endtime__lt=timeend_search,
    ).filter(
        Q(user_id__in=occupation_change_userids)  # only people that move to a different post
    ).annotate(
        shift_type=Value('changerev')
    ).annotate(
        post_id_new=Subquery(
            Planning.objects.filter(
                user_id=OuterRef('user_id'),
                confirmed=False,
                date=date,
                starttime__gt=timestart_search,
                starttime__lt=timeend_search,
                removed=False,
            ).values('post__post_fullname')[:1]
        )
    )

    # get all plannings that are currently confirmed
    confirmed_plans = Planning.objects.filter(
        confirmed=True,
        date=date,
        removed=False
    ).annotate(
        shift_type=Value('confirmed')
    )

    # get statistics about the shift change
    occupation_new_count = occupation_new.count()
    occupation_change_count = occupation_change.count()
    occupation_cancel_count = occupation_cancel.count()
    occupation_changerev_count = occupation_changerev.count()

    # merge all query results into a single one.
    occupation_total = itertools.chain(list(occupation_new), list(occupation_change), list(occupation_cancel), list(occupation_changerev))

    # group the query results by sector.
    occupation_total_grouped = {}
    for planning_obj in occupation_total:
        sector = planning_obj.post.sector
        post_id = planning_obj.post.post_fullname
        if sector not in occupation_total_grouped:
            occupation_total_grouped[sector] = {}
        if post_id not in occupation_total_grouped[sector]:
            occupation_total_grouped[sector][post_id] = []
        occupation_total_grouped[sector][post_id].append(planning_obj)

    # within each sector, group by post.
    for sector in occupation_total_grouped:
        # Sort the dictionary by post_id for each sector
        occupation_total_grouped[sector] = dict(sorted(occupation_total_grouped[sector].items(), key=lambda x: x[0]))

    # within each post group, sort by starttime.
    for sector, post_dict in occupation_total_grouped.items():
        for post_id, planning_list in post_dict.items():
            post_dict[post_id] = sorted(planning_list, key=lambda p: p.starttime)

    return render(request, 'planner/planner_shiftchange.html',
                  {
                      'occupation_total_grouped': occupation_total_grouped,
                      'occupation_new_count': occupation_new_count,
                      'occupation_change_count': occupation_change_count,
                      'occupation_cancel_count': occupation_cancel_count,
                      'occupation_changerev_count': occupation_changerev_count,
                      'dayname': dayname,
                      'timename': timename,
                      'timestart_search': timestart_search,
                      'timeend_search': timeend_search,
                      'timestart': timestart,
                      'timeend': timeend,
                      'date': date,
                      'confirmed_plans': confirmed_plans,
                  })

@staff_member_required
def add_planning(request, pk=None):
    if request.method == "POST":
        form = AddPlanningPlanner(request.POST)
        if form.is_valid():
            new_planning = form.save()
            new_planning.created_by = request.user
            new_planning.confirmed_by = request.user
            new_planning.save()
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "planningUpdated": None,
                        "showMessage": f"<b>Planning toegevoegd aan post <b>{new_planning.post}</b>."
                    })
                })
        return render(request, 'central/planningadd_form.html', {'form': form, 'planning': True, })
    else:
        # send extra context for slider
        shiftstart = list(ShiftTime.objects.all().values_list('timestart'))
        shiftstart = [i[0].strftime("%H:%M") for i in shiftstart]
        shiftend = list(ShiftTime.objects.all().values_list('timeend'))
        shiftend = [i[0].strftime("%H:%M") for i in shiftend]

        dayname = request.GET.get('dayname')
        day_preselected = ShiftDay.objects.filter(dayname=dayname)[0]
        preselected = (day_preselected.date, day_preselected.dayname)

        if pk:
            form = AddPlanningPlanner(initial={'post': str(pk), 'date': preselected, })
        else:
            form = AddPlanningPlanner(initial={'date': preselected, })
        return render(request, 'central/planningadd_form.html', {'form': form, 'shiftstart': shiftstart, 'shiftend': shiftend, 'planning': True, })


@staff_member_required
def add_occupation(request, pk=None):
    if request.method == "POST":
        form = AddOccupationPlanner(request.POST)
        if form.is_valid():
            new_planning = form.save()
            new_planning.created_by = request.user
            new_planning.confirmed_by = request.user
            new_planning.save()
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "planningUpdated": None,
                        "showMessage": f"<b>{new_planning.user} toegevoegd aan post <b>{new_planning.post}</b>."
                    })
                })
        return render(request, 'central/planningadd_form.html', {'form': form})
    else:
        # send extra context for slider
        shiftstart = list(ShiftTime.objects.all().values_list('timestart'))
        shiftstart = [i[0].strftime("%H:%M") for i in shiftstart]
        shiftend = list(ShiftTime.objects.all().values_list('timeend'))
        shiftend = [i[0].strftime("%H:%M") for i in shiftend]

        dayname = request.GET.get('dayname')
        day_preselected = ShiftDay.objects.filter(dayname=dayname)[0]
        preselected = (day_preselected.date, day_preselected.dayname)

        if pk:
            form = AddOccupationPlanner(initial={'post': str(pk), 'date': preselected, })
        else:
            form = AddOccupationPlanner(initial={'date': preselected, })
        return render(request, 'central/planningadd_form.html',
                      {'form': form, 'shiftstart': shiftstart, 'shiftend': shiftend})