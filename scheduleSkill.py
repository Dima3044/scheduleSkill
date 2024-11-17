add_activity = False
check_plans = False
schedule = {}


def add_todo(r_date, r_time, r_todo):
    global schedule

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
        plans = 'Ваши планы на ' + str(r_date) + ': |'
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
            plans += add_plan + '|'
            
        return plans


def handler(event, context):
    """
    Entry-point for Serverless Function.
    :param event: request payload.
    :param context: information about current execution context.
    :return: response to be serialized as JSON.
    """
    global add_activity, check_plans, schedule

    if add_activity == True:
        for i in range(len(event['request']['nlu']['entities'])):

            if event['request']['nlu']['entities'][i]['type'] == 'YANDEX.DATETIME':
                req_month = str(event['request']['nlu']['entities'][i]['value']['month'])
                if len(req_month) == 1:
                    req_month = '0' + req_month
                req_day = str(event['request']['nlu']['entities'][i]['value']['day'])
                if len(req_day) == 1:
                    req_day = '0' + req_day
                req_date = req_day + '.' + req_month

                if 'hour' in event['request']['nlu']['entities'][i]['value'].keys():
                    req_hour = event['request']['nlu']['entities'][i]['value']['hour']
                    if 'minute' in event['request']['nlu']['entities'][i]['value'].keys():                   
                        req_min = event['request']['nlu']['entities'][i]['value']['minute']
                        req_time = str(req_hour) + ':' + str(req_min)
                    else:
                        req_time = str(req_hour) + ':' + '00'
            
                req_todo = ''
                start_datetime = int(event['request']['nlu']['entities'][i]['tokens']['start'])
            
                for todo in range(start_datetime):
                    req_todo += event['request']['nlu']['tokens'][todo] + ' '
                if req_todo.split()[-1] == 'на' or req_todo.split()[-1] == 'в':
                    req_todo = req_todo.split()
                    del req_todo[-1]
                    req_todo = ' '.join(req_todo)

                add_activity = False
                text = add_todo(req_date, req_time, req_todo)

    elif check_plans == True:
        for i in range(len(event['request']['nlu']['entities'])):
            if event['request']['nlu']['entities'][i]['type'] == 'YANDEX.DATETIME':
                req_month = str(event['request']['nlu']['entities'][i]['value']['month'])
                if len(req_month) == 1:
                    req_month = '0' + req_month
                req_day = str(event['request']['nlu']['entities'][i]['value']['day'])
                if len(req_day) == 1:
                    req_day = '0' + req_day
                req_date = req_day + '.' + req_month
                text = watch_schedule(req_date)
                check_plans = False



    if 'добавить' in event['request']['command'] or 'добавь' in event['request']['command']:
        text = 'Укажите задачу'
        add_activity = True

    elif 'посмотреть' in event['request']['command']:
        text = 'На какой день вы хотите посмотреть расписание?'
        check_plans = True
        

    return {
        'version': event['version'],
        'session': event['session'],
        'response': {
            # Respond with the original request or welcome the user if this is the beginning of the dialog and the request has not yet been made.
            'text': text,
            # Don't finish the session after this response.
            'end_session': 'false'
        },
    }