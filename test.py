#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time

import jenkinsapi
from jenkinsapi.jenkins import Jenkins

import config
import telebot
from telebot import types

jenkins = Jenkins("http://jenkins.gistek.lanit.ru", username=config.username, password=config.password)
bot = telebot.TeleBot(config.token)

print("В jenkins авторизовались")


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    text = "{}({}): решил почитать /help".format(message.chat.username, message.chat.id)
    print(text)
    bot.send_message(message.chat.id, "Вот такой вот стремный /help.")

@bot.message_handler(commands=['helppp'])
def handle_start_help(message):
    text = "{}({}): решил почитать настоящий /help ;-)".format(message.chat.username, message.chat.id)
    print(text)
    bot.send_message(message.chat.id, "Сборка АРМ: /gistek_build_arm")

user_dict = {}

class User:
    def __init__(self, name):
        self.name = name
        self.arm = None
        self.issue_select = None
        self.issue_id = None

@bot.message_handler(commands=['gistek_build_arm'])
def stend_select(message):
    global name_user
    name_user = "{}({}): ".format(message.chat.username, message.chat.id)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('REA_TEST', 'PK', 'PI')
    msg = bot.reply_to(message, "Выберите стенд", reply_markup=markup)
    bot.register_next_step_handler(msg, arm_select)

def arm_select(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = User(name)
        user_dict[chat_id] = user
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("admin_kl", "admin_net", "all_mak_inf", "arm_access", "fpi_autoregistration", "gis_des", "is_transport", "kontrol", "load_ssb", "offline", "template_cleaner", "wmk_gistek")
        msg = bot.reply_to(message, "Выберите АРМ", reply_markup=markup)
        bot.register_next_step_handler(msg, issue_select)
    except Exception as e:
        bot.reply_to(message, 'oooops1')

def issue_select(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        user = user_dict[chat_id]
        user.arm = arm
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("Yes", "No")
        msg = bot.reply_to(message, "Есть задача?", reply_markup=markup)
        bot.register_next_step_handler(msg, issue)
    except Exception as e:
        bot.reply_to(message, 'oooops2')

def issue(message):
    try:
        chat_id = message.chat.id
        issue_select = message.text
        user = user_dict[chat_id]
        user.issue_select = issue_select
        if user.issue_select == "No":
            msg = bot.reply_to(message, "Введите 0:")
        if user.issue_select == "Yes":
            msg = bot.reply_to(message, "Введите номер:")
        bot.register_next_step_handler(msg, job_jenkins)
    except Exception as e:
        bot.reply_to(message, 'oooops3')

def job_jenkins(message):
    try:
        chat_id = message.chat.id
        issue_id = message.text
        user = user_dict[chat_id]
        user.issue_id = issue_id
        if user.issue_select == "No":
            params = {"stend": user.name}
        if user.issue_select == "Yes":
            params = {"stend": user.name, "issue_id": user.issue_id}
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        print(name_user + "cтучится в jenkins чтобы собрать " + str(user.arm) + " для " + user.name)
        jenkins.build_job('GISTEK_Pizi/Build_ARM/' + str(user.arm), params)
        print(name_user + "собирает " + str(user.arm) + " на " + user.name)
        bot.send_message(message.chat.id, "..еще 5 минуточек и " + str(user.arm) + " , для " + user.name + " соберется (если ошибки в jenkins не будет), а пока можно продолжать..")
    except Exception as e:
        bot.reply_to(message, 'oooops4')

bot.polling()
