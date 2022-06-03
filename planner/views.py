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

@staff_member_required
def planner(request, dayname=None):
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
    return render(request, 'planner/planner_list.html', {'currentday': dayname, 'alldays': alldays, 'daydate': daydate, })

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
    # cnt = 0

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