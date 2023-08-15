# intern grading report

if __name__ == "__main__":

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
        logging.warning(f"Include assignment {assignment.name} in dashboard")
        includedAssignments.append(assignment)
    if not includedAssignments:
        logging.error('No assignments matched include pattern(s).')
        exit(1)

    dashboardData = {}
    sections = course.get_sections()
    for section in sections:
        dashboardData[section.name] = {}
        for assignment in includedAssignments:
            dashboardData[section.name][(assignment.id)] = {
                    'numStudents': 0,
                    'numEntered': 0,
                    'assignmentName': assignment.name
                }

        time.sleep(.25)
        logging.warning(f"Get submissions for section {section.name}")
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
            if submission.user['name'] != 'Test Student':
                dashboardData[section.name][id]['numStudents'] += 1
            if (submission.entered_grade != None or submission.excused == True) and submission.user['name'] != 'Test Student':
                dashboardData[section.name][id]['numEntered'] += 1
    
    template = jinjaEnv.get_template('submission_report.html.j2')
    pageContent = template.render(submission_report=dashboardData,targetAssignmentIDs=includedAssignments)

    publishPageTitle = f'{course.course_code} Attendance Submission Dashboard'
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
