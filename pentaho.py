# -*- coding: utf-8 -*-
import re, logging, random, os

def pentaho_action(bot, errors, jenkins, test_run, message):
    try:
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        search_action = re.search("build|BUILD|Build|Собрать|сборка|собрать|билд|сбилди|deploy|Deploy|обнови|update|Update|UPDATE|Обнови|деплой", message.text)
        if search_action != None:
            search_action = search_action.group(0)
        if search_action in ["build", "BUILD", "Build", "Собрать", "сборка", "собрать", "билд", "сбилди"]:
            search_arm = re.search(r"plugins|fileProperties|quixote_theme|quixote-theme|langpack|cas_tek|cas-tek", message.text)
            if search_arm != None:
                arm = search_arm.group(0)
                if arm in ["plugins"]:
                    arm = "plugins"
                if arm in ["fileProperties"]:
                    arm = "fileProperties"
                if arm in ["quixote_theme", "quixote-theme"]:
                    arm = "quixote_theme"
                if arm in ["langpack"]:
                    arm = "langpack"
                if arm in ["cas_tek", "cas-tek"]:
                    arm = "cas_tek"
                jenkins.build_job('GISTEK_Pentaho/Build_' + arm)
                text = "{} собирает приложение {} для пентахи".format(name_user, arm)
                logging.warning( u"%s", text)
                text = "..еще 2 минуты приложение {} для пентахи соберется".format(arm)
                bot.send_message(message.chat.id, text)
                sti = random.choice(os.listdir("deploy_sti"))
                sti = "deploy_sti/{}".format(sti)
                sti = open(sti, 'rb')
                bot.send_sticker(message.chat.id, sti)
                job = jenkins.get_job('GISTEK_Pentaho/Build_' + arm)
                test_run(message, arm, "без параметров", 90, job)
            else: # если АРМ не указан
                bot.send_message(message.chat.id, "Я хоть и умный, но мне всё таки нужено знать, что собирать ((")
                # отправить стикер
                sti = random.choice(os.listdir("error_sti"))
                sti = "error_sti/{}".format(sti)
                sti = open(sti, 'rb')
                bot.send_sticker(message.chat.id, sti)
        elif search_action in ["deploy", "Deploy", "обнови", "update", "Update", "UPDATE", "Обнови", "деплой"]:
            # проверка на стенд
            search_stand = re.search(r"ПИ|пи|PI|pi|ПК|пк|PK|pk|REA_TEST|rea_test|PP|pp|ПП|пп|DKP|dkp|zero|ZERO", message.text)
            if search_stand != None:
                search_stand = search_stand.group(0)
            if search_stand in ["ПК", "пк", "PK", "pk"]:
                stand = "PK"
            elif search_stand in ["ПИ", "пи", "PI", "pi"]:
                stand = "PI"
            elif search_stand in ["REA_TEST", "rea_test", "PP", "pp", "ПП", "пп"]:
                stand = "REA_TEST"
            elif search_stand in ["ZERO", "zero", "зеро", "зиро", "нулевой"]:
                stand = "ZERO"
            elif search_stand in ["DKP", "dkp", "дкп", "ДКП"]:
                stand = "DKP"
            else:
                stand = "DKP"
                bot.send_message(message.chat.id, "Вы не указали стенд, но подумал я решил за вас и решил, что это будет " + stand)
            # проверка на тег
            search_version = re.search(r"[0-9].[0-9].[0-9]{2}|[0-9].[0-9].[0-9]", message.text)
            if search_version != None:
                search_version = search_version.group(0)
                tag = search_version
            else:
                tag = None
                bot.send_message(message.chat.id, "Тег не задан(( я не буду это обновлять")
            # проверка на приложение
            search_arm = re.search(r"plugins|fileProperties|quixote_theme|langpack|cas_tek", message.text)
            if search_arm != None:
                arm = search_arm.group(0)
                if arm in ["plugins"]:
                    arm = "plugins"
                if arm in ["fileProperties"]:
                    arm = "fileProperties"
                if arm in ["quixote_theme"]:
                    arm = "quixote_theme"
                if arm in ["langpack"]:
                    arm = "langpack"
                if arm in ["cas_tek"]:
                    arm = "cas_tek"
            else:
                arm = None
                bot.send_message(message.chat.id, "а как же приложение?! это же самое главное!")
            # проверка на номер задачи
            search_issue = re.search(r"#[0-9]{5}", message.text)
            if search_issue != None:
                search_issue = search_issue.group(0)
                issue_id = search_issue
            else:
                issue_id = "отсутствует"
            if arm != None and tag != None:
                if search_issue != None:
                    params = {"stand": stand, "version": tag, "tags": arm, "issue_id": issue_id}
                else:
                    params = {"stand": stand, "version": tag, "tags": arm}
                jenkins.build_job('GISTEK_Pentaho/Update_Pentaho', params)
                text = "..еще минута и на пентахах на {} обновятся {} до версии {}, задача {}".format(stand, arm, tag, issue_id)
                bot.send_message(message.chat.id, text)
                sti = random.choice(os.listdir("deploy_sti"))
                sti = "deploy_sti/{}".format(sti)
                sti = open(sti, 'rb')
                bot.send_sticker(message.chat.id, sti)
                job = jenkins.get_job('GISTEK_Pentaho/Update_Pentaho')
                test_run(message, arm, params, 70, job)
            else: # не указан тег или приложение
                sti = random.choice(os.listdir("error_sti"))
                sti = "error_sti/{}".format(sti)
                sti = open(sti, 'rb')
                bot.send_sticker(message.chat.id, sti)
        else:
            bot.send_message(message.chat.id, "Стоит указать что делать с этим - собрать? обновить?")
            # отправить стикер
            sti = random.choice(os.listdir("error_sti"))
            sti = "error_sti/{}".format(sti)
            sti = open(sti, 'rb')
            bot.send_sticker(message.chat.id, sti)
    except Exception as e:
        errors(message)
