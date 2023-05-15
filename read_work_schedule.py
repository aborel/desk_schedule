import sys
import dateutil.parser
import openpyxl


def read_work_schedules(xlsx_filename):
    wb_obj = openpyxl.load_workbook(xlsx_filename)
    sheet = wb_obj.active
    for row in sheet.iter_rows():
        if len(row) > 0:
            if row[0] is not None:
                cells = [cell.value for cell in row]
                if cells[0] is not None:
                    name = ' '.join((cells[1], cells[0]))
                    # Extract extended work hours
                    for x in cells[2:7]:
                        if x is None or not x[0].isdigit():
                            print(f'{x} is not a time')
                        else:
                            if not x[-1].isdigit():
                                x += '00'
                            x = x.replace('.','h').replace(':','h').replace('hh','h').replace('h-','h00-')
                            boundaries = x.split('-')
                            if len(boundaries) < 2:
                                print(f'WTF {x}')
                            else:
                                print(boundaries)
                    print(name)
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