import re
import sys

from bs4 import BeautifulSoup
import dateparser

# From https://absences.epfl.ch/cgi-bin/abs/lang=en/menu=plannings/listAbs?week=1
# or https://absences.epfl.ch/cgi-bin/abs/lang=en/instID=1459/menu=plannings/listAbs?date=20230227&week=1

def get_all_text(node):
    if node.nodeType == node.TEXT_NODE:
        return node.text
    else:
        text_string = ""
        for child_node in node.childNodes:
            text_string += get_all_text(child_node)
    return text_string


def list_divs(node, ntabs=0):
    all_subdivs = node.find_all('div')
    print(len(all_subdivs))
    subdivs = [div for div in all_subdivs if len(div.find_all('div')) > 0]
    for subdiv in subdivs:
        list_divs(subdiv, ntabs=ntabs+1)
    print('\t'*ntabs + f'{len(subdivs)} subdivs')


def parse_absences(htmlfile):
    HTMLFile = open(htmlfile, "r")
    index = HTMLFile.read()

    S = BeautifulSoup(index, 'lxml')
    try:
        tables = S.find_all('table')
        print(f'Found {len(tables)} tables in the page.')

        for idx, t in enumerate(tables):
            subtables = t.find_all('table')
            rows = t.find_all('tr')
            print(f'Table {idx} has {len(rows)} rows and contains {len(subtables)} sub-tables')
            print('Is FV in there?', t.decode_contents().find('Varrato'))
            print('Is Holidays in there?', t.decode_contents().find('Holidays'))
            for ridx, r in enumerate(rows):
                cols = r.find_all('td')
                if len(cols) == 1:
                    if  get_all_text(cols[0]) is None:
                        print(f'Weird column:')
                    else:
                        pass
                else:
                    print(f'\tRow {ridx} has {len(cols)} columns')

        print('---------')
        people_table = tables[3]
        print('Is FV really in there?', people_table.decode_contents().find('Varrato'))
        people_rows = people_table.find_all('tr')
        librarians = [get_all_text(row).strip() for row in people_rows]
        for row in people_rows:
            cols = row.find_all('td')
            #print()
            #print('---')

        fcDayThs = [th for th in S.find_all('th', class_='fc-day') if th.get('colspan') == '1']
        for th in fcDayThs:
            print([th.get('colspan')], get_all_text(th), th.get('data-date'))
        fcDayTds = S.find_all('td', class_='fc-day')
        print(f'Found {len(fcDayTds)} days')
        fcDayTds = S.find_all('td', class_='fc-day')

        absence_table = tables[5]

        #print(absence_table.decode_contents().find('Borel'))
        #print(absence_table.decode_contents().find('Varrato'))
        absence_rows = absence_table.find_all('tr')
        for ridx, row in enumerate(absence_rows):
            cells = row.find_all('td')
            print(len(cells))
            if (len(cells) > 0):
                print(cells[0].class_)
                #print(cells[0].decode_contents())
                all_divs = cells[0].find_all('div')
                inner_divs = [div for div in all_divs if len(div.find_all('div')) == 0]
                events = [div for div in all_divs if 'fc-timeline-event-harness' in div.get('class')]
                print(f'{len(events)} events')
                print(librarians[ridx], len(inner_divs), [(div.get('class'), get_all_text(div).strip(), div.get('style')) for div in events])

    except IndexError as e:
        print('no table found?', e)
    return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        htmlfile = sys.argv[1]
    else:
        htmlfile = "absences.html"

    output = parse_absences(htmlfile)
