# -*- coding: utf-8 -*-
import re, logging, random, os, config


def mobile_action(bot, errors, jenkins, test_run, message):
    try:
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        search_action = re.search("build|BUILD|Build|Собрать|сборка|собрать|билд|сбилди|deploy|Deploy|обнови|update|Update|UPDATE|Обнови|деплой", message.text)
        if search_action != None:
            search_action = search_action.group(0)
        if search_action in ["build", "BUILD", "Build", "Собрать", "сборка", "собрать", "билд", "сбилди"]:
            # ищем приложение
            search_arm = re.search(r"Android|android|мобилку|мобилка|portlet|портлет|web|web_service|веб|веб-сервис", message.text)
            if search_arm != None:
                arm = search_arm.group(0)
                if arm in ["Android", "android", "мобилка", "мобилку"]:
                    arm = "Android"
                if arm in ["portlet", "портлет"]:
                    arm = "portlet"
                if arm in ["web_service", "web", "веб", "веб-сервис"]:
                    arm = "web_service"
            else:
                arm = None
            # проверка на тег
            search_version = re.search(r"[0-9].[0-9].[0-9]{2}|[0-9].[0-9].[0-9]|[0-9].[0-9]{2}|[0-9].[0-9]", message.text)
            if search_version != None:
                search_version = search_version.group(0)
                tag = search_version
            else:
                tag = None
            # ищем стенд
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
            # ищем задачу (для сборки приложения)
            search_issue = re.search(r"#[0-9]{5}", message.text)
            if search_issue != None:
                search_issue = search_issue.group(0)
                issue_id = search_issue
            else:
                issue_id = None
            # проверка на приложение и тег
            if arm != None:
                if tag == None and issue_id == None:
                    bot.send_message(message.chat.id, "Версии нету, буду собирать последнюю")
                    params = {"stand": stand}
                if tag != None and issue_id == None:
                    params = {"stand": stand, "version": tag}
                if tag == None and issue_id != None:
                    bot.send_message(message.chat.id, "Версии нету, буду собирать последнюю")
                    params = {"stand": stand, "issue_id": issue_id}
                if tag != None and issue_id != None:
                    params = {"stand": stand, "issue_id": issue_id, "version": tag}
                jenkins.build_job('GISTEK_MobileApp/Build_' + arm, params)
                text = "{} собирает {} для мобилки".format(name_user, arm)
                logging.warning( u"%s", text)
                text = "..еще пара минут и {} для мобилки соберется".format(arm)
                bot.send_sticker(message.chat.id, random.choice(config.deploy_sticker))
                bot.send_message(message.chat.id, text)
                job = jenkins.get_job('GISTEK_MobileApp/Build_' + arm)
                test_run(message, arm, params, 160, job)
            else: # если АРМ не указан
                bot.send_message(message.chat.id, "Я хоть и умный, но мне всё таки нужено знать, что собирать ((")
                # отправить стикер
                bot.send_sticker(message.chat.id, random.choice(config.error_sticker))
        elif search_action in ["deploy", "Deploy", "обнови", "update", "Update", "UPDATE", "Обнови", "деплой"]:
            # проверка на стенд
            search_stand = re.search(r"ПИ|пи|PI|pi|ПК|пк|PK|pk|REA_TEST|rea_test|PP|pp|ПП|пп", message.text)
            if search_stand != None:
                search_stand = search_stand.group(0)
            if search_stand in ["ПК", "пк", "PK", "pk"]:
                stand = "PK"
            elif search_stand in ["ПИ", "пи", "PI", "pi"]:
                stand = "PI"
            elif search_stand in ["REA_TEST", "rea_test", "PP", "pp", "ПП", "пп"]:
                stand = "REA_TEST"
            else:
                bot.send_message(message.chat.id, "Вы не указали стенд, но я решил что это - тест")
                stand = "REA_TEST"
            # проверка на тег
            search_version = re.search(r"[0-9].[0-9].[0-9]{2}|[0-9].[0-9].[0-9]|[0-9].[0-9]{2}|[0-9].[0-9]", message.text)
            if search_version != None:
                search_version = search_version.group(0)
                tag = search_version
            else:
                tag = None
                bot.send_message(message.chat.id, "Тег не задан(( я не буду это обновлять")
            # проверка на приложение
            search_arm = re.search(r"portlet|портлет|web|web_service|веб|веб-сервис", message.text)
            if search_arm != None:
                arm = search_arm.group(0)
                if arm in ["portlet", "портлет"]:
                    arm = "portlet"
                if arm in ["web_service", "web", "веб", "веб-сервис"]:
                    arm = "web_service"
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
                jenkins.build_job('GISTEK_MobileApp/Update', params)
                text = "..еще минута и для мобильного приложения на {} обновится {} до версии {}, задача {}".format(stand, arm, tag, issue_id)
                bot.send_message(message.chat.id, text)
                bot.send_sticker(message.chat.id, random.choice(config.deploy_sticker))
                job = jenkins.get_job('GISTEK_MobileApp/Update')
                test_run(message, arm, params, 60, job)
            else: # не указан тег \ приложение \ ОЧ\ЗЧ портала
                bot.send_sticker(message.chat.id, random.choice(config.error_sticker))
        else:
            bot.send_message(message.chat.id, "Стоит указать что делать с этим - собрать? обновить?")
            # отправить стикер
            bot.send_sticker(message.chat.id, random.choice(config.error_sticker))
    except Exception as e:
        errors(message)
