import sqlite3
from countdown import Countdown

from datetime import datetime, timezone

from user_input_extractor import convert_input_to_datetime

def insert_countdown(countdown, cur):
    cur.execute(""" INSERT INTO countdowns VALUES (
        :countdown_id, 
        :countdown_owner_id,
        :countdown_name, 
        :countdown_date,
        :countdown_image, 
        :countdown_caption,
        :countdown_end_image, 
        :countdown_end_caption,
        :countdown_state
    )""", {
        'countdown_id': countdown['countdown_id'],
        'countdown_owner_id': countdown['countdown_owner_id'],
        'countdown_name': countdown['countdown_name'],
        'countdown_date': countdown['countdown_date'],
        'countdown_image': countdown['countdown_image'],
        'countdown_caption': countdown['countdown_caption'],
        'countdown_end_image': countdown['countdown_end_image'],
        'countdown_end_caption': countdown['countdown_end_caption'],
        'countdown_state': countdown['countdown_state']
    })

def delete_countdown(countdown, cur):
    cur.execute(""" DELETE FROM countdowns WHERE (
        countdown_id = :countdown_id
    )""", {
        'countdown_id': countdown['countdown_id']
    })

def update_countdown_in_db(cur, field_name, field_data, countdown):
    print(field_name, field_data)
    if field_name == 'countdown_name':
        cur.execute(""" UPDATE countdowns 
                        SET countdown_name = :field_data
                        WHERE countdown_id = :countdown_id
        """, {
            'field_data': field_data,
            'countdown_id': countdown['countdown_id']
        })
    elif field_name == 'countdown_date':
        cur.execute(""" UPDATE countdowns 
                        SET countdown_date = :field_data
                        WHERE countdown_id = :countdown_id
        """, {
            'field_data': field_data,
            'countdown_id': countdown['countdown_id']
        })
    elif field_name == 'countdown_image':
        cur.execute(""" UPDATE countdowns 
                        SET countdown_image = :field_data
                        WHERE countdown_id = :countdown_id
        """, {
            'field_data': field_data,
            'countdown_id': countdown['countdown_id']
        })
    elif field_name == 'countdown_caption':
        cur.execute(""" UPDATE countdowns 
                        SET countdown_caption = :field_data
                        WHERE countdown_id = :countdown_id
        """, {
            'field_data': field_data,
            'countdown_id': countdown['countdown_id']
        })
    elif field_name == 'countdown_end_image':
        cur.execute(""" UPDATE countdowns 
                        SET countdown_end_image = :field_data
                        WHERE countdown_id = :countdown_id
        """, {
            'field_data': field_data,
            'countdown_id': countdown['countdown_id']
        })
    elif field_name == 'countdown_end_caption':
        cur.execute(""" UPDATE countdowns 
                        SET countdown_end_caption = :field_data
                        WHERE countdown_id = :countdown_id
        """, {
            'field_data': field_data,
            'countdown_id': countdown['countdown_id']
        })
    elif field_name == 'countdown_state':
        cur.execute(""" UPDATE countdowns 
                        SET countdown_state = :field_data
                        WHERE countdown_id = :countdown_id
        """, {
            'field_data': field_data,
            'countdown_id': countdown['countdown_id']
        })

def append_countdown(countdown):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    insert_countdown(countdown, cur)
    conn.commit()
    conn.close()

def remove_countdown(countdown):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    delete_countdown(countdown, cur)
    conn.commit()
    conn.close()

def update_countdown(countdown, field_name, field_data):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    update_countdown_in_db(cur, field_name, field_data, countdown)
    conn.commit()
    conn.close()

def select_countdown_by_id(cur, countdown_id):
    cur.execute(""" SELECT * FROM countdowns WHERE (
        countdown_id = :countdown_id
    )""", {
        'countdown_id': countdown_id
    })

def select_countdown_by_name(cur, countdown_name):
    cur.execute(""" SELECT * FROM countdowns WHERE (
        countdown_name = :countdown_name
    )""", {
        'countdown_name': countdown_name
    })

def select_all_countdowns(cur):
    cur.execute(""" SELECT * FROM countdowns """)

def get_countdown_by_id(countdown_id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    select_countdown_by_id(cur, countdown_id)
    countdown = cur.fetchone()
    conn.close()
    return convert_countdown_tuple_to_dict(countdown)

def get_countdown_by_name(countdown_name):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    select_countdown_by_name(cur, countdown_name)
    countdown = cur.fetchone()
    conn.close()
    return convert_countdown_tuple_to_dict(countdown)

def get_countdowns():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    select_all_countdowns(cur)
    countdowns = cur.fetchall()
    conn.close()
    return [convert_countdown_tuple_to_dict(countdown) for countdown in countdowns]

def convert_countdown_tuple_to_dict(countdown):
    countdown_tuple = countdown
    return {
        'countdown_id': countdown_tuple[0],
        'countdown_owner_id': countdown_tuple[1],
        'countdown_name': countdown_tuple[2],
        'countdown_date': countdown_tuple[3],
        'countdown_image': countdown_tuple[4],
        'countdown_caption': countdown_tuple[5],
        'countdown_end_image': countdown_tuple[6],
        'countdown_end_caption': countdown_tuple[7],
        'countdown_state': countdown_tuple[8]
    }

def create_display_countdown_lists():
    countdowns = get_countdowns()
    countdown_lists = []
    for countdown in countdowns:
        countdown_lists.append([countdown['countdown_name']])
    return countdown_lists

def create_display_active_countdowns():
    countdowns = get_countdowns()
    countdown_lists = []
    for countdown in countdowns:
        if countdown['countdown_state'] == 'active':
            countdown_lists.append([countdown['countdown_name']])
    if countdown_lists: return countdown_lists
    else: return

def get_updated_caption(countdown):
    countdown_date = convert_input_to_datetime(countdown["countdown_date"])
    time_remaining = str(
        countdown_date - datetime.now(timezone.utc)
        ).split('.')[0]
    formated_countdown = (
        f'{countdown["countdown_caption"]}\n\n{time_remaining}'
    )
    return formated_countdown

def is_countdown_completed(countdown):
    countdown_date = convert_input_to_datetime(countdown["countdown_date"])
    if (countdown_date < datetime.now(timezone.utc)): return True
    else: return False