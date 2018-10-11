# -*- coding: utf-8 -*-
import telebot, config, database
from telebot import types, apihelper

apihelper.proxy = {'https':'socks5://' + config.proxy_server}
bot = telebot.TeleBot(config.token)

# main_menu = {"АРМ", "Пентаха", "Портал", "Мобильное приложение", "Интеграционная подсистема", "Сбор", "ПОИБ", "Перезапуск", "Синхронизация стендов", "Переподключиться"}


# @bot.message_handler(commands=['help', 'start'])
# def menu_1(message):
#     markup = types.ReplyKeyboardMarkup(row_width=3, one_time_keyboard=True)
#     markup.add("АРМ", "Пентаха", "Портал", "Мобильное приложение", "Интеграционная подсистема", "Сбор", "ПОИБ", "Перезапуск", "Синхронизация стендов", "Переподключиться")
#     msg = bot.reply_to(message, "Главное меню:", reply_markup=markup)
#     db_state(message)
#     bot.register_next_step_handler(msg, menu_2)
#
#
# def menu_2(message):
#     print('something')
#     # try:
#     #     if message.text== "АРМ":
#     #         arm_stand_select(message)
#     #     if message.text== "Пентаха":
#     #         pentaho_action_select(message)
#     #     if message.text== "Портал":
#     #         portal_action_select(message)
#     #     if message.text== "Мобильное приложение":
#     #         mobile_action_select(message)
#     #     if message.text== "Интеграционная подсистема":
#     #         integration_action_select(message)
#     #     if message.text== "Сбор":
#     #         pizi_action_select(message)
#     #     if message.text== "ПОИБ":
#     #         poib_action_select(message)
#     #     if message.text== "Перезапуск":
#     #         system_action_select(message)
#     #     if message.text== "Синхронизация стендов":
#     #         sync_start(message)
#     # except Exception as e:
#     #     errors(message)

@bot.message_handler(commands=["start"])
@bot.message_handler(func=lambda message: database.db_state(message) == 'menu')
def menu(message):
    # markup = types.ReplyKeyboardMarkup(row_width=3, one_time_keyboard=True)
    # markup.add("АРМ", "Пентаха", "Портал", "Мобильное приложение", "Интеграционная подсистема", "Сбор", "ПОИБ", "Перезапуск", "Синхронизация стендов", "Переподключиться")
    # msg = bot.reply_to(message, "Главное меню:", reply_markup=markup)
    # bot.register_next_step_handler(msg, database.db_step, 'app', 'pass', 'build_deploy')
    bot.send_message(message.chat.id, "Выбери, с чем будем работать")
    database.db_step(message, 'app', 'pass', 'buid_deploy')

@bot.message_handler(func=lambda message: database.db_state(message) == 'build_deploy')
def build_and_deploy(message):
    bot.send_message(message.chat.id, "Мы будем работать с " + message.text)



while True:
    bot.polling(none_stop=True)