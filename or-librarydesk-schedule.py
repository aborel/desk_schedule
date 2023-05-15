# From https://developers.google.com/optimization/scheduling/employee_scheduling

from ortools.sat.python import cp_model
import numpy
from numpy import array
import itertools
import argparse

max_shifts_per_day = 2

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

weekdays = {0: 'lundi',
            1: 'mardi',
            2: 'mercredi',
            3: 'jeudi',
            4: 'vendredi'
            }


def main():
    # This program tries to find an optimal assignment of librarians to shifts
    # (10 shifts per day, for 5 days), subject to some constraints (see below).
    # Each librarian can request to be assigned to specific shifts.
    # The optimal assignment maximizes the number of fulfilled shift requests.

    script_description = 'Generate a desk schedule from a file or from the variables in a Python script'
    parser = argparse.ArgumentParser(description=script_description)
    parser.add_argument('--no-file', action='store_true', help='do not read from Excel sheet, use work_schedule.py')
    parser.add_argument('--file', help='read from Excel sheet')

    args = parser.parse_args()
    print(args)

    num_shifts = 11
    num_days = 5

    if args.no_file:
        from work_schedule import librarians, shift_requests, meeting_slots
        from work_schedule import quota, locations, rules
    elif args.file is not None:
        from read_work_schedule import read_work_schedules
        shift_requests, librarians, locations, quota, meeting_slots, rules = read_work_schedules(args.file)
    else:
        from read_work_schedule import read_work_schedules
        filename = 'Horaires-guichets.xlsx'
        shift_requests, librarians, locations, quota, meeting_slots, rules = read_work_schedules(filename)

    num_locations = len(locations.keys())
    num_librarians = len(librarians.keys())

    all_librarians = range(num_librarians)
    all_shifts = range(num_shifts)
    all_days = range(num_days)
    all_locations = range(num_locations)

    # Maximum normal shift, the last one is special
    max_shift = num_shifts-1
 
    # Creates the model.
    model = cp_model.CpModel()
    v0 = model.NewBoolVar("buggyVarIndexToVarProto")
    # model.VarIndexToVarProto(0) always returns the last created variable...?

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

    if rules['oneLibrariaPerShift']:
        oneLibrariaPerShift = model.NewBoolVar('oneLibrariaPerShift')
        # Each shift at each location is assigned to exactly 1 librarian
        for d in all_days:
            for s in all_shifts:
                for lo in all_locations:
                    if s < locations[lo]['start'] or s > locations[lo]['end']:
                        model.Add(sum([shifts[(n, d, s, lo)] for n in all_librarians]) == 0).OnlyEnforceIf(oneLibrariaPerShift)
                        n_conditions += 1
                    elif s == all_shifts[-1] and (d == all_days[-1]):
                        model.Add(sum([shifts[(n, d, s, lo)] for n in all_librarians]) == 0).OnlyEnforceIf(oneLibrariaPerShift)
                        n_conditions += 1
                    else:
                        model.Add(sum([shifts[(n, d, s, lo)] for n in all_librarians]) == 1).OnlyEnforceIf(oneLibrariaPerShift)
                        n_conditions += 1 
        model.Proto().assumptions.append(oneLibrariaPerShift.Index())

    if rules['oneShiftAtATime']:
        # WIP : each librarian is using at most 1 seat at a time!
        oneShiftAtATime = model.NewBoolVar('oneShiftAtATime')
        for d in all_days:
            for s in all_shifts:
                for n in all_librarians:
                    model.Add(sum([shifts[(n, d, s, lo)] for lo in all_locations]) <= 1).OnlyEnforceIf(oneShiftAtATime)
                    n_conditions += 1 
        model.Proto().assumptions.append(oneShiftAtATime.Index())

    if rules['preferedRunLength']:
        # Each librarian works at most max_shifts_per_day=2 shift per day.
        # TODO: make that 2 SUCCESSIVE shifts if requested
        # TODO: mix Accueil and STM shifts over the week?
        preferedRunLength = model.NewBoolVar('preferedRunLength')
        for n in all_librarians:
            delta_vars = []
            for d in all_days:
                delta_vars.append([])
                model.Add(sum([shifts[(n, d, s, lo)]
                    for s in all_shifts for lo in all_locations]) +
                sum([shifts[(n, d, s, lo)]
                    for s in all_shifts[-1:] for lo in all_locations]) <= max_shifts_per_day)
                n_conditions += 1

                run_length = librarians[n]['prefered_length']
                
                # Successive shifts preference?
                # The number of changes from "busy" to "free" or back describes
                # the number of discontinuous shifts
                # somthing like sum(abs(shifts[(n, d, s+1, lo)]-shifts[(n, d, s, lo)]))
                for lo in all_locations:
                    for s in all_shifts[0:-run_length]:
                        tmp_var1 = model.NewIntVar(-max_shift, max_shift, 'tmp1deltan%dd%dlo%ds%d' % (n, d, lo, s))
                        model.Add((shifts[(n, d, s+1, lo)]-shifts[(n, d, s, lo)]) == tmp_var1).OnlyEnforceIf(preferedRunLength)
                        tmp_var2 = model.NewIntVar(0, max_shift, 'tmp2deltan%dd%dlo%ds%d' % (n, d, lo, s))
                        model.AddAbsEquality(tmp_var2, tmp_var1)
                        delta_vars[d].append(tmp_var2)
            model.Add(sum([delta_vars[d][s] for s in all_shifts[0:-run_length]])*run_length <= sum([shift_requests[n][d][s][lo] * shifts[(n, d, s, lo)]
                for lo in all_locations for s in all_shifts])).OnlyEnforceIf(preferedRunLength)
            n_conditions += 1

        model.Proto().assumptions.append(preferedRunLength.Index())
        

    if rules['maxOneLateShift']:
        # only assign max. one 18-20 shift for a given librarian
        maxOneLateShift = model.NewBoolVar('maxOneLateShift')
        s = all_shifts[-1]
        model.Add(sum([shifts[(n, d, s, lo)]
            for d in all_days for lo in all_locations]) <= 1).OnlyEnforceIf(maxOneLateShift)
        n_conditions += 1
        model.Proto().assumptions.append(maxOneLateShift.Index())

    if rules['noSeventeenToTwenty']:
        # prevent 17-18 + 18-20 sequence for any librarian
        noSeventeenToTwenty = model.NewBoolVar('noSeventeenToTwenty')
        for d in all_days:
            model.Add(sum([shifts[(n, d, s, lo)]
                for s in all_shifts[-2:] for lo in all_locations]) <= 1).OnlyEnforceIf(noSeventeenToTwenty)
            n_conditions += 1
        model.Proto().assumptions.append(noSeventeenToTwenty.Index())

    if rules['noTwelveToFourteen']:
        # prevent 12-13 + 13-14 sequence for any librarian
        noTwelveToFourteen = model.NewBoolVar('noTwelveToFourteen')
        for d in all_days:
            model.Add(sum([shifts[(n, d, s, lo)]
                for s in [12-8, 13-8] for lo in all_locations]) <= 1).OnlyEnforceIf(noTwelveToFourteen)
            n_conditions += 1
        model.Proto().assumptions.append(noTwelveToFourteen.Index())


    # Try to distribute the shifts evenly, so that each librarian works
    # his quota of shifts (or quota - 1) on the active or reserve locations

    noOutOfTimeShift = model.NewBoolVar('noOutOfTimeShift')
    minActiveShifts = model.NewBoolVar('minActiveShifts')
    maxActiveShifts = model.NewBoolVar('maxActiveShifts')
    minReserveShifts = model.NewBoolVar('minReserveShifts')
    maxReserveShifts = model.NewBoolVar('maxReserveShifts')
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
                        if s == all_shifts[-1]:
                            # Last shift must be counted twice, as it lasts 2 hours
                            num_shifts_reserve += shifts[(n, d, s, lo)]
                    out_of_time_shifts += shifts[(n, d, s, lo)] * (1-shift_requests[n][d][s][lo])
                    # Shifts during mandatory meetings also count as out of time
                    if d == meeting_slots[librarians[n]['sector']][0]:
                        if s >= meeting_slots[librarians[n]['sector']][1] and s <= meeting_slots[librarians[n]['sector']][2]:
                            out_of_time_shifts += shifts[(n, d, s, lo)] * 1
                    if d == meeting_slots['dir'] and librarians[n]['type'] == 'dir':
                        if s >= meeting_slots['dir'][1] and s <= meeting_slots['dir'][2]:
                            out_of_time_shifts += shifts[(n, d, s, lo)] * 1

        if rules['noOutOfTimeShift']:        
            model.Add(out_of_time_shifts < 1).OnlyEnforceIf(noOutOfTimeShift)
            n_conditions += 1
        if rules['minActiveShifts']:      
            model.Add(num_shifts_worked >= quota[librarians[n]['type']][0] - quota[librarians[n]['type']][0]//2 ).OnlyEnforceIf(minActiveShifts)
            n_conditions += 1
        if rules['minReserveShifts']: 
            model.Add(num_shifts_reserve >= quota[librarians[n]['type']][1] - 1).OnlyEnforceIf(minReserveShifts)
            n_conditions += 1
        if rules['maxActiveShifts']: 
            model.Add(num_shifts_worked <= quota[librarians[n]['type']][0]).OnlyEnforceIf(maxActiveShifts)
            n_conditions += 1
        if rules['maxReserveShifts']: 
            model.Add(num_shifts_reserve <= quota[librarians[n]['type']][1]).OnlyEnforceIf(maxReserveShifts)
            n_conditions += 1
        
    sector_score = len(all_days)*[{}]

    model.Proto().assumptions.append(noOutOfTimeShift.Index())
    model.Proto().assumptions.append(minActiveShifts.Index())
    model.Proto().assumptions.append(minReserveShifts.Index())
    model.Proto().assumptions.append(maxActiveShifts.Index())
    model.Proto().assumptions.append(maxReserveShifts.Index())
    
    for d in all_days:
        for sector in sector_semester_quotas:
            sector_score[d][sector] = sum([shifts[(n, d, s, lo)] for n in all_librarians
                for s in all_shifts for lo in all_locations if librarians[n]['sector'] == sector])

            #model.Add(sector_score[d][sector] <= sector_semester_quotas[sector])
    
    

    # pylint: disable=g-complex-comprehension
    model.Maximize(
        sum([shift_requests[n][d][s][lo] * shifts[(n, d, s, lo)] for n in all_librarians
                    for d in all_days for s in all_shifts for lo in all_locations]))
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
    
    if status == cp_model.INFEASIBLE:
        print('Damn. Wish I knew why.')
        stat_details = f'{solver.ResponseStats()}'
        print(f"**Solver statistics:**\n{stat_details}")
        for var_index in solver.ResponseProto().sufficient_assumptions_for_infeasibility:
            print(var_index, model.VarIndexToVarProto(var_index)) # prints "v1"

        exit(1)

    print()

    report = ''
    for d in all_days:
        line = f'Day {d}'
        print(line)
        report += '<br/>\n' + line + '<br/>\n'
        for lo in all_locations:
            for s in all_shifts:
                for n in all_librarians:
                    #print(n, d, s, lo)
                    #print(shifts[(n, d, s, lo)])
                    # FIXME don't forget the dir meeting check!!!
                    if solver.Value(shifts[(n, d, s, lo)]) == 1:
                        if shift_requests[n][d][s][lo] == 1:
                            if not d == meeting_slots[librarians[n]['sector']][0] or s < meeting_slots[librarians[n]['sector']][1] or s > meeting_slots[librarians[n]['sector']][2]:
                                if s < all_shifts[-1]:
                                    line = f'{librarians[n]["name"]} works 1h at {s+8}:00 on {weekdays[d]} at {locations[lo]["name"]} (OK with work hours).'
                                    print(line)
                                    report += line + '<br>\n'
                                else:
                                    line = f'{librarians[n]["name"]} works 2h at {s+8}:00 on {weekdays[d]} at {locations[lo]["name"]} (OK with work hours).'
                                    print(line)
                                    report += line + '<br>\n'
                            else:
                                line = f'{librarians[n]["name"]} works 1h at {s+8}:00 on {weekdays[d]} at {locations[lo]["name"]} (problem with a group meeting).'
                                print(line)
                                report += line + '<br>\n'                    
                        else:
                            line = f'{librarians[n]["name"]} works 1h at {s+8}:00 on {weekdays[d]} at {locations[lo]["name"]} (problem with work hours).'
                            # print(shift_requests[n][d])
                            print(line)
                            report += line + '<br/>\n'

        for sector in sector_semester_quotas:
            score = sum([solver.Value(shifts[(n, d, s, lo)]) for n in all_librarians
                        for s in all_shifts for lo in all_locations if librarians[n]['sector'] == sector])
            score += sum([solver.Value(shifts[(n, d, all_shifts[-1], lo)]) for n in all_librarians
                        for lo in all_locations if librarians[n]['sector'] == sector])
            
            unique_librarians = 0
            am_librarians = 0
            pm_librarians = 0
            for n in all_librarians:
                worked_today = sum([solver.Value(shifts[(n, d, s, lo)]) for s in all_shifts
                    for lo in all_locations if librarians[n]['sector'] == sector])
                if worked_today > 0:
                    unique_librarians += 1
                worked_am = sum([solver.Value(shifts[(n, d, s, lo)]) for s in all_shifts[0:6]
                    for lo in all_locations if librarians[n]['sector'] == sector])
                if worked_am > 0:
                    am_librarians += 1
                worked_pm = sum([solver.Value(shifts[(n, d, s, lo)]) for s in all_shifts[6:-1]
                    for lo in all_locations if librarians[n]['sector'] == sector])
                if worked_pm > 0:
                    pm_librarians += 1
            line = f'Daily shifts for {sector.upper()}: {score} (using {unique_librarians} unique librarian(s), minimum {sector_semester_quotas[sector]})'
            print(line)
            report += line + '<br/>\n'
            line = f'Morning (8h-13): {am_librarians} librarian(s), afternoon (12h-20h): {pm_librarians} librarian(s)'
            print(line)
            report += line + '<br/>\n'
    print()
    report += line + '<br/>\n'

    line = 'Librarians work summary'
    print(line)
    report += '<br/>\n' + line + '<br/>\n'
    for n in all_librarians:
        score = sum(solver.Value(shifts[(n, d, s, lo)])
            for d in all_days for s in all_shifts for lo in all_locations if locations[lo]['name'].lower().find('remplacement') < 0)
        score += sum(solver.Value(shifts[(n, d, all_shifts[-1], lo)])
            for d in all_days for lo in all_locations if locations[lo]['name'].lower().find('remplacement') < 0)
        score_reserve = sum(solver.Value(shifts[(n, d, s, lo)])
            for d in all_days for s in all_shifts for lo in all_locations if locations[lo]['name'].lower().find('remplacement') >= 0)
        score_reserve += sum(solver.Value(shifts[(n, d, all_shifts[-1], lo)])
            for d in all_days for lo in all_locations if locations[lo]['name'].lower().find('remplacement') >= 0)
        s1 = f'{librarians[n]["name"]} is working {score}/{quota[librarians[n]["type"]][0]}'
        s2 = f' and acting as a reserve for {score_reserve}/{quota[librarians[n]["type"]][1]} shifts'
        line = s1 + s2
        print(line)
        report += line + '<br/>\n'

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

#schedule, #guichetbiblio {  
  border collapse: collapse;
  width: 100%;
}

#schedule td, #schedule th {
  border: 1px solid #ddd;
  padding: 8px;
}

#guichetbiblio td, #guichetbiblio th {
  border: 1px solid #ddd;
  padding: 8px;
}

#schedule tr:nth-child(even){background-color: #f2f2f2;}
#guichetbiblio tr:nth-child(even){background-color: #f2f2f2;}

#schedule tr:hover {background-color: #ddd;}
#guichetbiblio tr:hover {background-color: #ddd;}

#schedule th {
  padding-top: 12px;
  padding-bottom: 12px;
  text-align: left;
  background-color: #04AA6D;
  color: white;
}

#guichetbiblio th {
  padding-top: 12px;
  padding-bottom: 12px;
  text-align: left;
  background-color: #0000FF;
  color: white;
}
</style></head>"""

    title = f"<h1>{main_title}</h1>"

    score = f"Solution score = {solver.ObjectiveValue()} (max possible result {n_conditions})"
    stat_details = f'{solver.ResponseStats()}'


    guichetbiblio_table = '<div><table id="guichetbiblio" class="table">\n'
    guichetbiblio_table += '<thead>'
    guichetbiblio_table += "<tr>\n"
    guichetbiblio_table += '<th scope="col">Poste</th>'
    for s in all_shifts:
        if s < all_shifts[-1]:
            guichetbiblio_table += f'<th scope="col">{(s+8):02}:00-{(s+9):02}:00</th>'
        else:
            guichetbiblio_table += f'<th scope="col">{(s+8):02}:00-{(s+10):02}:00</th>'
    guichetbiblio_table += "\n</tr>\n</thead>\n<tbody>"
    for d in all_days:
        for lo in all_locations:
            guichetbiblio_table += "<tr>\n"
            guichetbiblio_table += f"<td>{weekdays[d]} {locations[lo]['name']}</td>"
            for s in all_shifts:
                cell = "<td>N/A</td>"
                for n in all_librarians:
                    if solver.Value(shifts[(n, d, s, lo)]) == 1:
                        cell = f"<td>{librarians[n]['name']}</td>"
                guichetbiblio_table += cell
            guichetbiblio_table += "</tr>\n"
        guichetbiblio_table += "<tr>"
        for s in all_shifts:
            guichetbiblio_table += '<td></td>'
        guichetbiblio_table += "</tr>\n"

    guichetbiblio_table +=  "</tbody></table></div>"

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
            if s < all_shifts[-1]:
                table += f"<td>{(s+8):02}:00-{(s+9):02}:00 {locations[lo]['name']}</td>"
            else:
                table += f"<td>{(s+8):02}:00-{(s+10):02}:00 {locations[lo]['name']}</td>"
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
    body += f"\n<h2>Summary table (for guichetbiblio.epfl.ch)</h2>"
    body += f"\n{guichetbiblio_table}"
    body += f"\n<h2>Summary table (for other use cases)</h2>"
    body += f"\n{table}"
    body += f'\n<div>{report}</div></body>'

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
