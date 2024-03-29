import module
import tutor
import ReaderWriter
import timetable
import random
import math

class Scheduler:

	def __init__(self,tutorList, moduleList):
		self.tutorList = tutorList
		self.moduleList = moduleList
		self.TIME_TABLE_SLOTS = {}

	#Using the tutorlist and modulelist, create a timetable of 5 slots for each of the 5 work days of the week.
	#The slots are labelled 1-5, and so when creating the timetable, they can be assigned as such:
	#	timetableObj.addSession("Monday", 1, Smith, CS101, "module")
	#This line will set the session slot '1' on Monday to the module CS101, taught by tutor Smith. 
	#Note here that Smith is a tutor object and CS101 is a module object, they are not strings.
	#The day (1st argument) can be assigned the following values: "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"
	#The slot (2nd argument) can be assigned the following values: 1, 2, 3, 4, 5 in task 1 and 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 in tasks 2 and 3. 
	#Tutor (3rd argument) and module (4th argument) can be assigned any value, but if the tutor or module is not in the original lists, 
	#	your solution will be marked incorrectly. 
	#The final, 5th argument, is the session type. For task 1, all sessions should be "module". For task 2 and 3, you should assign either "module" or "lab" as the session type.
	#Every module needs one "module" and one "lab" session type. 
	
	#moduleList is a list of Module objects. A Module object, 'm' has the following attributes:
	# m.name  - the name of the module
	# m.topics - a list of strings, describing the topics that module covers e.g. ["Robotics", "Databases"]

	#tutorList is a list of Tutor objects. A Tutor object, 't', has the following attributes:
	# t.name - the name of the tutor
	# t.expertise - a list of strings, describing the expertise of the tutor. 

	#For Task 1:
	#Keep in mind that a tutor can only teach a module if the module's topics are a subset of the tutor's expertise. 
	#Furthermore, a tutor can only teach one module a day, and a maximum of two modules over the course of the week.
	#There will always be 25 modules, one for each slot in the week, but the number of tutors will vary.
	#In some problems, modules will cover 2 topics and in others, 3.
	#A tutor will have between 3-8 different expertise fields. 

	#For Task 2 and 3:
	#A tutor can only teach a lab if they have at least one expertise that matches the topics of the lab
	#Tutors can only manage a 'credit' load of 4, where modules are worth 2 and labs are worth 1.
	#A tutor can not teach more than 2 credits per day.

	#You should not use any other methods and/or properties from the classes, these five calls are the only methods you should need. 
	#Furthermore, you should not import anything else beyond what has been imported above. 

	#This method should return a timetable object with a schedule that is legal according to all constraints of task 1.
	def createSchedule(self):
		#Do not change this line
		timetableObj = timetable.Timetable(1)
		
		module_tutor_pairs = self.task_1_generate_module_tutor_pairs(timetableObj)
		self.task_1_can_solve_slot(timetableObj, module_tutor_pairs, 1)

		#Do not change this line
		return timetableObj

	def task_1_generate_module_tutor_pairs(self, time_table):
		"""
		Generate a valid list of module-tutor pairs. For a pair to be valid, the 
		topics of a module must all be in a tutors expertise. This is the as doing it
		in the task_1_can_assign_pair method but I do here to reduce the domain before we 
		start the backtracking.
		"""
		pairs = []
		for module in self.moduleList:
			for tutor in self.tutorList:
				if time_table.canTeach(tutor, module, False):
					pairs.append([module, tutor])

		return self.task_1_sort_domain(pairs)

	def task_1_can_solve_slot(self, time_table, pairs, slot):
		"""
		This is going to be my first attempt traversing the timetable vertically 
		starting on Monday, time slot 1. When time slot 5 is populated, move to the 
		next day, time slot 1.
		"""
		# check if all slots have been filled.
		if slot == 26:
			return True

		day, time_slot = self.task_1_minimum_remaining_value(slot)

		for pair in pairs:
			if self.task_1_can_assign_pair(time_table, day, pair):
				time_table.addSession(day, time_slot, pair[1], pair[0], 'module')
				pruned_pairs = self.task_1_forward_checking(pair, pairs)

				if self.task_1_can_solve_slot(time_table, pruned_pairs, slot + 1):
					return True

				del time_table.schedule[day][time_slot]
		# no solution.
		return False

	def task_1_can_assign_pair(self, time_table, day, pair):
		"""
		Check that the module-tutor pair given does not violate any of the 
		constraints.
		"""       
		# check the tutor is not teaching more than 2 modules.
		tutor_module_count = 0
		for day_slot in time_table.schedule.items():
			for slot in day_slot[1].values():
				# check that the tutor is not already teaching a module on the given day.
				if day_slot[0] == day and slot[0] == pair[1]:
					return False
				if slot[0] == pair[1]:
					tutor_module_count += 1

		if tutor_module_count >= 2:
			return False

		return True

	def task_1_minimum_remaining_value(self, slot):
		"""
		This method chooses the variable with the fewest remaining values. It is 
		effectively starting a Monday slot 1 then slot 2 ... slot 5 then going to 
		Tuesday slot 1 and repeating until Friday slot 5. It does this as the way to
		reduce the domain is by selecting a slot in the same day as the one just 
		selected as we can remove tutors and modules.
		"""
		time_table_slots = {
			'1': ['Monday', 1],
			'2': ['Monday', 2],
			'3': ['Monday', 3],
			'4': ['Monday', 4],
			'5': ['Monday', 5],
			'6': ['Tuesday', 1],
			'7': ['Tuesday', 2],
			'8': ['Tuesday', 3],
			'9': ['Tuesday', 4],
			'10': ['Tuesday', 5],
			'11': ['Wednesday', 1],
			'12': ['Wednesday', 2],
			'13': ['Wednesday', 3],
			'14': ['Wednesday', 4],
			'15': ['Wednesday', 5],
			'16': ['Thursday', 1],
			'17': ['Thursday', 2],
			'18': ['Thursday', 3],
			'19': ['Thursday', 4],
			'20': ['Thursday', 5],
			'21': ['Friday', 1],
			'22': ['Friday', 2],
			'23': ['Friday', 3],
			'24': ['Friday', 4],
			'25': ['Friday', 5]
		}
		slot_meta = time_table_slots[str(slot)] 
		return slot_meta[0], slot_meta[1]

	def task_1_sort_domain(self, pairs):
		"""
		This method returns the elements of the domain in ascending order of the 
		frequecy of their module.
		"""
		# for each module, count the number of elements with that module.
		module_count = {}
		for pair in pairs:
			module_name = pair[0].name
			count = module_count.get(module_name)
			if count is None:
				module_count[module_name] = 1
			else:
				module_count[module_name] += 1

		# sort by least common module count
		return sorted(pairs, key=lambda x: module_count[x[0].name])

	def task_1_forward_checking(self, pair, pairs):
		"""
		Apply forward checking to the given pairs to reduce the domain. by removing 
		all domain elements with the same module that was just selected. 
		"""
		pruned_pairs = [x for x in pairs if x[0] != pair[0]]
		return pruned_pairs

	#Now, we have introduced lab sessions. Each day now has ten sessions, and there is a lab session as well as a module session.
	#All module and lab sessions must be assigned to a slot, and each module and lab session require a tutor.
	#The tutor does not need to be the same for the module and lab session.
	#A tutor can teach a lab session if their expertise includes at least one topic covered by the module.
	#We are now concerned with 'credits'. A tutor can teach a maximum of 4 credits. Lab sessions are 1 credit, module sessiosn are 2 credits.
	#A tutor cannot teach more than 2 credits a day.
	def createLabSchedule(self):
		#Do not change this line
		timetableObj = timetable.Timetable(2)

		module_tutor_pairs = self.task_2_generate_module_tutor_pairs(timetableObj)
		self.task_2_generate_time_table_slot()
		self.task_2_can_solve_slot(timetableObj, module_tutor_pairs, 1)

		#Do not change this line
		return timetableObj

	def task_2_generate_module_tutor_pairs(self, time_table):
		"""
		Generate a valid list of module-tutor pairs. For a pair to be valid, the 
		topics of a module must all be in a tutors expertise. This is the as doing it
		in the task_2_can_assign_pair method but I do here to reduce the domain before we 
		start the backtracking.
		"""
		pairs = []
		for module in self.moduleList:
			for tutor in self.tutorList:
				if time_table.canTeach(tutor, module, False):
					pairs.append(self.ModuleTutorPair(module, tutor, False))
				if time_table.canTeach(tutor, module, True):
					pairs.append(self.ModuleTutorPair(module, tutor, True))
		# sort the pairs by their number of least constraining values. If there is a
		# tie-break, least frequent tutors come first then lab sessions come before 
		# modules as they have less constraints.
		return self.task_2_sort_domain(pairs)

	def task_2_generate_time_table_slot(self):
		"""
		This method generated the dict for the timetable slots. I just call this 
		rather than manualy writing out the dict.
		"""
		days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
		counter = 1
		for day in days:
			for i in range(1, 11):
				self.TIME_TABLE_SLOTS[str(counter)] = [day, i]
				counter += 1
		
	def task_2_can_solve_slot(self, time_table, pairs, slot):
		"""
		This is going to be my first attempt traversing the timetable vertically 
		starting on Monday, time slot 1. When time slot 10 is populated, move to 
		the next day, time slot 1.
		"""
		# check if all slots have been filled.
		if slot == 51:
			return True

		day, time_slot = self.task_2_minimum_remaining_value(slot)

		for pair in pairs:
			if self.task_2_can_assign_pair(time_table, day, pair):
				time_table.addSession(day, time_slot, pair.tutor, pair.module, pair.session_type)
				pruned_pairs = self.task_2_forward_checking(time_table, pair, pairs)

				if self.task_2_can_solve_slot(time_table, pruned_pairs, slot + 1):
					return True

				del time_table.schedule[day][time_slot]
		# no solution.
		return False

	def task_2_can_assign_pair(self, time_table, day, pair):
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

	def task_2_minimum_remaining_value(self, slot):
		"""
		This method chooses the variable with the fewest remaining values. It is 
		effectively starting a Monday slot 1 then slot 2 ... slot 10 then going to 
		Tuesday slot 1 and repeating until Friday slot 10. It does this as the way to
		reduce the domain is by selecting a slot in the same day as the one just 
		selected as we can remove tutors and modules.
		"""   
		slot_meta = self.TIME_TABLE_SLOTS[str(slot)] 
		return slot_meta[0], slot_meta[1]

	def task_2_sort_domain(self, pairs):
		"""
		This method is going to sort and return the elements of the domain.
		"""
		# for each module, count the number of elements with that module.
		module_count = {}
		tutor_count = {}
		for pair in pairs:
			m_count = module_count.get(pair.module_name)
			if m_count is None:
				module_count[pair.module_name] = 1
			else:
				module_count[pair.module_name] += 1
			t_count = tutor_count.get(pair.tutor.name)
			if t_count is None:
				tutor_count[pair.tutor.name] = 3 - pair.credit
			else:
				tutor_count[pair.tutor.name] += 3 - pair.credit

		# sort by least common module count
		return sorted(pairs, key=lambda x: (
			module_count[x.module_name], tutor_count[x.tutor.name], not x.is_lab, x.module.name
		))

	def task_2_forward_checking(self, time_table, pair, pairs):
		"""
		Apply forward checking to the given pairs to reduce the domain. by removing 
		all domain elements with the same module that was just selected. Will also 
		check that the tutor of the pair given has not reached their weekly credit
		limit.
		"""
		total_credits = 0
		for day_slots in time_table.schedule.items():
			for slot in day_slots[1].values():
				if slot[0] == pair.tutor:
					credit = 1 if slot[2] == 'lab' else 2
					total_credits += credit

		if total_credits >= 4:
			pruned_pairs = [
				x for x in pairs if x.tutor != pair.tutor and not (
					x.module == pair.module and x.is_lab == pair.is_lab
				)
			]
		else:
			pruned_pairs = [
				x for x in pairs if not (x.module == pair.module and x.is_lab == pair.is_lab)
			]
			
		return pruned_pairs

	class ModuleTutorPair:
		"""
		This class is for the storing of elements of the domain. It comes with a 
		few helper methods that are used in several of the backtracking methods.
		"""
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
		def module_name(self):
			module_name = self.module.name
			module_name = module_name + '_l' if self.is_lab else module_name
			return module_name

	#It costs £500 to hire a tutor for a single module.
	#If we hire a tutor to teach a 2nd module, it only costs £300. (meaning 2 modules cost £800 compared to £1000)
	#If those two modules are taught on consecutive days, the second module only costs £100. (meaning 2 modules cost £600 compared to £1000)

	#It costs £250 to hire a tutor for a lab session, and then £50 less for each extra lab session (£200, £150 and £100)
	#If a lab occurs on the same day as anything else a tutor teaches, then its cost is halved. 

	#Using this method, return a timetable object that produces a schedule that is close, or equal, to the optimal solution.
	#You are not expected to always find the optimal solution, but you should be as close as possible. 
	#You should consider the lecture material, particular the discussions on heuristics, and how you might develop a heuristic to help you here. 
	def createMinCostSchedule(self):
		#Do not change this line
		timetableObj = timetable.Timetable(3)

		module_tutor_pairs = self.task_2_generate_module_tutor_pairs(timetableObj)
		self.task_2_generate_time_table_slot()
		self.task_2_can_solve_slot(timetableObj, module_tutor_pairs, 1)
		timetableObj = self.simulated_annealing(timetableObj)

		#Do not change this line
		return timetableObj

	def simulated_annealing(self, time_table, iterations=100000):
		"""
		This method will do simulated_annealing to try find a better, or hopefully
		optimal solution. It will randomly swap two slots.
		"""
		def sigmoid(gamma):
			if gamma < 0:
				return 1 - 1 / (1 + math.exp(gamma))
			return 1 / (1 + math.exp(-gamma))

		days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

		initial = timetable.Timetable(3)
		for day_slots in time_table.schedule.items():
			for slot, value in day_slots[1].items():
				initial.schedule[day_slots[0]][slot] = time_table.schedule[day_slots[0]][slot]

		best_time_table = timetable.Timetable(3)
		time_table.scheduleChecker(self.tutorList, self.moduleList)
		lowest_cost = time_table.cost

		for k in range(1, iterations):
			T = iterations / k + 1

			if T == 0:
				break

			# randomly swap two slots
			day1 = days[random.randint(0, 4)]
			day2 = days[random.randint(0, 4)]
			slot1 = random.randint(1, 10)
			slot2 = random.randint(1, 10)
			module1 = time_table.getSession(day1, slot1)
			module2 = time_table.getSession(day2, slot2)
			time_table.addSession(day1, slot1, module2[0], module2[1], module2[2])
			time_table.addSession(day2, slot2, module1[0], module1[1], module1[2])

			if time_table.scheduleChecker(self.tutorList, self.moduleList):
				if time_table.cost < lowest_cost:
					lowest_cost = time_table.cost
					for day_slots in time_table.schedule.items():
						for slot, value in day_slots[1].items():
							best_time_table.schedule[day_slots[0]][slot] = time_table.schedule[day_slots[0]][slot]
				elif sigmoid((time_table.cost - lowest_cost) / T) < random.random():
					time_table.addSession(day1, slot1, module1[0], module1[1], module1[2])
					time_table.addSession(day2, slot2, module2[0], module2[1], module2[2])

		if best_time_table.scheduleChecker(self.tutorList, self.moduleList):
			return best_time_table
		initial.scheduleChecker(self.tutorList, self.moduleList)
		return initial

	#This simplistic approach merely assigns each module to a random tutor, iterating through the timetable. 
	def randomModSchedule(self, timetableObj):

		sessionNumber = 1
		days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
		dayNumber = 0
		for module in self.moduleList:
			tut = self.tutorList[random.randrange(0, len(self.tutorList))]

			timetableObj.addSession(days[dayNumber], sessionNumber, tut, module, "module")

			sessionNumber = sessionNumber + 1

			if sessionNumber == 6:
				sessionNumber = 1
				dayNumber = dayNumber + 1

	#This simplistic approach merely assigns each module and lab to a random tutor, iterating through the timetable.
	def randomModAndLabSchedule(self, timetableObj):

		sessionNumber = 1
		days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
		dayNumber = 0
		for module in self.moduleList:
			tut = self.tutorList[random.randrange(0, len(self.tutorList))]

			timetableObj.addSession(days[dayNumber], sessionNumber, tut, module, "module")

			sessionNumber = sessionNumber + 1

			if sessionNumber == 11:
				sessionNumber = 1
				dayNumber = dayNumber + 1

		for module in self.moduleList:
			tut = self.tutorList[random.randrange(0, len(self.tutorList))]

			timetableObj.addSession(days[dayNumber], sessionNumber, tut, module, "lab")

			sessionNumber = sessionNumber + 1

			if sessionNumber == 11:
				sessionNumber = 1
				dayNumber = dayNumber + 1


























