#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# блокирования файла, чтобы не запускали несколько раз
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
import os
import random

import jenkinsapi
from jenkinsapi.jenkins import Jenkins

# логирование, обозначается уровень логирования INFO/DEBUG/ERROR/CRITICAL
import logging
logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.INFO, filename = u'telegram_bot.log')

import config
import telebot
from telebot import types

bot = telebot.TeleBot(config.token)

import gitlab
gl = gitlab.Gitlab('http://git.gistek.lanit.ru', config.token_gitlab)
gl.auth()

# авторизация в jenkins'ах (зацикленаня, чтобы точно выполнилась)
def authentication(arg):
    i = arg
    while i != 1:
        try:
            global jenkins
            global jenkins_dkp
            jenkins = Jenkins("http://jenkins.gistek.lanit.ru", username=config.username, password=config.password)
            jenkins_dkp = Jenkins("http://jenkins-gistek.dkp.lanit.ru", username=config.username, password=config.password)
            logging.warning(u'В jenkins авторизовались')
            i = 1
        except Exception as e:
            logging.error(u"Авторизация не прошла, пробуем еще раз")

authentication(0)

# функция проверки доступа пользователя
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

# функция проверки доступа пользователя (для разработчиков - укороченная)
def secure_dev(message):
    global user_true
    if message.chat.id in config.true_id_dev:
        text = "Пользователь {} прошел проверку безопасности".format(message.chat.id)
        logging.warning( u"%s", text)
        user_true = "true"
    else:
        text = "Пользователь {} не прошел проверку безопасности".format(message.chat.id)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "Соррян, у вас нету нужных прав.")
        user_true = "false"

# функция сообщения об ошибке
def errors(message):
    text = "Ошибочка вышла, скорее всего с авторизацией в jenkins, ну или с параметрами."
    logging.error( u"%s", text)
    authentication(0)
    bot.reply_to(message, 'Попробуй еще разок, возможно он просто устал.')

# функция проверки на выполенния джобы в jenkins
def test_run(message, arm, params, time_timeout, job):
    name_user = "{}({}):".format(message.chat.username, message.chat.id)
    # пауза
    time.sleep(time_timeout)
    # получения номера задачи
    s = str(job.get_last_completed_build())
    #  обрезка лишних символов
    s = int(s[s.find('#')+1:])
    build = job.get_build(s)
    # получение статуса задачи true\false
    task_status = str(build.is_good())
    if task_status == "True":
        text = "Я сам в шоке, но {} готово!".format(job)
        bot.send_message(message.chat.id, text)
        text = "{} выполнилось {} c {}".format(name_user, arm, params)
        logging.warning( u"%s", text)
    else:
        text = "Ошибка, посмотрите логи и обратитесь к администратору"
        bot.send_message(message.chat.id, text)
        text = "{} не выполнилось {} с {}, сейчас посмотрим логи".format(name_user, arm, params)
        logging.error( u"%s", text)
        # получение из jenkins логов из джобы
        text = build.get_console()
        logging.error( u"###################\n%s\n###################", text)
        # создание файла для записи туда лога ошибки
        doc = str("error_{}.log".format(arm))
        fout = open(doc, 'w')
        print(text, file=fout)
        fout.close()
        # отправка файла пользователю
        doc = open(doc, 'rb')
        # print(doc)
        bot.send_document(message.chat.id, doc)
        # удаление файла с логом ошибки
        doc = str("error_{}.log".format(arm))
        os.remove(doc)

# функция получения тегов проекта из Gitlab
def tag_gitlab(name_project):
    project = gl.projects.get(name_project)
    num = 0
    for tags in project.tags.list():
        num += 1
        exec('item%d="%s"' % (num,str(tags.name)), globals())

# инициализация и стартовое меню бота
@bot.message_handler(commands=['help', 'start'])
def handle_true_help(message):
    if message.text == "/start":
        text = "{}({}): инициализировался".format(message.chat.username, message.chat.id)
        logging.warning( u"%s", text)
    text = "{}({}): решил почитать /help".format(message.chat.username, message.chat.id)
    logging.warning( u"%s", text)
    id_user = message.chat.id
    bot.send_message(message.chat.id, """Что я умею!
------------------------------------------
Сборка АРМ: /gistek_build_arm \n
Подсистема Пентахо: /gistek_pentaho \n
Подсистема Портал: /gistek_portal  \n
Подсистема мобильного приложения: /gistek_mobile \n
Подсистема интеграционная: /gistek_integration \n
Подсистема ПИЗИ: /gistek_pizi \n
Подсистема ПОИБ: /gistek_poib \n
Перезапуск подсистем /restart_system \n

Синхронизация данных между стендами: /sync
------------------------------------------""")
    secure_dev(message)
    if user_true == "true":
        bot.send_message(message.chat.id, "Авторизуюсь в jenkins. Подождите, это для вашего же блага.")
        authentication(0)
        bot.send_message(message.chat.id, "Успех. Делайте, то что нужно.")

user_dict = {}

# класс для переменных что используют функции
class Var:
    def __init__(self, name):
        self.build_deloy = None
        self.stend = name
        self.arm = None
        self.issue_select = None
        self.issue_id = None
        self.tag = None
        self.open_close = None

# джоба по синхронизации данных со стендов
@bot.message_handler(commands=['sync'])
def sync_start(message):
    secure_dev(message)
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
        errors(message)

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
        errors(message)

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
        errors(message)

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
        bot.send_message(message.chat.id, "..еще 2 минуты и " + str(var.arm) + ", для " + var.stend + " соберется (если ошибки в jenkins не будет).")
        job = jenkins.get_job('GISTEK_Pizi/Build_ARM/' + str(var.arm))
        test_run(message, var.arm, params, 70, job)
    except Exception as e:
        errors(message)

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
        errors(message)

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
        errors(message)

def pentaho_tag_select(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        if var.arm == "update_plugins":
            tag_gitlab("PENTAHO/pentaho-plugins")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item3, item4, item5)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, pentaho_issue_select)
        if var.arm == "update_fileProperties":
            tag_gitlab("PENTAHO/pentaho-fileProperties")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1, item2, item3, item4, item5, item6, item7, item8, item9)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, pentaho_issue_select)
        if var.arm == "update_quixote_theme":
            tag_gitlab("PENTAHO/quixote-theme")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1, item2, item3, item4, item5, item6, item7, item8)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, pentaho_issue_select)
        if var.arm == "update_langpack":
            tag_gitlab("PENTAHO/pentahoLanguagePacks")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item2, item3, item4, item5, item6, item7, item8, item9)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, pentaho_issue_select)
        if var.arm == "update_cas_tek":
            tag_gitlab("PENTAHO/pentaho-cas-tek")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1, item2)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, pentaho_issue_select)
        if var.arm == "update_mondrian":
            msg = bot.reply_to(message, "Введите номер версии (тег):")
            bot.register_next_step_handler(msg, pentaho_issue_select)
    except Exception as e:
        errors(message)

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
        errors(message)

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
        errors(message)

def pentaho_job_jenkins(message):
    try:
        chat_id = message.chat.id
        issue_id = message.text
        var = user_dict[chat_id]
        var.issue_id = issue_id
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        if var.issue_select == "No":
            params = {"stend": var.stend, "tags": str(var.arm), "version": str(var.tag)}
            if var.arm == "update_mondrian":
                params = {"stend": var.stend, "tags": str(var.arm)}
        if var.issue_select == "Yes":
            params = {"stend": var.stend, "tags": str(var.arm), "issue_id": var.issue_id, "version": str(var.tag)}
            if var.arm == "update_mondrian":
                params = {"stend": var.stend, "tags": str(var.arm), "issue_id": var.issue_id,}
        text = "{} cтучится в jenkins чтобы выполнить {} для Пентахи".format(name_user, var.arm)
        logging.warning( u"%s", text)
        jenkins.build_job('GISTEK_Pentaho/Update_Pentaho', params)
        text = "{} на пентахи выполняется {} версия {}".format(name_user, var.arm, var.tag)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "..еще 2 минуты и приложение " + str(var.arm) + " на Пентахе обновится, версия " + str(var.tag) + " (если ошибки в jenkins не будет)")
        job = jenkins.get_job('GISTEK_Pentaho/Update_Pentaho')
        test_run(message, var.arm, params, 70, job)
    except Exception as e:
        errors(message)

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
        bot.send_message(message.chat.id, "..еще 4 минуточек и плагин " + str(var.arm) + " соберется (если ошибки в jenkins не будет)")
        job = jenkins.get_job('GISTEK_Pentaho/Build_' + str(var.arm))
        test_run(message, var.arm, "Без этого", 240, job)
    except Exception as e:
        errors(message)

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
        errors(message)

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
        errors(message)

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
        errors(message)

def portal_tag_select(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        if var.arm == "hook-asset-publisher":
            tag_gitlab("PORTAL/hook-asset-publisher")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item2, item3, item4, item5)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, portal_issue_select)
        if var.arm == "hook-search":
            tag_gitlab("PORTAL/hook-search")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item2, item3, item4, item5, item6, item7)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, portal_issue_select)
        if var.arm == "inspinia-theme":
            tag_gitlab("PORTAL/inspinia-theme")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1, item2, item3, item4, item5, item6, item7, item8)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, portal_issue_select)
        if var.arm == "languagePackRU":
            tag_gitlab("PORTAL/hook-languagePackRU")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item2, item3, item4, item5, item6, item7)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, portal_issue_select)
        if var.arm == "login-hook":
            tag_gitlab("PORTAL/login-hook")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1, item2, item3, item4, item5, item6, item7, item8)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, portal_issue_select)
        if var.arm == "mainpageGEO":
            tag_gitlab("PORTAL/mainpageGEO")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1, item2, item3)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, portal_issue_select)
        if var.arm == "notification-portlet":
            tag_gitlab("PORTAL/notification-portlet")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1, item2)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, portal_issue_select)
        if var.arm == "npa-loader":
            tag_gitlab("PORTAL/npa-loader-portlet")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, portal_issue_select)
        if var.arm == "portal-iframe":
            tag_gitlab("PORTAL/portal-iframe")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item2, item3, item4)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, portal_issue_select)
        if var.arm == "reports-display-portlet":
            tag_gitlab("PORTAL/reports-display-portlet")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1, item2, item3, item4, item5, item6, item7, item8)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, portal_issue_select)
        if var.arm == "slider":
            tag_gitlab("PORTAL/slider")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1, item2, item3, item4)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, portal_issue_select)
        if var.arm == "subsystem-search":
            tag_gitlab("PORTAL/subsystem-search")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1, item2, item3, item4, item5, item6, item7)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, portal_issue_select)
        if var.arm == "support-mail-portlet":
            tag_gitlab("PORTAL/support-mail-portlet")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, portal_issue_select)
        if var.arm == "urc-theme":
            tag_gitlab("PORTAL/urc-theme")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1, item2, item3, item4, item5, item6)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, portal_issue_select)
        # msg = bot.reply_to(message, "Введите номер версии (тег):")
        # bot.register_next_step_handler(msg, portal_issue_select)
    except Exception as e:
        errors(message)

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
        errors(message)

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
        errors(message)

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
        bot.send_message(message.chat.id, "..еще 3 минуты и " + str(var.arm) + " на портале " + str(var.stend) + " обновится, версия " + str(var.tag) + " (если ошибки в jenkins не будет)")
        job = jenkins.get_job('GISTEK_Portal/Update_App')
        test_run(message, var.arm, params, 180, job)
    except Exception as e:
        errors(message)

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
        bot.send_message(message.chat.id, "..еще 3 минуты (или даже меньше) и портлет " + str(var.arm) + " соберется (если ошибки в jenkins не будет)")
        job = jenkins.get_job('GISTEK_Portal/' + str(var.arm))
        test_run(message, var.arm, "Без оных", 180, job)
    except Exception as e:
        errors(message)

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
        errors(message)

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
        bot.send_message(message.chat.id, "..еще 4 минуточек и приложение " + str(var.arm) + " соберется (если ошибки в jenkins не будет)")
        job = jenkins.get_job('GISTEK_MobileApp/Build_' + str(var.arm))
        test_run(message, var.arm, "Без оных", 200, job)
    except Exception as e:
        errors(message)

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
        errors(message)

def mobile_tag_select(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        if var.arm == "update_web_service":
            tag_gitlab("MOBILE-APP/web-service-java")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item2, item3, item4, item5)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, mobile_job_jenkins)
        if var.arm == "update_langpack":
            tag_gitlab("MOBILE-APP/tek-portlet")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item2, item3, item4, item5, item6, item7, item8, item9)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, mobile_job_jenkins)
        # msg = bot.reply_to(message, "Введите номер версии (тег):")
        # bot.register_next_step_handler(msg, mobile_job_jenkins)
    except Exception as e:
        errors(message)

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
        bot.send_message(message.chat.id, "..еще 2 минуты и обновится " + str(var.arm) + " для мобильного приложения, версия " + str(var.tag) + " (если ошибки в jenkins не будет)")
        job = jenkins.get_job('GISTEK_MobileApp/Update')
        test_run(message, var.arm, params, 120, job)
    except Exception as e:
        errors(message)

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
        errors(message)

def integration_stand_select(message):
    try:
        chat_id = message.chat.id
        stend = message.text
        var = user_dict[chat_id]
        var.stend = stend
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("update", "update_generator", "update_logui")
        msg = bot.reply_to(message, "Выберите приложение для обновления:", reply_markup=markup)
        bot.register_next_step_handler(msg, integration_tag_select)
    except Exception as e:
        errors(message)

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
        errors(message)

def integration_tag_select(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        if var.arm == "update_generator":
            tag_gitlab("INTEGRATIONAL/generator")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1, item2, item3, item4, item5, item6, item7, item8, item9)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, integration_job_jenkins)
        if var.arm == "update":
            tag_gitlab("INTEGRATIONAL/is")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1, item2, item3, item4, item5, item6, item7, item8, item9)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, integration_job_jenkins)
        if var.arm == "update_logui":
            tag_gitlab("INTEGRATIONAL/log-ui")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1, item2)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, integration_job_jenkins)
        # msg = bot.reply_to(message, "Введите номер версии (тег):")
        # bot.register_next_step_handler(msg, integration_job_jenkins)
    except Exception as e:
        errors(message)

def integration_build_tag_select(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        if var.arm == "Build_generator":
            tag_gitlab("INTEGRATIONAL/generator")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1, item2, item3, item4, item5, item6, item7, item8, item9)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, integration_build_job_jenkins)
        if var.arm == "Build_mis":
            tag_gitlab("INTEGRATIONAL/is")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1, item2, item3, item4, item5, item6, item7, item8, item9)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, integration_build_job_jenkins)
        if var.arm == "Build_LogUI":
            tag_gitlab("INTEGRATIONAL/log-ui")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1, item2)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, integration_build_job_jenkins)
        # msg = bot.reply_to(message, "Введите номер версии (тег):")
        # bot.register_next_step_handler(msg, integration_build_job_jenkins)
    except Exception as e:
        errors(message)

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
        bot.send_message(message.chat.id, "..еще 3 минуты и приложение " + str(var.arm) + " для интеграционной подсистемы соберется (если ошибки в jenkins не будет)")
        job = jenkins.get_job('GISTEK_Integration/' + str(var.arm))
        test_run(message, var.arm, params, 180, job)
    except Exception as e:
        errors(message)

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
        bot.send_message(message.chat.id, "..еще 5 минуточек и приложение " + str(var.arm) + " для интеграционной подсистемы выкатится (если ошибки в jenkins не будет)")
        job = jenkins.get_job('GISTEK_Integration/Update')
        test_run(message, var.arm, params, 300, job)
    except Exception as e:
        errors(message)

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
        errors(message)

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
        errors(message)

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
            bot.send_message(message.chat.id, "..еще 3 минуты и " + str(var.arm) + " для сбора соберется (если ошибки в jenkins не будет)")
            job = jenkins.get_job('GISTEK_Pizi/Build_' + str(var.arm))
            test_run(message, var.arm, "Без оных", 185, job)
        if var.build_deloy == "Deploy":
            params = {"stend": var.stend}
            text = "{} cтучится в jenkins чтобы собрать обновить {} для Сбора на {}".format(name_user, var.arm, var.stend)
            logging.warning( u"%s", text)
            jenkins.build_job('GISTEK_Pizi/Update_' + str(var.arm), params)
            text = "{} обновляет на Сборе {}".format(name_user, var.arm)
            logging.warning( u"%s", text)
            bot.send_message(message.chat.id, "..еще 2 минуты и приложение " + str(var.arm) + " на Сборе обновится (если ошибки в jenkins не будет)")
            job = jenkins.get_job('GISTEK_Pizi/Update_' + str(var.arm))
            test_run(message, var.arm, params, 120, job)
    except Exception as e:
        errors(message)

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
            bot.send_message(message.chat.id, "..еще 5 минуточек и ПОИБ соберется (если ошибки в jenkins не будет)")
            job = jenkins.get_job('GISTEK_Poib/Build')
            test_run(message, "перезапуск ПОИБ", "без параметров", 250, job)
        if var.build_deloy == "Deploy":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('REA_TEST', 'PI')
            msg = bot.reply_to(message, "Выберите стенд", reply_markup=markup)
            bot.register_next_step_handler(msg, poib_app_select)
    except Exception as e:
        errors(message)

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
        errors(message)

def poib_tag_select(message):
    chat_id = message.chat.id
    arm = message.text
    var = user_dict[chat_id]
    var.arm = arm
    tag_gitlab("SECURITY/poib")
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add(item92, item93, item94, item95, item96, item97, item98, item99)
    msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
    bot.register_next_step_handler(msg, poib_issue_select)

def poib_issue_select(message):
    try:
        chat_id = message.chat.id
        tag = message.text
        var = user_dict[chat_id]
        var.tag = tag
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("Yes", "No")
        msg = bot.reply_to(message, "Есть задача?", reply_markup=markup)
        bot.register_next_step_handler(msg, poib_issue)
    except Exception as e:
        errors(message)

def poib_issue(message):
    try:
        chat_id = message.chat.id
        issue_select = message.text
        var = user_dict[chat_id]
        var.issue_select = issue_select
        if var.issue_select == "No":
            msg = bot.reply_to(message, "Введите 0:")
        if var.issue_select == "Yes":
            msg = bot.reply_to(message, "Введите номер:")
        bot.register_next_step_handler(msg, poib_job_jenkins)
    except Exception as e:
        errors(message)

def poib_job_jenkins(message):
    try:
        chat_id = message.chat.id
        issue_id = message.text
        var = user_dict[chat_id]
        var.issue_id = issue_id
        params = {"stend": var.stend, "version": str(var.tag)}
        text = "{} cтучится в jenkins чтобы выполнить {} для ПОИБ".format(name_user, var.arm)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        jenkins.build_job('GISTEK_Poib/' + str(var.arm), params)
        text = "{} на ПОИБ выполняется {} версия {}".format(name_user, var.arm, var.tag)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "..еще 2 минуты и приложение " + str(var.arm) + " на ПОИБ обновится, версия " + str(var.tag) + " (если ошибки в jenkins не будет)")
        job = jenkins.get_job('GISTEK_Poib/' + str(var.arm))
        test_run(message, var.arm, params, 120, job)
    except Exception as e:
        errors(message)

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
        # if var.stend == "PI":
        #     bot.send_message(message.chat.id, "")
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('pizi_app', 'poib', 'portal_open', 'portal_close', 'pentaho', 'pentaho_oil_gas', 'pentaho_ee', 'pentaho_electro', 'pentaho_integr', "pentaho_coal", 'robot')
        msg = bot.reply_to(message, "Выберите что будем перезагружать:", reply_markup=markup)
        bot.register_next_step_handler(msg, system_job_jenkins)
    except Exception as e:
        errors(message)

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
        text = "{} перезагружается {} на {}".format(name_user, var.arm, var.stend)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "..еще минуты и приложение " + str(var.arm) + " на " + str(var.stend) + " перезапустится, (если ошибки в jenkins не будет)")
        job = jenkins.get_job('GISTEK_Restart')
        test_run(message, var.arm, params, 40, job)
    except Exception as e:
        errors(message)

@bot.message_handler(commands=['dev_klochkov'])

def action_select(message):
    secure_dev(message)
    if user_true == "true":
        global name_user
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('restart', 'deploy')
        msg = bot.reply_to(message, "Что делаем?", reply_markup=markup)
        bot.register_next_step_handler(msg, dev_select)

def dev_select(message):
    try:
        chat_id = message.chat.id
        build_deloy = message.text
        var = Var(build_deloy)
        user_dict[chat_id] = var
        var.build_deloy = build_deloy
        if var.build_deloy == "restart":
            params = {"stand": "DEV", "system": "pentaho"}
            text = "{} cтучится в jenkins чтобы перезагрузить pentaho на DEV".format(name_user)
            logging.warning( u"%s", text)
            bot.send_message(message.chat.id, "пыжимся и тужимся... ")
            jenkins.build_job('GISTEK_Restart', params)
            text = "{} перезагружается pentaho на DEV".format(name_user)
            logging.warning( u"%s", text)
            bot.send_message(message.chat.id, "..еще минуты и приложение pentaho на DEV перезапустится, (если ошибки в jenkins не будет)")
            job = jenkins.get_job('GISTEK_Restart')
            test_run(message, "Без оных", params, 70, job)
        if var.build_deloy == "deploy":
            tag_gitlab("PENTAHO/pentaho-fileProperties")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1, item2, item3, item4, item5, item6, item7, item8, item9)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, dev_job)
            # msg = bot.reply_to(message, "Введите номер версии (тег):")
            # bot.register_next_step_handler(msg, dev_job)
    except Exception as e:
        errors(message)

def dev_job(message):
    try:
        chat_id = message.chat.id
        tag = message.text
        var = user_dict[chat_id]
        var.tag = tag
        text = "{} cтучится в jenkins чтобы собрать для пентахи fileProperties".format(name_user)
        logging.warning( u"%s", text)
        params = {"version": var.tag}
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        jenkins.build_job('GISTEK_Pentaho/Build_fileProperties', params)
        text = "{} собирает fileProperties".format(name_user)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "..еще 3 минуты и плагин fileProperties соберется (если ошибки в jenkins не будет)")
        job = jenkins.get_job('GISTEK_Pentaho/Build_fileProperties')
        test_run(message, "Без параметров", params, 180, job)
        params = {"stand": "DEV", "tags": "fileProperties", "version": str(var.tag)}
        text = "{} cтучится в jenkins чтобы обновить fileProperties версии {} для пентахи на DEV".format(name_user, var.tag)
        logging.warning( u"%s", text)
        jenkins.build_job('GISTEK_Pentaho/Update_Pentaho', params)
        text = "{} на Пентахах DEV обновляется fileProperties версия {}".format(name_user, var.tag)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "..еще 2 минуты и приложение fileProperties на пентахах DEV обновится до версии " + str(var.tag) + " (если ошибки в jenkins не будет)")
        job = jenkins.get_job('GISTEK_Pentaho/Update_Pentaho')
        test_run(message, "Без оных", params, 120, job)
    except Exception as e:
        errors(message)

# #funny
# @bot.message_handler(content_types=["text"])
# def random_answer_messages(message):
#     os.system("curl http://copout.me/get-excuse/143 > lol.py")
#     os.system('echo $(grep "<p>" lol.py | grep -v "Голосов" | grep -v "спаме") > lol.py')
#     os.system('sed -i \'s|<p>|"|g\' lol.py')
#     os.system('sed -i \'s|</p>|",|g\' lol.py')
#     os.system('sed -i "1 s|^|text = [|" lol.py')
#     os.system('sed -i \'1 s|$|Такие дела"]|\' lol.py')
#     import lol
#     text = random.choice(lol.text)
#     bot.send_message(message.chat.id, text)

bot.polling(none_stop=True)
