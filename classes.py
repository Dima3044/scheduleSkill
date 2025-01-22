from datetime import datetime, timedelta
import pytz


class Requests():
    def check_words(task, action):
        if action == 'delete':
            words = ['удали', 'убери', 'убрать']
        elif action == 'add':
            words = ['добав', 'созда', 'сдела']
        elif action == 'watch':
            words = ['посмотреть', 'узнать', 'скажи', 'покажи', 'озвучь']
        elif action == 'schedule':
            words = ['расписание', 'планы', 'задач']
        elif action == 'edit':
            words = ['редактир', 'измени']

        for word in words:
            if word in task:
                return True
        return False

    def convert_to_mins(time_moment):
        hours = int(time_moment.split(':')[0])
        minutes = int(time_moment.split(':')[1])
        converted = hours * 60 + minutes
        return converted

    def get_date(event, context):  # найти дату в запросе
        req_date = ''
        for i in range(len(event['request']['nlu']['entities'])):
            if event['request']['nlu']['entities'][i]['type'] == 'YANDEX.DATETIME':
                if event['request']['nlu']['entities'][i]['value']['day_is_relative'] == True:
                    user_timezone = pytz.timezone(event['meta']['timezone'])
                    days_delta = event['request']['nlu']['entities'][i]['value']['day']
                    correction = timedelta(days=days_delta)
                    req_date = (datetime.now(user_timezone) + correction).strftime('%d.%m')  
                    return req_date   

                elif 'month' in event['request']['nlu']['entities'][i]['value'].keys():
                    req_month = str(event['request']['nlu']['entities'][i]['value']['month'])
                    if len(req_month) == 1:
                        req_month = '0' + req_month
                    if 'day' in event['request']['nlu']['entities'][i]['value'].keys():
                        req_day = str(event['request']['nlu']['entities'][i]['value']['day'])
                    else:
                        if event['request']['nlu']['entities'][i-1]['type'] == 'YANDEX.NUMBER':
                            req_day = str(event['request']['nlu']['entities'][i-1]['value'])
                        else:
                            return 'Не расслышала дату'

                    if len(req_day) == 1:
                        req_day = '0' + req_day
                    req_date = str(req_day) + '.' + str(req_month)
                    return req_date
        if req_date == '':
            return 'Не расслышала дату'

    def get_time(event, context):  # найти конкретное время в запросе
        req_time = ''
        for i in range(len(event['request']['nlu']['entities'])):
            if event['request']['nlu']['entities'][i]['type'] == 'YANDEX.DATETIME':
                hour = str(event['request']['nlu']['entities'][i]['value']['hour'])
                if 'minute' in event['request']['nlu']['entities'][i]['value'].keys():
                    minute = str(event['request']['nlu']['entities'][i]['value']['minute'])
                    if len(minute) == 1:
                        minute = '0' + minute
                else:
                    minute = '00'
        req_time = hour + ':' + minute
        if req_time == '':
            req_time = 'Не расслышала время'
        return req_time

    def get_timeperiod(event, context):  # найти временной промежуток в запросе
        time_period_index = []

        for i in range(len(event['request']['nlu']['entities'])):
            if event['request']['nlu']['entities'][i]['type'] == 'YANDEX.DATETIME':
                if 'hour' in event['request']['nlu']['entities'][i]['value'].keys():
                    list.append(time_period_index, i)
        if len(time_period_index) == 0:
            return 'Не расслышала время'
        time_period_start = str(event['request']['nlu']['entities'][time_period_index[0]]['value']['hour'])
        if 'minute' in event['request']['nlu']['entities'][time_period_index[0]]['value']:
            time_period_start += ':' + str(event['request']['nlu']['entities'][time_period_index[0]]['value']['minute'])
        else:
            time_period_start += ':00'

        time_period_end = str(event['request']['nlu']['entities'][time_period_index[1]]['value']['hour'])
        if 'minute' in event['request']['nlu']['entities'][time_period_index[1]]['value']:
            time_period_end += ':' + str(event['request']['nlu']['entities'][time_period_index[1]]['value']['minute'])
        else:
            time_period_end += ':00'

        return time_period_start + ' - ' + time_period_end

    def get_todo(event, context):  # найти занятие в запросе
        req_todo = ''
        for i in range(len(event['request']['nlu']['entities'])):
            if event['request']['nlu']['entities'][i]['type'] == 'YANDEX.DATETIME':
                start_datetime = event['request']['nlu']['entities'][i]['tokens']['start']
                for k in range(start_datetime):
                    if k == (start_datetime-1) and event['request']['nlu']['tokens'][k] == 'с':
                        continue
                    req_todo += event['request']['original_utterance'].split(' ')[k] + ' '
                if start_datetime == 1:
                    req_todo = event['request']['nlu']['tokens'][0]
                return req_todo


class Notes():

    def clear(event, context, notes, note_date):  # удаление заметки
        event_len = len(event['request']['nlu']['entities'])
        if event_len == 0:
            return 'Не расслышала номер заметки'
        for entity in range(event_len):
            if event['request']['nlu']['entities'][entity]['type'] == 'YANDEX.NUMBER':
                note_number = str(event['request']['nlu']['entities'][entity]['value'])
        if note_number in notes[note_date].keys():
            del notes[note_date][note_number]
            if len(notes[note_date]) == 0:
                del notes[note_date]
            return f'Заметка номер {note_number} на {note_date} удалена!'
        else:
            return f'У Вас нет заметки номер {note_number} на {note_date}'

    def watch(note_date, notes):  # просмотр заметок
        if note_date in notes.keys():
            text = 'Ваши заметки: \n'
            for note_number in notes[note_date]:
                text += f'№{note_number}: {notes[note_date][note_number]} |\n'
            return text
        else:
            return f'У Вас нет заметок на {note_date}'

    def add(event, context, notes, note_date):  # создать заметку
        if note_date not in notes.keys():
            notes[note_date] = {}
            note_number = 1
        else:
            for k in range(1, len(notes[note_date]) + 1):
                if str(k) not in notes[note_date].keys():
                    note_number = k
                    break
                else:
                    note_number = k + 1
        notes[note_date][note_number] = event['request']['original_utterance']
        return f'Заметка номер {note_number} на {note_date} добавлена'


class Schedule():

    def clear(r_date, r_time, schedule):  # удалить задачу
        if r_date not in schedule.keys():
            return 'На этот день у Вас нет планов'
        else:
            if r_time not in schedule[r_date].keys():
                return 'У Вас нет планов на это время'
            else:
                del schedule[r_date][r_time]

                if len(schedule[r_date].keys()) == 0:
                    del schedule[r_date]
                return 'Задача удалена'

    def add(r_date, r_time, r_todo, schedule):  # добавить задачу
        period_start = r_time.split(' - ')[0]
        period_end = r_time.split(' - ')[1]
        if int(period_end.split(':')[0]) < int(period_start.split(':')[0]):
            return 'Время конца занятия должно быть больше, чем время начала'
        elif int(period_end.split(':')[0]) == int(period_start.split(':')[0]):
            if int(period_end.split(':')[1]) < int(period_start.split(':')[1]):
                return 'Время конца занятия должно быть больше, чем время начала'

        r_todo = '-' + period_end + ' ' + r_todo
        r_time = period_start
        if r_date not in schedule.keys():
            schedule[r_date] = {}
            schedule[r_date][r_time] = r_todo
            return 'Задача добавлена'
        else:
            mins_in_period = []
            start_time = Requests.convert_to_mins(period_start)
            end_time = Requests.convert_to_mins(period_end)
            for minute in range(start_time, end_time):
                mins_in_period.append(minute)

            for todo_start in schedule[r_date]:
                booked_mins = []
                todo_end = schedule[r_date][todo_start].split(' ')[0]
                todo_end = str.strip(todo_end, '-')
                todo_start_in_min = Requests.convert_to_mins(todo_start)
                todo_end_in_min = Requests.convert_to_mins(todo_end)
                for booked in range(todo_start_in_min, todo_end_in_min):
                    booked_mins.append(booked)
                if (len(mins_in_period) + len(booked_mins)) != len(set(mins_in_period + booked_mins)):
                    return f'Пересечение. {r_date} у вас есть планы \
                {todo_start}{schedule[r_date][todo_start]}'
            schedule[r_date][r_time] = r_todo
            return 'Задача добавлена'

    def watch(r_date, schedule, notes):  # посмотреть расписание
        if r_date == 'Не расслышала дату':
            return 'Извините, не расслышала дату'
        elif r_date not in schedule.keys():
            return 'На этот день у Вас ещё нет планов'
        else:
            plans = 'Ваши планы на ' + str(r_date) + ': \n '
            time_to_mins = []
            for time in schedule[r_date]:
                mins_amount = Requests.convert_to_mins(time)
                time_to_mins.append(mins_amount)
            list.sort(time_to_mins)
            for mins in time_to_mins:
                h = (mins - mins % 60) // 60
                mins = mins - h * 60
                h = str(h)
                mins = str(mins)
                if len(mins) == 1:
                    mins = '0' + mins
                res_time = h + ':' + mins
                add_plan = res_time + schedule[r_date][res_time]
                plans += add_plan + ' |\n '
            plans += Notes.watch(r_date, notes)
            return plans
