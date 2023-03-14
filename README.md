Canvas Bot
==========

git clone git@github.com:jimwitte/canvas-bot.git

Cron Task
----------
@hourly /home/ubuntu/canvas-bot/cron.sh >> /dev/null 2>&1

cron.sh Environment Variables
---------------------
* CANVAS_COURSE_ID
* CANVAS_GROUPSET_NAME

.env Credentials
----------------
* API_URL
* API_KEY
