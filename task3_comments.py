"""
Methods used in task 3. This is used for testing of methods and ideas. My final 
working solution will be added to the scheduler.py file.
"""
import module
import tutor
import ReaderWriter
import timetable
import random
import math

from time import time
"""
Methods for testing.
"""
def solve_timetable_test(file_name):
    rw = ReaderWriter.ReaderWriter()
    tutors, modules = rw.readRequirements(file_name)
    time_table = timetable.Timetable(2)
    module_tutor_pairs = generate_module_tutor_pairs(time_table, modules, tutors)
    can_solve_slot(time_table, module_tutor_pairs, 1)
    print(file_name + ': ' + str(time_table.scheduleChecker(tutors, modules)))
    print('Table cost: ' + str(time_table.cost))

"""
Core methods for the CSP backtracking.
"""
TIME_TABLE_SLOTS = {}
bound = 18750
min_cost_time_table = None

def solve_timetable():
    rw = ReaderWriter.ReaderWriter()
    tutors, modules = rw.readRequirements("ExampleProblems/Problem1.txt")
    time_table = timetable.Timetable(2)
    module_tutor_pairs = generate_module_tutor_pairs(time_table, modules, tutors)
    generate_time_table_slot()
    # attempt to solve the task
    can_solve_slot(time_table, module_tutor_pairs, 1)
    print_timetable(time_table, tutors, modules)

def generate_module_tutor_pairs(time_table, modules, tutors):
    """
    Generate a valid list of module-tutor pairs. For a pair to be valid, the 
    topics of a module must all be in a tutors expertise. This is the as doing it
    in the can_assign_pair method but I do here to reduce the domain before we 
    start the backtracking.
    """
    pairs = []
    for module in modules:
        for tutor in tutors:
            if time_table.canTeach(tutor, module, False):
                pairs.append(ModuleTutorPair(module, tutor, False))
            if time_table.canTeach(tutor, module, True):
                pairs.append(ModuleTutorPair(module, tutor, True))
    # sort the pairs by their number of least constraining values. If there is a
    # tie-break, lab sessions come before modules as they have less constraints.
    return sort_domain(pairs)

def generate_time_table_slot():
    global TIME_TABLE_SLOTS
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    counter = 1
    for day in days:
        for i in range(1, 11):
            TIME_TABLE_SLOTS[str(counter)] = [day, i]
            counter += 1
    
def can_solve_slot(time_table, pairs, slot, cost=0):
    """
    This is going to be my first attempt traversing the timetable vertically 
    starting on Monday, time slot 1. When time slot 5 is populated, move to the 
    next day, time slot 1.
    """
    global bound, min_cost_time_table
    # check if all slots have been filled and the cost is smallest possible.
    if slot == 51:
        if cost == 10150:
            return True
        bound = cost
        min_cost_time_table = time_table
        return False

    day, time_slot = minimum_remaining_value(slot)

    pairs = sorted(pairs, key=lambda x: calc_node_cost(time_table, day, x))

    for pair in pairs:
        if can_assign_pair(time_table, day, pair):
            new_cost = path_cost(pair, slot, cost)
            if new_cost >= bound:
                continue

            time_table.addSession(day, time_slot, pair.tutor, pair.module, pair.session_type)
            
            print(str(slot) + ' Assigned ' + pair.module.name + ' : ' + pair.tutor.name + ' : ' + pair.session_type)
            print(str(slot) + ' cost: ' + str(new_cost) + ' | ' + str(bound))

            pruned_pairs = forward_checking(pair, pairs)

            if can_solve_slot(time_table, pruned_pairs, slot + 1, new_cost):
                return True

            del time_table.schedule[day][time_slot]
    # no solution.
    return False

def can_assign_pair(time_table, day, pair):
    """
    Check that the module-tutor pair given does not violate any of the 
    constraints. The constraints are:
    1) A tutor cannot teach more than 2 credits a day,
    2) A tutor can teach a maximum of 4 credits,
    """       
    # check that the tutor is not already teaching more than 2 credits that day.
    day_credits = 0
    for slot in time_table.schedule[day].values():
        if slot[0] == pair.tutor:
            credit = 1 if slot[2] == 'lab' else 2
            day_credits += credit

    if day_credits + pair.credit > 2:
        return False

    # check the tutor is not teaching more than 4 credits.
    total_credits = 0
    for day_slots in time_table.schedule.items():
        for slot in day_slots[1].values():
            if slot[0] == pair.tutor:
                credit = 1 if slot[2] == 'lab' else 2
                total_credits += credit

    if total_credits + pair.credit > 4:
        return False

    # passed all tests, pair is valid.
    return True

def path_cost(pair, slot, cost):
    """
    """
    def heuristic(slot):
        return 50 * (50 - slot)

    return cost + heuristic(slot)

def minimum_remaining_value(slot):
    """
    This method chooses the variable with the fewest remaining values. It is 
    effectively starting a Monday slot 1 then slot 2 ... slot 10 then going to 
    Tuesday slot 1 and repeating until Friday slot 10. It does this as the way to
    reduce the domain is by selecting a slot in the same day as the one just 
    selected as we can remove tutors and modules.
    """   
    slot_meta = TIME_TABLE_SLOTS[str(slot)] 
    return slot_meta[0], slot_meta[1]

def sort_domain(pairs):
    """
    This method is going to sort and return the elements of the domain.
    """
    # for each module, count the number of elements with that module.
    module_count = {}
    for pair in pairs:
        module_name = pair.module.name + '_l' if pair.is_lab else pair.module.name
        count = module_count.get(module_name)
        if count is None:
            module_count[module_name] = 1
        else:
            module_count[module_name] += 1

    # sort by least common module count
    return sorted(pairs, key=lambda x: (module_count[x.name], not x.is_lab))

def calc_node_cost(time_table, day, pair):
    """
    This method will calculate the cost of adding the given pair.
    """
    PREV_DAY = {
        'Tuesday': 'Monday',
        'Wednesday': 'Tuesday',
        'Thursday': 'Wednesday',
        'Friday': 'Thursday'
    }

    if pair.is_lab:
        # look in the and calc cost of adding this lab
        labs = 0
        for slot in time_table.schedule[day].values():
            if slot[2] == 'lab' and slot[0] == pair.tutor:
                labs += 1
        return 250 - (50 * labs)
    else:
        first_day = None
        # check to see if the tutor is already teaching a module this week and if 
        # so, what day it is on
        for day_slots in time_table.schedule.items():
            for slot in day_slots[1].values():
                if slot[0] == pair.tutor and not slot[2] == 'lab':
                    first_day = day_slots[0]
        
        if first_day is not None or day != 'Monday':
            if first_day == PREV_DAY[day]:
                return 100
            return 300
        return 500

def forward_checking(pair, pairs):
    """
    Apply forward checking to the given pairs to reduce the domain. by removing 
    all domain elements with the same module that was just selected. 
    """
    pruned_pairs = [
        x for x in pairs if not (x.module == pair.module and x.is_lab == pair.is_lab)
    ]
        
    return pruned_pairs

class ModuleTutorPair:

    def __init__(self, module, tutor, is_lab):
        self.module = module
        self.tutor = tutor
        self.is_lab = is_lab

    def __str__(self):
        return '(' + self.module.name + ', ' + self.tutor.name + ', ' + self.session_type + ')' 

    def __repr__(self):
        return str(self)

    @property
    def session_type(self):
        if self.is_lab:
            return 'lab'
        return 'module'
    
    @property
    def credit(self):
        if self.is_lab:
            return 1
        return 2

    @property
    def name(self):
        module_name = self.module.name
        module_name = module_name + '_l' if self.is_lab else module_name
        return module_name

"""
Utitlity methods
"""
def print_timetable(time_table, tutors, modules):
    """
    Print the time table as well as showing if the solution found is valid.
    """
    print('----------------------------')
    for day, slots in time_table.schedule.items():
        for slot_name, slot_val in slots.items():
            print(str(slot_name) + ': ' + slot_val[1].name + ' ' + slot_val[2] + ': ' + slot_val[0].name)
    print('----------------------------')
    print('Table valid status: ' + str(time_table.scheduleChecker(tutors, modules)))
    print('Table cost: ' + str(time_table.cost))

solve_timetable()