import datetime
import math
import numpy as np
from django.urls import reverse
from central.models import Planning

def matchoverlap(planning_start, planning_end, occ_start, occ_end, reference=False):  # input unix time stamps
    if reference:  # with a reference, unix converted to time since reference.
        return range(max(planning_start, occ_start) - reference, min(planning_end, occ_end) - reference)
    else:
        return range(max(planning_start, occ_start), min(planning_end, occ_end))


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
    minimumLeft = 0  # minimum time left of planning and occ to be kept afterwards in seconds
    planning = []

    # create a reference id (id2) to have a valid lookup later of the original planning entry
    id2 = 1
    # outside loop, to  make sure every occ and plan gets an idea, even if there is no overlap
    for o in occ:
        o['id2'] = id2
        id2 += 1
    for p in plan:
        p['id2'] = id2
        id2 += 1

    import logging
    logging.warning(f">>>>>> MakePlanning STARTED")



    while True:
        logging.warning("----------------- loop -----------------")
        counter = 0
        logging.warning(f"occ: {occ}")
        logging.warning(f"plan: {plan}")
        for o in occ:
            logging.warning(f"o: {o}")
            overlap = []
            for p in plan:
                logging.warning(f"p: {p}")
                # find best overlap
                ov = matchoverlap(o['start'], o['end'], p['start'], p['end'])
                logging.warning(f"overlap ov: {ov} ({o['id']}-{p['id']})")
                if len(ov) > 0:
                    overlap.append(ov)
            if not overlap:
                break
            counter += 1
            overlap_lengths = [len(x) for x in overlap]
            logging.warning(f"overlap lengths: {overlap_lengths}")
            best_plan = plan[overlap_lengths.index(max(overlap_lengths))]
            logging.warning(f"best plan: {best_plan['id']}")
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
            id2 += 1  # overlap found, thus chance of splitting up the planning (although it only happens with AD and BC). To be sure we just add +1 to id2
            # START
            if o['start'] < best_plan['start']:  # A: occ remainder at start
                logging.warning(f"A  - o:{o['id']}, p:{best_plan['id']}")
                occ.append({'id': o['id'], 'id2': id2, 'start': o['start'], 'end': best_plan['start']})
            elif best_plan['start'] < o['start']:  # B: plan remainder at start
                logging.warning(f"B  - o:{o['id']}, p:{best_plan['id']}")
                plan.append({'id': best_plan['id'], 'id2': id2, 'start': best_plan['start'], 'end': o['start']})

            id2 += 1  # here we work with the overlap part, if present, which we want to have a different id2 for lookup later
            # END
            if best_plan['end'] > o['end']:  # C: plan remainder at end
                logging.warning(f"C  - o:{o['id']}, p:{best_plan['id']}")
                plan.append({'id': best_plan['id'], 'id2': id2, 'start': o['end'], 'end': best_plan['end']})

            elif o['end'] > best_plan['end']:  # D: occ remainder at end
                logging.warning(f"D  - o:{o['id']}, p:{best_plan['id']}")
                occ.append({'id': best_plan['id'], 'id2': id2, 'start': best_plan['end'], 'end': o['end']})

            # # update plan and occ
            # if o['start'] - best_plan['start'] > minimumLeft:  # planning has remainder at start
            #     plan.append({'id': best_plan['id'], 'id2': id2, 'start': best_plan['start'], 'end': o['start']})
            #
            # elif best_plan['start'] - o['start'] > minimumLeft:  # occ has remainder at start
            #     occ.append({'id': o['id'], 'id2': id2, 'start': o['start'], 'end': best_plan['start']})
            #
            # if best_plan['end'] - o['end'] > minimumLeft:  # planning has remainder at end
            #     occ.append({'id': best_plan['id'], 'id2': id2, 'start': best_plan['end'], 'end': o['end']})
            #
            # elif o['end'] - best_plan['end'] > minimumLeft:  # occ has remainder at end, else is perfect overlap
            #     plan.append({'id': o['id'], 'id2': id2, 'start': o['end'], 'end': best_plan['end']})



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

            plan.remove(best_plan)  # remove from planning, since added new ones
            occ.remove(o)  # remove from occ, since added new ones

        if counter == 0:
            logging.warning(f"I am done here.")
            logging.warning(f"planning: {planning}")
            logging.warning("----------------- END LOOP -----------------")
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
        import logging
        logging.warning(f"BestMergeRowArray --> fits: {fits}")
        bestfit = np.argmax(fits)
        logging.warning(f"BestMergeRowArray --> bestfit: {bestfit}")
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
    import logging
    logging.warning(f"BestMergeArrays")
    # array2_2 = []
    while True:
        counter = 0
        for row1 in array1:  # PLANNING
            logging.warning(f"BestMergeArrays --> row1: {row1}")
            fits = []
            for row2 in array2:  # OCCUPATION
                logging.warning(f"BestMergeArrays --> row2: {row2}")
                logging.warning(f"sum(CountNotZero2D([row2, row1])) --> {sum(CountNotZero2D([row2, row1]))}")
                logging.warning(f"CountNotZero1D(Sum(row2, row1))[0] --> {CountNotZero1D(Sum(row2, row1))[0]}")
                if sum(CountNotZero2D([row2, row1])) == CountNotZero1D(Sum(row2, row1))[0]:
                    fits.append(CountNotZero1D(Sum(row2, row1))[0])
                else:
                    fits.append(0)

            if fits:
                logging.warning(f"BestMergeArrays --> fits: {fits}")
                bestfit = np.argmax(fits)
                logging.warning(f"BestMergeArrays --> fits[bestfit]: {fits[bestfit]}")
                if fits[bestfit] > 0:
                    array2[bestfit] = Sum(row1, array2[bestfit])
                    # array2_2.append(Sum(row1, array2[bestfit]))
                    array1.remove(row1)
                    counter += 1
                else:
                    array2.append(row1)

                logging.warning(f"end row2 iteration --> array1: {array1}")
                logging.warning(f"end row2 iteration --> array2: {array2}")
                    # array2_2.append(row1)
            # else:
            # if not array2:
            #     array1.remove(row1)
            #     array2.append(row1)

                # array2.append(row1)

        if counter == 0:
            break

    return array1, array2

def PlanningToArray(occ, plannew, time_start, time_end, resolution=900):
    last_cell = math.ceil(time_end / resolution)
    first_cell = math.ceil(time_start / resolution)
    ArrayWidth = last_cell - first_cell
    import logging

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

    import logging


    plannewTable = []
    logging.warning(f"plannew: {plannew}")
    for idx, p in enumerate(plannew):

        logging.warning(f"XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        logging.warning(f"idx: {idx}")
        loc_start = round(p['start'] / resolution) - first_cell
        if loc_start < 0:
            loc_start = 0
        loc_end = round(p['end'] / resolution) - first_cell
        if loc_end < 0:
            continue
        length = loc_end - loc_start
        row = [0] * ArrayWidth
        row[loc_start:loc_end] = [p['id2']] * length
        logging.warning(f"row: {row}")
        plannewTable.append(row)
    plannewTableOG = plannewTable[:]


    finalTable = occTable[:]


    logging.warning(f"plannewTable: {plannewTable}")
    logging.warning(f"finalTable: {finalTable}")

    # try to fit in now planning: find best fit, i.e. when the total number of gaps in the row is minimal
    # _, finalTable = BestMergeArrays(plannewTable[:], finalTable[:])

    finalTable = finalTable + plannewTable

    logging.warning(f"00000000>>>>>>>>>>>>>>>>> finalTable:")
    for temp in finalTable:
        logging.warning(f"{temp}")

    for row in finalTable:
        fits = []
        for row1 in finalTable:
            if sum(CountNotZero2D([row1, row])) == CountNotZero1D(Sum(row1, row))[0]:
                fits.append(CountNotZero1D(Sum(row1, row))[0])
            else:
                fits.append(0)
            logging.warning(f'fitssss: {fits}')
        if fits:
            logging.warning('fits found')
            bestfit = np.argmax(fits)
            if fits[bestfit] > 0:
                finalTable[bestfit] = Sum(row, finalTable[bestfit])
                finalTable.remove(row)

        else:
            finalTable.append(row)




    # finalTable2 = []
    # finalTable_Copy = finalTable[:]
    # for row in finalTable:
    #     finalTable2 = BestMergeRowArray(finalTable_Copy, row)

        # fits = []
        # for row1 in array1:
        #     if sum(CountNotZero2D([row1, row])) == CountNotZero1D(Sum(row1, row))[0]:
        #         fits.append(CountNotZero1D(Sum(row1, row))[0])
        #     else:
        #         fits.append(0)
        # if fits:
        #     import logging
        #     logging.warning(f"BestMergeRowArray --> fits: {fits}")
        #     bestfit = np.argmax(fits)
        #     logging.warning(f"BestMergeRowArray --> bestfit: {bestfit}")
        #     if fits[bestfit] > 0:
        #         array1[bestfit] = Sum(row, array1[bestfit])
        #     else:
        #         array1.append(row)
        # else:
        #     array1.append(row)
        #
        # return array1




    # logging.warning(f"OUTPUT:")
    # logging.warning(f"plannewTable: {plannewTable}")
    # logging.warning(f"finalTable: {finalTable}")

    return occTable, plannewTableOG, finalTable

def TableHeaderFooter(headerfoot, time_start=0, time_end=86400, resolution=900, colspan=1):
    last_cell = math.ceil(time_end / resolution)
    first_cell = math.ceil(time_start / resolution)
    ArrayWidth = last_cell - first_cell

    html = f"<{headerfoot} style='background-color:#f2f2f2;'><th></th>"
    header = ""
    for idx, i in enumerate(range(ArrayWidth)):  # get number of columns
        if i % colspan == 0:
            time = datetime.datetime.fromtimestamp(resolution * idx + time_start - 3600).strftime("%H:%M")
            # header += f"<th>{idx} <br> {time} <br>{int(resolution * idx + time_start)}</th>"
            header += f"<th colspan='{colspan}' style='border-left:1px solid #8c8c8c;'>{time}</th>"

    html += header
    html += f"</{headerfoot}>"

    return html

def ArrayToTable(planning, postname, postpk, LUT, dayname, rowcolor):
    html = ""
    import logging
    logging.warning(f">>>>>>>>>>>>>>>>> POST: {postname}")
    logging.warning(f">>>>>>>>>>>>>>>>> planning:")
    for temp in planning:
        logging.warning(f"{temp}")
    for idx, row in enumerate(planning):
        html += f"<tr style='background-color:{rowcolor};'>"  #

        if idx == 0:
            # url = f"{reverse('occupation-add', args=str(postpk))}?dayname={dayname}"

            html += f"<td rowspan='{len(planning)}' class='rowheader'><b>Post {postname}</td>"
            # html += f"<td rowspan='{len(planning)}' class='rowheader'><b>Post {postname} <a class='btn btn-info badge text-dark' hx-get='{url}' hx-target='#dialoghtmx' style='cursor:pointer; background-color: #337ab7; border-color: #337ab7;'><i class='fas fa-plus'></i></a></td>"
        else:
            html += "<td style='display:none;'></td>"  # fill with invisible cells (rowspan not supported by DataTables)



        # determine lengths of planning items, so right colspan can be used.
        ind = np.where(np.diff(row) != 0)[0]+1  # determine indices of change, add 1 to shift 1 (diff gives position of last value)
        ind = np.insert(ind, 0, 0)  # add first index
        spans = np.diff(ind)  # get the length of each of the changes (difference between each index)
        spans = np.append(spans, len(row)-sum(spans))  # add the length of the last value

        logging.warning(f"ind: {ind}")
        logging.warning(f"spans: {spans}")
        for idx in range(len(ind)):
            if row[ind[idx]] == 0:
                html += "<td></td>" * spans[idx]
            else:
                info = next(item for item in LUT if item["id2"] == row[ind[idx]])  # get corresponding data (id, starttime, endtime) of this item. Especially if plan is cut in half, start and end time are very useful!

                details = Planning.objects.get(pk=info['id'])

                start = info['start']
                end = info['end']

                url = reverse('planner-modify', args=(details.pk, start, end))
                comment = f"({details.comment})" if details.comment else ""

                logging.warning(f">>>>>>>>>>>>>>>>> I was here")

                porto = " <i class='fas fa-phone-volume'></i>" if details.porto else ""
                bike = f" <i class='fas fa-bicycle'></i><span style='font-size:0.7em;'> {details.bike}</span>" if details.bike else ""

                logging.warning(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {details.starttime <= datetime.datetime.now().time() and details.date == datetime.datetime.now().date()}")

                if not details.external and not details.user:  # than planning
                    html += f"<td colspan='{spans[idx]}' class='cutoverflow text-muted' style='background-color: #da9b4e; cursor:pointer;' hx-get='{url}' hx-target='#dialoghtmx'><i>Vacant{bike}{porto} {comment}</i></td>"
                elif details.external:  # planning for external
                    html += f"<td colspan='{spans[idx]}' class='cutoverflow text-muted' style='background-color: #c1c1c1; cursor:pointer;' hx-get='{url}' hx-target='#dialoghtmx'><i>Extern{bike}{porto} {comment}</i></td>"
                elif details.confirmed and not details.signed_off:
                    html += f"<td colspan='{spans[idx]}' class='cutoverflow' style='background-color: #5cb85c; cursor:pointer;' hx-get='{url}' hx-target='#dialoghtmx'>{details.user.first_name} {details.user.last_name}{bike}{porto} {comment}</td>"  #{details.pk} | {start} - {end}
                elif details.signed_off:
                    html += f"<td colspan='{spans[idx]}' class='cutoverflow' style='background-color: #587793; cursor:pointer;' hx-get='{url}' hx-target='#dialoghtmx'>{details.user.first_name} {details.user.last_name}{bike}{porto} {comment}</td>"  #{details.pk} | {start} - {end}
                elif details.starttime <= datetime.datetime.now().time() and details.date == datetime.datetime.now().date():  # needs confirmation
                    html += f"<td colspan='{spans[idx]}' class='cutoverflow' style='background-color: #74a9d8; cursor:pointer;' hx-get='{url}' hx-target='#dialoghtmx'>{details.user.first_name} {details.user.last_name}{bike}{porto} {comment}</td>"  #{details.pk} | {start} - {end}
                else:
                    html += f"<td colspan='{spans[idx]}' class='cutoverflow' style='background-color: #337ab7; cursor:pointer;' hx-get='{url}' hx-target='#dialoghtmx'>{details.user.first_name} {details.user.last_name}{bike}{porto} {comment}</td>"
                for i in range(spans[idx]-1):  # fill with invisible cells (colspan not supported by DataTables)
                    html += "<td style='display:none;'></td>"

        html += "</tr>"
    return html
