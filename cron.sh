#!/usr/bin/env bash

cd $(dirname "${BASH_SOURCE[0]}")


# development sandbox course
export CANVAS_COURSE_ID=793
export CANVAS_GROUPSET_NAME="test section groupset"
python3 user_set_section_only.py
python3 update_section_groups.py
