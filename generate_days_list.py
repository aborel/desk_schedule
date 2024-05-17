from datetime import date, timedelta
import locale


"""
Print a series of working days suitable for use in the Excel input file
Useful mostly for extended periods of more than 1 week,
 i.e. Summer & Winter vacations
"""

# Set the locale to French:
# day names will be 0 = Lundi to 6 = Dimanche
locale.setlocale(locale.LC_ALL, 'fr_FR')


def get_start_to_end(start_date, end_date):
    date_list = []
    k = 0
    for i in range(0, (end_date - start_date).days + 1):
        current_day = start_date + timedelta(days=i)
        if current_day.weekday() not in [5, 6]: 
            date_list.append(f'{k}\t{current_day.strftime("%A %d-%m-%Y")}')
            k += 1
    return date_list


if __name__ == '__main__':
    # Modify these dates as needed
    start = date(2024, 7, 8)
    end = date(2024, 8, 30)
    dates = get_start_to_end(start, end)

    for d in dates:
        print(d)
