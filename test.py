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

@bot.message_handler(commands=['start'])
def handle_start_help(message):
    text = "{}({}): инициализировался".format(message.chat.username, message.chat.id)
    print(text)
    bot.send_message(message.chat.id, "Привет, друг. Тут нет ничего интересного - уходи.")

@bot.message_handler(commands=['help'])
def handle_start_help(message):
    text = "{}({}): решил почитать /help".format(message.chat.username, message.chat.id)
    print(text)
    bot.send_message(message.chat.id, "Вот такой вот стремный /help.")

@bot.message_handler(commands=['helppp'])
def handle_start_help(message):
    text = "{}({}): решил почитать настоящий /help ;-)".format(message.chat.username, message.chat.id)
    print(text)
    bot.send_message(message.chat.id, """
Сборка АРМ: /gistek_build_arm \n
Подсистема Пентахо: /gistek_pentaho \n
Подсистема Портал: /gistek_portal  \n
Подсистема мобильного приложения: /gistek_mobile \n
Подсистема ПИЗИ: /gistek_pizi""")

user_dict = {}

class Var:
    def __init__(self, name):
        self.stend = name
        self.arm = None
        self.build_deloy = None
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
        stend = message.text
        var = Var(stend)
        user_dict[chat_id] = var
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("admin_kl", "admin_net", "all_mak_inf", "arm_access", "fpi-autoregistration", "gis_des", "is_transport", "kontrol", "load_ssb", "offline", "template_cleaner", "wmk_gistek")
        msg = bot.reply_to(message, "Выберите АРМ", reply_markup=markup)
        bot.register_next_step_handler(msg, arm_issue_select)
    except Exception as e:
        bot.reply_to(message, 'oooops1')

def arm_issue_select(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("Yes", "No")
        msg = bot.reply_to(message, "Есть задача?", reply_markup=markup)
        bot.register_next_step_handler(msg, arm_issue)
    except Exception as e:
        bot.reply_to(message, 'oooops2')

def arm_issue(message):
    try:
        chat_id = message.chat.id
        issue_select = message.text
        var = user_dict[chat_id]
        var.issue_select = issue_select
        if var.issue_select == "No":
            msg = bot.reply_to(message, "Введите 0:")
        if var.issue_select == "Yes":
            msg = bot.reply_to(message, "Введите номер:")
        bot.register_next_step_handler(msg, arm_job_jenkins)
    except Exception as e:
        bot.reply_to(message, 'oooops3')

def arm_job_jenkins(message):
    try:
        chat_id = message.chat.id
        issue_id = message.text
        var = user_dict[chat_id]
        var.issue_id = issue_id
        if var.issue_select == "No":
            params = {"stend": var.stend}
        if var.issue_select == "Yes":
            params = {"stend": var.stend, "issue_id": var.issue_id}
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        print(name_user + "cтучится в jenkins чтобы собрать " + str(var.arm) + " для " + var.stend)
        jenkins.build_job('GISTEK_Pizi/Build_ARM/' + str(var.arm), params)
        print(name_user + "собирает " + str(var.arm) + " на " + var.stend)
        bot.send_message(message.chat.id, "..еще 5 минуточек и " + str(var.arm) + ", для " + var.stend + " соберется (если ошибки в jenkins не будет), а пока можно продолжать..")
    except Exception as e:
        bot.reply_to(message, 'oooops4')

@bot.message_handler(commands=['gistek_pentaho'])
def action_select(message):
    global name_user
    name_user = "{}({}): ".format(message.chat.username, message.chat.id)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Build', 'Deploy (not work yet)')
    msg = bot.reply_to(message, "Выберите, что будем делать", reply_markup=markup)
    bot.register_next_step_handler(msg, pentaho_app_select)

def pentaho_app_select(message):
    try:
        chat_id = message.chat.id
        build_deloy = message.text
        var = Var(build_deloy)
        user_dict[chat_id] = var
        var.build_deloy = build_deloy
        if var.build_deloy == "Build":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add("FileProperties", "integr_clearcache", "integr_readmetadata", "languagePack", "pentaho-cas-tek", "Plugin", "quixote-theme")
            msg = bot.reply_to(message, "Выберите плагин для сборки:", reply_markup=markup)
            bot.register_next_step_handler(msg, pentaho_job_jenkins)
    except Exception as e:
        bot.reply_to(message, 'oooops1')

def pentaho_job_jenkins(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        print(name_user + "cтучится в jenkins чтобы собрать для пентахи " + str(var.arm))
        jenkins.build_job('GISTEK_Pentaho/Build_' + str(var.arm))
        print(name_user + "собирает " + str(var.arm))
        bot.send_message(message.chat.id, "..еще 5 минуточек и плагин " + str(var.arm) + " соберется (если ошибки в jenkins не будет), а пока можно продолжать..")
    except Exception as e:
        bot.reply_to(message, 'oooops4')

@bot.message_handler(commands=['gistek_portal'])
def action_select(message):
    global name_user
    name_user = "{}({}): ".format(message.chat.username, message.chat.id)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Build', 'Deploy (not work yet)')
    msg = bot.reply_to(message, "Выберите, что будем делать", reply_markup=markup)
    bot.register_next_step_handler(msg, portal_app_select)

def portal_app_select(message):
    try:
        chat_id = message.chat.id
        build_deloy = message.text
        var = Var(build_deloy)
        user_dict[chat_id] = var
        var.build_deloy = build_deloy
        if var.build_deloy == "Build":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add("languagePackRU", "support-mail-portlet", "hook-search", "subsystem-search", "hook-asset-publisher", "urc-theme", "mainpageGEO", "slider", "npa-loader", "inspinia-theme", "login-hook", "reports-display-portlet")
            msg = bot.reply_to(message, "Выберите портлет для сборки:", reply_markup=markup)
            bot.register_next_step_handler(msg, portal_job_jenkins)
    except Exception as e:
        bot.reply_to(message, 'oooops1')

def portal_job_jenkins(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        print(name_user + "cтучится в jenkins чтобы собрать портлет " + str(var.arm))
        jenkins.build_job('GISTEK_Portal/' + str(var.arm))
        print(name_user + "собирает " + str(var.arm))
        bot.send_message(message.chat.id, "..еще 5 минуточек и портлет " + str(var.arm) + " соберется (если ошибки в jenkins не будет), а пока можно продолжать..")
    except Exception as e:
        bot.reply_to(message, 'oooops4')

@bot.message_handler(commands=['gistek_mobile'])
def action_select(message):
    global name_user
    name_user = "{}({}): ".format(message.chat.username, message.chat.id)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Build', 'Deploy (not work yet)')
    msg = bot.reply_to(message, "Выберите, что будем делать", reply_markup=markup)
    bot.register_next_step_handler(msg, mobile_app_select)

def mobile_app_select(message):
    try:
        chat_id = message.chat.id
        build_deloy = message.text
        var = Var(build_deloy)
        user_dict[chat_id] = var
        var.build_deloy = build_deloy
        if var.build_deloy == "Build":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add("Android", "tek-portlet", "web-service-java")
            msg = bot.reply_to(message, "Выберите приложение для сборки:", reply_markup=markup)
            bot.register_next_step_handler(msg, mobile_job_jenkins)
    except Exception as e:
        bot.reply_to(message, 'oooops1')

def mobile_job_jenkins(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        print(name_user + "cтучится в jenkins чтобы собрать приложение " + str(var.arm))
        jenkins.build_job('GISTEK_MobileApp/Build_' + str(var.arm))
        print(name_user + "собирает " + str(var.arm))
        bot.send_message(message.chat.id, "..еще 5 минуточек и приложение " + str(var.arm) + " соберется (если ошибки в jenkins не будет), а пока можно продолжать..")
    except Exception as e:
        bot.reply_to(message, 'oooops4')

@bot.message_handler(commands=['gistek_integration'])
def action_select(message):
    global name_user
    name_user = "{}({}): ".format(message.chat.username, message.chat.id)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Build', 'Deploy (not work yet)')
    msg = bot.reply_to(message, "Выберите, что будем делать", reply_markup=markup)
    bot.register_next_step_handler(msg, integration_app_select)

def integration_app_select(message):
    try:
        chat_id = message.chat.id
        build_deloy = message.text
        var = Var(build_deloy)
        user_dict[chat_id] = var
        var.build_deloy = build_deloy
        if var.build_deloy == "Build":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add("Build")
            msg = bot.reply_to(message, "Выберите приложение для сборки:", reply_markup=markup)
            bot.register_next_step_handler(msg, integration_job_jenkins)
    except Exception as e:
        bot.reply_to(message, 'oooops1')

def integration_job_jenkins(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        print(name_user + "cтучится в jenkins чтобы собрать приложение " + str(var.arm) + " для интеграционной подситсемы")
        jenkins.build_job('GISTEK_Integration/' + str(var.arm))
        print(name_user + "собирает для интеграционной подсистемы " + str(var.arm))
        bot.send_message(message.chat.id, "..еще 5 минуточек и приложение " + str(var.arm) + " для интеграционной подсистемы соберется (если ошибки в jenkins не будет), а пока можно продолжать..")
    except Exception as e:
        bot.reply_to(message, 'oooops4')

@bot.message_handler(commands=['gistek_pizi'])
def action_select(message):
    global name_user
    name_user = "{}({}): ".format(message.chat.username, message.chat.id)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Build', 'Deploy')
    msg = bot.reply_to(message, "Выберите, что будем делать", reply_markup=markup)
    bot.register_next_step_handler(msg, pizi_stend_select)

def pizi_stend_select(message):
    try:
        chat_id = message.chat.id
        build_deloy = message.text
        var = Var(build_deloy)
        user_dict[chat_id] = var
        var.build_deloy = build_deloy
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('REA_TEST', 'PK', 'PI')
        msg = bot.reply_to(message, "Выберите стенд", reply_markup=markup)
        bot.register_next_step_handler(msg, pizi_app_select)
    except Exception as e:
        bot.reply_to(message, 'oooops1')

def pizi_app_select(message):
    try:
        chat_id = message.chat.id
        stend = message.text
        var = user_dict[chat_id]
        var.stend = stend
        if var.build_deloy == "Build":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add("App", "DB_change_script", "DB_refresh_db")
            msg = bot.reply_to(message, "Выберите приложение для сборки:", reply_markup=markup)
            bot.register_next_step_handler(msg, pizi_job_jenkins)
        if var.build_deloy == "Deploy":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add("App", "Robot")
            msg = bot.reply_to(message, "Выберите приложение для обновления:", reply_markup=markup)
            bot.register_next_step_handler(msg, pizi_job_jenkins)
    except Exception as e:
        bot.reply_to(message, 'oooops2')

def pizi_job_jenkins(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        if var.build_deloy == "Build":
            print(name_user + "cтучится в jenkins чтобы собрать приложение " + str(var.arm) + " для Сбора")
            jenkins.build_job('GISTEK_Pizi/Build_' + str(var.arm))
            print(name_user + "собирает для сбора " + str(var.arm))
            bot.send_message(message.chat.id, "..еще 5 минуточек и " + str(var.arm) + " для сбора соберется (если ошибки в jenkins не будет), а пока можно продолжать..")
        if var.build_deloy == "Deploy":
            params = {"stend": var.stend}
            print(name_user + "cтучится в jenkins чтобы собрать обновить " + str(var.arm) + " для Сбора")
            jenkins.build_job('GISTEK_Pizi/Update_' + str(var.arm), params)
            print(name_user + "обновляет на Сборе " + str(var.arm))
            bot.send_message(message.chat.id, "..еще 5 минуточек и приложение " + str(var.arm) + " на Сборе обновится (если ошибки в jenkins не будет), а пока можно продолжать..")
    except Exception as e:
        bot.reply_to(message, 'oooops3')

bot.polling()
