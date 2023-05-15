# From https://developers.google.com/optimization/scheduling/employee_scheduling

from ortools.sat.python import cp_model
from numpy import array


def main():
    # This program tries to find an optimal assignment of librarians to shifts
    # (10 shifts per day, for 5 days), subject to some constraints (see below).
    # Each librarian can request to be assigned to specific shifts.
    # The optimal assignment maximizes the number of fulfilled shift requests.
    num_librarians = 43
    num_shifts = 10
    num_days = 5
    all_librarians = range(num_librarians)
    all_shifts = range(num_shifts)
    all_days = range(num_days)
    # pseudo-random matrix of requests as per
    # https://stackoverflow.com/questions/19597473/binary-random-array-with-a-specific-proportion-of-ones
    # shift_requests = [numpy.random.choice([0, 1], size=(5,10), p=[4./6, 2./6]) for k in range(43)]
    shift_requests = [array([[0, 1, 0, 0, 1, 1, 1, 0, 0, 0],
       [0, 1, 0, 0, 1, 1, 0, 0, 0, 1],
       [1, 1, 0, 0, 0, 0, 1, 1, 1, 0],
       [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 1, 0, 0, 0, 1, 1]]), array([[1, 0, 1, 0, 0, 0, 0, 0, 1, 1],
       [0, 0, 0, 0, 1, 1, 1, 0, 1, 0],
       [1, 0, 0, 0, 0, 0, 0, 0, 1, 1],
       [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
       [0, 1, 0, 1, 0, 0, 0, 1, 0, 0]]), array([[0, 0, 1, 1, 0, 1, 1, 0, 0, 0],
       [0, 1, 0, 0, 0, 1, 0, 1, 0, 0],
       [0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
       [0, 0, 1, 0, 0, 0, 0, 0, 1, 0],
       [1, 0, 1, 1, 0, 0, 0, 1, 0, 0]]), array([[0, 0, 0, 1, 0, 1, 0, 1, 1, 0],
       [0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
       [0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
       [0, 0, 1, 1, 0, 1, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 1, 0, 0, 0]]), array([[1, 1, 0, 1, 1, 0, 1, 0, 1, 1],
       [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
       [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 1, 1, 1, 0, 0, 0, 1]]), array([[1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
       [0, 1, 1, 0, 0, 0, 1, 0, 1, 1],
       [0, 0, 0, 0, 0, 1, 0, 1, 0, 0],
       [0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]]), array([[0, 0, 1, 0, 1, 1, 0, 0, 0, 0],
       [0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
       [1, 0, 0, 1, 1, 0, 0, 0, 1, 0],
       [0, 0, 0, 0, 1, 0, 1, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 1, 0, 0]]), array([[1, 0, 0, 1, 0, 0, 1, 0, 0, 1],
       [0, 0, 0, 0, 0, 1, 1, 1, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
       [0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
       [1, 0, 0, 1, 0, 0, 0, 0, 0, 0]]), array([[1, 0, 1, 0, 0, 1, 0, 1, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
       [0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
       [0, 1, 1, 1, 1, 0, 0, 1, 1, 0],
       [0, 1, 1, 0, 0, 0, 0, 0, 0, 1]]), array([[0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
       [0, 0, 1, 1, 0, 0, 1, 0, 0, 0],
       [0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
       [0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
       [0, 0, 1, 1, 0, 0, 0, 1, 0, 0]]), array([[1, 1, 1, 1, 0, 1, 0, 1, 0, 0],
       [1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
       [0, 1, 0, 0, 1, 0, 1, 0, 0, 0],
       [0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
       [0, 1, 0, 0, 0, 1, 0, 0, 1, 0]]), array([[0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
       [0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
       [0, 0, 0, 0, 1, 1, 0, 0, 0, 1],
       [0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
       [1, 0, 1, 1, 0, 1, 1, 1, 1, 1]]), array([[0, 1, 0, 0, 1, 0, 0, 1, 0, 1],
       [0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
       [0, 1, 0, 1, 0, 0, 0, 0, 0, 0],
       [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
       [1, 1, 0, 0, 0, 1, 0, 0, 1, 0]]), array([[0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
       [1, 0, 1, 0, 1, 0, 0, 0, 0, 0],
       [1, 0, 0, 1, 0, 1, 0, 1, 0, 0],
       [0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
       [0, 0, 1, 0, 1, 0, 0, 0, 0, 0]]), array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 1, 1, 0, 0, 0, 0, 1, 0, 0],
       [0, 1, 0, 0, 0, 1, 0, 1, 1, 0],
       [0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
       [1, 0, 0, 0, 1, 1, 1, 1, 1, 0]]), array([[1, 0, 0, 1, 0, 0, 1, 0, 1, 0],
       [1, 0, 1, 1, 0, 0, 1, 0, 0, 0],
       [0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
       [0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
       [0, 1, 0, 1, 0, 0, 1, 0, 0, 0]]), array([[0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
       [0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
       [1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 1, 0, 0, 0]]), array([[0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
       [1, 0, 1, 0, 0, 1, 1, 0, 0, 1],
       [1, 1, 0, 0, 0, 0, 0, 1, 0, 0],
       [0, 1, 1, 0, 0, 0, 0, 0, 1, 1],
       [0, 1, 1, 0, 1, 0, 0, 0, 0, 1]]), array([[1, 0, 1, 1, 0, 0, 0, 1, 0, 1],
       [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
       [0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
       [0, 0, 0, 0, 1, 1, 1, 0, 1, 0],
       [0, 0, 0, 1, 1, 0, 1, 1, 1, 1]]), array([[1, 0, 1, 0, 0, 0, 1, 0, 0, 0],
       [0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
       [0, 0, 0, 1, 1, 1, 0, 0, 1, 0],
       [1, 0, 0, 1, 1, 1, 0, 0, 0, 0],
       [1, 0, 1, 0, 0, 1, 0, 0, 1, 1]]), array([[0, 0, 0, 1, 1, 0, 0, 1, 1, 1],
       [0, 1, 0, 0, 1, 1, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
       [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 1, 1, 0, 0, 1, 1, 0, 0]]), array([[1, 0, 0, 0, 1, 1, 0, 1, 0, 0],
       [0, 1, 1, 0, 0, 0, 0, 0, 0, 1],
       [0, 1, 0, 1, 0, 1, 1, 0, 0, 0],
       [1, 0, 0, 0, 0, 0, 1, 1, 1, 1],
       [0, 1, 0, 0, 1, 1, 0, 0, 0, 0]]), array([[1, 1, 1, 0, 1, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 1, 1, 0, 0, 0, 1],
       [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 1, 0, 1, 0, 0, 0, 0, 1, 0]]), array([[0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
       [0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
       [1, 1, 0, 0, 1, 1, 1, 0, 0, 0],
       [0, 0, 0, 0, 1, 0, 1, 1, 0, 0],
       [0, 1, 1, 0, 0, 1, 0, 1, 0, 0]]), array([[1, 0, 1, 1, 1, 0, 1, 0, 0, 0],
       [0, 1, 0, 1, 0, 0, 0, 0, 1, 0],
       [0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
       [1, 0, 1, 0, 0, 1, 0, 0, 1, 0],
       [1, 0, 0, 0, 0, 1, 0, 1, 1, 0]]), array([[0, 0, 0, 1, 0, 1, 0, 1, 0, 0],
       [0, 1, 0, 0, 0, 0, 1, 1, 0, 1],
       [1, 1, 0, 1, 0, 0, 0, 0, 0, 0],
       [0, 1, 1, 1, 0, 1, 1, 0, 0, 1],
       [1, 0, 0, 1, 0, 0, 0, 1, 1, 1]]), array([[0, 1, 1, 0, 1, 1, 1, 0, 0, 0],
       [0, 0, 1, 0, 1, 0, 0, 0, 0, 0],
       [0, 1, 1, 0, 1, 0, 1, 0, 0, 0],
       [1, 0, 0, 0, 0, 0, 1, 1, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]), array([[1, 1, 0, 1, 1, 0, 0, 1, 0, 0],
       [0, 1, 1, 0, 0, 1, 0, 0, 0, 1],
       [0, 1, 0, 0, 0, 1, 1, 0, 0, 1],
       [0, 1, 1, 0, 0, 1, 0, 0, 0, 0],
       [1, 1, 0, 0, 1, 0, 1, 0, 0, 0]]), array([[0, 1, 0, 0, 1, 0, 1, 0, 1, 1],
       [1, 0, 0, 0, 0, 0, 1, 1, 0, 1],
       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
       [0, 1, 1, 1, 1, 0, 1, 1, 0, 1]]), array([[0, 1, 0, 1, 0, 1, 1, 1, 0, 0],
       [1, 1, 1, 1, 0, 1, 0, 1, 0, 0],
       [1, 0, 0, 1, 0, 0, 1, 0, 0, 1],
       [1, 0, 0, 1, 0, 0, 1, 0, 0, 0],
       [0, 0, 0, 1, 0, 1, 0, 0, 0, 0]]), array([[1, 0, 0, 1, 0, 0, 0, 0, 1, 0],
       [0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
       [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
       [0, 1, 0, 0, 1, 0, 1, 0, 1, 0],
       [0, 0, 0, 1, 1, 1, 1, 0, 1, 0]]), array([[1, 0, 0, 0, 0, 1, 0, 1, 0, 0],
       [0, 0, 0, 0, 1, 1, 0, 0, 1, 0],
       [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [1, 0, 0, 0, 0, 0, 1, 1, 1, 1],
       [0, 0, 0, 0, 0, 0, 1, 0, 1, 0]]), array([[1, 1, 0, 0, 0, 1, 0, 1, 1, 0],
       [1, 1, 0, 1, 1, 0, 0, 1, 0, 1],
       [0, 1, 0, 0, 1, 1, 0, 1, 1, 0],
       [0, 0, 0, 0, 1, 0, 1, 0, 0, 0],
       [0, 0, 1, 1, 1, 1, 1, 0, 1, 1]]), array([[1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
       [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
       [0, 1, 0, 0, 1, 0, 0, 1, 0, 0],
       [1, 1, 1, 0, 1, 1, 0, 0, 1, 0],
       [1, 1, 1, 1, 0, 0, 1, 0, 0, 0]]), array([[0, 0, 1, 0, 1, 0, 1, 1, 0, 1],
       [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
       [0, 1, 0, 1, 0, 0, 0, 0, 0, 1],
       [0, 1, 0, 0, 1, 0, 0, 0, 1, 0],
       [1, 1, 0, 0, 1, 1, 1, 0, 0, 0]]), array([[0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
       [1, 1, 0, 1, 1, 0, 0, 1, 0, 0],
       [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
       [0, 0, 1, 0, 1, 0, 1, 1, 0, 0],
       [0, 0, 1, 0, 1, 0, 0, 0, 1, 0]]), array([[1, 1, 0, 0, 1, 0, 0, 0, 1, 0],
       [1, 0, 0, 0, 0, 0, 0, 1, 1, 1],
       [0, 1, 0, 0, 1, 1, 0, 1, 0, 0],
       [1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
       [1, 0, 0, 0, 1, 0, 0, 0, 0, 1]]), array([[0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
       [0, 1, 1, 0, 0, 0, 0, 1, 0, 1],
       [1, 1, 0, 0, 0, 1, 0, 0, 0, 0],
       [1, 0, 1, 0, 0, 1, 0, 0, 1, 1],
       [0, 1, 0, 1, 1, 0, 0, 0, 0, 0]]), array([[0, 1, 0, 0, 1, 1, 0, 0, 1, 1],
       [0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
       [0, 0, 0, 1, 0, 0, 0, 1, 1, 1],
       [1, 0, 1, 0, 1, 0, 0, 0, 1, 0],
       [1, 1, 0, 0, 0, 1, 0, 0, 0, 0]]), array([[0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
       [1, 1, 1, 0, 1, 0, 1, 0, 0, 0],
       [0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
       [0, 1, 0, 1, 0, 0, 1, 1, 0, 0],
       [0, 0, 0, 1, 1, 0, 0, 1, 1, 0]]), array([[0, 0, 0, 0, 0, 1, 0, 1, 0, 0],
       [0, 0, 0, 1, 0, 1, 0, 0, 0, 1],
       [0, 1, 1, 0, 0, 0, 0, 0, 1, 0],
       [0, 0, 0, 0, 1, 1, 0, 0, 1, 1],
       [0, 0, 0, 0, 0, 0, 0, 1, 1, 0]]), array([[0, 1, 1, 0, 1, 1, 1, 0, 1, 0],
       [1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
       [0, 1, 0, 1, 0, 0, 0, 0, 0, 1],
       [0, 0, 0, 1, 0, 0, 1, 1, 0, 0],
       [0, 0, 0, 1, 1, 0, 1, 1, 1, 0]]), array([[1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
       [0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
       [0, 0, 1, 0, 0, 0, 1, 0, 1, 0],
       [0, 0, 1, 1, 0, 1, 1, 0, 1, 1]])]

    # Creates the model.
    model = cp_model.CpModel()

    # Creates shift variables.
    # shifts[(n, d, s)]: librarian 'n' works shift 's' on day 'd'.
    shifts = {}
    for n in all_librarians:
        for d in all_days:
            for s in all_shifts:
                shifts[(n, d,
                        s)] = model.NewBoolVar('shift_n%id%is%i' % (n, d, s))

    # Each shift is assigned to exactly one librarian.
    # TODO: make that 2 or 3; changing the constant raises an error: need to be smarter?
    for d in all_days:
        for s in all_shifts:
            model.Add(sum(shifts[(n, d, s)] for n in all_librarians) == 1)

    # Each librarian works at most two shifts per day.
    # TODO: make that 2 SUCCESSIVE shifts
    for n in all_librarians:
        for d in all_days:
            model.Add(sum(shifts[(n, d, s)] for s in all_shifts) <= 2)

    # Try to distribute the shifts evenly, so that each librarian works
    # min_shifts_per_librarian shifts. If this is not possible, because the total
    # number of shifts is not divisible by the number of librarians, some librarians will
    # be assigned one more shift.
    min_shifts_per_librarian = (num_shifts * num_days) // num_librarians
    if num_shifts * num_days % num_librarians == 0:
        max_shifts_per_librarian = min_shifts_per_librarian
    else:
        max_shifts_per_librarian = min_shifts_per_librarian + 1
    for n in all_librarians:
        num_shifts_worked = 0
        for d in all_days:
            for s in all_shifts:
                num_shifts_worked += shifts[(n, d, s)]
        model.Add(min_shifts_per_librarian <= num_shifts_worked)
        model.Add(num_shifts_worked <= max_shifts_per_librarian)

    # pylint: disable=g-complex-comprehension
    model.Maximize(
        sum(shift_requests[n][d][s] * shifts[(n, d, s)] for n in all_librarians
            for d in all_days for s in all_shifts))
    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    solver.Solve(model)
    for d in all_days:
        print('Day', d)
        for n in all_librarians:
            for s in all_shifts:
                if solver.Value(shifts[(n, d, s)]) == 1:
                    if shift_requests[n][d][s] == 1:
                        print('librarian', n, 'works shift', s, '(requested).')
                    else:
                        print('librarian', n, 'works shift', s, '(not requested).')
        print()

    # Statistics.
    print()
    print('Statistics')
    print('  - Number of shift requests met = %i' % solver.ObjectiveValue(),
          '(out of', num_librarians * min_shifts_per_librarian, ')')
    print('  - wall time       : %f s' % solver.WallTime())


if __name__ == '__main__':
    main()
