#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
simple bot with pwned service
"""

import subprocess
from queue import Queue, Empty
from threading import Thread
import time
from telegram.ext import Updater, MessageHandler, Filters
import sys

TOKEN = ''
COMMAND = []
PROC_POOL = {}

def tg_command(bot, update):
    "handler telegram commands"
    command = update.message.text
    chat_id = update.message.chat_id
    print(command)

    if command == '/restart':
        print('restart proc')
        start_proc(chat_id, bot)
        bot.send_message(chat_id=chat_id, text="restart")
    elif command == '/start':
        start_proc(chat_id, bot)
        bot.send_message(chat_id=chat_id, text="start")
    elif command == '/stop':
        stop_proc(chat_id)

def run_command(bot, update):
    """send command."""
    command = update.message.text
    chat_id = update.message.chat_id

    print("chat id:" + str(chat_id))
    print('"' + command + '"')

    if not (chat_id in PROC_POOL):
        bot.send_message(chat_id=chat_id, text="proc is not running /start")
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

        if result != '':
            bot.send_message(chat_id=chat_id, text=result)
            print(result)

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

def main():
    """Start the bot."""
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text, run_command))
    dp.add_handler(MessageHandler(Filters.command, tg_command))

    # Start the Bot
    updater.start_polling()
    updater.idle()

    print("stop")
    for k in list(PROC_POOL):
        stop_proc(k)

def check():
    global COMMAND
    argv = sys.argv
    args = len(argv)
    COMMAND = argv[1:]
    if args == 1:
        print('Warning, no argument is set.')
        sys.exit(1)

    print('running "%s", "%s"' % (argv[1], COMMAND))

if __name__ == '__main__':
    check()
    main()
