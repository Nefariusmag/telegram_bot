#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def lock_file(fname):
    import fcntl
    _lock_file = open(fname, 'a+')
    try:
        fcntl.flock(_lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        return "Процесс уже используется."
    return _lock_file

lock = lock_file('telegram_jenkins.py')

import time

import jenkinsapi
from jenkinsapi.jenkins import Jenkins

import logging
logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.INFO, filename = u'telegram_bot.log')

import config
import telebot
from telebot import types

i = 0
while i != 1:
    try:
        jenkins = Jenkins("http://jenkins.gistek.lanit.ru", username=config.username, password=config.password)
        jenkins_dkp = Jenkins("http://jenkins-gistek.dkp.lanit.ru", username=config.username, password=config.password)
        bot = telebot.TeleBot(config.token)
        i = 1
    except Exception as e:
        logging.error(u"Авторизация не прошла, пробуем еще раз")

logging.warning(u'В jenkins авторизовались')

def secure(message):
    global user_true
    if message.chat.id in config.true_id:
        text = "Пользователь {} прошел проверку безопасности".format(message.chat.id)
        logging.warning( u"%s", text)
        user_true = "true"
    else:
        text = "Пользователь {} не прошел проверку безопасности".format(message.chat.id)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "Соррян, у вас нету нужных прав.")
        user_true = "false"

@bot.message_handler(commands=['start'])
def handle_start(message):
    text = "{}({}): инициализировался".format(message.chat.username, message.chat.id)
    logging.warning( u"%s", text)
    bot.send_message(message.chat.id, "Привет, друг. Тут нет ничего интересного - уходи.")

@bot.message_handler(commands=['helppp'])
def handle_true_help(message):
    text = "{}({}): решил почитать настоящий /help ;-)".format(message.chat.username, message.chat.id)
    logging.warning( u"%s", text)
    id_user = message.chat.id
    secure(message)
    if user_true == "true":
        bot.send_message(message.chat.id, """Что я умею!

Сборка АРМ: /gistek_build_arm \n
Подсистема Пентахо: /gistek_pentaho \n
Подсистема Портал: /gistek_portal  \n
Подсистема мобильного приложения: /gistek_mobile \n
Подсистема интеграционная: /gistek_integration \n
Подсистема ПИЗИ: /gistek_pizi \n
Подсистема ПОИБ: /gistek_poib \n
Перезапуск подсистем /restart_system \n

Синхронизация данных между стендами: /sync""")

@bot.message_handler(commands=['help'])
def handle_help(message):
    text = "{}({}): решил почитать /help".format(message.chat.username, message.chat.id)
    logging.warning( u"%s", text)
    bot.send_message(message.chat.id, "Вот такой вот стремный /help.")

user_dict = {}

class Var:
    def __init__(self, name):
        self.build_deloy = None
        self.stend = name
        self.arm = None
        self.issue_select = None
        self.issue_id = None
        self.tag = None
        self.open_close = None

@bot.message_handler(commands=['sync'])
def sync_start(message):
    secure(message)
    if user_true == "true":
        global name_user
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('sync_dev_pk', 'sync_pk_pi', 'sync_pk_pp')
        msg = bot.reply_to(message, "Выберите откуда куда передаем данные", reply_markup=markup)
        bot.register_next_step_handler(msg, sync_select)

def sync_select(message):
    try:
        chat_id = message.chat.id
        stend = message.text
        var = Var(stend)
        user_dict[chat_id] = var
        text = "{} запускает {}".format(name_user, var.stend)
        logging.warning( u"%s", text)
        jenkins_dkp.build_job(str(var.stend))
    except Exception as e:
        text = "{} неведомая херня, но джоба выполняется, прячу багу".format(name_user)
        logging.warning( u"%s", text)
    text = "{} запустилась {}".format(name_user, var.stend)
    logging.warning( u"%s", text)
    bot.send_message(message.chat.id, "Запустилась синхронизация, в среднем выполняется 45 минут. Можно продолжать работу.")

@bot.message_handler(commands=['gistek_build_arm'])
def stend_select(message):
    secure(message)
    if user_true == "true":
        global name_user
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
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
        markup.add("admin_kl", "admin_net", "all_mak_inf", "arm_access", "fpi-autoregistration", "gis_des", "is_transport", "kontrol", "load_ssb", "offline", "template_cleaner", "wmk_gistek", "arm_remover")
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
        text = "{} cтучится в jenkins чтобы собрать {} для {}".format(name_user, var.arm, var.stend)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        jenkins.build_job('GISTEK_Pizi/Build_ARM/' + str(var.arm), params)
        text = "{} собирает {} на {}".format(name_user, var.arm, var.stend)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "..еще 5 минуточек и " + str(var.arm) + ", для " + var.stend + " соберется (если ошибки в jenkins не будет), а пока можно продолжать..")
    except Exception as e:
        bot.reply_to(message, 'oooops4')

##### start

@bot.message_handler(commands=['gistek_pentaho'])
def action_select(message):
    secure(message)
    if user_true == "true":
        global name_user
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Build', 'Deploy')
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
            markup.add("fileProperties", "integr_clearcache", "integr_readmetadata", "langpack", "cas_tek", "plugins", "quixote_theme")
            msg = bot.reply_to(message, "Выберите плагин для сборки:", reply_markup=markup)
            bot.register_next_step_handler(msg, pentaho_build_job_jenkins)
        if var.build_deloy == "Deploy":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('REA_TEST', 'PK', 'PI')
            msg = bot.reply_to(message, "Выберите стенд", reply_markup=markup)
            bot.register_next_step_handler(msg, pentaho_app_2_select)
    except Exception as e:
        bot.reply_to(message, 'oooops1')

def pentaho_app_2_select(message):
    try:
        chat_id = message.chat.id
        stend = message.text
        var = user_dict[chat_id]
        var.stend = stend
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("update_plugins", "update_fileProperties", "update_quixote_theme", "update_langpack", "update_cas_tek", "update_mondrian")
        msg = bot.reply_to(message, "Выберите что будем обновлять:", reply_markup=markup)
        bot.register_next_step_handler(msg, pentaho_tag_select)
    except Exception as e:
        bot.reply_to(message, 'oooops2')

def pentaho_tag_select(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        msg = bot.reply_to(message, "Введите номер версии (тег):")
        bot.register_next_step_handler(msg, pentaho_issue_select)
    except Exception as e:
        bot.reply_to(message, 'oooops3')

def pentaho_issue_select(message):
    try:
        chat_id = message.chat.id
        tag = message.text
        var = user_dict[chat_id]
        var.tag = tag
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("Yes", "No")
        msg = bot.reply_to(message, "Есть задача?", reply_markup=markup)
        bot.register_next_step_handler(msg, pentaho_issue)
    except Exception as e:
        bot.reply_to(message, 'oooops4')

def pentaho_issue(message):
    try:
        chat_id = message.chat.id
        issue_select = message.text
        var = user_dict[chat_id]
        var.issue_select = issue_select
        if var.issue_select == "No":
            msg = bot.reply_to(message, "Введите 0:")
        if var.issue_select == "Yes":
            msg = bot.reply_to(message, "Введите номер:")
        bot.register_next_step_handler(msg, pentaho_job_jenkins)
    except Exception as e:
        bot.reply_to(message, 'oooops5')

def pentaho_job_jenkins(message):
    try:
        chat_id = message.chat.id
        issue_id = message.text
        var = user_dict[chat_id]
        var.issue_id = issue_id
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        if var.issue_select == "No":
            if var.arm == "update_plugins":
                params = {"stend": var.stend, "tags": str(var.arm), "version": str(var.tag)}
            if var.arm == "update_fileProperties":
                params = {"stend": var.stend, "tags": str(var.arm), "version": str(var.tag)}
            if var.arm == "update_quixote_theme":
                params = {"stend": var.stend, "tags": str(var.arm), "version": str(var.tag)}
            if var.arm == "update_langpack":
                params = {"stend": var.stend, "tags": str(var.arm), "version": str(var.tag)}
            if var.arm == "update_cas_tek":
                params = {"stend": var.stend, "tags": str(var.arm), "version": str(var.tag)}
            if var.arm == "update_mondrian":
                params = {"stend": var.stend, "tags": str(var.arm)}
        if var.issue_select == "Yes":
            if var.arm == "update_plugins":
                params = {"stend": var.stend, "tags": str(var.arm), "issue_id": var.issue_id, "version": str(var.tag)}
            if var.arm == "update_fileProperties":
                params = {"stend": var.stend, "tags": str(var.arm), "issue_id": var.issue_id, "version": str(var.tag)}
            if var.arm == "update_quixote_theme":
                params = {"stend": var.stend, "tags": str(var.arm), "issue_id": var.issue_id, "version": str(var.tag)}
            if var.arm == "update_langpack":
                params = {"stend": var.stend, "tags": str(var.arm), "issue_id": var.issue_id, "version": str(var.tag)}
            if var.arm == "update_cas_tek":
                params = {"stend": var.stend, "tags": str(var.arm), "issue_id": var.issue_id, "version": str(var.tag)}
            if var.arm == "update_mondrian":
                params = {"stend": var.stend, "tags": str(var.arm), "issue_id": var.issue_id,}
        text = "{} cтучится в jenkins чтобы выполнить {} для ПОИБ".format(name_user, var.arm)
        logging.warning( u"%s", text)
        jenkins.build_job('GISTEK_Pentaho/Update_Pentaho', params)
        text = "{} на ПОИБ выполняется {} версия {}".format(name_user, var.arm, var.tag)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "..еще 7 минут и приложение " + str(var.arm) + " на ПОИБ обновится, версия " + str(var.tag) + " (если ошибки в jenkins не будет), а пока можно продолжать..")
    except Exception as e:
        bot.reply_to(message, 'oooops6')

def pentaho_build_job_jenkins(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        text = "{} cтучится в jenkins чтобы собрать для пентахи  {}".format(name_user, var.arm)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        jenkins.build_job('GISTEK_Pentaho/Build_' + str(var.arm))
        text = "{} собирает {}".format(name_user, var.arm)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "..еще 5 минуточек и плагин " + str(var.arm) + " соберется (если ошибки в jenkins не будет), а пока можно продолжать..")
    except Exception as e:
        bot.reply_to(message, 'oooops7')

##### finish

@bot.message_handler(commands=['gistek_portal'])
def action_select(message):
    secure(message)
    if user_true == "true":
        global name_user
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Build', 'Deploy')
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
            markup.add("hook-asset-publisher", "hook-search", "inspinia-theme", "languagePackRU", "login-hook", "mainpageGEO", "notification-portlet", "npa-loader", "portal-iframe", "reports-display-portlet", "slider", "subsystem-search", "support-mail-portlet", "urc-theme")
            msg = bot.reply_to(message, "Выберите портлет для сборки:", reply_markup=markup)
            bot.register_next_step_handler(msg, portal_build_job_jenkins)
        if var.build_deloy == "Deploy":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('REA_TEST', 'PK', 'PI')
            msg = bot.reply_to(message, "Выберите стенд:", reply_markup=markup)
            bot.register_next_step_handler(msg, portal_public_internal_select)
    except Exception as e:
        bot.reply_to(message, 'oooops1')

def portal_public_internal_select(message):
    try:
        chat_id = message.chat.id
        stend = message.text
        var = user_dict[chat_id]
        var.stend = stend
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('public', 'internal')
        msg = bot.reply_to(message, "Открытая или закрытая часть портала?", reply_markup=markup)
        bot.register_next_step_handler(msg, portal_app_2_select)
    except Exception as e:
        bot.reply_to(message, 'oooops2')

def portal_app_2_select(message):
    try:
        chat_id = message.chat.id
        open_close = message.text
        var = user_dict[chat_id]
        var.open_close = open_close
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("hook-asset-publisher", "hook-search", "inspinia-theme", "languagePackRU", "login-hook", "mainpageGEO", "notification-portlet", "npa-loader", "portal-iframe", "reports-display-portlet", "slider", "subsystem-search", "support-mail-portlet", "urc-theme")
        msg = bot.reply_to(message, "Выберите какой портлет будем обновлять:", reply_markup=markup)
        bot.register_next_step_handler(msg, portal_tag_select)
    except Exception as e:
        bot.reply_to(message, 'oooops3')

def portal_tag_select(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        msg = bot.reply_to(message, "Введите номер версии (тег):")
        bot.register_next_step_handler(msg, portal_issue_select)
    except Exception as e:
        bot.reply_to(message, 'oooops4')

def portal_issue_select(message):
    try:
        chat_id = message.chat.id
        tag = message.text
        var = user_dict[chat_id]
        var.tag = tag
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("Yes", "No")
        msg = bot.reply_to(message, "Есть задача?", reply_markup=markup)
        bot.register_next_step_handler(msg, portal_issue)
    except Exception as e:
        bot.reply_to(message, 'oooops5')

def portal_issue(message):
    try:
        chat_id = message.chat.id
        issue_select = message.text
        var = user_dict[chat_id]
        var.issue_select = issue_select
        if var.issue_select == "No":
            msg = bot.reply_to(message, "Введите 0:")
        if var.issue_select == "Yes":
            msg = bot.reply_to(message, "Введите номер:")
        bot.register_next_step_handler(msg, portal_job_jenkins)
    except Exception as e:
        bot.reply_to(message, 'oooops6')

def portal_job_jenkins(message):
    try:
        chat_id = message.chat.id
        issue_id = message.text
        var = user_dict[chat_id]
        var.issue_id = issue_id
        text = "{} cтучится в jenkins чтобы обновить {} на портале {} в {}".format(name_user, var.arm, var.stend, var.open_close)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        if var.issue_select == "No":
            params = {"stend": var.stend, "public_internal": str(var.open_close), "TARGET_TAGS": str(var.arm), "version": str(var.tag)}
        if var.issue_select == "Yes":
            params = {"stend": var.stend, "public_internal": str(var.open_close), "TARGET_TAGS": str(var.arm), "issue_id": var.issue_id, "version": str(var.tag)}
        jenkins.build_job('GISTEK_Portal/Update_App', params)
        text = "{} на портале {} обновляет {}".format(name_user, var.stend, var.arm)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "..еще 2 минуты и " + str(var.arm) + " на портале " + str(var.stend) + " обновится, версия " + str(var.tag) + " (если ошибки в jenkins не будет), а пока можно продолжать..")
    except Exception as e:
        bot.reply_to(message, 'oooops7')

def portal_build_job_jenkins(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        text = "{} cтучится в jenkins чтобы собрать портлет  {}".format(name_user, var.arm)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        jenkins.build_job('GISTEK_Portal/' + str(var.arm))
        text = "{} собирает {}".format(name_user, var.arm)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "..еще 1 минута (или даже меньше) и портлет " + str(var.arm) + " соберется (если ошибки в jenkins не будет), а пока можно продолжать..")
    except Exception as e:
        bot.reply_to(message, 'oooops8')

@bot.message_handler(commands=['gistek_mobile'])
def action_select(message):
    global name_user
    name_user = "{}({}):".format(message.chat.username, message.chat.id)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Build', 'Deploy')
    msg = bot.reply_to(message, "Выберите, что будем делать", reply_markup=markup)
    bot.register_next_step_handler(msg, mobile_action_select)

def mobile_action_select(message):
    try:
        chat_id = message.chat.id
        build_deloy = message.text
        var = Var(build_deloy)
        user_dict[chat_id] = var
        var.build_deloy = build_deloy
        if var.build_deloy == "Build":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add("Android", "portlet", "web_service")
            msg = bot.reply_to(message, "Выберите приложение для сборки:", reply_markup=markup)
            bot.register_next_step_handler(msg, mobile_job_build_jenkins)
        if var.build_deloy == "Deploy":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('REA_TEST', 'PI')
            msg = bot.reply_to(message, "Выберите стенд", reply_markup=markup)
            bot.register_next_step_handler(msg, mobile_app_select)
    except Exception as e:
        bot.reply_to(message, 'oooops1')

def mobile_job_build_jenkins(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        text = "{} cтучится в jenkins чтобы собрать приложение {}".format(name_user, var.arm)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        jenkins.build_job('GISTEK_MobileApp/Build_' + str(var.arm))
        text = "{} собирает {}".format(name_user, var.arm)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "..еще 5 минуточек и приложение " + str(var.arm) + " соберется (если ошибки в jenkins не будет), а пока можно продолжать..")
    except Exception as e:
        bot.reply_to(message, 'oooops2')


def mobile_app_select(message):
    try:
        chat_id = message.chat.id
        stend = message.text
        var = user_dict[chat_id]
        var.stend = stend
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("update_web_service", "update_portlet")
        msg = bot.reply_to(message, "Выберите что будем обновлять:", reply_markup=markup)
        bot.register_next_step_handler(msg, mobile_tag_select)
    except Exception as e:
        bot.reply_to(message, 'oooops2')

def mobile_tag_select(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        msg = bot.reply_to(message, "Введите номер версии (тег):")
        bot.register_next_step_handler(msg, mobile_job_jenkins)
    except Exception as e:
        bot.reply_to(message, 'oooops3')

def mobile_job_jenkins(message):
    try:
        chat_id = message.chat.id
        tag = message.text
        var = user_dict[chat_id]
        var.tag = tag
        params = {"stand": var.stend, "tags": str(var.arm), "version": str(var.tag)}
        text = "{} cтучится в jenkins чтобы обновить {} для мобильного приложения".format(name_user, var.arm)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        jenkins.build_job('GISTEK_MobileApp/Update', params)
        text = "{} для мобильного приложения выполняется {} тег {}".format(name_user, var.arm, var.tag)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "..еще 2 минуты и обновится " + str(var.arm) + " для мобильного приложения, версия " + str(var.tag) + " (если ошибки в jenkins не будет), а пока можно продолжать..")
    except Exception as e:
        bot.reply_to(message, 'oooops4')

@bot.message_handler(commands=['gistek_integration'])
def action_select(message):
    secure(message)
    if user_true == "true":
        global name_user
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Build', 'Deploy')
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
            markup.add('REA_TEST', 'PI')
            msg = bot.reply_to(message, "Выберите стенд", reply_markup=markup)
            bot.register_next_step_handler(msg, integration_build_stand_select)
        if var.build_deloy == "Deploy":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('REA_TEST', 'PI')
            msg = bot.reply_to(message, "Выберите стенд", reply_markup=markup)
            bot.register_next_step_handler(msg, integration_stand_select)
    except Exception as e:
        bot.reply_to(message, 'oooops1')

def integration_stand_select(message):
    try:
        chat_id = message.chat.id
        stend = message.text
        var = user_dict[chat_id]
        var.stend = stend
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("update", "update_generator")
        msg = bot.reply_to(message, "Выберите приложение для обновления:", reply_markup=markup)
        bot.register_next_step_handler(msg, integration_tag_select)
    except Exception as e:
        bot.reply_to(message, 'oooops2')

def integration_build_stand_select(message):
    try:
        chat_id = message.chat.id
        stend = message.text
        var = user_dict[chat_id]
        var.stend = stend
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("Build_mis", "Build_generator", "Build_LogUI")
        msg = bot.reply_to(message, "Выберите приложение для сборки:", reply_markup=markup)
        bot.register_next_step_handler(msg, integration_build_tag_select)
    except Exception as e:
        bot.reply_to(message, 'oooops2')

def integration_tag_select(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        msg = bot.reply_to(message, "Введите номер версии (тег):")
        bot.register_next_step_handler(msg, integration_job_jenkins)
    except Exception as e:
        bot.reply_to(message, 'oooops3')

def integration_build_tag_select(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        msg = bot.reply_to(message, "Введите номер версии (тег):")
        bot.register_next_step_handler(msg, integration_build_job_jenkins)
    except Exception as e:
        bot.reply_to(message, 'oooops3')

def integration_build_job_jenkins(message):
    try:
        chat_id = message.chat.id
        tag = message.text
        var = user_dict[chat_id]
        var.tag = tag
        params = {"stand": var.stend, "version": str(var.tag)}
        text = "{} cтучится в jenkins чтобы собрать приложение {} для интеграционной подсистемы".format(name_user, var.arm)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        jenkins.build_job('GISTEK_Integration/' + str(var.arm), params)
        text = "{} собирает для интеграционной подсистемы {}".format(name_user, var.arm)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "..еще 3 минуты и приложение " + str(var.arm) + " для интеграционной подсистемы соберется (если ошибки в jenkins не будет), а пока можно продолжать..")
    except Exception as e:
        bot.reply_to(message, 'oooops3')

def integration_job_jenkins(message):
    try:
        chat_id = message.chat.id
        tag = message.text
        var = user_dict[chat_id]
        var.tag = tag
        params = {"stand": var.stend, "tags": str(var.arm), "version": str(var.tag)}
        text = "{} cтучится в jenkins чтобы обновить приложение {} для интеграционной подсистемы".format(name_user, var.arm)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        jenkins.build_job('GISTEK_Integration/Update', params)
        text = "{} обновляет на интеграционной подсистеме {}".format(name_user, var.arm)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "..еще 5 минуточек и приложение " + str(var.arm) + " для интеграционной подсистемы выкатится (если ошибки в jenkins не будет), а пока можно продолжать..")
    except Exception as e:
        bot.reply_to(message, 'oooops4')

@bot.message_handler(commands=['gistek_pizi'])
def action_select(message):
    secure(message)
    if user_true == "true":
        global name_user
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
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
            text = "{} cтучится в jenkins чтобы собрать приложение {} для Сбора".format(name_user, var.arm)
            logging.warning( u"%s", text)
            jenkins.build_job('GISTEK_Pizi/Build_' + str(var.arm))
            text = "{} собирает для сбора {}".format(name_user, var.arm)
            logging.warning( u"%s", text)
            bot.send_message(message.chat.id, "..еще 5 минуточек и " + str(var.arm) + " для сбора соберется (если ошибки в jenkins не будет), а пока можно продолжать..")
        if var.build_deloy == "Deploy":
            params = {"stend": var.stend}
            text = "{} cтучится в jenkins чтобы собрать обновить {} для Сбора на {}".format(name_user, var.arm, var.stend)
            logging.warning( u"%s", text)
            jenkins.build_job('GISTEK_Pizi/Update_' + str(var.arm), params)
            text = "{} обновляет на Сборе {}".format(name_user, var.arm)
            logging.warning( u"%s", text)
            bot.send_message(message.chat.id, "..еще 2 минуты и приложение " + str(var.arm) + " на Сборе обновится (если ошибки в jenkins не будет), а пока можно продолжать..")
    except Exception as e:
        bot.reply_to(message, 'oooops3')

@bot.message_handler(commands=['gistek_poib'])
def action_select(message):
    secure(message)
    if user_true == "true":
        global name_user
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Build', 'Deploy')
        msg = bot.reply_to(message, "Выберите, что будем делать", reply_markup=markup)
        bot.register_next_step_handler(msg, poib_select)

def poib_select(message):
    try:
        chat_id = message.chat.id
        build_deloy = message.text
        var = Var(build_deloy)
        user_dict[chat_id] = var
        var.build_deloy = build_deloy
        if var.build_deloy == "Build":
            bot.send_message(message.chat.id, "пыжимся и тужимся... ")
            text = "{} cтучится в jenkins чтобы собрать приложение для ПОИБ".format(name_user)
            logging.warning( u"%s", text)
            jenkins.build_job('GISTEK_Poib/Build')
            text = "{} собирает ПОИБ".format(name_user)
            logging.warning( u"%s", text)
            bot.send_message(message.chat.id, "..еще 5 минуточек и ПОИБ соберется (если ошибки в jenkins не будет), а пока можно продолжать..")
        if var.build_deloy == "Deploy":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('REA_TEST', 'PI')
            msg = bot.reply_to(message, "Выберите стенд", reply_markup=markup)
            bot.register_next_step_handler(msg, poib_app_select)
    except Exception as e:
        bot.reply_to(message, 'oooops1')

def poib_app_select(message):
    try:
        chat_id = message.chat.id
        stend = message.text
        var = user_dict[chat_id]
        var.stend = stend
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("Update_DB", "Update_App")
        msg = bot.reply_to(message, "Выберите что будем обновлять:", reply_markup=markup)
        bot.register_next_step_handler(msg, poib_tag_select)
    except Exception as e:
        bot.reply_to(message, 'oooops2')

def poib_tag_select(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        msg = bot.reply_to(message, "Введите номер версии (тег):")
        bot.register_next_step_handler(msg, poib_job_jenkins)
    except Exception as e:
        bot.reply_to(message, 'oooops3')

def poib_job_jenkins(message):
    try:
        chat_id = message.chat.id
        tag = message.text
        var = user_dict[chat_id]
        var.tag = tag
        params = {"stend": var.stend, "version": str(var.tag)}
        text = "{} cтучится в jenkins чтобы выполнить {} для ПОИБ".format(name_user, var.arm)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        jenkins.build_job('GISTEK_Poib/' + str(var.arm), params)
        text = "{} на ПОИБ выполняется {} версия {}".format(name_user, var.arm, var.tag)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "..еще 2 минуты и приложение " + str(var.arm) + " на ПОИБ обновится, версия " + str(var.tag) + " (если ошибки в jenkins не будет), а пока можно продолжать..")
    except Exception as e:
        bot.reply_to(message, 'oooops4')

@bot.message_handler(commands=['restart_system'])
def action_select(message):
    secure(message)
    if user_true == "true":
        global name_user
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('REA_TEST', 'PK', 'PI')
        msg = bot.reply_to(message, "Выберите стенд", reply_markup=markup)
        bot.register_next_step_handler(msg, system_select)

def system_select(message):
    try:
        chat_id = message.chat.id
        stend = message.text
        var = Var(stend)
        user_dict[chat_id] = var
        var.stend = stend
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('pizi_app', 'poib', 'portal_open', 'portal_close', 'pentaho', 'pentaho_oil_gas', 'pentaho_ee', 'pentaho_electro', 'pentaho_integr', "pentaho_coal", 'robot')
        msg = bot.reply_to(message, "Выберите что будем перезагружать:", reply_markup=markup)
        bot.register_next_step_handler(msg, system_job_jenkins)
    except Exception as e:
        bot.reply_to(message, 'oooops2')

def system_job_jenkins(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        params = {"stand": var.stend, "system": var.arm}
        text = "{} cтучится в jenkins чтобы перезагрузить {} на {}".format(name_user, var.arm, var.stend)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        jenkins.build_job('GISTEK_Restart', params)
        text = "{} перезагружается {} на {}".format(name_user, var.arm, var.tag)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "..еще минуты и приложение " + str(var.arm) + " на " + str(var.stend) + " перезапустится, (если ошибки в jenkins не будет), а пока можно продолжать..")
    except Exception as e:
        bot.reply_to(message, 'oooops4')

bot.polling(none_stop=True)
