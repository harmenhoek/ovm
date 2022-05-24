import datetime
import math
import numpy as np
from django.urls import reverse
from central.models import Planning

def matchoverlap(planning_start, planning_end, occ_start, occ_end, reference=False):  # input unix time stamps
    if reference:  # with a reference, unix converted to time since reference.
        return range(max(planning_start, occ_start) - reference, min(planning_end, occ_end) - reference + 1)
    else:
        return range(max(planning_start, occ_start), min(planning_end, occ_end) + 1)


def toSeconds(date, time, reference=False):
    # converts datetime date and time to seconds from Unix (reference=False) or from reference (in seconds from Unix)
    if reference:
        return int(datetime.datetime.combine(date, time).strftime('%s')) - reference
    else:
        return int(datetime.datetime.combine(date, time).strftime('%s'))


def visualizePlanning(plan, time_start, time_end, resolution=900):
    # planning, occ, overlap  inputs as dict with ranges: planning = {range(100, 200), range(150, 300), etc
    # resolution is displayed resolution in seconds

    last_cell = math.ceil(time_end / resolution)
    first_cell = math.ceil(time_start / resolution)

    """
    TODO: make sure loop is executed at least once (planning must always show up once!)
    """

    html = "<table>"
    for i in plan:
        loc_start = math.floor(i['start'] / resolution)
        loc_end = math.ceil(i['end'] / resolution)
        # html += f"<tr><td colspan='{loc_start-first_cell-1}'></td>"
        html += "<tr>"
        for j in range((loc_start - first_cell)):
            html += "<td></td>"

        for j in range(1, loc_end - loc_start):
            html += f"<td>{i['id']}</td>"

        # html += f"<td colspan='{last_cell - loc_end}'></td>"
        for j in range((last_cell - loc_end)):
            html += "<td></td>"

        html += "</tr>"
    html += "</table>"
    return html

def MakePlanning(occ, plan):  # make planning here
    minimumLeft = 100  # minimum time left of planning and occ to be kept afterwards in seconds
    planning = []

    # create a reference id (id2) to have a valid lookup later of the original planning entry
    id2 = 1
    for o in occ:  # outside loop, to  make sure every occ gets a id2?
        o['id2'] = id2
        id2 += 1
    for p in plan:  #both, no idea why it sometimes doesn't work
        p['id2'] = id2
        id2 += 1


    while True:
        counter = 0
        for o in occ:

            overlap = []
            for p in plan:
                p['id2'] = id2  # inside loop to make sure every split up gets a new id2.
                id2 += 1
                # find best overlap
                ov = matchoverlap(o['start'], o['end'], p['start'], p['end'])
                if len(ov) > 0:
                    overlap.append(ov)
            if not overlap:
                break
            counter += 1
            overlap_lengths = [len(x) for x in overlap]
            best_plan = plan[overlap_lengths.index(max(overlap_lengths))]
            # make planning, update plan, update occ

            '''
            p1 = best_plan['start']
            o1 = o['start']
            p2 = best_plan['end']
            o2 = o['end']
                            time -->
            option 1: _____p1_____o1_____ --> original planning has remainder at start
            option 2: _____o1_____p1_____ --> original occupation has remainder at start
            option 3: _____p2_____o2_____ --> original planning has remainder at end
            option 4: _____p1_____o1_____ --> original occupation has remainder at end

            '''

            # update plan and occ
            if o['start'] - best_plan['start'] > minimumLeft:  # planning has remainder at start
                plan.append({'id': best_plan['id'], 'id2': id2, 'start': best_plan['start'], 'end': o['start']})
            elif best_plan['start'] - o['start'] > minimumLeft:  # occ has remainder at start
                occ.append({'id': o['id'], 'id2': id2, 'start': o['start'], 'end': best_plan['start']})
            if best_plan['end'] - o['end'] > minimumLeft:  # planning has remainder at end
                plan.append({'id': best_plan['id'], 'id2': id2, 'start': o['end'], 'end': best_plan['end']})
            elif o['end'] - best_plan['end'] > minimumLeft:  # occ has remainder at end, else is perfect overlap
                occ.append({'id': o['id'], 'id2': id2, 'start': best_plan['end'], 'end': o['end']})
            plan.remove(best_plan)  # remove from planning, since added new ones
            occ.remove(o)  # remove from occ, since added new ones

            # create planning
            if best_plan['start'] > o['start']:  # occ has remainder
                planning_start = best_plan['start']
            else:  # occ fully filled from start (perfect or with remainder planning)
                planning_start = o['start']
            if best_plan['end'] < o['end']:  # occ has remainder
                planning_end = best_plan['end']
            else:  # occ fully filled to end (perfect or with remainder planning)
                planning_end = o['end']
            planning.append({'id': (best_plan['id'], o['id']), 'start': planning_start, 'end': planning_end})

        if counter == 0:
            break

    return planning, plan, occ

def CountNotZero1D(array1d):
    return [sum(x != 0 for x in array1d)]

def CountNotZero2D(array2d):
    return [sum(x != 0 for x in y) for y in array2d]

def Sum(array1, array2):
    return [x + y for x, y in zip(array1, array2)]


def BestMergeRowArray(array1, row):
    fits = []
    for row1 in array1:
        if sum(CountNotZero2D([row1, row])) == CountNotZero1D(Sum(row1, row))[0]:
            fits.append(CountNotZero1D(Sum(row1, row))[0])
        else:
            fits.append(0)
    if fits:
        bestfit = np.argmax(fits)
        if fits[bestfit] > 0:
            array1[bestfit] = Sum(row, array1[bestfit])
        else:
            array1.append(row)
    else:
        array1.append(row)

    return array1


def BestMergeArrays(array1, array2):
    # this function checks if 2 arrays can be merged, i.e. there is no overlap. It checks for the best fit (i.e. it
    # adds rows so that the longest has the least amount of zeros.
    while True:
        counter = 0
        for row1 in array1:
            fits = []
            for row2 in array2:
                if sum(CountNotZero2D([row2, row1])) == CountNotZero1D(Sum(row2, row1))[0]:
                    fits.append(CountNotZero1D(Sum(row2, row1))[0])
                else:
                    fits.append(0)
            if fits:
                bestfit = np.argmax(fits)
                if fits[bestfit] > 0:
                    array2[bestfit] = Sum(row1, array2[bestfit])
                    array1.remove(row1)
                    counter += 1
                else:
                    array2.append(row1)
            else:
                array2.append(row1)

        if counter == 0:
            break

    return array1, array2

def PlanningToArray(occ, plannew, time_start, time_end, resolution=900):
    last_cell = math.ceil(time_end / resolution)
    first_cell = math.ceil(time_start / resolution)
    ArrayWidth = last_cell - first_cell

    occTable = []
    # first create occ in list, then fit in plannew (leftovers from plan)
    for idx, o in enumerate(occ):
        loc_start = round(o['start'] / resolution) - first_cell
        if loc_start < 0:
            loc_start = 0
        loc_end = round(o['end'] / resolution) - first_cell
        if loc_end < 0:
            continue
        length = loc_end - loc_start
        row = [0] * ArrayWidth
        row[loc_start:loc_end] = [o['id2']] * length

        # find best fit for the row in existing table
        occTable = BestMergeRowArray(occTable, row)


    plannewTable = []
    for idx, p in enumerate(plannew):
        loc_start = round(p['start'] / resolution) - first_cell
        if loc_start < 0:
            loc_start = 0
        loc_end = round(p['end'] / resolution) - first_cell
        if loc_end < 0:
            continue
        length = loc_end - loc_start
        row = [0] * ArrayWidth
        row[loc_start:loc_end] = [p['id2']] * length
        plannewTable.append(row)
    plannewTableOG = plannewTable[:]




    finalTable = occTable[:]
    # try to fit in now planning: find best fit, i.e. when the total number of gaps in the row is minimal
    plannewTable, finalTable = BestMergeArrays(plannewTable, finalTable)

    return occTable, plannewTableOG, finalTable

def TableHeaderFooter(headerfoot, time_start=0, time_end=86400, resolution=900, colspan=1):
    last_cell = math.ceil(time_end / resolution)
    first_cell = math.ceil(time_start / resolution)
    ArrayWidth = last_cell - first_cell

    html = f"<{headerfoot} style='background-color:#f2f2f2;'><th></th>"
    header = ""
    for idx, i in enumerate(range(ArrayWidth)):  # get number of columns
        if i % colspan == 0:
            time = datetime.datetime.fromtimestamp(resolution * idx + time_start).strftime("%H:%M")
            # header += f"<th>{idx} <br> {time} <br>{int(resolution * idx + time_start)}</th>"
            header += f"<th colspan='{colspan}' style='border-left:1px solid #8c8c8c;'>{time}</th>"

    html += header
    html += f"</{headerfoot}>"

    return html

def ArrayToTable(planning, postname, postpk, LUT, dayname, rowcolor):
    html = ""
    for idx, row in enumerate(planning):
        html += f"<tr style='background-color:{rowcolor};'>"  #

        if idx == 0:
            url = f"{reverse('occupation-add', args=str(postpk))}?dayname={dayname}"

            html += f"<td rowspan='{len(planning)}' class='rowheader'><b>Post {postname} <a class='btn btn-info badge text-dark' hx-get='{url}' hx-target='#dialoghtmx' style='cursor:pointer; background-color: #337ab7; border-color: #337ab7;'><i class='fas fa-plus'></i></a></td>"
        else:
            html += "<td style='display:none;'></td>"  # fill with invisible cells (rowspan not supported by DataTables)



        # determine lengths of planning items, so right colspan can be used.
        ind = np.where(np.diff(row) != 0)[0]+1  # determine indices of change, add 1 to shift 1 (diff gives position of last value)
        ind = np.insert(ind, 0, 0)  # add first index
        spans = np.diff(ind)  # get the length of each of the changes (difference between each index)
        spans = np.append(spans, len(row)-sum(spans))  # add the length of the last value
        for idx in range(len(ind)):
            if row[ind[idx]] == 0:
                html += "<td></td>" * spans[idx]
            else:
                info = next(item for item in LUT if item["id2"] == row[ind[idx]])  # get corresponding data (id, starttime, endtime) of this item. Especially if plan is cut in half, start and end time are very useful!

                details = Planning.objects.get(pk=info['id'])

                start = info['start']
                end = info['end']

                url = reverse('planner-modify', args=(details.pk, start, end))

                if not details.user:  # than planning
                    html += f"<td colspan='{spans[idx]}' class='cutoverflow' style='background-color: #da9b4e; cursor:pointer;' hx-get='{url}' hx-target='#dialoghtmx'><i></i></td>"
                elif details.confirmed:
                    html += f"<td colspan='{spans[idx]}' class='cutoverflow' style='background-color: #5cb85c; cursor:pointer;' hx-get='{url}' hx-target='#dialoghtmx'>{details.user.first_name} {details.user.last_name}</td>"  #{details.pk} | {start} - {end}
                else:
                    html += f"<td colspan='{spans[idx]}' class='cutoverflow' style='background-color: #337ab7; cursor:pointer;' hx-get='{url}' hx-target='#dialoghtmx'>{details.user.first_name} {details.user.last_name}</td>"
                for i in range(spans[idx]-1):  # fill with invisible cells (colspan not supported by DataTables)
                    html += "<td style='display:none;'></td>"

        html += "</tr>"
    return html
