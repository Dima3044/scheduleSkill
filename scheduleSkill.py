from datetime import datetime, timedelta
import pytz


add_activity = False
check_plans = False
delete_activity = False
edit_activity = False
edit_count = ''
schedule = {}

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
                    day_index = event['request']['nlu']['entities'][i]['tokens']['start'] - 2
                    req_day = str(event['request']['nlu']['tokens'][day_index])

                if len(req_day) == 1:
                    req_day = '0' + req_day
                req_date = req_day + '.' + str(req_month)
                return req_date
            else:
                return 404


def get_time(event, context):
    req_time = ''
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
                start_datetime = event['request']['nlu']['entities'][i]['tokens']['start'] - 2
            else:
                continue
            for k in range(start_datetime):
                req_todo += event['request']['original_utterance'].split(' ')[k] + ' '
            del req_todo.split(' ')[-1]
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
    r_todo = ' - ' + r_time.split(' - ')[1] + ' ' + r_todo
    r_time = r_time.split(' - ')[0]
    if r_date not in schedule.keys():
        schedule[r_date] = {}
        schedule[r_date][r_time] = r_todo
        return 'Задача добавлена'
    else:
        if r_time in schedule[r_date].keys():
            return 'Это время уже занято'
        else:
            schedule[r_date][r_time] = r_todo 
            return 'Задача добавлена'

def watch_schedule(r_date):
    global schedule

    if r_date not in schedule.keys():
        return 'На этот день у вас ещё нет планов'
    else:
        plans = 'Ваши планы на ' + str(r_date) + ': \n '
        time_to_mins = []
        for time in schedule[r_date]:
            mins = time.split(':')
            mins_amount = int(mins[0]) * 60 + int(mins[1])
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
            add_plan = res_time + ' ' + schedule[r_date][res_time]
            plans += add_plan + ' |\n '
            
        return plans


def handler(event, context):
    """
    Entry-point for Serverless Function.
    :param event: request payload.
    :param context: information about current execution context.
    :return: response to be serialized as JSON.
    """
    global add_activity, check_plans, delete_activity, edit_activity, edit_count, schedule
    if 'value' in event['state']['user'].keys():
        schedule = event['state']['user']['value']
    if event['request']['command'] == '':
        text = 'Здравствуйте! Я навык Расписание дня. Я могу добавить задачи в ваше расписание, показать их вам, а также удалять и редактировать. Чем могу быть полезна?'
    else:
        text = 'Жду вашей команды'
        
    if add_activity == True:

        req_date = get_date(event, context)
        req_time = get_time(event, context)
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


    elif edit_activity == True:
        if edit_count == 0:
            req_date = get_date(event, context)
            req_time = get_time(event, context)

            if req_date in schedule.keys() and req_time in schedule[req_date].keys():
                clear_activity(req_date, req_time)
                edit_count += 1
                text = 'Укажите занятие, дату и время'
            else:
                text = 'Не нашла у вас занятий на это время'
                edit_count = ''
                edit_activity = False

        elif edit_count == 1:
            req_date = get_date(event, context)
            req_time = get_time(event, context)
            req_todo = get_todo(event, context)

            if req_date == 404:
                text = 'Не могу распознать дату. Повторите запрос, пожалуйста.'
            elif req_time == 404:
                text = 'Не могу распознать время. Повторите запрос, пожалуйста.'
            elif req_todo == 404:
                text = 'Не могу распознать занятие. Повторите запрос, пожалуйста.'
            else:
                edit_activity = False
                edit_count = ''
                text = add_todo(req_date, req_time, req_todo)
        

    elif 'добавить' in event['request']['command'] or 'добавь' in event['request']['command'] or 'создать' in event['request']['command'] or 'создай' in event['request']['command']:
        text = 'Укажите задачу'
        add_activity = True

    elif 'посмотреть' in event['request']['command'] or 'покажи' in event['request']['command']:
        text = 'На какой день вы хотите посмотреть расписание?'
        check_plans = True

    elif 'удалить' in event['request']['command'] or 'удали' in event['request']['command']:
        text = 'Назовите день и время, на которые вы хотите удалить занятие'
        delete_activity = True

    elif 'редактировать' in event['request']['command'] or 'изменить' in event['request']['command']:
        text = 'Назовите дату и время, на которые вы хотите изменить занятие' 
        edit_count = 0
        edit_activity = True
        
    elif 'очистить расписание' in event['request']['command']:
        schedule.clear()
        text = 'Расписание очищено!'

    return {
        'version': event['version'],
        'session': event['session'],
        'response': {
            'text': text,
            # Don't finish the session after this response.
            'end_session': 'false',
        },
        'user_state_update':{
            'value': schedule
        }
    }