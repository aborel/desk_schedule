import sys
import numpy
import dateutil.parser
import openpyxl


def read_work_schedules(xlsx_filename):
    wb_obj = openpyxl.load_workbook(xlsx_filename)
    sheet = wb_obj.active
    n = 0
    s = 0
    d = 0
    lo = 0
    availability = []
    librarians = {}
    empty_roster = numpy.zeros(shape=(5, 10, 3), dtype=numpy.int8)
    for row in sheet.iter_rows():
        if len(row) > 0:
            if row[0] is not None:
                cells = [cell.value for cell in row]
                if cells[0] is not None:
                    availability.append(empty_roster)
                    name = ' '.join((cells[1], cells[0]))
                    print(name)
                    librarians[n] = name
                    # Extract extended work hours
                    for x in cells[2:7]:
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
                                # rules:
                                # - start time: if minutes are non-zero, round up
                                # - end time: if minutes are non-zero, round down
                                k = 0
                                for b in boundaries:
                                    split_b = b.strip().split('h')
                                    hour = int(split_b[0])
                                    if split_b[1] > '00':
                                        if k % 2 == 1:
                                            hour += 1
                                        else:
                                            pass
                                    else:
                                        pass
                                    print([b, hour])

                    
        else:
            break
    print()



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Syntaxe: {sys.argv[0]} <XLSX filename>')
        print('Le fichier XLSX doit contenir les horaires étendus des collaborateurs')
        exit(1)
    else:
        read_work_schedules(sys.argv[1])