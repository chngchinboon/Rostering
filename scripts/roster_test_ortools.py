from __future__ import division
from __future__ import print_function
from ortools.sat.python import cp_model


class EmployeePartialSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, shifts, num_employees, num_days, num_shifts, sols):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._shifts = shifts
        self._num_employees = num_employees
        self._num_days = num_days
        self._num_shifts = num_shifts
        self._solutions = set(sols)
        self._solution_count = 0

    def on_solution_callback(self):
        self._solution_count += 1
        if self._solution_count in self._solutions:
            print('Solution %i' % self._solution_count)
            for d in range(self._num_days):
                print('Day %i' % d)
                for n in range(self._num_employees):
                    is_working = False
                    for s in range(self._num_shifts):
                        if self.Value(self._shifts[(n, d, s)]):
                            is_working = True
                            print('  employee %i works shift %i' % (n, s))
                    if not is_working:
                        print('  employee {} does not work'.format(n))
            print()

    def solution_count(self):
        return self._solution_count


def main():
    # Data.
    num_employees = 10
    num_shifts = 2
    num_days = 15
    all_employees = range(num_employees)
    all_shifts = range(num_shifts)
    all_days = range(num_days)
    # Creates the model.
    model = cp_model.CpModel()

    # Creates shift variables.
    # shifts[(n, d, s)]: employee 'n' works shift 's' on day 'd'.
    shifts = {}
    for n in all_employees:
        for d in all_days:
            for s in all_shifts:
                shifts[(n, d, s)] = model.NewBoolVar('shift_n%id%is%i' % (n, d,
                                                                          s))

    # Each shift is assigned to exactly one employee in the schedule period.
    for d in all_days:
        for s in all_shifts:
            model.Add(sum(shifts[(n, d, s)] for n in all_employees) == 1)

    # Each employee works at most one shift per day.
    for n in all_employees:
        for d in all_days:
            model.Add(sum(shifts[(n, d, s)] for s in all_shifts) <= 1)

    # min_shifts_per_employee is the largest integer such that every employee
    # can be assigned at least that many shifts. If the number of employees doesn't
    # divide the total number of shifts over the schedule period,
    # some employees have to work one more shift, for a total of
    # min_shifts_per_employee + 1.
    min_shifts_per_employee = (num_shifts * num_days) // num_employees
    max_shifts_per_employee = min_shifts_per_employee + 1
    for n in all_employees:
        num_shifts_worked = sum(
            shifts[(n, d, s)] for d in all_days for s in all_shifts)
        model.Add(min_shifts_per_employee <= num_shifts_worked)
        model.Add(num_shifts_worked <= max_shifts_per_employee)

    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    # Display the first five solutions.
    a_few_solutions = range(5)
    solution_printer = EmployeePartialSolutionPrinter(
        shifts, num_employees, num_days, num_shifts, a_few_solutions)
    solver.SearchForAllSolutions(model, solution_printer)

    # Statistics.
    print()
    print('Statistics')
    print('  - conflicts       : %i' % solver.NumConflicts())
    print('  - branches        : %i' % solver.NumBranches())
    print('  - wall time       : %f ms' % solver.WallTime())
    print('  - solutions found : %i' % solution_printer.solution_count())


if __name__ == '__main__':
    main()