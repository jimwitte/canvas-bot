# pass CANVAS_COURSE_ID, CANVAS_GROUPSET_NAME as environment variables

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

    CANVAS_COURSE_ID = os.environ.get("CANVAS_COURSE_ID", None)
    CANVAS_GROUPSET_NAME = os.environ.get('CANVAS_GROUPSET_NAME', 'Section Groups')

    if not all([API_URL, API_KEY, CANVAS_COURSE_ID, CANVAS_GROUPSET_NAME]):
        print("Required env variable(s) not found.")
        exit(1)

    canvas = Canvas(API_URL, API_KEY)
    course = canvas.get_course(CANVAS_COURSE_ID)

    sanitized_course_code = course.course_code.replace("/", "_")

    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=logging.WARNING,
        handlers=[
            logging.FileHandler(f"{sanitized_course_code}.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    logging.info(f"starting update section groups...")

    groupset_id = None

    group_categories = course.get_group_categories()
    for groupset in group_categories:
        if groupset.name == CANVAS_GROUPSET_NAME:
            groupset_id = groupset.id
            break

    if groupset_id is None:
        # Assuming course.create_groupset(name) creates a new groupset and returns its ID
        new_groupset = course.create_group_category(CANVAS_GROUPSET_NAME)
        groupset_id = new_groupset.id
        if groupset_id:
            logging.info(f"Created new groupset with name: {CANVAS_GROUPSET_NAME}.")
        else:
            logging.error(f"Failed to create groupset with name: {CANVAS_GROUPSET_NAME}.")
            exit(1)

        groupset = canvas.get_group_category(groupset_id)

        logging.warning(f"Checking/changing section groupset: {groupset} course: {course.course_code}")

        groups = groupset.get_groups()

        if not groups:
            # create groups if needed
            sections = course.get_sections()
            for section in sections:
                sectionid = section.id
                group_name = section.name
                group = groupset.create_group(name=group_name, description=section.id)

        groups = groupset.get_groups()

        for group in groups:
            # update group membership
            memberships = group.get_memberships()
            time.sleep(.25)
            group_members = set([int(member.user_id) for member in memberships])
            group_description = group.description
            if group_description != None:
                sectionid = int(group.description)  #sectionid stored in group description field
                section = course.get_section(sectionid)
                enrollments = section.get_enrollments()
                section_members = set([int(enrollment.user_id) for enrollment in enrollments
                                    if enrollment.type == 'StudentEnrollment' and enrollment.enrollment_state == 'active'])
                for user_id in (section_members - group_members):
                    user = course.get_user(user_id)
                    logging.warning(f'added {user} to group: {group.name}')
                    group.create_membership(user_id)
                    time.sleep(.25)
