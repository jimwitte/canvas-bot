#!/usr/bin/env bash

cd $(dirname "${BASH_SOURCE[0]}")

##### FALL 2023 #####

# LAS 100: 36793
# LAS 101: 37183
# LAS 102: 37182
# LAS 122: 36270
# LAS 399: 37185

# LAS 100 FALL 2023
export CANVAS_COURSE_ID=36793
export CANVAS_GROUPSET_NAME='Section Groups'
python3 user_set_section_only.py
python3 update_section_groups.py

# LAS 101 FALL 2023
export CANVAS_COURSE_ID=37183
export CANVAS_GROUPSET_NAME='Section Groups'
# publish reports to LAS399
export CANVAS_PUBLISH_COURSE_ID=37185
python3 user_set_section_only.py
python3 update_section_groups.py
python3 intern_grade_report.py
python3 absent_report.py

# LAS 102 FALL 2023
export CANVAS_COURSE_ID=37182
export CANVAS_GROUPSET_NAME='Section Groups'
python3 user_set_section_only.py
python3 update_section_groups.py

# LAS 122 FALL 2023
export CANVAS_COURSE_ID=36270
export CANVAS_GROUPSET_NAME='Section Groups'
python3 user_set_section_only.py
python3 update_section_groups.py

# LAS 399 FALL 2023
export CANVAS_COURSE_ID=37185
export CANVAS_GROUPSET_NAME='Section Groups'
python3 user_set_section_only.py
python3 update_section_groups.py


##### SPRING 2023 #####
# # development sandbox course
# export CANVAS_COURSE_ID=793
# export CANVAS_GROUPSET_NAME='Section Groups'
# python3 user_set_section_only.py
# python3 update_section_groups.py

# # LAS 399 SPRING 2023
# export CANVAS_COURSE_ID=35719
# export CANVAS_GROUPSET_NAME='Section Groups'
# python3 user_set_section_only.py
# #python3 update_section_groups.py


######### Fall 2022 ###############

# LAS 100 FALL 2022
#export CANVAS_COURSE_ID=22556
#export CANVAS_GROUPSET_NAME='Section Groups'
#python3 user_set_section_only.py
#python3 update_section_groups.py

# LAS 101 FALL 2022
#export CANVAS_COURSE_ID=22598
#export CANVAS_GROUPSET_NAME='Section Groups'
    # publish grade report and absent report to LAS399
#export CANVAS_PUBLISH_COURSE_ID=22602
#python3 user_set_section_only.py
#python3 update_section_groups.py
#python3 intern_grade_report.py
#python3 absent_report.py

# LAS 399 FALL 2022
#export CANVAS_COURSE_ID=22602
#export CANVAS_GROUPSET_NAME='Section Groups'
#python3 user_set_section_only.py
#python3 update_section_groups.py

# LAS 102 FALL 2022
#export CANVAS_COURSE_ID=22599
#export CANVAS_GROUPSET_NAME='Section Groups'
#python3 user_set_section_only.py
#python3 update_section_groups.py

# LAS 122 FALL 2022
#export CANVAS_COURSE_ID=21009
#export CANVAS_GROUPSET_NAME='Section Groups'
#python3 user_set_section_only.py
#python3 update_section_groups.py
