import re

from bs4 import BeautifulSoup
import dateparser

# From https://absences.epfl.ch/cgi-bin/abs/lang=en/menu=plannings/listAbs?week=1
# or https://absences.epfl.ch/cgi-bin/abs/lang=en/instID=1459/menu=plannings/listAbs?date=20230227&week=1

HTMLFile = open("absences-test-en.html", "r")
index = HTMLFile.read()

S = BeautifulSoup(index, 'lxml')
try:
    absence_table = S.find_all('table')[0]
    for row in absence_table.find_all('tr'):
        for cell in row.find_all('td')[0:5]:
            try:
                s = cell.find_all('a')[0].decode_contents()
            except IndexError:
                s = cell.decode_contents()
            s = s.replace(' ', ' ')
            s = s.replace('early morning', '8:00 AM')
            s = s.replace('end of morning', '1:00 PM')
            s = s.replace('early afternoon', '1:00 PM')
            s = s.replace('end of afternoon', '8:00 PM')
            if len(re.findall('[0-9]{4} [0-9]{4}', s)) > 0:
                print(s)
                print('Found one!')
                s = s[0:-2] + ':' + s[-2:]
            print(s, '\t', dateparser.parse(s))
        print('\n')
except IndexError:
    print('no table found?')
