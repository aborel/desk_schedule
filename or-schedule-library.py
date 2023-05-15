# From https://developers.google.com/optimization/scheduling/employee_scheduling

from ortools.sat.python import cp_model
import numpy
from numpy import array

# based on K_Guichets//K2_Guichets_physiques/K2.03_Tournus/quotas_par_guichetier_20190131.JPG
# TODO: ask for the rule for bl+coordinator
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

locations = {
    0: 'Accueil 1',
    1: 'Accueil 2',
    2: 'STM'
}

def main():
    # This program tries to find an optimal assignment of librarians to shifts
    # (10 shifts per day, for 5 days), subject to some constraints (see below).
    # Each librarian can request to be assigned to specific shifts.
    # The optimal assignment maximizes the number of fulfilled shift requests.
    num_librarians = 43
    num_shifts = 10
    num_days = 5
    # TODO: deal with replacement shifts later
    num_locations = 3
    all_librarians = range(num_librarians)
    all_shifts = range(num_shifts)
    all_days = range(num_days)
    all_locations = range(num_locations)
    # TODO use locations

    # pseudo-random matrix of requests as per
    # https://stackoverflow.com/questions/19597473/binary-random-array-with-a-specific-proportion-of-ones
    # shift_requests = [numpy.random.choice([0, 1], size=(5,10, 3), p=[4./6, 2./6]) for k in range(43)]

    shift_requests = [numpy.random.choice([0, 1], size=(5,10, 3), p=[5./6, 1./6]) for k in range(43)]


    # Creates the model.
    model = cp_model.CpModel()

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
    #print(shifts)

    # Each shift is assigned to exactly 3 librarians (1 per location).
    # TODO: make that 2 or 3; changing the constant raises an error: need to be smarter?
    for d in all_days:
        for s in all_shifts:
            for lo in all_locations:
                model.Add(sum(shifts[(n, d, s, lo)] for n in all_librarians) == 1)

    # Each librarian works at most 1 shift per day.
    # TODO: make that 2 SUCCESSIVE shifts
    for n in all_librarians:
        for d in all_days:
            model.Add(sum(shifts[(n, d, s, lo)]
                for s in all_shifts for lo in all_locations) <= 1)

    # Try to distribute the shifts evenly, so that each librarian works
    # min_shifts_per_librarian shifts. If this is not possible, because the total
    # number of shifts is not divisible by the number of librarians, some librarians will
    # be assigned one more shift.
    
    min_shifts_per_librarian = (num_shifts * num_days * num_locations) // num_librarians
    print('min_shifts_per_librarian: ', min_shifts_per_librarian)
    if num_shifts * num_days % num_librarians == 0:
        max_shifts_per_librarian = min_shifts_per_librarian
    else:
        max_shifts_per_librarian = min_shifts_per_librarian + 1
    for n in all_librarians:
        num_shifts_worked = 0
        for d in all_days:
            for s in all_shifts:
                for lo in all_locations:
                    num_shifts_worked += shifts[(n, d, s, lo)]
        model.Add(min_shifts_per_librarian <= num_shifts_worked)
        print('max_shifts_per_librarian: ', max_shifts_per_librarian)
        model.Add(num_shifts_worked <= max_shifts_per_librarian)

    # pylint: disable=g-complex-comprehension
    model.Maximize(
        sum(shift_requests[n][d][s][lo] * shifts[(n, d, s, lo)] for n in all_librarians
            for d in all_days for s in all_shifts for lo in all_locations))
    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    print('Solved (hopefully)?', status)
    print('cp_model.FEASIBLE', cp_model.FEASIBLE)
    print('cp_model.INFEASIBLE', cp_model.INFEASIBLE)
    print('cp_model.OPTIMAL', cp_model.OPTIMAL)
    
    for d in all_days:
        print('Day', d)
        for lo in all_locations:
            for s in all_shifts:
                for n in all_librarians:
                    #print(n, d, s, lo)
                    #print(shifts[(n, d, s, lo)])
                    if solver.Value(shifts[(n, d, s, lo)]) == 1:
                        if shift_requests[n][d][s][lo] == 1:
                            print(f'librarian {n} works shift {s} at location {locations[lo]} (requested).')
                        else:
                            print(f'librarian {n} works shift {s} at location {locations[lo]} (unrequested).')
        print()

    # Statistics.

    print()
    print('Statistics')
    print('  - Number of shift requests met = %i' % solver.ObjectiveValue(),
          '(out of', num_librarians * min_shifts_per_librarian, ')')
    print('  - wall time       : %f s' % solver.WallTime())


if __name__ == '__main__':
    main()
