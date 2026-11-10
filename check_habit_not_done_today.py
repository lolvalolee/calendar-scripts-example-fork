"""Habit not done today — request a report on desktop, notify elsewhere.

Every value here is a **constant of this script**, not a parameter: the backend
does not pass any of it through ``handler_extra_data``.

Desktop gets a ``notification_habit_ask_complish`` request (the user picks the
status and time in the client); a plain text message goes to the second
transport for a nudge. The report date is **today in the user's timezone**, not
in the script host's zone.
"""
import sys

from calendar_scripts.models import (
    Habit,
    Message,
    NotificationTransport,
    Profile,
)

sys.path.append('./')

#: Name of the habit to check. The server-side ``?search=`` does not work on
#: encrypted fields, so the habit is matched on the client.
HABIT_NAME = 'My habit'

#: Text of the plain text reminder.
REMINDER = 'The habit has not been done today.'

#: Title of the desktop card that asks for a habit report.
REPORT_TITLE = 'Did you do the habit today?'


def handle():
    matches = [habit for habit in Habit.objects() if habit.name.value == HABIT_NAME]
    if not matches:
        print(f'check_habit_not_done_today: habit not found: {HABIT_NAME}')
        return

    habit = matches[0]

    if (habit.count_today or 0) >= 1:
        return

    report_date = Profile.current().today().isoformat()

    Message.habit_report_request(
        REPORT_TITLE,
        report_date,
        NotificationTransport.desktop(),
    )
    Message.simple_message(REMINDER, NotificationTransport.telegram())
