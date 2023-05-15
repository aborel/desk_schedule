#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import numpy
import dateutil.parser
import openpyxl

# TODO replace with values determined by the defined locations
#max_shift = 10
# max_location = 5
#max_day = 5

# TODO replace with values extracted from the Excel spreadsheet
# Sector and direction meetings:
# - day (0 = Monday)
# - start slot (0 = 8:00)
# - end slot (0 = 8:00)
"""
meeting_slots = {
    'dir': (3, 0, 5),
    'spi': (1, 5, 6),
    'cado': (1, 1, 2),
    'search': (1, 3, 4)
}
"""


def read_work_schedules(xlsx_filename):
    wb_obj = openpyxl.load_workbook(xlsx_filename)

    sheet = wb_obj['jours']
    weekdays = {}
    max_day = None
    for row in sheet.iter_rows():
        if len(row) > 0:
            if row[0] is not None:
                cells = [cell.value for cell in row]
                if cells[0] is not None:
                    try:
                        number = int(cells[0])
                    except ValueError:
                        pass
                    value = cells[1]
                    weekdays[number] = value
    max_day = number + 1
    print(weekdays)

    # Get locations from 2nd sheet
    sheet = wb_obj['guichets']
    locations = {}
    for row in sheet.iter_rows():
        if len(row) > 0:
            cells = [cell.value for cell in row]
            print(cells)
            if cells[0] is not None:
                name = cells[1]
                locations[cells[0]] = {'name': cells[1], 'times': {}}
                day = -1
                for x in cells[2:2+len(weekdays.keys())]:
                    day += 1
                    times = []
                    if x is None or not x[0].isdigit():
                        print(f'{x} is not a time')
                    else:
                        location_hours = x.split('-')
                        for l in location_hours:
                            hh = int(l.lower().split('h')[0])-8
                            mm = l.lower().split('h')[1]
                            if len(mm) > 0:
                                mm = int(mm)
                            else:
                                mm = 0
                            times.append(hh)
                    print('times: ', times)
                
                    locations[cells[0]]['times'][day] = {'start': times[0], 'end': times[1]}

    sheet = wb_obj['quotas']
    quota = {}
    for row in sheet.iter_rows():
        if len(row) > 0:
            cells = [cell.value for cell in row]
            print(cells)
            if cells[0] is not None:
                cells = [cell.value for cell in row]
                category = cells[0]
                worked = int(cells[1])
                reserve = int(cells[2])
                quota[category] = (worked, reserve)

    print(locations)
    max_location = len(locations.keys())    
    max_shift = max([locations[k]['times'][day]['end'] for d in weekdays.keys() for k in locations]) + 1
    max_shift -= min([locations[k]['times'][day]['start'] for d in weekdays.keys() for k in locations])
    print(max_location, max_shift)

    sheet = wb_obj['séances']
    meeting_slots = {}
    for row in sheet.iter_rows():
        if len(row) > 0:
            if row[0] is not None:
                cells = [cell.value for cell in row]
                if cells[0] is not None:
                    group = cells[0]
                    day = cells[1]     
                    times = []
                    ktimes = -1               
                    for x in cells[2:4]:
                        #print(cells[2:4], cells[2], cells[3], x)
                        ktimes += 1
                        if x is None or not x[0].isdigit():
                            print(f'{x} is not a time')
                        else:
                            hh = int(x.lower().split('h')[0])-8
                            mm = x.lower().split('h')[1]
                            if len(mm) > 0:
                                mm = int(mm)
                            else:
                                mm = 0
                            if ktimes == 1 and mm == 0 :
                                times.append(hh-1)
                            else:
                                times.append(hh)
                    print(times)
                    meeting_slots[group] = (day, times[0], times[1])

    sheet = wb_obj['guichetiers']
    n = -1
    availability = []
    librarians = {}
    for row in sheet.iter_rows():
        if len(row) > 0:
            if row[0] is not None:
                cells = [cell.value for cell in row]
                if cells[0] is not None:
                    name = ' '.join((cells[1], cells[0]))
                    print(name)
                    n += 1
                    librarians[n] = {'name': name}
                    librarians[n]['sector'] = cells[2]
                    librarians[n]['type'] = cells[3]
                    librarians[n]['prefered_length'] = cells[4+max_day]
                    # TODO replace fixed constants!
                    new_roster = numpy.zeros(shape=(max_day, max_shift+1, max_location), dtype=numpy.int8)
                    d = -1
                    # Extract extended work hours
                    for x in cells[4:4+max_day]:
                        # new day
                        d += 1
                        if x is None or not x[0].isdigit():
                            print(f'{x} is not a time')
                        else:
                            if not x[-1].isdigit():
                                x += '00'
                            x = x.lower().replace('/','-').replace("–", "-")
                            x = x.replace('.','h').replace(':','h').replace('hh','h').replace('h-','h00-')
                            boundaries = x.split('-')
                            if len(boundaries) < 2:
                                print(f'WTF {x}')
                            else:
                                print(boundaries)
                                int_boundaries = []
                                # rules:
                                # - start time: if minutes are non-zero, round up
                                # - end time: if minutes are non-zero, round down
                                # also: remove 1 from end time to get the beginning of the last slot
                                k = 0
                                for b in boundaries:
                                    split_b = b.strip().split('h')
                                    hour = int(split_b[0])
                                    if k % 2 == 0:
                                        if split_b[1] > '00':
                                            hour += 1
                                    else:
                                        hour -= 1

                                    #print([b, hour])
                                    int_boundaries.append(hour-8)
                                    k += 1
                                print(int_boundaries)
                                for slot in range(len(int_boundaries) // 2):
                                    k = int_boundaries[slot*2]
                                    while k <= int_boundaries[slot*2+1]:
                                        # 10 regular shifts (8-17h) and 1 2-hour shift at 18:00, only 1 location
                                        if k < max_shift:
                                            for lo in range(max_location):
                                                new_roster[d][k][lo] = 1
                                        if k == max_shift and not d == (max_day-1):
                                            new_roster[d][k][0] = 1

                                        k += 1
            
                    # print(new_roster)
                    availability.append(new_roster)
        else:
            break
    print()

    sheet = wb_obj['règles']
    rules = {}
    for row in sheet.iter_rows():
        if len(row) > 0:
            if row[0] is not None:
                cells = [cell.value for cell in row]
                if cells[0] is not None:
                    name = cells[0]
                    try:
                        value = int(cells[1])
                    except ValueError:
                        value = 0
                    rules[name] = (value > 0)


    
    return availability, librarians, locations, quota, meeting_slots, rules, weekdays


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Syntaxe: {sys.argv[0]} <XLSX filename>')
        print('Le fichier XLSX doit contenir les horaires étendus des collaborateurs')
        exit(1)
    else:
        availabilities, librarians, locations, quota, meeting_slots, rules, weekdays = read_work_schedules(sys.argv[1])
        outfile = open('work_schedule.py', 'w')
        outfile.write('from numpy import array, int8\n\n')
        outfile.write(f'librarians = {str(librarians)}\n')
        outfile.write(f'shift_requests = {str(availabilities)}\n')
        outfile.write(f'\nmeeting_slots = {str(meeting_slots)}\n')
        outfile.write(f'\nlocations = {str(locations)}\n')
        outfile.write(f'\nquota = {str(quota)}\n')
        outfile.write(f'\nrules = {str(rules)}\n')
        outfile.write(f'\nweekdays = {str(weekdays)}\n')
