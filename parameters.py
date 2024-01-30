PASSWORD_MYSQL = ''
PASSWORD_POSTGRES = '909932'
USER_MYSQL = 0
USER_POSTGRES = 'maximilianotombolini'

from datetime import time, timedelta

FORM_DATE_FORMAT = "%Y-%m"
SCHEDULE_RECORDS_DATE_FORMAT = "%m-%Y"
SCHEDULE_RECORDS_TIME_FORMAT = "%H:%M:%S"

STANDARD_CHECK_IN_WEEKDAY = time(9, 0, 0)
STANDARD_CHECK_IN_SATURDAY = time(10, 0, 0)
STANDARD_CHECK_OUT_WEEKDAY = time(18, 30, 0)
STANDARD_CHECK_OUT_SATURDAY = time(14, 0, 0)
STANDARD_LUNCH_BREAK_START = time(14, 0, 0)
STANDARD_LUNCH_BREAK_DURATION = timedelta(minutes=45)
STANDARD_TOTAL_HOURS_WORKED_WEEKDAY = timedelta(hours=8, minutes=45)
STANDARD_TOTAL_HOURS_WORKED_SATURDAY = timedelta(hours=4)