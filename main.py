# TODO: redo scraping info that uses substring so it isn't as ugly

import re
from robobrowser import RoboBrowser

#temporary for debugging
from pprint import pprint

baseURL = 'https://dashboard.okaloosaschools.com'
loginURL = '/parentportal/PP000.pgm'

loginCred = {
	'wrkuser'  : '',
	'wrkpasswd': ''
}

studentInfo = {
	'birthdate': '',
	'gender'   : '',
	'race'     : '',

	'school'  : '',
	'grade'   : '',
	'date'    : '',
	'homeroom': '',

	'gpa-weight'  : '',
	'gpa-noweight': ''
}

schedule = {
	'semester1': {
		'classes' : [],
		'periods' : [],
		'teachers': [],
		'quarter1': [],
		'quarter2': [],
		'exams'   : [],
		'total'   : [],
		'final'   : []
	}
}

### Read Credential File ###
configFile = open(".config", "r")
for line in configFile.readlines():
	splitted = line.split(":")

	if splitted[0] == "wrkuser":
		loginCred["wrkuser"] = splitted[1].replace('\n', '')
	elif splitted[0] == "wrkpasswd":
		loginCred["wrkpasswd"] = splitted[1].replace('\n', '')

configFile.close()

print(loginCred)

### Init ###
browser = RoboBrowser(history=True, parser="html.parser")

### Login ###
browser.open(baseURL + loginURL)
loginForm = browser.get_form(enctype=re.compile(r'multipart/form-data'))

loginForm['wrkuser'].value = loginCred['wrkuser']
loginForm['wrkpasswd'].value = loginCred['wrkpasswd']

browser.submit_form(loginForm)

### Redirect ###

body = browser.select('body')
redirectURL = body[0].get('onload')

redirectURL = redirectURL[18:-3]

browser.open(baseURL + redirectURL)

### Logged In ###
# print(browser.parsed)

# debugfile = open("debug.html", "w")
# debugfile.write(str(browser.parsed))
# debugfile.close()

### Student Info ###
sideBar = browser.find_all("table", class_="classarea")[0].find_all("td")

studentInfo['birthdate'] = str(sideBar[1]).replace('<td align="left"><u><b>Birthdate</b></u>: ', "")[:5]#[42:47]
studentInfo['gender'] = str(sideBar[1])[71:-5]
studentInfo['race'] = str(sideBar[2])[47:].replace('</td>', "")
studentInfo['school'] = str(sideBar[4])[39:].replace('</td>', '').strip()
studentInfo['grade'] = str(sideBar[5])[38:-37]
studentInfo['date'] = str(sideBar[5])[-14:-5]
studentInfo['homeroom'] = str(sideBar[7])[41:-5]

### Grade Stuff ###
gradeSection = browser.find_all("table", class_="classarea")[3].find_all("tr")
gradeSection = gradeSection[2:-1]

counter = 2

### Teacher Info ###
for sec in gradeSection:
 	#print(sec.find_all("td"))
	for className in sec.find_all("td"):
		if 'title' in className.attrs:
			if counter % 2 == 0:
				schedule['semester1']['classes'].append(className.attrs['title'])
			else:
				schedule['semester1']['teachers'].append(className.attrs['title'])

			counter += 1
			#print(className.attrs['title'])

#print(gradeSection)
#print(str(gradeSection[0]))

print("\nStudent data:")
pprint(studentInfo)
print("\nSchedule:")
pprint(schedule)
#print(str(sideBarElements[7])[41:-5])