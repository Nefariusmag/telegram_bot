# -*- coding: utf-8 -*-

import time, os, re, logging, jenkinsapi, telebot, random, config, gitlab

from jenkinsapi.jenkins import Jenkins
from telebot import types, apihelper

# логирование, обозначается уровень логирования INFO/DEBUG/ERROR/CRITICAL
logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.INFO)
# logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.INFO, filename = u'telegram_bot.log')

apihelper.proxy = {'https':'socks5://' + config.proxy_server}

bot = telebot.TeleBot(config.token)
gl = gitlab.Gitlab(config.url_gitlab, config.token_gitlab, api_version=3)
gl.auth()


# авторизация в jenkins'ах (зацикленаня, чтобы точно выполнилась)
def authentication(arg):
    i = arg
    while i != 1:
        try:
            global jenkins
            global jenkins_dkp
            jenkins = Jenkins(config.url_jenkins, username=config.username, password=config.password)
            jenkins_dkp = Jenkins(config.url_jenkins2, username=config.username, password=config.password)
            logging.warning(u'В jenkins авторизовались')
            i = 1
        except Exception as e:
            logging.error(u"Авторизация не прошла, пробуем еще раз")


authentication(0)

user_dict = {}


# класс для переменных что используют функции
class Var:
    def __init__(self, name):
        self.build_deploy = None
        self.stand = name
        self.arm = None
        self.issue_select = None
        self.issue_id = "отсутствует"
        self.tag = None
        self.open_close = None
        # ПИЗИ
        self.gtafo = "release"
        self.gtarm = "release"
        self.gttechnologist = "release"
        self.gtonl = "drelease"
        self.gtimpxml = "release"
        self.gtxml = "release"
        self.gttransport = "release"
        self.gtcontrol = "release"
        self.gtexpgisee = "release"
        self.gtdownload = "release"
        self.gtclassifier = "release"
        self.classifier_view = "release"
        self.ticket = "release"
        self.sso_server = "release"
        self.registration = "release"
        self.loadssb = "release"


# функция проверки доступа пользователя
def secure(message):
    global user_true
    if message.chat.id in config.true_id:
        text = "{}({}): прошел проверку безопасности".format(message.chat.username, message.chat.id)
        logging.warning(u"%s", text)
        user_true = "true"
    else:
        text = "{}({}): не прошел проверку безопасности".format(message.chat.username, message.chat.id)
        logging.warning(u"%s", text)
        bot.send_message(message.chat.id, "Соррян, у вас нету нужных прав.")
        user_true = "false"


# функция проверки доступа пользователя (для разработчиков - укороченная)
def secure_dev(message):
    global user_true
    if message.chat.id in config.true_id_dev:
        text = "{}({}): прошел проверку безопасности".format(message.chat.username, message.chat.id)
        logging.warning(u"%s", text)
        user_true = "true"
    else:
        text = "{}({}): не прошел проверку безопасности".format(message.chat.username, message.chat.id)
        logging.warning(u"%s", text)
        bot.send_message(message.chat.id, "Соррян, у вас нету нужных прав.")
        user_true = "false"


# функция сообщения об ошибке
def errors(message):
    text = "Ошибочка вышла. Соберем тут все параметры: \n{}".format(locals())
    logging.error(u"%s", text)
    bot.reply_to(message, 'Вышла ошибка, обратитесь к @nefariusmag.')
    # отправить стикер
    sti = open("kill_sti/1.webp", 'rb')
    bot.send_sticker(message.chat.id, sti)
    text = "Ошибка при работе с ботом у {}".format(message.chat.username)
    # отправить стикер
    bot.send_message("-216046302", text)
    sti = open("kill_sti/2.webp", 'rb')
    bot.send_sticker("-216046302", sti)


# функция проверки на выполенния джобы в jenkins
def test_run(message, arm, params, time_timeout, job):
    name_user = "{}({}):".format(message.chat.username, message.chat.id)
    # пауза
    time.sleep(time_timeout)
    # получения номера задачи
    s = str(job.get_last_completed_build())
    #  обрезка лишних символов
    s = int(s[s.find('#')+1:])
    # получение статуса задачи
    build = job.get_build(s)
    task_status = str(build.is_good())
    # сравнение статуса с true\false
    if task_status == "True":
        text = "Я сам в шоке, но {} готово!".format(job)
        bot.send_message(message.chat.id, text)
        # получить рандомный стикер из папки
        sti = random.choice(os.listdir("true_sti"))
        # добавить к стикеру путь до папки
        sti = "true_sti/{}".format(sti)
        # подгрузить стикеры в память
        sti = open(sti, 'rb')
        # отправить стикер
        bot.send_sticker(message.chat.id, sti)
        text = "{} выполнилось {} c {}".format(name_user, arm, params)
        logging.warning(u"%s", text)
    else:
        text = "Ошибка, посмотрите логи и обратитесь к администратору"
        bot.send_message(message.chat.id, text)
        # отправить стикер
        sti = random.choice(os.listdir("logs_sti"))
        sti = "logs_sti/{}".format(sti)
        sti = open(sti, 'rb')
        bot.send_sticker(message.chat.id, sti)
        text = "{} не выполнилось {} с {}, сейчас посмотрим логи".format(name_user, arm, params)
        logging.error(u"%s", text)
        # получение из jenkins логов из джобы
        text = build.get_console()
        logging.error(u"###################\n%s\n###################", text)
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
        exec('item%d="%s"' % (num, str(tags.name)), globals())


# инициализация и стартовое меню бота
@bot.message_handler(commands=['help', 'start'])
def menu_help(message):
    if message.text == "/start":
        text = "{}({}): инициализировался".format(message.chat.username, message.chat.id)
        logging.warning(u"%s", text)
    text = "{}({}): решил почитать /help".format(message.chat.username, message.chat.id)
    logging.warning(u"%s", text)
    id_user = message.chat.id
    markup = types.ReplyKeyboardMarkup(row_width=3, one_time_keyboard=True)
    markup.add("АРМ", "Пентаха", "Портал", "Мобильное приложение", "Интеграционная подсистема", "Сбор", "ПОИБ", "Перезапуск", "Синхронизация стендов", "Переподключиться")
    msg = bot.reply_to(message, "Главное меню:", reply_markup=markup)
    bot.register_next_step_handler(msg, menu_help_2)


def menu_help_2(message):
    try:
        chat_id = message.chat.id
        stand = message.text
        var = Var(stand)
        user_dict[chat_id] = var
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        text = "{} выбрал: {}".format(name_user, var.stand)
        logging.warning(u"%s", text)
        if stand == "АРМ":
            arm_stand_select(message)
        if stand == "Пентаха":
            pentaho_action_select(message)
        if stand == "Портал":
            portal_action_select(message)
        if stand == "Мобильное приложение":
            mobile_action_select(message)
        if stand == "Интеграционная подсистема":
            integration_action_select(message)
        if stand == "Сбор":
            pizi_action_select(message)
        if stand == "ПОИБ":
            poib_action_select(message)
        if stand == "Перезапуск":
            system_action_select(message)
        if stand == "Синхронизация стендов":
            sync_start(message)
        if stand == "Переподключиться":
            authentication(0)
            bot.send_message(chat_id, "Переподключение к jenkins выполнено.")
            menu_help(message)
    except Exception as e:
        errors(message)


# джоба по синхронизации данных со стендов
@bot.message_handler(commands=['sync'])
def sync_start(message):
    secure_dev(message)
    if user_true == "true":
        global name_user
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        text = "{} решил синхронизировать стенды".format(name_user)
        logging.warning(u"%s", text)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('sync_dev_pk', 'sync_pk_pi', 'sync_pk_pp', "Назад в главное меню")
        msg = bot.reply_to(message, "Выберите откуда куда передаем данные", reply_markup=markup)
        bot.register_next_step_handler(msg, sync_select)


def sync_select(message):
        try:
            chat_id = message.chat.id
            stand = message.text
            var = Var(stand)
            user_dict[chat_id] = var
            var.stand = stand
            text = "{} синхронизирует {}".format(name_user, var.stand)
            logging.warning(u"%s", text)
            if var.stand == "Назад в главное меню":
                menu_help(message)
            else:
                # специально для Юры и его лени
                try:
                    jenkins_dkp = Jenkins(config.url_jenkins2, username=config.username, password=config.password)
                except Exception as e:
                    text = "{} второй раз пробуем авторизоваться так как в первом ошибка".format(name_user)
                    logging.warning(u"%s", text)
                    jenkins_dkp = Jenkins(config.url_jenkins2, username=config.username, password=config.password)
                text = "Авторизация в jenkins_dkp прошла и теперь {} запускает {}".format(name_user, var.stand)
                logging.warning(u"%s", text)
                try:
                    jenkins_dkp.build_job(str(var.stand))
                except Exception as e:
                    text = "{} неведомая херня, но джоба выполняется, прячу багу".format(name_user)
                    logging.warning(u"%s", text)
                text = "{} запустилась {}".format(name_user, var.stand)
                logging.warning(u"%s", text)
                bot.send_message(message.chat.id, "Запустилась синхронизация, в среднем выполняется 45 минут. Можно продолжать работу.")
        except Exception as e:
            errors(message)


def arm_stand_select(message):
    secure(message)
    if user_true == "true":
        global name_user
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        markup = types.ReplyKeyboardMarkup(row_width=3, one_time_keyboard=True)
        markup.add('DKP', 'ZERO', 'REA_TEST', 'PK', 'PI', "Назад в главное меню")
        msg = bot.reply_to(message, "Выберите стенд:", reply_markup=markup)
        bot.register_next_step_handler(msg, arm_select)


def arm_select(message):
    try:
        chat_id = message.chat.id
        stand = message.text
        var = Var(stand)
        user_dict[chat_id] = var
        var.stand = stand
        if stand == "Назад в главное меню":
            menu_help(message)
        else:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add("admin_kl", "admin_net", "all_mak_inf", "arm_access", "fpi-autoregistration", "gis_des", "is_transport", "kontrol", "load_ssb", "offline", "template_cleaner", "wmk_gistek", "arm_remover")
            msg = bot.reply_to(message, "Выберите АРМ:", reply_markup=markup)
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
            arm_ask(message)
        if var.issue_select == "Yes":
            msg = bot.reply_to(message, "Введите номер:")
            bot.register_next_step_handler(msg, arm_ask)
    except Exception as e:
        errors(message)


def arm_ask(message):
    try:
        chat_id = message.chat.id
        issue_id = message.text
        var = user_dict[chat_id]
        var.issue_id = issue_id
        markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
        markup.add("Да", "Начать с начала", "Вернуться в главное меню")
        text = "Собрать {} для {} № задачи {}".format(var.arm, var.stand, var.issue_id)
        msg = bot.reply_to(message, text, reply_markup=markup)
        bot.register_next_step_handler(msg, arm_job_jenkins)
    except Exception as e:
        errors(message)


def arm_job_jenkins(message):
    try:
        chat_id = message.chat.id
        var = user_dict[chat_id]
        areyousure = message.text
        if areyousure == "Начать с начала":
            arm_stand_select(message)
        if areyousure == "Вернуться в главное меню":
            menu_help(message)
        if areyousure == "Да":
            if var.issue_select == "No":
                params = {"stand": var.stand}
            if var.issue_select == "Yes":
                params = {"stand": var.stand, "issue_id": var.issue_id}
            text = "{} cтучится в jenkins чтобы собрать {} для {}".format(name_user, var.arm, var.stand)
            logging.warning(u"%s", text)
            bot.send_message(message.chat.id, "пыжимся и тужимся... ")
            try:
                jenkins.build_job('GISTEK_Pizi/Build_ARM/' + str(var.arm), params)
            except Exception:
                bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
                authentication(0)
                jenkins.build_job('GISTEK_Pizi/Build_ARM/' + str(var.arm), params)
            text = "{} собирает {} на {}".format(name_user, var.arm, var.stand)
            logging.warning(u"%s", text)
            bot.send_message(message.chat.id, "..еще 2 минуты и " + str(var.arm) + ", для " + var.stand + " соберется.")
            job = jenkins.get_job('GISTEK_Pizi/Build_ARM/' + str(var.arm))
            test_run(message, var.arm, params, 70, job)
            menu_help(message)
    except Exception:
        errors(message)


def pentaho_action_select(message):
    secure(message)
    if user_true == "true":
        global name_user
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
        markup.add('Build', 'Deploy', "Назад в главное меню")
        msg = bot.reply_to(message, "Выберите, что будем делать", reply_markup=markup)
        bot.register_next_step_handler(msg, pentaho_app_select)


def pentaho_app_select(message):
    try:
        chat_id = message.chat.id
        build_deploy = message.text
        var = Var(build_deploy)
        user_dict[chat_id] = var
        var.build_deploy = build_deploy
        if var.build_deploy == "Build":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add("fileProperties", "integr_clearcache", "integr_readmetadata", "langpack", "cas_tek", "plugins", "quixote_theme")
            msg = bot.reply_to(message, "Выберите плагин для сборки:", reply_markup=markup)
            bot.register_next_step_handler(msg, pentaho_build_job_jenkins)
        if var.build_deploy == "Deploy":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('DKP', 'ZERO', 'REA_TEST', 'PK', 'PI')
            msg = bot.reply_to(message, "Выберите стенд", reply_markup=markup)
            bot.register_next_step_handler(msg, pentaho_app_2_select)
        if var.build_deploy == "Назад в главное меню":
            menu_help(message)
    except Exception as e:
        errors(message)


def pentaho_app_2_select(message):
    try:
        chat_id = message.chat.id
        stand = message.text
        var = user_dict[chat_id]
        var.stand = stand
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("plugins", "fileProperties", "quixote_theme", "langpack", "cas_tek", "mondrian")
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
        if var.arm == "plugins":
            tag_gitlab("PENTAHO/pentaho-plugins")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item3, item4, item5)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, pentaho_issue_select)
        if var.arm == "fileProperties":
            tag_gitlab("PENTAHO/pentaho-fileProperties")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1, item2, item3, item4, item5, item6, item7, item8, item9)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, pentaho_issue_select)
        if var.arm == "quixote_theme":
            tag_gitlab("PENTAHO/quixote-theme")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1, item2, item3, item4, item5, item6, item7, item8)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, pentaho_issue_select)
        if var.arm == "langpack":
            tag_gitlab("PENTAHO/pentahoLanguagePacks")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item2, item3, item4, item5, item6, item7, item8, item9)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, pentaho_issue_select)
        if var.arm == "cas_tek":
            tag_gitlab("PENTAHO/pentaho-cas-tek")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1, item2)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, pentaho_issue_select)
        if var.arm == "mondrian":
            pentaho_job_jenkins(message)
            # msg = bot.reply_to(message, "Введите номер версии (тег):")
            # bot.register_next_step_handler(msg, pentaho_issue_select)
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
            pentaho_job_jenkins(message)
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
            params = {"stand": var.stand, "tags": str(var.arm), "version": str(var.tag)}
            if var.arm == "mondrian":
                params = {"stand": var.stand, "tags": str(var.arm)}
        if var.issue_select == "Yes":
            params = {"stand": var.stand, "tags": str(var.arm), "issue_id": var.issue_id, "version": str(var.tag)}
            if var.arm == "update_mondrian":
                params = {"stand": var.stand, "tags": str(var.arm), "issue_id": var.issue_id,}
        text = "{} cтучится в jenkins чтобы выполнить обновление {} для Пентахи".format(name_user, var.arm)
        logging.warning(u"%s", text)
        try:
            jenkins.build_job('GISTEK_Pentaho/Update_Pentaho', params)
        except Exception:
            bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
            authentication(0)
            jenkins.build_job('GISTEK_Pentaho/Update_Pentaho', params)
        text = "{} обновляет на пентахе {} до версии {}".format(name_user, var.arm, var.tag)
        logging.warning(u"%s", text)
        bot.send_message(message.chat.id, "..еще 2 минуты и приложение " + str(var.arm) + " на Пентахе обновится, версия " + str(var.tag))
        job = jenkins.get_job('GISTEK_Pentaho/Update_Pentaho')
        test_run(message, var.arm, params, 70, job)
        menu_help(message)
    except Exception as e:
        errors(message)


def pentaho_build_job_jenkins(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        text = "{} cтучится в jenkins чтобы собрать для пентахи  {}".format(name_user, var.arm)
        logging.warning(u"%s", text)
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        try:
            jenkins.build_job('GISTEK_Pentaho/Build_' + str(var.arm))
        except Exception:
            bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
            authentication(0)
            jenkins.build_job('GISTEK_Pentaho/Build_' + str(var.arm))
        text = "{} собирает {}".format(name_user, var.arm)
        logging.warning(u"%s", text)
        bot.send_message(message.chat.id, "..еще 4 минуточек и плагин " + str(var.arm) + " соберется")
        job = jenkins.get_job('GISTEK_Pentaho/Build_' + str(var.arm))
        test_run(message, var.arm, "Без этого", 240, job)
        menu_help(message)
    except Exception as e:
        errors(message)


def portal_action_select(message):
    secure(message)
    if user_true == "true":
        global name_user
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
        markup.add('Build', 'Deploy', "Назад в главное меню")
        msg = bot.reply_to(message, "Выберите, что будем делать", reply_markup=markup)
        bot.register_next_step_handler(msg, portal_app_select)


def portal_app_select(message):
    try:
        chat_id = message.chat.id
        build_deploy = message.text
        var = Var(build_deploy)
        user_dict[chat_id] = var
        var.build_deploy = build_deploy
        if var.build_deploy == "Build":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add("hook-asset-publisher", "hook-search", "inspinia-theme", "languagePackRU", "login-hook", "mainpageGEO", "notification-portlet", "npa-loader", "portal-iframe", "reports-display-portlet", "slider", "subsystem-search", "support-mail-portlet", "urc-theme")
            msg = bot.reply_to(message, "Выберите портлет для сборки:", reply_markup=markup)
            bot.register_next_step_handler(msg, portal_build_job_jenkins)
        if var.build_deploy == "Deploy":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('DKP', 'ZERO', 'REA_TEST', 'PK', 'PI')
            msg = bot.reply_to(message, "Выберите стенд:", reply_markup=markup)
            bot.register_next_step_handler(msg, portal_public_internal_select)
        if var.build_deploy == "Назад в главное меню":
            menu_help(message)
    except Exception as e:
        errors(message)


def portal_public_internal_select(message):
    try:
        chat_id = message.chat.id
        stand = message.text
        var = user_dict[chat_id]
        var.stand = stand
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
        if var.open_close == "public":
            markup.add("hook-asset-publisher", "hook-search", "languagePackRU", "mainpageGEO", "npa-loader", "portal-iframe", "slider", "subsystem-search", "support-mail-portlet", "urc-theme", "lar_public", "sync")
        if var.open_close == "internal":
            markup.add("hook-search", "inspinia-theme", "languagePackRU", "login-hook", "notification-portlet", "portal-iframe", "reports-display-portlet", "subsystem-search", "support-mail-portlet", "lar_int", "lar_int_pub")
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
        if var.arm == "lar_int" or var.arm == "lar_int_pub" or var.arm == "lar_public":
            msg = bot.reply_to(message, "Введите номер версии (тег):")
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
            portal_ask(message)
        if var.issue_select == "Yes":
            msg = bot.reply_to(message, "Введите номер:")
        bot.register_next_step_handler(msg, portal_ask)
    except Exception as e:
        errors(message)


def portal_ask(message):
    try:
        chat_id = message.chat.id
        issue_id = message.text
        var = user_dict[chat_id]
        var.issue_id = issue_id
        markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
        markup.add("Да", "Начать с начала", "Вернуться в главное меню")
        text = "Обновить {} до версии {} на {} части на стенде {}, с № задачи: {}".format(var.arm, var.tag, var.open_close, var.stand, var.issue_id)
        msg = bot.reply_to(message, text, reply_markup=markup)
        bot.register_next_step_handler(msg, portal_job_jenkins)
    except Exception as e:
        errors(message)


def portal_job_jenkins(message):
    try:
        chat_id = message.chat.id
        var = user_dict[chat_id]
        areyousure = message.text
        if areyousure == "Начать с начала":
            portal_action_select(message)
        if areyousure == "Вернуться в главное меню":
            menu_help(message)
        if areyousure == "Да":
            text = "{} cтучится в jenkins чтобы обновить {} на портале {} в {}".format(name_user, var.arm, var.stand, var.open_close)
            logging.warning(u"%s", text)
            bot.send_message(message.chat.id, "пыжимся и тужимся... ")
            if var.issue_select == "No":
                params = {"stand": var.stand, "public_internal": str(var.open_close), "TARGET_TAGS": str(var.arm), "version": str(var.tag)}
            if var.issue_select == "Yes":
                params = {"stand": var.stand, "public_internal": str(var.open_close), "TARGET_TAGS": str(var.arm), "issue_id": var.issue_id, "version": str(var.tag)}
            try:
                jenkins.build_job('GISTEK_Portal/Update_App', params)
            except Exception:
                bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
                authentication(0)
                jenkins.build_job('GISTEK_Portal/Update_App', params)
            text = "{} на портале {} обновляет {}".format(name_user, var.stand, var.arm)
            logging.warning(u"%s", text)
            bot.send_message(message.chat.id, "..еще 3 минуты и " + str(var.arm) + " на портале " + str(var.stand) + " обновится, версия " + str(var.tag))
            job = jenkins.get_job('GISTEK_Portal/Update_App')
            test_run(message, var.arm, params, 180, job)
            menu_help(message)
    except Exception as e:
        errors(message)


def portal_build_job_jenkins(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        text = "{} cтучится в jenkins чтобы собрать портлет  {}".format(name_user, var.arm)
        logging.warning(u"%s", text)
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        try:
            jenkins.build_job('GISTEK_Portal/' + str(var.arm))
        except Exception:
            bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
            authentication(0)
            jenkins.build_job('GISTEK_Portal/' + str(var.arm))
        text = "{} собирает {}".format(name_user, var.arm)
        logging.warning(u"%s", text)
        bot.send_message(message.chat.id, "..еще 3 минуты (или даже меньше) и портлет " + str(var.arm) + " соберется")
        job = jenkins.get_job('GISTEK_Portal/' + str(var.arm))
        test_run(message, var.arm, "Без оных", 180, job)
        menu_help(message)
    except Exception as e:
        errors(message)


def mobile_action_select(message):
    secure(message)
    if user_true == "true":
        global name_user
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
        markup.add('Build', 'Deploy', "Назад в главное меню")
        msg = bot.reply_to(message, "Выберите, что будем делать", reply_markup=markup)
        bot.register_next_step_handler(msg, mobile_action_select_2)


def mobile_action_select_2(message):
    try:
        chat_id = message.chat.id
        build_deploy = message.text
        var = Var(build_deploy)
        user_dict[chat_id] = var
        var.build_deploy = build_deploy
        if var.build_deploy == "Build":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add("Android", "portlet", "web_service")
            msg = bot.reply_to(message, "Выберите приложение для сборки:", reply_markup=markup)
            bot.register_next_step_handler(msg, mobile_job_build_jenkins)
        if var.build_deploy == "Deploy":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('DKP', 'ZERO', 'REA_TEST', 'PI')
            msg = bot.reply_to(message, "Выберите стенд", reply_markup=markup)
            bot.register_next_step_handler(msg, mobile_app_select)
        if var.build_deploy == "Назад в главное меню":
            menu_help(message)
    except Exception as e:
        errors(message)


def mobile_job_build_jenkins(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        text = "{} cтучится в jenkins чтобы собрать приложение {}".format(name_user, var.arm)
        logging.warning(u"%s", text)
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        try:
            jenkins.build_job('GISTEK_MobileApp/Build_' + str(var.arm))
        except Exception:
            bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
            authentication(0)
            jenkins.build_job('GISTEK_MobileApp/Build_' + str(var.arm))
        text = "{} собирает {}".format(name_user, var.arm)
        logging.warning(u"%s", text)
        bot.send_message(message.chat.id, "..еще 4 минуточек и приложение " + str(var.arm) + " соберется")
        job = jenkins.get_job('GISTEK_MobileApp/Build_' + str(var.arm))
        test_run(message, var.arm, "Без оных", 200, job)
        menu_help(message)
    except Exception as e:
        errors(message)


def mobile_app_select(message):
    try:
        chat_id = message.chat.id
        stand = message.text
        var = user_dict[chat_id]
        var.stand = stand
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("web_service", "portlet")
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
        if var.arm == "web_service":
            tag_gitlab("MOBILE-APP/web-service-java")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item2, item3, item4, item5)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, mobile_job_jenkins)
        if var.arm == "langpack":
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
        params = {"stand": var.stand, "tags": str(var.arm), "version": str(var.tag)}
        text = "{} cтучится в jenkins чтобы обновить {} для мобильного приложения".format(name_user, var.arm)
        logging.warning(u"%s", text)
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        try:
            jenkins.build_job('GISTEK_MobileApp/Update', params)
        except Exception:
            bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
            authentication(0)
            jenkins.build_job('GISTEK_MobileApp/Update', params)
        text = "{} для мобильного приложения выполняется {} тег {}".format(name_user, var.arm, var.tag)
        logging.warning(u"%s", text)
        bot.send_message(message.chat.id, "..еще 2 минуты и обновится " + str(var.arm) + " для мобильного приложения, версия " + str(var.tag))
        job = jenkins.get_job('GISTEK_MobileApp/Update')
        test_run(message, var.arm, params, 120, job)
        menu_help(message)
    except Exception as e:
        errors(message)


def integration_action_select(message):
    secure(message)
    if user_true == "true":
        global name_user
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
        markup.add('Build', 'Deploy', "Назад в главное меню")
        msg = bot.reply_to(message, "Выберите, что будем делать", reply_markup=markup)
        bot.register_next_step_handler(msg, integration_app_select)


def integration_app_select(message):
    try:
        chat_id = message.chat.id
        build_deploy = message.text
        var = Var(build_deploy)
        user_dict[chat_id] = var
        var.build_deploy = build_deploy
        if var.build_deploy == "Build":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('DKP', 'ZERO', 'REA_TEST', 'PI')
            msg = bot.reply_to(message, "Выберите стенд", reply_markup=markup)
            bot.register_next_step_handler(msg, integration_build_stand_select)
        if var.build_deploy == "Deploy":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('DKP', 'ZERO', 'REA_TEST', 'PI')
            msg = bot.reply_to(message, "Выберите стенд", reply_markup=markup)
            bot.register_next_step_handler(msg, integration_stand_select)
        if var.build_deploy == "Назад в главное меню":
            menu_help(message)
    except Exception as e:
        errors(message)


def integration_stand_select(message):
    try:
        chat_id = message.chat.id
        stand = message.text
        var = user_dict[chat_id]
        var.stand = stand
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("mis", "generator", "logui")
        msg = bot.reply_to(message, "Выберите приложение для обновления:", reply_markup=markup)
        bot.register_next_step_handler(msg, integration_tag_select)
    except Exception as e:
        errors(message)


def integration_build_stand_select(message):
    try:
        chat_id = message.chat.id
        stand = message.text
        var = user_dict[chat_id]
        var.stand = stand
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
        if var.arm == "generator":
            tag_gitlab("INTEGRATIONAL/generator")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1, item2, item3, item4, item5, item6, item7, item8, item9)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, integration_job_jenkins)
        if var.arm == "mis":
            tag_gitlab("INTEGRATIONAL/is")
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(item1, item2, item3, item4, item5, item6, item7, item8, item9)
            msg = bot.reply_to(message, "Выберите номер версии (тег):", reply_markup=markup)
            bot.register_next_step_handler(msg, integration_job_jenkins)
        if var.arm == "logui":
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
        params = {"stand": var.stand, "version": str(var.tag)}
        text = "{} cтучится в jenkins чтобы собрать приложение {} для интеграционной подсистемы для {}".format(name_user, var.arm, var.stand)
        logging.warning(u"%s", text)
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        try:
            jenkins.build_job('GISTEK_Integration/' + str(var.arm), params)
        except Exception:
            bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
            authentication(0)
            jenkins.build_job('GISTEK_Integration/' + str(var.arm), params)
        text = "{} собирает для интеграционной подсистемы {}".format(name_user, var.arm)
        logging.warning(u"%s", text)
        bot.send_message(message.chat.id, "..еще 3 минуты и приложение " + str(var.arm) + " для интеграционной подсистемы соберется")
        job = jenkins.get_job('GISTEK_Integration/' + str(var.arm))
        test_run(message, var.arm, params, 180, job)
        menu_help(message)
    except Exception as e:
        errors(message)


def integration_job_jenkins(message):
    try:
        chat_id = message.chat.id
        tag = message.text
        var = user_dict[chat_id]
        var.tag = tag
        params = {"stand": var.stand, "tags": str(var.arm), "version": str(var.tag)}
        text = "{} cтучится в jenkins чтобы обновить приложение {} для интеграционной подсистемы на {}".format(name_user, var.arm, var.stand)
        logging.warning(u"%s", text)
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        try:
            jenkins.build_job('GISTEK_Integration/Update', params)
        except Exception:
            bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
            authentication(0)
            jenkins.build_job('GISTEK_Integration/Update', params)
        text = "{} обновляет на интеграционной подсистеме {}".format(name_user, var.arm)
        logging.warning(u"%s", text)
        bot.send_message(message.chat.id, "..еще 5 минуточек и приложение " + str(var.arm) + " для интеграционной подсистемы выкатится")
        job = jenkins.get_job('GISTEK_Integration/Update')
        test_run(message, var.arm, params, 300, job)
        menu_help(message)
    except Exception as e:
        errors(message)

# # принимает сообщения от начальника на деплой
# @bot.message_handler(func=lambda message: re.search(r"monitor |registration |formfillonline |sso-server |transport |afo |import-ps-ues-gisee |loadssb |ticket |classifier-view |classifier ", message.text))
# def pizi_repost_build_deploy(message):
#     secure(message)
#     name_user = "{}({}):".format(message.chat.username, message.chat.id)
#     if user_true == "true":
#         try:
#             try:
#                 from_whom = str(message.forward_from.id)
#             except Exception as e:
#                 bot.send_message(message.chat.id, "Это не репост от Федорова!")
#                 from_whom = str(message.chat.id)
#             if from_whom == "238305929": # Босс ли?
#                 # выбор версии приложения
#                 version_for_pizi(message, "gtafo", "afo")
#                 version_for_pizi(message, "gtarm", "monitor")
#                 version_for_pizi(message, "gtarm", "monitor")
#                 version_for_pizi(message, "gttechnologist", "monitor")
#                 version_for_pizi(message, "gttechnologist", "monitor")
#                 version_for_pizi(message, "gtonl", "formfillonline")
#                 version_for_pizi(message, "gtonl", "formfillonline")
#                 version_for_pizi(message, "gtimpxml", "gtimpxml")
#                 version_for_pizi(message, "gtxml", "gtxml")
#                 version_for_pizi(message, "gttransport", "transport")
#                 version_for_pizi(message, "gtcontrol", "gtcontrol")
#                 version_for_pizi(message, "gtexpgisee", "gtexpgisee")
#                 version_for_pizi(message, "gtdownload", "gtdownload")
#                 version_for_pizi(message, "gtclassifier", "gtclassifier")
#                 version_for_pizi(message, "classifier_view", "classifier-view")
#                 version_for_pizi(message, "ticket", "ticket")
#                 version_for_pizi(message, "sso_server", "sso_server")
#                 version_for_pizi(message, "registration", "registration")
#                 version_for_pizi(message, "loadssb", "loadssb")
#                 # выбор стенда
#                 version = re.search("на ПИ", message.text)
#                 if version != None:
#                     stand = "PI"
#                     text = "На прод деплоим \n---------------- \ngtafo версии - {} \ngtarm версии - {} \ngttechnologist версии - {} \ngtonl версии - {} \ngtimpxml версии - {} \ngtxml версии - {} \ngttransport версии - {} \ngtcontrol версии - {} \ngtexpgisee версии - {} \ngtdownload версии - {} \ngtclassifier версии - {} \nclassifier_view версии - {} \nticket версии - {} \nsso-server версии - {} \nregistration версии - {} \nloadssb версии - {} \n----------------".format(gtafo, gtarm, gttechnologist, gtonl, gtimpxml, gtxml, gttransport, gtcontrol, gtexpgisee, gtdownload, gtclassifier, classifier_view, ticket, sso_server, registration, loadssb)
#                     bot.send_message(message.chat.id, text)
#                     bot.send_message(message.chat.id, "Есть 15 секунд на подумать, отмена через jenkins")
#                     time.sleep(15)
#                 else:
#                     stand = "REA_TEST"
#                 bot.send_message(message.chat.id, "Cходи, завари чайку пока этот сбор деплоится))")
#                 params = {"TAG_GTAFO": gtafo, "TAG_GTARM": gtarm, "TAG_GTTECHNOLOGIST": gttechnologist, "TAG_GTONL": gtonl, "TAG_GTIMPXML": gtimpxml, "TAG_GTXML": gtxml, "TAG_GTTRANSPORT": gttransport, "TAG_GTCONTROL": gtcontrol, "TAG_GTEXPGISEE": gtexpgisee, 	"TAG_GTDOWNLOAD": gtdownload, "TAG_GTCLASSIFIER": gtclassifier, "TAG_CLASSIFIER_VIEW": classifier_view, "TAG_TICKET": ticket, "TAG_SSO_SERVER": sso_server, "TAG_REGISTRATION": registration, "TAG_LOADSSB": loadssb, "stand": stand}
#                 text = "{} cтучится в jenkins чтобы обновить приложения Сбора".format(name_user)
#                 logging.warning( u"%s", text)
#                 try:
#                     jenkins.build_job('GISTEK_Pizi/Build_and_Deploy', params)
#                 except Exception:
#                     bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
#                     authentication(0)
#                     jenkins.build_job('GISTEK_Pizi/Build_and_Deploy', params)
#                 text = "{} собирает приложения для Сбора".format(name_user)
#                 logging.warning( u"%s", text)
#                 bot.send_message(message.chat.id, "..еще 7 минут и обновим приложения Сбора")
#                 job = jenkins.get_job('GISTEK_Pizi/Build_and_Deploy')
#                 test_run(message, "Build_and_Deploy", params, 420, job)
#                 menu_help(message)
#             else:
#                 bot.send_message(message.chat.id, "Нету апрува от начальника, в другой раз.")
#         except Exception as e:
#             errors(message)


def pizi_action_select(message):
    secure_dev(message)
    if user_true == "true":
        global name_user
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        markup = types.ReplyKeyboardMarkup(row_width=3, one_time_keyboard=True)
        markup.add('Build', 'Deploy', "Build_and_Deploy", "Назад в главное меню")
        msg = bot.reply_to(message, "Выберите, что будем делать", reply_markup=markup)
        bot.register_next_step_handler(msg, pizi_stand_select)


def pizi_stand_select(message):
    try:
        chat_id = message.chat.id
        build_deploy = message.text
        var = Var(build_deploy)
        user_dict[chat_id] = var
        var.build_deploy = build_deploy
        if var.build_deploy == "Назад в главное меню":
            menu_help(message)
        if var.build_deploy == "Deploy" or var.build_deploy == "Build_and_Deploy":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('DKP', 'ZERO', 'REA_TEST', 'PK', 'PI')
            msg = bot.reply_to(message, "Выберите стенд", reply_markup=markup)
            bot.register_next_step_handler(msg, pizi_app_select)
        if var.build_deploy == "Build":
            pizi_app_select(message)
    except Exception as e:
        errors(message)


def pizi_app_select(message):
    try:
        chat_id = message.chat.id
        var = user_dict[chat_id]
        stand = message.text
        var.stand = stand
        if var.stand == "PI" or var.stand == "PK" or var.stand == 'REA_TEST' or var.stand == 'ZERO':
            secure(message)
            if user_true == "true":
                pass
            else:
                menu_help(message)
        if var.build_deploy == "Build" or var.build_deploy == "Build_and_Deploy":
            markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
            markup.add("App", "DB_change_script", "DB_refresh_db")
            msg = bot.reply_to(message, "Выберите приложение для сборки:", reply_markup=markup)
            bot.register_next_step_handler(msg, pizi_build_job_jenkins)
        if var.build_deploy == "Deploy":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add("App", "Robot")
            msg = bot.reply_to(message, "Выберите приложение для обновления:", reply_markup=markup)
            bot.register_next_step_handler(msg, pizi_job_jenkins)
    except Exception as e:
        errors(message)


def pizi_job_jenkins(message):
    try:
        chat_id = message.chat.id
        var = user_dict[chat_id]
        if var.arm == None:
            arm = message.text
            var.arm = arm
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        params = {"stand": var.stand}
        text = "{} cтучится в jenkins чтобы обновить {} для Сбора на {}".format(name_user, var.arm, var.stand)
        logging.warning(u"%s", text)
        try:
            jenkins.build_job('GISTEK_Pizi/Update_' + str(var.arm), params)
        except Exception:
            bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
            authentication(0)
            jenkins.build_job('GISTEK_Pizi/Update_' + str(var.arm), params)
        text = "{} обновляет на Сборе {}".format(name_user, var.arm)
        logging.warning(u"%s", text)
        bot.send_message(message.chat.id, "..еще 2 минуты и приложение " + str(var.arm) + " на Сборе обновится")
        job = jenkins.get_job('GISTEK_Pizi/Update_' + str(var.arm))
        test_run(message, var.arm, params, 120, job)
        menu_help(message)
    except Exception as e:
        errors(message)


def pizi_build_job_jenkins(message):
    try:
        chat_id = message.chat.id
        arm = message.text
        var = user_dict[chat_id]
        var.arm = arm
        if var.arm == "App":
            markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
            markup.add("Да", "Изменить версии", "Вернуться в главное меню")
            text = "Собрать Сбор с \ngtafo версии - {} \ngtarm версии - {} \ngttechnologist версии - {} \ngtonl версии - {} \ngtimpxml версии - {} \ngtxml версии - {} \ngttransport версии - {} \ngtcontrol версии - {} \ngtexpgisee версии - {} \ngtdownload версии - {} \ngtclassifier версии - {} \nclassifier_view версии - {} \nticket версии - {} \nsso-server версии - {} \nregistration версии - {} \nloadssb версии - {}".format(var.gtafo, var.gtarm, var.gttechnologist, var.gtonl, var.gtimpxml, var.gtxml, var.gttransport, var.gtcontrol, var.gtexpgisee, var.gtdownload, var.gtclassifier, var.classifier_view, var.ticket, var.sso_server, var.registration, var.loadssb)
            msg = bot.reply_to(message, text, reply_markup=markup)
            bot.register_next_step_handler(msg, pizi_build_job_jenkins_2)
        else:
            bot.send_message(message.chat.id, "пыжимся и тужимся... ")
            text = "{} cтучится в jenkins чтобы собрать приложение {} для Сбора".format(name_user, var.arm)
            logging.warning( u"%s", text)
            try:
                jenkins.build_job('GISTEK_Pizi/Build_' + str(var.arm))
            except Exception:
                bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
                authentication(0)
                jenkins.build_job('GISTEK_Pizi/Build_' + str(var.arm))
            text = "{} собирает для сбора {}".format(name_user, var.arm)
            logging.warning( u"%s", text)
            bot.send_message(message.chat.id, "..еще минута и " + str(var.arm) + " для Cбора соберется")
            job = jenkins.get_job('GISTEK_Pizi/Build_' + str(var.arm))
            test_run(message, var.arm, "Без оных", 55, job)
            menu_help(message)
    except Exception as e:
        errors(message)


def pizi_build_job_jenkins_2(message):
    try:
        chat_id = message.chat.id
        var = user_dict[chat_id]
        areyousure = message.text
        if areyousure == "Вернуться в главное меню":
            menu_help(message)
        elif areyousure == "Да" or areyousure == "Всё ок":
            bot.send_message(message.chat.id, "пыжимся и тужимся... ")
            params = {"TAG_GTAFO": var.gtafo, "TAG_GTARM": var.gtarm, "TAG_GTTECHNOLOGIST": var.gttechnologist, "TAG_GTONL": var.gtonl, "TAG_GTIMPXML": var.gtimpxml, "TAG_GTXML": var.gtxml, "TAG_GTTRANSPORT": var.gttransport, "TAG_GTCONTROL": var.gtcontrol, "TAG_GTEXPGISEE": var.gtexpgisee, 	"TAG_GTDOWNLOAD": var.gtdownload, "TAG_GTCLASSIFIER": var.gtclassifier, "TAG_CLASSIFIER_VIEW": var.classifier_view, "TAG_TICKET": var.ticket, "TAG_SSO_SERVER": var.sso_server, "TAG_REGISTRATION": var.registration, "TAG_LOADSSB": var.loadssb}
            text = "{} cтучится в jenkins чтобы собрать приложения для Сбора".format(name_user)
            logging.warning(u"%s", text)
            try:
                jenkins.build_job('GISTEK_Pizi/Build_App', params)
            except Exception:
                bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
                authentication(0)
                jenkins.build_job('GISTEK_Pizi/Build_App', params)
            text = "{} собирает приложения для Сбора".format(name_user)
            logging.warning(u"%s", text)
            bot.send_message(message.chat.id, "..еще 3 минуты и соберем приложения для Сбора")
            job = jenkins.get_job('GISTEK_Pizi/Build_App')
            test_run(message, "Build_App", params, 185, job)
            if var.build_deploy == "Build_and_Deploy":
                var.build_deploy = "Deploy"
                bot.send_message(message.chat.id, "Теперь выложим это добро на сервер.")
                pizi_job_jenkins(message)
            else:
                menu_help(message)
        # if areyousure == "Изменить версии":
        else:
            markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
            markup.add("Всё ок", "Вернуться в главное меню", "gtafo", "gtarm", "gttechnologist", "gtonl", "gtimpxml", "gtxml", "gttransport", "gtcontrol", "gtexpgisee", "gtdownload", "gtclassifier", "classifier-view", "ticket", "sso-server", "registration", "loadssb")
            text = "Выберите, что надо изменить. Текущие версии \ngtafo - {} \ngtarm - {} \ngttechnologist - {} \ngtonl - {} \ngtimpxml - {} \ngtxml - {} \ngttransport - {} \ngtcontrol - {} \ngtexpgisee - {} \ngtdownload - {} \ngtclassifier - {} \nclassifier-view - {} \nticket - {} \nsso-server - {} \nregistration - {} \nloadssb - {}".format(var.gtafo, var.gtarm, var.gttechnologist, var.gtonl, var.gtimpxml, var.gtxml, var.gttransport, var.gtcontrol, var.gtexpgisee, var.gtdownload, var.gtclassifier, var.classifier_view, var.ticket, var.sso_server, var.registration, var.loadssb)
            msg = bot.reply_to(message, text, reply_markup=markup)
            bot.register_next_step_handler(msg, pizi_build_job_jenkins_3)
    except Exception as e:
        errors(message)


def pizi_build_job_jenkins_3(message):
    try:
        areyousure = message.text
        if areyousure == "Вернуться в главное меню":
            menu_help(message)
        elif areyousure == "Всё ок":
            pizi_build_job_jenkins_2(message)
        elif areyousure == "gtafo" or areyousure == "gtarm" or areyousure == "gttechnologist" or areyousure == "gtonl" or areyousure == "gtimpxml" or areyousure == "gtimpxml" or areyousure == "gtxml" or areyousure == "gttransport" or areyousure == "gtcontrol" or areyousure == "gtexpgisee" or areyousure == "gtdownload" or areyousure == "gtclassifier" or areyousure == "classifier-view" or areyousure == "ticket" or areyousure == "sso-server" or areyousure == "registration" or areyousure == "loadssb":
            chat_id = message.chat.id
            arm = message.text
            var = user_dict[chat_id]
            var.arm = arm
            markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
            markup.add("release", "dev-fedorov", "dev-brykov", "dev-turchinskiy")
            text = "Выберите, ветку (или напишите свою)"
            msg = bot.reply_to(message, text, reply_markup=markup)
            bot.register_next_step_handler(msg, pizi_build_job_jenkins_4)
    except Exception as e:
        errors(message)


def pizi_build_job_jenkins_4(message):
    try:
        chat_id = message.chat.id
        var = user_dict[chat_id]
        if var.arm == "gtafo":
            var.gtafo = message.text
        if var.arm == "gtarm":
            var.gtarm = message.text
        if var.arm == "gttechnologist":
            var.gttechnologist = message.text
        if var.arm == "gtonl":
            var.gtonl = message.text
        if var.arm == "gtimpxml":
            var.gtimpxml = message.text
        if var.arm == "gtxml":
            var.gtxml = message.text
        if var.arm == "gttransport":
            var.gttransport = message.text
        if var.arm == "gtcontrol":
            var.gtcontrol = message.text
        if var.arm == "gtexpgisee":
            var.gtexpgisee = message.text
        if var.arm == "gtdownload":
            var.gtdownload = message.text
        if var.arm == "gtclassifier":
            var.gtclassifier = message.text
        if var.arm == "classifier-view":
            var.classifier_view = message.text
        if var.arm == "ticket":
            var.ticket = message.text
        if var.arm == "sso-server":
            var.sso_server = message.text
        if var.arm == "registration":
            var.registration = message.text
        if var.arm == "loadssb":
            var.loadssb = message.text
        pizi_build_job_jenkins_2(message)
    except Exception as e:
        errors(message)


def poib_action_select(message):
    secure(message)
    if user_true == "true":
        global name_user
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
        markup.add('Build', 'Deploy', "Назад в главное меню")
        msg = bot.reply_to(message, "Выберите, что будем делать", reply_markup=markup)
        bot.register_next_step_handler(msg, poib_select)


def poib_select(message):
    try:
        chat_id = message.chat.id
        build_deploy = message.text
        var = Var(build_deploy)
        user_dict[chat_id] = var
        var.build_deploy = build_deploy
        if var.build_deploy == "Build":
            bot.send_message(message.chat.id, "пыжимся и тужимся... ")
            text = "{} cтучится в jenkins чтобы собрать приложение для ПОИБ".format(name_user)
            logging.warning(u"%s", text)
            try:
                jenkins.build_job('GISTEK_Poib/Build')
            except Exception:
                bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
                authentication(0)
                jenkins.build_job('GISTEK_Poib/Build')
            text = "{} собирает ПОИБ".format(name_user)
            logging.warning(u"%s", text)
            bot.send_message(message.chat.id, "..еще минута и ПОИБ соберется")
            job = jenkins.get_job('GISTEK_Poib/Build')
            test_run(message, "сборка ПОИБ", "без параметров", 230, job)
            menu_help(message)
        if var.build_deploy == "Deploy":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('DKP', 'ZERO', 'REA_TEST', 'PI')
            msg = bot.reply_to(message, "Выберите стенд", reply_markup=markup)
            bot.register_next_step_handler(msg, poib_app_select)
        if var.build_deploy == "Назад в главное меню":
            menu_help(message)
    except Exception as e:
        errors(message)


def poib_app_select(message):
    try:
        chat_id = message.chat.id
        stand = message.text
        var = user_dict[chat_id]
        var.stand = stand
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
            poib_job_jenkins(message)
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
        if var.issue_select == "No":
            params = {"stand": var.stand, "version": str(var.tag)}
        elif var.issue_select != "No":
            params = {"stand": var.stand, "version": str(var.tag), "issue_id": str(var.issue_id)}
        text = "{} cтучится в jenkins чтобы выполнить {} для ПОИБ".format(name_user, var.arm)
        logging.warning(u"%s", text)
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        try:
            jenkins.build_job('GISTEK_Poib/' + str(var.arm), params)
        except Exception:
            bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
            authentication(0)
            jenkins.build_job('GISTEK_Poib/' + str(var.arm), params)
        text = "{} на ПОИБ выполняется {} версия {}".format(name_user, var.arm, var.tag)
        logging.warning(u"%s", text)
        bot.send_message(message.chat.id, "..еще 2 минуты и приложение " + str(var.arm) + " на ПОИБ обновится, версия " + str(var.tag))
        job = jenkins.get_job('GISTEK_Poib/' + str(var.arm))
        test_run(message, var.arm, params, 120, job)
        menu_help(message)
    except Exception as e:
        errors(message)


def system_action_select(message):
    secure(message)
    if user_true == "true":
        global name_user
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        markup = types.ReplyKeyboardMarkup(row_width=3, one_time_keyboard=True)
        markup.add('DKP', 'ZERO', 'REA_TEST', 'PK', 'PI', "Назад в главное меню")
        msg = bot.reply_to(message, "Выберите стенд", reply_markup=markup)
        bot.register_next_step_handler(msg, system_select_restart)


def system_select_restart(message):
    try:
        chat_id = message.chat.id
        stand = message.text
        var = Var(stand)
        user_dict[chat_id] = var
        var.stand = stand
        # if var.stand == "PI":
        #     bot.send_message(message.chat.id, "")
        if var.stand == "Назад в главное меню":
            menu_help(message)
        else:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('pizi_app', 'poib', 'portal_open', 'portal_close', 'pentaho_all', 'pentaho_oil_gas', 'pentaho_ee', 'pentaho_electro', 'pentaho_integr', "pentaho_coal", 'robot')
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
        params = {"stand": var.stand, "system": var.arm}
        text = "{} cтучится в jenkins чтобы перезагрузить {} на {}".format(name_user, var.arm, var.stand)
        logging.warning(u"%s", text)
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        try:
            jenkins.build_job('GISTEK_Restart', params)
        except Exception:
            bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
            authentication(0)
            jenkins.build_job('GISTEK_Restart', params)
        text = "{} перезагружается {} на {}".format(name_user, var.arm, var.stand)
        logging.warning(u"%s", text)
        bot.send_message(message.chat.id, "..еще минуты и приложение " + str(var.arm) + " на " + str(var.stand) + " перезапустится")
        job = jenkins.get_job('GISTEK_Restart')
        test_run(message, var.arm, params, 40, job)
        menu_help(message)
    except Exception as e:
        errors(message)


@bot.message_handler(commands=['dev_klochkov'])
def dev_action_select(message):
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
        build_deploy = message.text
        var = Var(build_deploy)
        user_dict[chat_id] = var
        var.build_deploy = build_deploy
        if var.build_deploy == "restart":
            params = {"stand": "DEV", "system": "pentaho"}
            text = "{} cтучится в jenkins чтобы перезагрузить pentaho на DEV".format(name_user)
            logging.warning(u"%s", text)
            bot.send_message(message.chat.id, "пыжимся и тужимся... ")
            try:
                jenkins.build_job('GISTEK_Restart', params)
            except Exception:
                bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
                authentication(0)
                jenkins.build_job('GISTEK_Restart', params)
            text = "{} перезагружается pentaho на DEV".format(name_user)
            logging.warning(u"%s", text)
            bot.send_message(message.chat.id, "..еще минуты и приложение pentaho на DEV перезапустится")
            job = jenkins.get_job('GISTEK_Restart')
            test_run(message, "Без оных", params, 70, job)
            menu_help(message)
        if var.build_deploy == "deploy":
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
        logging.warning(u"%s", text)
        params = {"version": var.tag}
        bot.send_message(message.chat.id, "пыжимся и тужимся... ")
        try:
            jenkins.build_job('GISTEK_Pentaho/Build_fileProperties', params)
        except Exception:
            bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
            authentication(0)
            jenkins.build_job('GISTEK_Pentaho/Build_fileProperties', params)
        text = "{} собирает fileProperties".format(name_user)
        logging.warning(u"%s", text)
        bot.send_message(message.chat.id, "..еще 3 минуты и плагин fileProperties соберется")
        job = jenkins.get_job('GISTEK_Pentaho/Build_fileProperties')
        test_run(message, "Без параметров", params, 180, job)
        params = {"stand": "DEV", "tags": "fileProperties", "version": str(var.tag)}
        text = "{} cтучится в jenkins чтобы обновить fileProperties версии {} для пентахи на DEV".format(name_user, var.tag)
        logging.warning(u"%s", text)
        try:
            jenkins.build_job('GISTEK_Pentaho/Update_Pentaho', params)
        except Exception:
            bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
            authentication(0)
            jenkins.build_job('GISTEK_Pentaho/Update_Pentaho', params)
        text = "{} на Пентахах DEV обновляется fileProperties версия {}".format(name_user, var.tag)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "..еще 2 минуты и приложение fileProperties на пентахах DEV обновится до версии " + str(var.tag))
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

import pizi, integration, poib, portal, mobile, pentaho, arm, restart


@bot.message_handler(commands=['pizi'])
def main_pizi_action(message):
    secure(message)
    if user_true == "true":
        pizi.pizi_action(bot, errors, jenkins, test_run, message)


@bot.message_handler(commands=['build_arm'])
def main_arm_action(message):
    secure(message)
    if user_true == "true":
        arm.arm_action(bot, errors, jenkins, test_run, message)


@bot.message_handler(commands=['restart'])
def main_restart_action(message):
    secure(message)
    if user_true == "true":
        restart.restart_action(bot, errors, jenkins, test_run, message)


@bot.message_handler(commands=['poib'])
def main_poib_action(message):
    secure(message)
    if user_true == "true":
        poib.poib_action(bot, errors, jenkins, test_run, message)


@bot.message_handler(commands=['integration'])
def main_integration_action(message):
    secure(message)
    if user_true == "true":
        integration.integration_action(bot, errors, jenkins, test_run, message)


@bot.message_handler(commands=['pentaho'])
def main_pentaho_action(message):
    secure(message)
    if user_true == "true":
        pentaho.pentaho_action(bot, errors, jenkins, test_run, message)


@bot.message_handler(commands=['portal'])
def main_portal_action(message):
    secure(message)
    if user_true == "true":
        portal.portal_action(bot, errors, jenkins, test_run, message)


@bot.message_handler(commands=['mobile'])
def main_mobile_action(message):
    secure(message)
    if user_true == "true":
        mobile.mobile_action(bot, errors, jenkins, test_run, message)

# принимает сообщения от начальника на деплой
@bot.message_handler(func=lambda message: re.search(r"monitor |registration |formfillonline |sso-server |transport |afo |import-ps-ues-gisee |loadssb |ticket |classifier-view |classifier ", message.text))
def main_pizi_repost_buld_deploy(message):
    secure(message)
    if user_true == "true":
        pizi.pizi_repost_build_deploy(bot, errors, jenkins, test_run, message)


while True:
    # try:
    #     bot.polling(none_stop=True)
    # except Exception as e:
    #     text = "Ошибка соединения, перелогиниваемся."
    #     logging.warning( u"%s", text)
    #     authentication(0)
    bot.polling(none_stop=True)
