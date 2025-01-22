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
        text = 'Здравствуйте! Я навык Планировщик дня. Я могу добавить задачи \
        и заметки в ваше расписание, показать их Вам,\
        а также удалять и редактировать. Если запутаетесь, то скажите "помощь"!\
        Чем могу быть полезна?'
    else:
        text = 'Жду Вашей команды'
    task = event['request']['command']

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
        if Requests.check_words(task, 'watch'):
            text = Notes.watch(note_date, notes)
            task = ''
        else:
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

    elif Requests.check_words(task, 'watch'):
        if 'заметк' in task:
            note_date = Requests.get_date(event, context)
            if note_date == 'Не расслышала дату':
                text = note_date
            else:
                text = Notes.watch(note_date, notes)
        elif Requests.check_words(task, 'schedule'):
            req_date = Requests.get_date(event, context)
            text = Schedule.watch(req_date, schedule, notes)
        else:
            text = 'Извините, не поняла, что Вы хотите посмотреть. Повторите, пожалуйста.'

    elif Requests.check_words(task, 'delete'):
        if 'заметк' in task:
            note_date = Requests.get_date(event, context)
            if note_date == 'Не расслышала дату':
                text = note_date
            elif note_date not in notes.keys():
                text = f'У Вас нет заметок на {note_date}'
            else:
                text = 'Назовите номер заметки'
                delete_note = True
        elif Requests.check_words(task, 'schedule'):
            text = 'Назовите день и время, на которые Вы хотите удалить занятие'
            delete_activity = True
        else:
            text = 'Извините, не поняла, что Вы хотите удалить. Повторите, пожалуйста.'

    elif Requests.check_words(task, 'add'):
        if 'заметк' in task:
            text = 'Назовите содержимое заметки'
            note_date = Requests.get_date(event, context)
            if note_date != 'Не расслышала дату':
                add_note = True
            else:
                text = 'Не расслышала, на какой день Вы хотите добавить заметку'   
        elif Requests.check_words(task, 'schedule'):
            add_date = Requests.get_date(event, context)
            if add_date == 'Не расслышала дату':
                text = add_date
            else:
                text = 'Укажите задачу и временной промежуток'
                add_activity = True
        else:
            text = 'Извините, не поняла, что Вы хотите добавить. Повторите, пожалуйста.'

    elif Requests.check_words(task, 'edit'):
        text = 'Назовите дату и время, на которые Вы хотите изменить занятие' 
        edit_count = 0
        edit_activity = True

    elif 'помощь' in task or 'что ты умеешь' in task:
        text = 'Чтобы добавить запись в расписание, скажите:"Создай задачу(заметку) на ДАТА".\n\
    Чтобы удалить заметку, скажите:"Удали заметку на ДАТА".\n\
    Чтобы удалить задачу, скажите:"Удали задачу".\n\
    Для просмотра расписания или заметок, скажите:"Покажи расписание(заметки) на ДАТА"\n\
    Чтобы изменить запись, скажите:"Отредактируй"'
        
    return {
        'version': event['version'],
        'session': event['session'],
        'response': {
            'text': text,
            'end_session': 'false',
        },
        'user_state_update': {
            'value': schedule,
            'notes': notes
        }
    }
