import os
import asyncio
from datetime import datetime
import random
from uuid import uuid4
import logging

from pyrogram import Client, filters
from pyrogram.errors import MessageNotModified, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup,\
CallbackQuery, ReplyKeyboardMarkup, ForceReply

from callback_messages import HELP_TEXT
from user_input_extractor import convert_input_to_datetime
from sequence_details import sequence_details

#logging.basicConfig(filename='run.log', level=logging.DEBUG,
#                    format='%(asctime)s:%(levelname)s:%(message)s')

app_name = 'DeepBlue_Telegram_Bot'
api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
bot_token = os.environ['BOT_TOKEN']

app = Client(
    app_name, api_id, api_hash, bot_token
)

countdowns = []
sequences = []


## command '/help 'command'(optional) 'verbose'(optional)
    ## if no args then list commands and small descriptions
    ## if 1 arg and arg is in list of commads
        # in depth description of command
        # if -v as arg 2 add examples

## Command /set 'id'
    # only chat admin
        # if date in future
            # create countdown message
            # pin created message
            # wait 5 to 8 seconds
            # if date in future
                # update message
                # edit pinned message
            # else if date in passed
                # unpin countdown message
                # create launch message
                # send launch message
                # pin launch message
        # else if date not in past
            # send private error message
    # if not admin, log event

async def update_countdown_data(countdown_id, field_name, field_data):
    global countdowns
    for countdown in countdowns:
        if countdown['countdown_id'] == countdown_id:
            countdown.update({field_name: field_data})

async def extract_field_data(action, message):
    if action['input_type'] == 'text':
        return message.text
    if action['input_type'] == 'date_time':
        return convert_input_to_datetime(message.text)
    elif action['input_type'] == 'image':
        try:
            return await app.download_media(message)
        except ValueError as e:
            print(e, 'Attempted to extract media!')

def remove_sequence_from_sequences(sequence):
    global sequences
    try:
        sequences.remove(sequence)
    except KeyError as e:
        print(e)

async def create_sequence_manager(sequence, message):
    for action in sequence_details['create_actions']:
        if sequence['action'] == action['action_name']:
            field_data = await extract_field_data(action, message)
            if field_data:
                await update_countdown_data(sequence['countdown_id'], 
                                    action['field_name'], field_data)
                if action['followup_action']:
                    sequence.update({'action': action['followup_action']})
                    return await app.send_message(message.chat.id, 
                                        action['followup_message'], 
                                        reply_markup=ForceReply())
                else:
                    remove_sequence_from_sequences(sequence)
                    return await app.send_message(message.chat.id, 
                                        action['followup_message'])
            else:
                return await app.send_message(message.chat.id, 
                                        action['retry_message'], 
                                        reply_markup=ForceReply())

async def add_countdown_to_sequence(sequence, message):
    global countdowns, sequences
    for countdown in countdowns:
        if message.text == countdown['countdown_name']:
            sequence.update({'countdown_id': countdown['countdown_id']})

async def create_display_countdown_fields(sequence):
    global countdowns
    display_fields = []
    
    for countdown in countdowns:
        if countdown['countdown_id'] == sequence['countdown_id']:
            countdown_keys = countdown.keys()
    for key in countdown_keys:
        if key != 'countdown_id':
            display_fields.append([key])

    print(display_fields)
    return display_fields



async def edit_sequence_manager(sequence, message):
    for action in sequence_details['edit_actions']:
        if sequence['action'] == 'select_countdown':
            await add_countdown_to_sequence(sequence, message)
            countdown_fields = await create_display_countdown_fields(sequence)
            await app.send_message(
                message.chat.id, 
                action['followup_message'],
                reply_markup=ReplyKeyboardMarkup(
                    countdown_fields,
                    resize_keyboard=True
                )
            )
            

@app.on_message(filters.reply)
async def add_countdown_information(client, message):
    global sequences
    try:
        user_id = message.from_user.id
        for sequence in sequences:
            if user_id == sequence['user_id']:
                if sequence['sequence'] == 'create_countdown':
                    return await create_sequence_manager(sequence, message)
                elif sequence['sequence'] == 'edit_countdown':
                    return await edit_sequence_manager(sequence, message)

    except FloodWait as e:
        await asyncio.sleep(e.x)

def create_countdown_dict(countdown_id, message):
    countdown = {
        'countdown_id': countdown_id, 
        'countdown_owner_id': message.from_user.id,
        'countdown_onwner_username': message.from_user.username,
        }
    return countdown

def create_sequence_dict( countdown_id, message):
    sequence = {
        'sequence': 'create_countdown', 
        'action': 'add_name',
        'sequence_id': uuid4(), 
        'user_id': message.from_user.id,
        'countdown_id': countdown_id, 
        'status': 'response_pending',
        }
    return sequence

def edit_sequence_dict(message):
    sequence = {
        'sequence': 'edit_countdown',
        'sequence_id': uuid4(), 
        'user_id': message.from_user.id,
        'action': 'select_countdown',
        'status': 'response_pending',
        }
    return sequence

@app.on_message(filters.command('create'))
async def create_countdown(client, message):
    global countdowns, sequences
    countdown_id = uuid4()
    countdowns.append(create_countdown_dict(countdown_id, message))
    sequences.append(create_sequence_dict(countdown_id, message))

    try:
        await message.reply(
            'What do you want to name the countdown?', 
            reply_markup=ForceReply()
            )
    except FloodWait as e:
        await asyncio.sleep(e.x)

def create_display_countdown_lists():
    global countdowns
    countdown_lists = []
    for countdown in countdowns:
        countdown_lists.append([countdown['countdown_name']])
    return countdown_lists

@app.on_message(filters.command('edit'))
async def edit_countdown(client, message):
    global sequences
    sequences.append(edit_sequence_dict(message))
    display_countdown = create_display_countdown_lists()
    try:
        await message.reply(
            'Which countdown do you want to edit?',
            reply_markup=ReplyKeyboardMarkup(
                display_countdown,
                resize_keyboard=True
            )
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)

## Command /preview id
    # only in admin chat

## Command /stop
    # only countdown owners

## Command 'kill'
    # only super user

print("Telegram bot is up and running!")
app.run()