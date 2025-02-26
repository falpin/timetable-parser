import parser
from datetime import datetime
import pytz
import json
import requests
import time
import config

api_key = config.API_KEY[0]

headers = {
    'X-API-Key': api_key,
    'Content-Type': 'application/json'
}


def now_time():
    now = datetime.now()
    tz = pytz.timezone('Europe/Moscow')
    now_moscow = now.astimezone(tz)
    current_time = now_moscow.strftime("%H:%M:%S")
    current_date = now_moscow.strftime("%Y.%m.%d")
    return current_date, current_time

def now_week():
    now = datetime.now()
    tz = pytz.timezone('Europe/Moscow')
    now_moscow = now.astimezone(tz)
    week_number = now_moscow.isocalendar()[1]
    return week_number


def send_courses():
    for complex_name in parser.COMPLEX:
        courses = json.loads(parser.get_courses(parser.COMPLEX[complex_name]))
        if courses == {}: return
        data["complex"] = complex_name
        response = requests.post('https://falpin.ru/api/save_groups', json=data, headers=headers)
        date, time = now_time()
        print(f"{date} {time}:    Сохранение групп: {json.loads(response.text)}")

def send_schedule():
    data = {}
    data["week"] = now_week()
    for complex_name in parser.COMPLEX:
        courses = json.loads(parser.get_courses(parser.COMPLEX[complex_name]))
        if courses == {}: return
        for course in courses:
            groups = courses[course]
            for group in groups:
                group_url = groups[group]
                schedule = json.loads(parser.get_schedule(group_url))
                data[group] = schedule
                date, time = now_time()
                print(f"[ {date} {time} ]    Группа {group} получена...")
    response = requests.post('https://falpin.ru/api/save_schedule', json=data, headers=headers)
    date, time = now_time()
    print(f"{date} {time}:    Сохранение расписания: {json.loads(response.text)}")

send_schedule()