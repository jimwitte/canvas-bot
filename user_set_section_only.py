# pass CANVAS_COURSE_ID as environment variable


if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    import sys
    from canvasapi import Canvas
    import time
    import logging

    # connection info from .env file
    load_dotenv()
    API_URL = os.environ.get('API_URL', None)
    API_KEY = os.environ.get('API_KEY', None)
   

    # set environment before run
    CANVAS_COURSE_ID = os.environ.get('CANVAS_COURSE_ID', None)
    CANVAS_SECTION_ONLY = os.environ.get('CANVAS_SECTION_ONLY', True)

    if not all([API_URL, API_KEY, CANVAS_COURSE_ID]):
        print("Required env variable(s) not found.")
        exit(1)

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

    logging.warning(f"Checking/changing enrollments to section-only for: {course}")

    sections = course.get_sections()
    section_limited = CANVAS_SECTION_ONLY  # desired state, "true" by default

    for section in sections:
        enrollments = section.get_enrollments()
        for enrollment in enrollments:
            if (not enrollment.limit_privileges_to_course_section == section_limited
                    and enrollment.type == 'StudentEnrollment'
                    and enrollment.enrollment_state == 'active'):
                time.sleep(.25)
                section.enroll_user(
                    user=enrollment.user['id'],
                    enrollment={
                        'limit_privileges_to_course_section': section_limited
                    }
                )
                logging.warning(
                    f"{enrollment.user['name']} {enrollment.user['id']} changed section-only to {section_limited}"
                )