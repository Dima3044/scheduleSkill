from classes import *

add_date = ''
delete_note = False
note_date = ''
add_note = False
add_activity = False
delete_activity = False
edit_activity = False
edit_count = ''
schedule = {}
notes = {}


def handler(event, context):
    global add_activity, delete_activity, edit_activity, edit_count, schedule
    global notes, add_note, note_date, delete_note, add_date
    if 'notes' in event['state']['user'].keys():
        notes = event['state']['user']['notes']
    if 'value' in event['state']['user'].keys():
        schedule = event['state']['user']['value']
    if event['request']['command'] == '':
        text = 'Здравствуйте! Я навык Расписание дня. Я могу добавить задачи \
        в Ваше расписание, показать их Вам,\
        а также удалять и редактировать. Чем могу быть полезна?'
    else:
        text = 'Жду Вашей команды'

    if add_activity == True:
        req_time = Requests.get_timeperiod(event, context)
        req_todo = Requests.get_todo(event, context)
        if add_date == 'Не расслышала дату':
            text = add_date
        elif req_time == 'Не расслышала время':
            text = req_time
        else:
            add_activity = False
            text = Schedule.add(add_date, req_time, req_todo, schedule)

    elif delete_activity == True:
        req_date = Requests.get_date(event, context)
        req_time = Requests.get_time(event, context)
        text = Schedule.clear(req_date, req_time, schedule)
        delete_activity = False

    elif add_note == True:
        text = Notes.add(event, context, notes, note_date)
        add_note = False

    elif delete_note == True:
        text = Notes.clear(event, context, notes, note_date)
        delete_note = False

    elif edit_activity == True:
        if edit_count == 0:
            add_date = Requests.get_date(event, context)
            req_time = Requests.get_time(event, context)
            text = add_date + req_time
            if add_date in schedule.keys() and req_time in schedule[add_date].keys():
                Schedule.clear(add_date, req_time, schedule)
                edit_count += 1
                text = 'Укажите новые занятие и время'
            else:
                text = 'Не нашла у Вас занятий на это время'
                edit_count = ''
                edit_activity = False

        elif edit_count == 1:
            req_timeperiod = Requests.get_timeperiod(event, context)
            req_todo = Requests.get_todo(event, context)
            if req_timeperiod == 'Не расслышала время':
                text = req_timeperiod
            else:
                edit_activity = False
                edit_count = ''
                text = Schedule.add(add_date, req_timeperiod, req_todo, schedule)

    elif 'посмотреть заметки' in event['request']['command']:
        note_date = Requests.get_date(event, context)
        text = Notes.watch(note_date, notes)

    elif 'удалить заметку' in event['request']['command']:
        note_date = Requests.get_date(event, context)

        if note_date not in notes.keys():
            text = f'У Вас нет заметок на {note_date}'
        elif note_date == 'Не расслышала дату':
            text = note_date
        else:
            text = 'Назовите номер заметки'
            delete_note = True

    elif 'сделать заметку' in event['request']['command'] or 'создать заметку' in event['request']['command']:
        text = 'Назовите содержимое заметки'
        note_date = Requests.get_date(event, context)
        if note_date != 'Не расслышала дату':
            add_note = True
        else:
            text = 'Не расслышала, на какой день Вы хотите добавить заметку'

    elif 'добавить' in event['request']['command'] or 'добавь' in event['request']['command'] or 'создать' in event['request']['command'] or 'создай' in event['request']['command']:
        add_date = Requests.get_date(event, context)
        if add_date == 'Не расслышала дату':
            text = add_date
        else:
            text = 'Укажите задачу и временной промежуток'
            add_activity = True

    elif 'посмотреть расписание' in event['request']['command'] or 'покажи' in event['request']['command']:
        req_date = Requests.get_date(event, context)
        text = Schedule.watch(req_date, schedule, notes)

    elif 'удалить' in event['request']['command'] or 'удали' in event['request']['command']:
        text = 'Назовите день и время, на которые Вы хотите удалить занятие'
        delete_activity = True

    elif 'редактировать' in event['request']['command'] or 'изменить' in event['request']['command']:
        text = 'Назовите дату и время, на которые Вы хотите изменить занятие' 
        edit_count = 0
        edit_activity = True
    return {
        'version': event['version'],
        'session': event['session'],
        'response': {
            'text': text,
            'end_session': 'false',
        },
        'user_state_update':{
            'value': schedule,
            'notes': notes
        }
    }
