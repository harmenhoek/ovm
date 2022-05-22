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

    alldays = ShiftDay.objects.filter(active=True)
    return render(request, 'planner/planner_list.html', {'currentday': dayname, 'alldays': alldays, 'daydate': daydate, })

@staff_member_required
def plannertable(request, dayname):
    resolution = 15 * 60
    time_start = 7 * 60 * 60
    time_end = 24 * 60 * 60
    headercolspan = 4

    daydate = ShiftDay.objects.get(dayname__iexact=dayname).date

    reference = toSeconds(daydate, datetime.time(0, 0))

    posts = Post.objects.values('pk', 'post_fullname').filter(active=True).order_by('post_fullname')
    html = TableHeaderFooter('thead', time_start=time_start, time_end=time_end, resolution=resolution, colspan=headercolspan)
    html += "<tbody>"

    temp = []

    for post in posts:
        # get data
        planning = Planning.objects.filter(removed=False, user=None, date=daydate, post__pk=post['pk']).values()
        occupation = Planning.objects.filter(removed=False, date=daydate, post__pk=post['pk']).exclude(user=None).values()
        plan = []
        # restructure
        for p in planning:
            plan.append({'id': p['id'], 'start': toSeconds(p['date'], p['starttime'], reference=reference), 'end': toSeconds(p['date'], p['endtime'], reference=reference)})

        occ = []
        for o in occupation:
            occ.append({'id': o['id'], 'start': toSeconds(o['date'], o['starttime'], reference=reference), 'end': toSeconds(o['date'], o['endtime'], reference=reference)})

        temp.append(plan)
        planning, plannew, occnew = MakePlanning(occ[:], plan[:])  # pass copies  DO NOT DO ANYTHING WITH occnew, it is the non overlap only!
        LUT = plannew + occ
        occTable, plannewTable, finalTable = PlanningToArray(occ, plannew, time_start, time_end, resolution)


        html += ArrayToTable(finalTable, post['post_fullname'], post['pk'], LUT)

    html += TableHeaderFooter('tfoot', time_start=time_start, time_end=time_end, resolution=resolution, colspan=headercolspan)
    html += "</tbody>"

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
        start = datetime.datetime.combine(date.today(), datetime.time(0, 0)) + datetime.timedelta(seconds=start)
        end = datetime.datetime.combine(date.today(), datetime.time(0, 0)) + datetime.timedelta(seconds=end)

        form = ModifyPlanningPlanner(instance=plan_item, initial={'startime': start, 'endtime': end})

    return render(request, 'central/planningmodify_form.html', {
        'form': form, 'plan_pk': plan_item.pk,
    })


@staff_member_required
def add_planning(request, pk=None):
    if request.method == "POST":
        form = AddPlanningPlanner(request.POST)
        if form.is_valid():
            new_planning = form.save()
            new_planning.confirmed = True
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
        if pk:
            form = AddPlanningPlanner(initial={'post': str(pk)})
        else:
            form = AddPlanningPlanner()
        return render(request, 'central/planningadd_form.html', {'form': form, 'shiftstart': shiftstart, 'shiftend': shiftend, 'planning': True, })


@staff_member_required
def add_occupation(request, pk=None):
    if request.method == "POST":
        form = AddOccupationPlanner(request.POST)
        if form.is_valid():
            new_planning = form.save()
            new_planning.confirmed = True
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
        if pk:
            form = AddOccupationPlanner(initial={'post': str(pk)})
        else:
            form = AddOccupationPlanner()
        return render(request, 'central/planningadd_form.html',
                      {'form': form, 'shiftstart': shiftstart, 'shiftend': shiftend})