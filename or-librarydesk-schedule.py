# From https://developers.google.com/optimization/scheduling/employee_scheduling

from ortools.sat.python import cp_model
import numpy
from numpy import array
import itertools

max_shfts_per_day = 2

# based on K_Guichets//K2_Guichets_physiques/K2.03_Tournus/quotas_par_guichetier_20190131.JPG
# TODO: ask for the rule for bl+coordinator
# Sample quota object; actual values extracted from the Excel spreadsheet
"""
quota = {
    '40': (3, 2),
    '50': (3, 2),
    '60': (4, 3),
    '70': (4, 3),
    '80': (5, 3),
    '90': (5, 4),
    '100': (5, 4),
    'dir': (2, 0),
    'bl40': (2, 2),
    'bl50': (2, 2),
    'bl60': (3, 2),
    'bl70': (3, 2),
    'bl80': (3, 2),
    'bl90': (3, 2),
    'bl100': (3, 2),
    'coord40': (3, 2),
    'coord50': (3, 2),
    'coord60': (3, 3),
    'coord70': (3, 3),
    'coord80': (3, 3),
    'coord90': (3, 4),
    'coord100': (3, 4),
}
"""

sector_semester_quotas = {
    'search': 6,
    'cado': 6,
    'spi': 1
}

sector_holiday_quotas = {
    'search': 3,
    'cado': 3,
    'spi': 1
}

weekdays = {0: 'Monday',
    1: 'Tuesday',
    2: 'Wednsday',
    3: 'Thursday',
    4: 'Friday'
    }

def main():
    # This program tries to find an optimal assignment of librarians to shifts
    # (10 shifts per day, for 5 days), subject to some constraints (see below).
    # Each librarian can request to be assigned to specific shifts.
    # The optimal assignment maximizes the number of fulfilled shift requests.
    num_shifts = 11
    num_days = 5

    from work_schedule import librarians, shift_requests, meeting_slots, quota, locations


    # What is the longest desk stay that someone requested?
    max_req_run_length = max([librarian['prefered_length'] for librarian in librarians])
    # Limit this to the max number of shifts per day
    max_run_length = min([max_req_run_length, max_shfts_per_day])

    num_locations = len(locations.keys())
    num_librarians = len(librarians.keys())

    all_librarians = range(num_librarians)
    all_shifts = range(num_shifts)
    all_days = range(num_days)
    all_locations = range(num_locations)


    max_shift = num_shifts-1
    masks = numpy.zeros(shape=(max_run_length, max_shift, max_shift), dtype=numpy.int8)
    for rl in range(max_run_length):
        for offset in range(max_shift-rl):
            for k in range(rl+1):
                masks[rl][offset][offset+k] = 1


    # Creates the model.
    model = cp_model.CpModel()
    # Let's see how many conditions we define
    n_conditions = 0

    # Creates shift variables.
    # shifts[(n, d, s, lo)]: 
    # librarian 'n' works shift 's' on day 'd' at location lo.
    shifts = {}
    for n in all_librarians:
        for d in all_days:
            for s in all_shifts:
                for lo in all_locations:
                    shifts[(n, d, s, lo)] = \
                        model.NewBoolVar('shift_n%id%is%ilo%i' % (n, d, s, lo))

    # Each shift at each location is assigned to exactly 1 librarian
    for d in all_days:
        for s in all_shifts:
            for lo in all_locations:
                if s < locations[lo]['start'] or s > locations[lo]['end']:
                    model.Add(sum(shifts[(n, d, s, lo)] for n in all_librarians) == 0)
                    n_conditions += 1
                elif s == all_shifts[-1] and (lo > 0 or d == all_days[-1]):
                    model.Add(sum(shifts[(n, d, s, lo)] for n in all_librarians) == 0)
                    n_conditions += 1
                else:
                    model.Add(sum(shifts[(n, d, s, lo)] for n in all_librarians) == 1)
                    n_conditions += 1 
    # WIP : each librarian is using at most 1 seat at a time!
    for d in all_days:
        for s in all_shifts:
            for n in all_librarians:
                model.Add(sum(shifts[(n, d, s, lo)] for lo in all_locations) <= 1)
                n_conditions += 1 

    # Each librarian works at most max_shifts_per_day=2 shift per day.
    # TODO: make that 2 SUCCESSIVE shifts if requested
    # TODO: mix Accueil and STM shifts over the week
    for n in all_librarians:
        for d in all_days:
            model.Add(sum(shifts[(n, d, s, lo)]
                for s in all_shifts for lo in all_locations) <= max_shfts_per_day)
            n_conditions += 1
            successive_shifts = 0
            # Successive shifts preference applicable until 17h only
            for s in all_shifts[0:-2]:
                #print(sum([shift_requests[n][d][s][lo] for lo in all_locations]))
                reduced_shifts = [sum([shifts[(n, d, s, lo)]*shift_requests[n][d][s][lo]]) for lo in all_locations]

            run_length = 0
            for shift in range(len(reduced_shifts)):
                if reduced_shifts[shift] == 1:
                    pass
            """
                #model.Add(shift_group[0] == 1 and shift_group[1] == librarians[n]['prefered_length'])
            
                n_conditions += 1
            """

        # only assign max. one 18-20 shift for a given librarian
        s = all_shifts[-1]
        model.Add(sum(shifts[(n, d, s, lo)]
            for d in all_days for lo in all_locations) <= 1)
        n_conditions += 1

    # Try to distribute the shifts evenly, so that each librarian works
    # min_shifts_per_librarian shifts. If this is not possible, because the total
    # number of shifts is not divisible by the number of librarians, some librarians will
    # be assigned one more shift.
    
    # min_shifts_per_librarian = (num_shifts * num_days * num_locations) // num_librarians
    # min_shifts_per_librarian = 1

    for n in all_librarians:
        num_shifts_worked = 0
        num_shifts_reserve = 0
        out_of_time_shifts = 0
        for d in all_days:
            run_length = 0
            for s in all_shifts:
                for lo in all_locations:
                    if locations[lo]['name'].lower().find('remplacement') < 0:
                        num_shifts_worked += shifts[(n, d, s, lo)]
                        if s == all_shifts[-1]:
                            # Last shift must be counted twice, as it lasts 2 hours
                            num_shifts_worked += shifts[(n, d, s, lo)]
                    else:
                        num_shifts_reserve += shifts[(n, d, s, lo)]
                    out_of_time_shifts += shifts[(n, d, s, lo)] * (1-shift_requests[n][d][s][lo])
                    # Shifts during mandatory meetings also count as out of time
                    if d == meeting_slots[librarians[n]['sector']][0]:
                        if s >= meeting_slots[librarians[n]['sector']][1] and s <= meeting_slots[librarians[n]['sector']][2]:
                            out_of_time_shifts += shifts[(n, d, s, lo)] * 1
                    if d == meeting_slots['dir'] and librarians[n]['type'] == 'dir':
                        if s >= meeting_slots['dir'][1] and s <= meeting_slots['dir'][2]:
                            out_of_time_shifts += shifts[(n, d, s, lo)] * 1

        model.Add(out_of_time_shifts < 1)
        n_conditions += 1
        #model.Add(min_shifts_per_librarian <= num_shifts_worked)
        model.Add(num_shifts_worked >= quota[librarians[n]['type']][0] - 1)
        n_conditions += 1
        model.Add(num_shifts_reserve >= quota[librarians[n]['type']][1] - 1)
        n_conditions += 1
        model.Add(num_shifts_worked <= quota[librarians[n]['type']][0])
        n_conditions += 1
        model.Add(num_shifts_reserve <= quota[librarians[n]['type']][1])
        n_conditions += 1

    
    sector_score = len(all_days)*[{}]
    
    for d in all_days:
        for sector in sector_semester_quotas:
            sector_score[d][sector] = sum([shifts[(n, d, s, lo)] for n in all_librarians
                for s in all_shifts for lo in all_locations if librarians[n]['sector'] == sector])

            #model.Add(sector_score[d][sector] <= sector_semester_quotas[sector])
    
    

    # pylint: disable=g-complex-comprehension
    model.Maximize(
        sum(shift_requests[n][d][s][lo] * shifts[(n, d, s, lo)] for n in all_librarians
            for d in all_days for s in all_shifts for lo in all_locations))
    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    #status = solver.Solve(model)
    solution_printer = cp_model.ObjectiveSolutionPrinter()
    status = solver.SolveWithSolutionCallback(model, solution_printer)

    print()
    print('Quality of the solution: definition of constants')
    print('cp_model.FEASIBLE', cp_model.FEASIBLE)
    print('cp_model.INFEASIBLE', cp_model.INFEASIBLE)
    print('cp_model.OPTIMAL', cp_model.OPTIMAL)
    print('-\nSolved? ', status, solver.StatusName())
    
    print()
    for d in all_days:
        print('Day', d)
        for lo in all_locations:
            for s in all_shifts:
                for n in all_librarians:
                    #print(n, d, s, lo)
                    #print(shifts[(n, d, s, lo)])
                    if solver.Value(shifts[(n, d, s, lo)]) == 1:
                        if shift_requests[n][d][s][lo] == 1:
                            if not d == meeting_slots[librarians[n]['sector']][0] or s < meeting_slots[librarians[n]['sector']][1] or s > meeting_slots[librarians[n]['sector']][2]:
                                if s < all_shifts[-1]:
                                    print(f'{librarians[n]["name"]} works 1h at {s+8}:00 on {weekdays[d]} at {locations[lo]["name"]} (OK with work hours).')
                                else:
                                    print(f'{librarians[n]["name"]} works 2h at {s+8}:00 on {weekdays[d]} at {locations[lo]["name"]} (OK with work hours).')
                            else:
                                print(f'{librarians[n]["name"]} works 1h at {s+8}:00 on {weekdays[d]} at {locations[lo]["name"]} (problem with a group meeting).')                                
                        else:
                            # print(shift_requests[n][d])
                            print(f'{librarians[n]["name"]} works 1h at {s+8}:00 on {weekdays[d]} at {locations[lo]["name"]} (problem with work hours).')

        for sector in sector_semester_quotas:
            score = sum([solver.Value(shifts[(n, d, s, lo)]) for n in all_librarians
                        for s in all_shifts for lo in all_locations if librarians[n]['sector'] == sector])
            score += sum([solver.Value(shifts[(n, d, all_shifts[-1], lo)]) for n in all_librarians
                        for lo in all_locations if librarians[n]['sector'] == sector])
            
            unique_librarians = 0
            for n in all_librarians:
                worked_today = sum([solver.Value(shifts[(n, d, s, lo)]) for s in all_shifts
                    for lo in all_locations if librarians[n]['sector'] == sector])
                if worked_today > 0:
                    unique_librarians += 1
            print(f'Daily shifts for {sector.upper()}: {score} (using {unique_librarians} unique librarian(s), minimum {sector_semester_quotas[sector]}')
    print()

    for n in all_librarians:
        score = sum(solver.Value(shifts[(n, d, s, lo)])
            for d in all_days for s in all_shifts for lo in all_locations if lo < 3)
        score += sum(solver.Value(shifts[(n, d, all_shifts[-1], lo)])
            for d in all_days for lo in all_locations if lo < 3)
        score_reserve = sum(solver.Value(shifts[(n, d, s, lo)])
            for d in all_days for s in all_shifts for lo in all_locations if lo >= 3)
        s1 = f'{librarians[n]["name"]} is working {score}/{quota[librarians[n]["type"]][0]}'
        s2 = f' and acting as a reserve for {score_reserve}/{quota[librarians[n]["type"]][1]} shifts'
        print(s1 + s2)

    # Prepare HTML output

    main_title = "Proposed desk schedule"
    
    datatables_script = """<script type="text/javascript"
              src="https://code.jquery.com/jquery-3.3.1.min.js"
              crossorigin="anonymous"></script>\n"""
    datatables_script += '<script type="text/javascript" src="https://cdn.datatables.net/v/dt/dt-1.10.20/datatables.js"></script>'
    
    header = f"<head><title>{main_title}</title>\n{datatables_script}\n"

    header += """<style>

body {
    font-family: Arial, Helvetica, sans-serif;
}

#schedule {  
  border collapse: collapse;
  width: 100%;
}

#schedule td, #schedule th {
  border: 1px solid #ddd;
  padding: 8px;
}

#schedule tr:nth-child(even){background-color: #f2f2f2;}

#schedule tr:hover {background-color: #ddd;}

#schedule th {
  padding-top: 12px;
  padding-bottom: 12px;
  text-align: left;
  background-color: #04AA6D;
  color: white;
}
</style></head>"""

    title = f"<h1>{main_title}</h1>"

    score = f"Solution score = {solver.ObjectiveValue()} (max possible result {n_conditions})"
    stat_details = f'{solver.ResponseStats()}'

    table = '<div><table id="schedule" class="table">\n'
    table += '<thead>'
    table += "<tr>\n"
    table += '<th scope="col">Time</th>'
    for d in all_days:
        table += f'<th scope="col">{weekdays[d]}</th>'

    table += "\n</tr>\n</thead>\n<tbody>"

    for s in all_shifts:
        for lo in all_locations:
            table += "<tr>\n"
            table += f"<td>{s+8}:00-{s+9}:00 {locations[lo]['name']}</td>"
            for d in all_days:
                cell = "<td>N/A</td>"
                for n in all_librarians:
                    if solver.Value(shifts[(n, d, s, lo)]) == 1:
                        cell = f"<td>{librarians[n]['name']}</td>"
                table += cell


            table += "\n</tr>\n"


    table +=  "</tbody></table></div>"

    datatables_init = """
    <script>
    $(document).ready(function() {
        $('#schedule').DataTable({
    "paging": false
});
    });
  </script>
    """
    body = f"<body>\n{title}\n{datatables_init}\n<div>{score}</div><pre><code>"
    body += f"<h2>Technical statistics:</h2>\n{stat_details}</code></pre>"
    body += f"\n{table}</body>"

    html = f"<html>\n{header}\n{body}</html>"

    outfile = open('or-desk-schedule.html', 'w')
    outfile.write(html)
    outfile.close()

    # Statistics.

    print()
    print('**Statistics:**')
    print(f' - {score}')
    print()
    print(f"**Solver statistics:**\n{stat_details}")


if __name__ == '__main__':
    main()
