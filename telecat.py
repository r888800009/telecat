#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
simple bot with cli service
"""
import logging
import subprocess
from queue import Queue, Empty
from threading import Thread
import time
import json
import sys
from telegram.ext import Updater, MessageHandler, Filters

COMMAND = []
CONFIG = {}
PROC_POOL = {}

LOGGER = logging.getLogger(__name__)

def restrict_user(bot, chat_id, user):
    if CONFIG['restrict-user']:
        bot.send_message(chat_id=chat_id, text="Already configured")
        return

    username = '' if user.username is None else '(%s)'% user.username
    print('Restrict bots only for this user?')
    print('[%s]: "%s" %s' % (str(user.id), user.first_name, username))

    choice = input('[y/n]: ').lower()

    if choice == 'y':
        update_config('restrict-user', True)
        update_config('restrict-user-id', user.id)
        save_config()
    else:
        print('Cancel setting')

def tg_command(update, context):
    "handler telegram commands"
    command = update.message.text
    chat_id = update.message.chat_id
    user = update.message.from_user

    print(command)

    if CONFIG['restrict-user'] and CONFIG['restrict-user-id'] != user.id:
        print('not allow')
        return

    if command == '/restart':
        print('restart proc')
        start_proc(chat_id, context.bot)
        context.bot.send_message(chat_id=chat_id, text="restart")
    elif command == '/start':
        print('start proc')
        start_proc(chat_id, context.bot)
        context.bot.send_message(chat_id=chat_id, text="start")
    elif command == '/stop':
        stop_proc(chat_id)
    elif command == '/register':
        restrict_user(context.bot, chat_id, user)
    else:
        print('undefine command')

def run_command(update, context):
    """send command."""
    command = update.message.text
    chat_id = update.message.chat_id
    user = update.message.from_user

    print("chat id:" + str(chat_id))
    print('"' + command + '"')

    if CONFIG['restrict-user'] and CONFIG['restrict-user-id'] != user.id:
        return

    if not (chat_id in PROC_POOL):
        context.bot.send_message(chat_id=chat_id, text="proc is not running /start")
        return

    session = PROC_POOL[chat_id]
    proc = session.get('proc')

    proc.stdin.write((command + '\n').encode('utf8'))
    proc.stdin.flush()

def tg_output(out, str_queue):
    """get process stdout"""
    for line in iter(out.readline, b''):
        str_queue.put(line.decode('utf8'))

    out.close()

def tg_send(chat_id, bot, str_queue, running):
    """auto send process stdout"""
    while running[0]:
        result = ''
        while True:
            try:
                line = str_queue.get_nowait()
            except Empty:
                break
            else:
                result += line

        if result.strip() != '':
            print('"' + result + '"')
            bot.send_message(chat_id=chat_id, text=result)

        time.sleep(0.25)

def start_proc(chat_id, bot):
    """start a process for chat room"""
    if chat_id in PROC_POOL:
        stop_proc(chat_id)

    session = {}
    PROC_POOL[chat_id] = session
    proc = subprocess.Popen(
        COMMAND, stdout=subprocess.PIPE,
        stdin=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)

    str_queue = Queue()
    running = [True]

    t = Thread(target=tg_output, args=(proc.stdout, str_queue))
    t.daemon = True
    t.start()

    send_t = Thread(target=tg_send, args=(chat_id, bot, str_queue, running))
    send_t.daemon = True
    send_t.start()

    session['t'] = t
    session['str_queue'] = str_queue
    session['send_t'] = send_t
    session['proc'] = proc
    session['running'] = running
    print(session)

def stop_proc(chat_id):
    """Stop proc in chat room"""
    session = PROC_POOL[chat_id]

    proc = session.get('proc')
    running = session.get('running')

    proc.stdin.close()
    proc.wait()

    running[0] = False

    PROC_POOL.pop(chat_id, None)

def error(update, context):
    """log Errors"""
    LOGGER.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    updater = Updater(CONFIG['token'], use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.command, tg_command))
    dp.add_handler(MessageHandler(Filters.text, run_command))

    # log all errors
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()

    print("stop")
    for k in list(PROC_POOL):
        stop_proc(k)

def update_config(key, val):
    """update config file"""
    global CONFIG

    print('update "%s"' % key)
    CONFIG[key] = val

def save_config():
    """save config"""
    print('save config')
    with open('config.json', 'w') as f:
        json.dump(CONFIG, f, indent=2)

def create_config_file():
    """create_config_file"""
    global CONFIG

    print("First start")
    print("copy example config")

    CONFIG = json.loads(open("config.example.json").read())

    tg_token = input("telegram token: ")
    print('"%s"' % tg_token)

    update_config('token', tg_token)

    save_config()

def load_config():
    """load config file"""
    global CONFIG

    config_data = ''
    try:
        config_data = open('config.json').read()
    except FileNotFoundError:
        create_config_file()
        config_data = open('config.json').read()

    CONFIG = json.loads(config_data)

def check():
    """check argument"""
    global COMMAND
    argv = sys.argv
    args = len(argv)
    COMMAND = argv[1:]
    if args == 1:
        print('Warning, no argument is set.')
        print('example: ./telecat.py ./a.out')
        sys.exit(1)

    print('running "%s", "%s"' % (argv[1], COMMAND))

if __name__ == '__main__':
    check()
    load_config()
    main()
