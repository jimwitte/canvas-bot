import datetime as dt
import time
import os
import sys
from canvasapi import Canvas
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
import logging

def startsWith(str,checklist=[]):
    found = False
    for c in checklist:
        if str.startswith(c):
            found = True
    return found

def addToReport(canvasUser,canvasSection,canvasAssignment,fieldName,report):
    """ add absence or excused to report data """
    if not canvasUser['id'] in report:
        report[canvasUser['id']] = {
            'name': canvasUser['name'],
            'login': canvasUser['login_id'],
            'section': canvasSection.name,
            'absences': [],
            'excused': []
        }
    report[canvasUser['id']][fieldName].append(canvasAssignment['name'])

def addToSummary(canvasAssignment,fieldName,summary):
    if not canvasAssignment['id'] in summary:
        summary[canvasAssignment['id']] = {
            'numAbsent': 0,
            'numExcused': 0,
            'numSubmitted': 0,
            'name': canvasAssignment['name']
        }
    summary[canvasAssignment['id']][fieldName] += 1

def assignmentSort(assignmentToSort):
    return assignmentToSort.name

def studentSort(studentDict):
    return len(studentDict['absences']) + len(studentDict['excused'])/20

# jinja2 setup
fileLoader = FileSystemLoader('templates')
jinjaEnv = Environment(loader=fileLoader, extensions=['jinja2_time.TimeExtension'])

load_dotenv()
API_URL = os.environ.get('API_URL', None)
API_KEY = os.environ.get('API_KEY', None)
CANVAS_COURSE_ID = os.environ.get('CANVAS_COURSE_ID', None)
CANVAS_PUBLISH_COURSE_ID = os.environ.get('CANVAS_PUBLISH_COURSE_ID', None)

if not all([API_URL, API_KEY, CANVAS_COURSE_ID]):
    print("Required environment variable not set.")
    exit(1)

if CANVAS_PUBLISH_COURSE_ID == None:
    CANVAS_PUBLISH_COURSE_ID = CANVAS_COURSE_ID

# include assignments with names that start with these strings
includeAssignmentPatterns = ['Att','att','Week','week']

canvas = Canvas(API_URL, API_KEY)
course = canvas.get_course(CANVAS_COURSE_ID)

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.WARNING,
    handlers=[
        logging.FileHandler(f"{course.course_code}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

assignments = course.get_assignments()
includedAssignments = []
for assignment in assignments:
    if startsWith(assignment.name, includeAssignmentPatterns):
        logging.warning(f"Include assignment {assignment.name} in absent report")
        includedAssignments.append(assignment)
if not includedAssignments:
    logging.error('No assignments matched include pattern(s).')
    exit(1)

includedAssignments.sort(key=assignmentSort)
reportData = {}
summaryData = {}
sections = course.get_sections()
for section in sections:
    if "Test Section" not in section.name:
        logging.warning(f"Getting absences & excused for section {section.name}")
        submissions = section.get_multiple_submissions(
            student_ids='all',
            assignment_ids=[i.id for i in includedAssignments],
            enrollment_state='active',
            state_based_on_date=True,
            include=['assignment','user']
            )

        for submission in submissions:
            submissionAssignment = submission.assignment
            id = submissionAssignment['id']
            if submission.entered_grade == '0' and submission.user['name'] != 'Test Student':
                addToReport(submission.user,section,submission.assignment,'absences',reportData)
                addToSummary(submission.assignment,'numAbsent',summaryData)
                # logging.warning(f"Found grade=0 for {submission.user['name']} in section {section.name}")
            if (submission.excused == True) and submission.user['name'] != 'Test Student':
                addToReport(submission.user,section,submission.assignment,'excused',reportData)
                addToSummary(submission.assignment,'numExcused',summaryData)
                # logging.warning(f"Found excused for {submission.user['name']} in section {section.name}")
            if (submission.entered_grade != None or submission.excused == True) and submission.user['name'] != 'Test Student':
                addToSummary(submission.assignment,'numSubmitted',summaryData)
    
# convert reportData to list for sorting
reportList = []
for student in reportData:
    reportList.append(reportData[student])

reportList.sort(reverse=True,key=studentSort)

template = jinjaEnv.get_template('absent_report.html.j2')
pageContent = template.render(absent_report=reportList,summary_report=summaryData)

publishPageTitle = f'{course.course_code} Absent & Excused Report'
publishCourse = canvas.get_course(CANVAS_PUBLISH_COURSE_ID)
publishCoursePages = publishCourse.get_pages(search_term=publishPageTitle)

publishPage = None
for page in publishCoursePages:
    if page.title == publishPageTitle:
        publishPage = page

if publishPage == None:
    logging.warning(f"Create page {publishPageTitle}")
    publishCourse.create_page(
        wiki_page={
        'title': publishPageTitle,
        'editing_roles': 'teachers',
        'published': False,
        'body': pageContent
        }
    )
else:
    logging.warning(f"update page {publishPageTitle}")
    publishPage.edit(
        wiki_page={
        'body': pageContent
        }
    )
