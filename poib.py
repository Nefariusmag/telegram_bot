# -*- coding: utf-8 -*-
import re, logging, os, random

def poib_action(bot, errors, jenkins, test_run, message):
    try:
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        search_action = re.search("build|BUILD|Build|Собрать|сборка|собрать|билд|сбилди|deploy|Deploy|обнови|update|Update|UPDATE|Обнови|деплой", message.text)
        if search_action != None:
            search_action = search_action.group(0)
        if search_action in ["build", "BUILD", "Build", "Собрать", "сборка", "собрать", "билд", "сбилди"]:
            jenkins.build_job('GISTEK_Poib/Build')
            text = "{} собирает ПОИБ".format(name_user)
            logging.warning( u"%s", text)
            bot.send_message(message.chat.id, "..еще минута и ПОИБ соберется")
            job = jenkins.get_job('GISTEK_Poib/Build')
            test_run(message, "сборка ПОИБ", "без параметров", 65, job)
        elif search_action in ["deploy", "Deploy", "обнови", "update", "Update", "UPDATE", "Обнови", "деплой"]:
            search_stand = re.search(r"ПИ |пи |PI |pi |ПК |пк |PK |pk |REA_TEST |rea_test |PP |pp |ПП |пп ", message.text)
            if search_stand != None:
                search_stand = search_stand.group(0)
            if search_stand in ["ПК", "пк", "PK", "pk"]:
                stand = "PK"
            elif search_stand in ["ПИ", "пи", "PI", "pi"]:
                stand = "PI"
            elif search_stand in ["REA_TEST", "rea_test", "PP", "pp", "ПП", "пп"]:
                stand = "REA_TEST"
            else:
                bot.send_message(message.chat.id, "Вы не указали стенд, но подумал я решил за вас и решил, что это будет тестовый")
                stand = "REA_TEST"
            search_version = re.search(r"[0-9].[0-9].[0-9]{2}|[0-9].[0-9].[0-9]", message.text)
            if search_version != None:
                search_version = search_version.group(0)
                tag = search_version
            else:
                tag = "1.5.9"
            search_issue = re.search(r"#[0-9]{5}", message.text)
            if search_issue != None:
                search_issue = search_issue.group(0)
                issue_id = search_issue
                params = {"stand": stand, "version": tag, "issue_id": issue_id}
            else:
                params = {"stand": stand, "version": tag}
                issue_id = "отсутствует"
            jenkins.build_job('GISTEK_Poib/Update_App', params)
            text = "..еще 2 минуты и ПОИБ на {} обновится до версии {}, задача {}".format(stand, tag, issue_id)
            bot.send_message(message.chat.id, text)
            job = jenkins.get_job('GISTEK_Poib/Update_App')
            test_run(message, "poib", params, 120, job)
        else:
            bot.send_message(message.chat.id, "Что делать то?")
            sti = random.choice(os.listdir("error_sti"))
            sti = "error_sti/{}".format(sti)
            sti = open(sti, 'rb')
            bot.send_sticker(message.chat.id, sti)
    except Exception as e:
        errors(message)
