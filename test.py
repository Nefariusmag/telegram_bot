#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @bot.message_handler(commands=['gistek_build_arm_pk'])
# @bot.message_handler(content_types=["text"])
# @bot.callback_query_handler(func=lambda call: True)
#
#
# @bot.message_handler(regexp="SOME_REGEXP")
# @bot.message_handler(content_types=['document', 'audio'])
# @bot.message_handler(filters)
#
# {'new_chat_member': None, 'location': None, 'delete_chat_photo': None, 'left_chat_member': None, 'caption': None, 'forward_date': None, 'from_user': {'first_name': 'gistek_info_devops_bot', 'username': 'GISTEKdevops_bot', 'id': 357145828, 'last_name': None}, 'forward_from': None, 'new_chat_title': None, 'audio': None, 'message_id': 1346, 'edit_date': None, 'video': None, 'photo': None, 'voice': None, 'migrate_from_chat_id': None, 'pinned_message': None, 'document': None, 'reply_to_message': None, 'migrate_to_chat_id': None, 'forward_from_chat': None, 'contact': None, 'supergroup_chat_created': None, 'venue': None, 'content_type': 'text', 'entities': None, 'chat': {'first_name': 'Дмитрий', 'username': 'nefariusmag', 'all_members_are_administrators': None, 'type': 'private', 'last_name': 'Ерохин', 'id': 121860960, 'title': None}, 'text': 'nefariusmag(121860960): АРМы для ПП, выбирай!', 'new_chat_photo': None, 'group_chat_created': None, 'date': 1493012735, 'sticker': None, 'channel_chat_created': None}
#
# @bot.message_handler(regexp="gistek_build \w+")
# def any_subsystem(message):
#     text = "{}({}): {}".format(message.chat.username, message.chat.id, message.text)
#     print(text)
#     bot.send_message(message.chat.id, message.text)
"""
This Example will show you how to use register_next_step handler.
"""
import time

import telebot
from telebot import types

API_TOKEN = '357145828:AAEKuo0euMlBGQvUZNLiicj5823mMxPoTuQ'

bot = telebot.TeleBot(API_TOKEN)

user_dict = {}


class User:
    def __init__(self, name):
        self.name = name
        self.age = None
        self.sex = None


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    msg = bot.reply_to(message, """\
Hi there, I am Example bot.
What's your name?
""")
    bot.register_next_step_handler(msg, process_name_step)


def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = User(name)
        user_dict[chat_id] = user
        msg = bot.reply_to(message, 'How old are you?')
        bot.register_next_step_handler(msg, process_age_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_age_step(message):
    try:
        chat_id = message.chat.id
        age = message.text
        if not age.isdigit():
            msg = bot.reply_to(message, 'Age should be a number. How old are you?')
            bot.register_next_step_handler(msg, process_age_step)
            return
        user = user_dict[chat_id]
        user.age = age
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Male', 'Female')
        msg = bot.reply_to(message, 'What is your gender', reply_markup=markup)
        bot.register_next_step_handler(msg, process_sex_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_sex_step(message):
    try:
        chat_id = message.chat.id
        sex = message.text
        user = user_dict[chat_id]
        if (sex == u'Male') or (sex == u'Female'):
            user.sex = sex
        else:
            raise Exception()
        bot.send_message(chat_id, 'Nice to meet you ' + user.name + '\n Age:' + str(user.age) + '\n Sex:' + user.sex)
    except Exception as e:
        bot.reply_to(message, 'oooops')


bot.polling()
