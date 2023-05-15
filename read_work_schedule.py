import sys
import numpy
import dateutil.parser
import openpyxl


def read_work_schedules(xlsx_filename):
    wb_obj = openpyxl.load_workbook(xlsx_filename)
    sheet = wb_obj.active
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
                    librarians[n] = name
                    new_roster = numpy.zeros(shape=(5, 10, 3), dtype=numpy.int8)
                    d = -1
                    # Extract extended work hours
                    for x in cells[2:7]:
                        # new day
                        d += 1
                        if x is None or not x[0].isdigit():
                            print(f'{x} is not a time')
                        else:
                            if not x[-1].isdigit():
                                x += '00'
                            x = x.lower().replace('/','-')
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
                                    k = int_boundaries[slot]
                                    while k <= int_boundaries[slot+1]:
                                        # artificial cut-off at 18h00, 18-20h to be handled later
                                        if k < 10:
                                            new_roster[d][k][0] = 1
                                            new_roster[d][k][1] = 1
                                            new_roster[d][k][2] = 1
                                        k += 1
            
                    # print(new_roster)
                    availability.append(new_roster)
        else:
            break
    print()
    return availability, librarians


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Syntaxe: {sys.argv[0]} <XLSX filename>')
        print('Le fichier XLSX doit contenir les horaires étendus des collaborateurs')
        exit(1)
    else:
        availabilities, librarians = read_work_schedules(sys.argv[1])
        outfile = open('work_schedule.py', 'w')
        outfile.write('from numpy import array, int8\n\n')
        outfile.write(f'librarians = {str(librarians)}\n')
        outfile.write(f'shift_requests = {str(availabilities)}\n')


