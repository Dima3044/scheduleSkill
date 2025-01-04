from datetime import datetime, timedelta
import pytz

delete_note = False
note_date = ''
add_note = False
add_activity = False
check_plans = False
delete_activity = False
edit_activity = False
edit_count = ''
schedule = {}
notes = {}

def clear_note(event, context):
    global note_date, notes
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



def create_note(event, context):
    global notes, note_date
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

def convert_to_mins(time_moment):
    hours = int(time_moment.split(':')[0])
    minutes = int(time_moment.split(':')[1])
    converted = hours * 60 + minutes
    return converted

def get_date(event, context):
    req_date = ''
    for i in range(len(event['request']['nlu']['entities'])):
        if event['request']['nlu']['entities'][i]['type'] == 'YANDEX.DATETIME':
            if event['request']['nlu']['entities'][i]['value']['day_is_relative'] == True:
                user_timezone = pytz.timezone(event['meta']['timezone'])
                days_delta = event['request']['nlu']['entities'][i]['value']['day']
                correction = timedelta(days = days_delta)
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
                        return 404

                if len(req_day) == 1:
                    req_day = '0' + req_day
                req_date = str(req_day) + '.' + str(req_month)
                return req_date
    if req_date == '':
        return 404


def get_time(event, context):
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
    return req_time

def get_timeperiod(event, context):
    time_period_index = []

    for i in range(len(event['request']['nlu']['entities'])):
        if event['request']['nlu']['entities'][i]['type'] == 'YANDEX.DATETIME':
            if 'hour' in event['request']['nlu']['entities'][i]['value'].keys():
                list.append(time_period_index, i)

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

def get_todo(event, context):
    req_todo = ''
    
    for i in range(len(event['request']['nlu']['entities'])):
        if event['request']['nlu']['entities'][i]['type'] == 'YANDEX.DATETIME':
            if event['request']['nlu']['entities'][i]['value']['day_is_relative'] == True:
                start_datetime = event['request']['nlu']['entities'][i]['tokens']['start'] - 1
            elif 'month' in event['request']['nlu']['entities'][i]['value'].keys():
                start_datetime = event['request']['nlu']['entities'][i]['tokens']['start']
            else:
                continue
            for k in range(start_datetime):
                req_todo += event['request']['original_utterance'].split(' ')[k] + ' '
            if start_datetime == 0:
                req_todo = event['request']['nlu']['tokens'][0]
            return req_todo

def clear_activity(r_date, r_time):
    global schedule
    if r_date not in schedule.keys():
        return 'На этот день у вас нет планов'
    else:
        if r_time not in schedule[r_date].keys():
            return 'У вас нет планов на это время'
        else:
            del schedule[r_date][r_time]

            if len(schedule[r_date].keys()) == 0:
                del schedule[r_date]
                
            return 'Задача удалена'

def add_todo(r_date, r_time, r_todo):
    global schedule
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
        start_time = convert_to_mins(period_start)
        end_time = convert_to_mins(period_end)
        for minute in range(start_time, end_time):
            mins_in_period.append(minute)

        for todo_start in schedule[r_date]:
            booked_mins = []
            todo_end = schedule[r_date][todo_start].split(' ')[0]
            todo_end = str.strip(todo_end, '-')
            todo_start_in_min = convert_to_mins(todo_start)
            todo_end_in_min = convert_to_mins(todo_end)
            for booked in range(todo_start_in_min, todo_end_in_min):
                booked_mins.append(booked)
            if (len(mins_in_period) + len(booked_mins)) != len(set(mins_in_period + booked_mins)):
                return f'Пересечение. {r_date} у вас есть планы \
            {todo_start}{schedule[r_date][todo_start]}'
        schedule[r_date][r_time] = r_todo
        return 'Задача добавлена'

def watch_schedule(r_date):
    global schedule

    if r_date not in schedule.keys():
        return 'На этот день у Вас ещё нет планов'
    else:
        plans = 'Ваши планы на ' + str(r_date) + ': \n '
        time_to_mins = []
        for time in schedule[r_date]:
            mins_amount = convert_to_mins(time)
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
            
        return plans


def handler(event, context):
    """
    Entry-point for Serverless Function.
    :param event: request payload.
    :param context: information about current execution context.
    :return: response to be serialized as JSON.
    """
    global add_activity, check_plans, delete_activity, edit_activity, edit_count, schedule, notes, add_note, note_date, delete_note
    if 'notes' in event['state']['user'].keys():
        notes = event['state']['user']['notes']
    if 'value' in event['state']['user'].keys():
        schedule = event['state']['user']['value']
    if event['request']['command'] == '':
        text = 'Здравствуйте! Я навык Расписание дня. Я могу добавить задачи в Ваше расписание, показать их Вам,\
        а также удалять и редактировать. Чем могу быть полезна?'
    else:
        text = 'Жду Вашей команды'
        
    if add_activity == True:

        req_date = get_date(event, context)
        req_time = get_timeperiod(event, context)
        req_todo = get_todo(event, context)

        if req_date == 404:
            text = 'Не смогла распознать дату'
        elif req_time == 404:
            text = 'Не смогла распознать время'
        elif req_todo == 404:
            text = 'Не смогла распознать занятие'
        else:
            add_activity = False
            text = add_todo(req_date, req_time, req_todo)

    elif check_plans == True:
        req_date = get_date(event, context)
        text = watch_schedule(req_date)
        check_plans = False

    elif delete_activity == True:
        req_date = get_date(event, context)
        req_time = get_time(event, context)
        text = clear_activity(req_date, req_time)
        delete_activity = False

    elif add_note == True:
        text = create_note(event, context)
        add_note = False

    elif delete_note == True:
        text = clear_note(event, context)
        delete_note = False


    elif edit_activity == True:
        if edit_count == 0:
            req_date = get_date(event, context)
            req_time = get_time(event, context)

            if req_date in schedule.keys() and req_time in schedule[req_date].keys():
                clear_activity(req_date, req_time)
                edit_count += 1
                text = 'Укажите занятие, дату и время'
            else:
                text = 'Не нашла у Вас занятий на это время'
                edit_count = ''
                edit_activity = False

        elif edit_count == 1:
            req_date = get_date(event, context)
            req_timeperiod = get_timeperiod(event, context)
            req_todo = get_todo(event, context)

            if req_date == 404:
                text = 'Не могу распознать дату. Повторите запрос, пожалуйста.'
            elif req_timeperiod == 404:
                text = 'Не могу распознать время. Повторите запрос, пожалуйста.'
            elif req_todo == 404:
                text = 'Не могу распознать занятие. Повторите запрос, пожалуйста.'
            else:
                edit_activity = False
                edit_count = ''
                text = add_todo(req_date, req_timeperiod, req_todo)

    elif 'удалить заметку' in event['request']['command']:
        note_date = get_date(event, context)
        
        if note_date not in notes.keys():
            text = f'У Вас нет заметок на {note_date}'
        elif note_date == 404:
            text = 'Не расслышала дату'
        else: 
            text = 'Назовите номер заметки'
            delete_note = True

    elif 'сделать заметку' in event['request']['command'] or 'создать заметку' in event['request']['command']:
        text = 'Назовите содержимое заметки'
        note_date = get_date(event, context)
        if note_date != 404:
            add_note = True
        else:
            text = 'Не расслышала, на какой день Вы хотите добавить заметку'

    elif 'добавить' in event['request']['command'] or 'добавь' in event['request']['command'] or 'создать' in event['request']['command'] or 'создай' in event['request']['command']:
        text = 'Укажите задачу'
        add_activity = True

    elif 'посмотреть' in event['request']['command'] or 'покажи' in event['request']['command']:
        text = 'На какой день Вы хотите посмотреть расписание?'
        check_plans = True

    elif 'удалить' in event['request']['command'] or 'удали' in event['request']['command']:
        text = 'Назовите день и время, на которые Вы хотите удалить занятие'
        delete_activity = True

    elif 'редактировать' in event['request']['command'] or 'изменить' in event['request']['command']:
        text = 'Назовите дату и время, на которые Вы хотите изменить занятие' 
        edit_count = 0
        edit_activity = True
        
    elif 'очистить расписание' in event['request']['command']:
        schedule.clear()
        text = 'Расписание очищено!'

    elif 'пояс' in event['request']['command']:
        user_timezone = pytz.timezone(event['meta']['timezone'])
        text = datetime.now(user_timezone) 

    elif 'тест' in event['request']['command']:
        text = notes['04.01']['1']

    return {
        'version': event['version'],
        'session': event['session'],
        'response': {
            'text': text,
            # Don't finish the session after this response.
            'end_session': 'false',
        },
        'user_state_update':{
            'value': schedule,
            'notes': notes
        }
    }