import re
import os
import pathlib

from bs4 import BeautifulSoup
import dateparser

# From https://absences.epfl.ch/cgi-bin/abs/lang=en/menu=plannings/listAbs?week=1
# or https://absences.epfl.ch/cgi-bin/abs/lang=en/instID=1459/menu=plannings/listAbs?date=20230227&week=1
# The week argument appears to have no effect

def parse_absence_html(ls):
    HTMLFile = open(os.path.join(str(ls.parents[0]), ls.name), "r")
    index = HTMLFile.read()

    S = BeautifulSoup(index, 'lxml')
    try:
        absence_table = S.find_all('table')[0]
        for row in absence_table.find_all('tr'):
            print('\n')
            cells = list(row.find_all('td'))[0:5]
            if len(cells) == 5:
                del cells[-2]
                if not cells[-1].decode_contents() == 'télétravail' and not cells[-1].decode_contents() == 'télétravail':
                    elements = []
                    for idx, cell in enumerate(cells):
                        try:
                            s = cell.find_all('a')[0].decode_contents()
                        except IndexError:
                            s = cell.decode_contents()
                        s = s.replace(' ', ' ').lower()
                        print('original:', s)
                        s = s.replace(' ', ' ')
                        s = s.replace('early afternoon', '1300')
                        s = s.replace('début après-midi', '1300')
                        s = s.replace('end of afternoon', '2000')
                        s = s.replace('fin après-midi', '2000')
                        s = s.replace('early morning', '0800')
                        s = s.replace('début matinée', '0800')
                        s = s.replace('end of morning', '1159')
                        s = s.replace('midi', '1159')
                        print('processed:', s)
                        if len(re.findall('[0-9]{4} [0-9]{4}', s)) > 0:
                            # print('Found one!')
                            s = s[0:-2] + ':' + s[-2:]
                            elements.append(dateparser.parse(s))
                        else:
                            elements.append(s)
                    print(elements)
        print('\n')
    except IndexError:
        print('no table found?')


if __name__ == "__main__":
    absence_folder = './absences'
    absence_files = pathlib.Path(absence_folder).glob('*.html')

    for htmlfile in absence_files:
        parse_absence_html(htmlfile)