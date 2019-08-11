from bs4 import BeautifulSoup
import urllib
import re

class Course:
	def __init__(self, name, has_alt_days=False):
		self.name = name
		self.meeting_list = []
		self.has_alt_days = has_alt_days

	def add(self, meeting):
		self.meeting_list.append(meeting)

	def has_conflict(self, day, start_time, end_time):
		conflict_set = CourseConflict(self)

		conflict_exists = False

		for item in self.meeting_list:
			conflict = item.does_conflict(day, start_time, end_time) 

			if conflict != None:
				conflict_exists = True
				conflict_set.conflicting_meetings.append(conflict)

		if conflict_exists:
			return conflict_set
		else:
			return None	

	def print_me(self):
		print(self.name)

		for item in self.meeting_list:
			item.print_me()

		if self.has_alt_days:
			print("Note - class has alternate times for certain dates. Check Academic Timetable for details.")

class CourseConflict:
	def __init__(self, course):
		self.course = course
		self.conflicting_meetings = []

	def print_me(self):
		print(self.course.name)

		for item in self.conflicting_meetings:
			item.print_me();

		if self.course.has_alt_days:
			print("Note - class has alternate times for certain dates. Check Academic Timetable for details.")

class CourseMeeting:
	def __init__(self, classtype="", days="", start_time=-1, end_time=-1):
		self.classtype = classtype
		self.days = days
		self.start_time = start_time
		self.end_time = end_time

	def does_conflict(self, event_day, event_start_time, event_end_time):
		same_day = self.days.__contains__(event_day)

		same_time = (event_start_time >= self.start_time and event_start_time < self.end_time) or (event_end_time > self.start_time and event_end_time <= self.end_time)

		if same_day and same_time:
			return self 
		else:
			return None

	def print_me(self):
		print(self.classtype + " " + self.days + " " + str(self.start_time) + "-" + str(self.end_time))

def parse_start_time(time_string):
	return int(time_string[0:4])

def parse_end_time(time_string):
	return int(time_string[5:9])

def add_alt_days(classtype, course, days, times):
	for i in range(0, len(days)):
		new_meeting = CourseMeeting()

		new_meeting.classtype = classtype

		if days[i] == "M":
			new_meeting.days = "M     " 
		elif days[i] == "T":
			new_meeting.days = " T    "
		elif days[i] == "W":
			new_meeting.days = "  W   " 
		elif days[i] == "R":
			new_meeting.days = "   R  "
		elif days[i] == "F":
			new_meeting.days = "    F "
		else:
			return False

		new_meeting.start_time = parse_start_time(times[ 9*i : 9*(i+1) ])
		new_meeting.end_time = parse_end_time(times[ 9*i : 9*(i+1) ])

		course.add(new_meeting)

	return True

def obtain_course_data():
	url = 'https://dalonline.dal.ca/PROD/fysktime.P_DisplaySchedule?s_term=202010,202020&s_subj=CSCI&s_district=100'

	response = urllib.urlopen(url).read()

	soup = BeautifulSoup(response, "lxml")

	tables = soup.findAll('table', 'dataentrytable')

	rows = list(tables[1].findAll('tr'))

	count = 0

	all_courses = []

	for item in rows:
		if item.has_attr('valign'):
			#add new course to end of list when we see a title
			all_courses.append(Course(item.b.text, False))
		
		else:
			cols_lec = list(item.findAll('td', class_="dettl")) 
			cols_lab = list(item.findAll('td', class_="dettb"))
			cols_tut = list(item.findAll('td', class_="dettt"))

			cols = cols_lec + cols_lab + cols_tut

			if len(cols) > 2:
				new_meeting = CourseMeeting()

				new_meeting.classtype = cols[3].text

				days = ""

				has_alt_days = False

				for i in range(6,11):
					day = cols[i].p.text

					if len(day) > 1:
						has_alt_days = add_alt_days(new_meeting.classtype, all_courses[len(all_courses)-1], day, cols[11].text)
					else:
						new_meeting.days = new_meeting.days + day	

				if not has_alt_days:
					new_meeting.start_time = parse_start_time(cols[11].text)
					new_meeting.end_time = parse_end_time(cols[11].text)
					
					all_courses[len(all_courses)-1].add(new_meeting)
				else:
					all_courses[len(all_courses)-1].has_alt_days = True

				has_alt_days = False

	return all_courses

print("TODO: ADD OTHER PAGE. CURRENTLY ONLY GRABS PAGE 1 OF TIMETABLE.")

course_data = obtain_course_data()

day_input = raw_input("Enter day of week of event: ").upper()

while day_input != "MONDAY" and day_input != "TUESDAY" and day_input != "WEDNESDAY" and day_input != "THURSDAY" and day_input != "FRIDAY":
	day_input = raw_input("Enter day of week of event: ").upper()

day_letter = day_input[0]

time_string = raw_input("Enter timespan of event in format '0000-0000': ")

while re.search("([0-1][0-9]|2[0-3])([0-5][0-9])-([0-1][0-9]|2[0-3])([0-5][0-9])", time_string) == None:
	time_string = raw_input("Enter timespan of event in format '0000-0000': ")

event_start_time = parse_start_time(time_string)
event_end_time = parse_end_time(time_string)

conflict_list = []

for item in course_data:
	conflict_list.append(item.has_conflict(day_letter, event_start_time, event_end_time))

if len(conflict_list) > 0:
	print("CONFLICTS FOUND:")
	for item in conflict_list:
		if item != None:
			item.print_me()
			print("")
else:
	print("NO CONFLICTS FOUND.")


