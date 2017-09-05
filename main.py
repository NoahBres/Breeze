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
	},

	'semester2' : {
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

''' 
Info:

classes
	category summary
		category
		weight
		percent
	category
		assignment
			due date
			recevied
			max
			weight
			grade
			note
'''
classes = {
	'category_summary': [
		
	],

	'category': [
	]
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

### Teacher/Class Info ###
for sec in gradeSection:
 	#print(sec.find_all("td"))
	for className in sec.find_all("td"):
		if 'title' in className.attrs:
			if counter % 2 == 0:
				schedule['semester1']['classes'].append(className.attrs['title'])
			else:
				schedule['semester1']['teachers'].append(className.attrs['title'])

			counter += 1

### Period Info ###
for sec in gradeSection:
	for period in sec.find_all('td', { "title": "", "align": "" }):
		schedule['semester1']['periods'].append(period.text)

### Grade Info ###
for sec in gradeSection:
	for i, boop in enumerate(sec.find_all('td', { "align": "right" })):
		if(i + 5 % 5 == 0):
			schedule['semester1']['quarter1'].append(boop.findChildren()[0].text)
			#print(boop.findChildren()[0].text)
		if(i + 5 % 5 == 1):
			schedule['semester1']['quarter2'].append(boop.findChildren()[0].text)
		if(i + 5 % 5 == 2):
			schedule['semester1']['exams'].append(boop.text)
		if(i + 5 % 5 == 3):
			schedule['semester1']['total'].append(boop.text)
		if(i + 5 % 5 == 4):
			schedule['semester1']['final'].append(boop.text)

### Class Grade Info ###
#apparently wrkgrpd=1 is 1st quarter and wrkgrpd=2 is 2nd quarter. This needs to best tested with others quarters
SMURFID = redirectURL[32:64]

grPdReqUrlStart = "https://dashboard.okaloosaschools.com/parentportal/DP400.pgm?task=setgrpd&SmurfId="
grPdReqUrlEnd = "&timestamp=&wrkgrpd=1"

grPdReqUrl = grPdReqUrlStart + SMURFID + grPdReqUrlEnd
print(grPdReqUrl)

schlReqStart = "https://dashboard.okaloosaschools.com/parentportal/DP400.pgm?task=setschl&SmurfId="
schlReqEnd = "&timestamp=&wrkschl=0211"

schlReqUrl = schlReqStart + SMURFID + schlReqEnd
print(schlReqUrl)

for sec in gradeSection:
	for i, boop in enumerate(sec.find_all('td', { "align": "right" })):
		if(i + 5 % 5 == 0):
			# browser.follow_link(boop.findChildren()[0])
			browser.session.get(grPdReqUrl)
			browser.session.get(schlReqUrl)
			browser.open('https://dashboard.okaloosaschools.com/parentportal/PP200.pgm?SMURFID=' + SMURFID)
			print(browser.parsed)
			
			debugfile = open("debug.html", "a")
			debugfile.write("\n\n\n" + str(browser.parsed))
			debugfile.close()

			browser.back()

			# print(boop.findChildren()[0])


print("\nStudent data:")
pprint(studentInfo)
print("\nSchedule:")
pprint(schedule)


# javascript:Send_Set_GrPd_Request('1');
# 	Send_Set_Schl_Request('0211');
# 	lnkProc('https://dashboard.okaloosaschools.com/parentportal/', '53753817031820170902122482973922', 
# 	'DP400', '', '', 'PP200', 
# 	'', '1001350', '001', '4602020856', 
# 	'495034725');

# https://dashboard.okaloosaschools.com/parentportal/DP400.pgm?SMURFID=53753817031820170902122482973922&rand=817017318

# https://dashboard.okaloosaschools.com/parentportal/PP200.pgm?SmurfId=53753817031820170902122482973922&rand=495034725