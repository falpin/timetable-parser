import requests
from bs4 import BeautifulSoup
import re

URL = "https://pronew.chenk.ru/blocks/manage_groups/website/"
COMPLEX = ["list.php?id=1", "list.php?id=3"]

def get_table_courses(complex):  # получение всех групп и курсов
    response = requests.get(URL+complex)
    soup = BeautifulSoup(response.text, 'html.parser')
    courses = soup.find_all('div', class_='spec-year-block-container')
    course_dict = {}

    for course in courses:
        spec_course_blocks = course.find_all('div', class_='spec-year-block')
        for spec_course in spec_course_blocks:
            year_name = spec_course.find(
                'span', class_='spec-year-name').text.strip()
            year_name = year_name.replace(":", '')

            if year_name not in course_dict:
                course_dict[year_name] = {}

            groups = spec_course.find_all('span', class_='group-block')
            for group in groups:
                group_link_tag = group.find('a')
                group_name = group_link_tag.text.strip()
                group_link = group_link_tag['href'].strip()
                course_dict[year_name][group_name] = group_link

    return course_dict

def get_schedule(group):  # расписание для указанной группы
    response = requests.get(URL+group)
    schedule_dict = {}

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        schedule = soup.find('div', class_='timetableContainer')  # вся неделя
        days = schedule.find_all('td', attrs={'style': True})  # все дни

        for day in days:
            day_week = day.find('div', class_='dayHeader').text.strip()
            day_schedule = day.find(
                'div', attrs={'style': 'padding-left: 6px;'})  # расписание дня

            lessons_list = []

            lessons = day_schedule.find_all(
                'div', class_='lessonBlock')  # блок пар
            for lesson in lessons:
                lesson_time_block = lesson.find(
                    'div', class_='lessonTimeBlock').text.strip().split('\n')
                lesson_number = lesson_time_block[0].strip()
                try:
                    lesson_time_start = lesson_time_block[1].strip()
                    lesson_time_finish = lesson_time_block[2].strip()
                except:
                    lesson_time_start = "???"
                    lesson_time_finish = "???"

                lesson_info = {
                    'number': lesson_number,
                    'time_start': lesson_time_start,
                    'time_finish': lesson_time_finish,
                    'lessons': []
                }

                lesson_name = "Пары нет"
                discBlocks = lesson.find_all('div', class_='discBlock')
                for discBlock in discBlocks:
                    if 'cancelled' in discBlock.get('class', []):
                        continue

                    header_div = discBlock.find('div', class_='discHeader')
                    try:
                        lesson_name = header_div.find('span').get('title')
                        lesson_name = re.sub(r'\(.*?\)', '', lesson_name)
                        lesson_name = lesson_name.strip()
                    except:
                        lesson_name = "Пары нет"

                    lesson_teachers_data = discBlock.find_all('div', class_='discSubgroup')
                    lesson_data = []
                    for subgroup in lesson_teachers_data:
                        teacher = subgroup.find(
                            'div', class_='discSubgroupTeacher').text.strip()
                        classroom = subgroup.find('div', class_='discSubgroupClassroom').text.strip()
                        classroom = classroom.replace("???", '')
                        lesson_data.append({
                            'teacher': teacher,
                            'classroom': classroom
                        })
                        
                    lesson_info['lessons'].append({
                        'name': lesson_name,
                        'teachers': lesson_data
                    })

                if lesson_name != "Пары нет" and lesson_name != "":
                    lessons_list.append(lesson_info)

            schedule_dict[day_week] = lessons_list

    else:
        schedule_dict['Ошибка'] = f"Ошибка при запросе: {response.status_code}"

    return schedule_dict