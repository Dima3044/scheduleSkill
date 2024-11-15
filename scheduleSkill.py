add_activity = False

def add_todo():
    global add_activity, add_date, add_time, user_req

    if user_req == 'добавить' or user_req == 'добавь':
        return 'Укажите, чем и когда хотите заняться '
    


def handler(event, context):
    """
    Entry-point for Serverless Function.
    :param event: request payload.
    :param context: information about current execution context.
    :return: response to be serialized as JSON.
    """
    global add_activity, add_date, add_time
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
            text = req_todo
            

        

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