# -*- coding: utf-8 -*-
import re, logging, random, os

def portal_action(bot, errors, jenkins, test_run, message):
    try:
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        search_action = re.search("build|BUILD|Build|Собрать|сборка|собрать|билд|сбилди|deploy|Deploy|обнови|update|Update|UPDATE|Обнови|деплой", message.text)
        if search_action != None:
            search_action = search_action.group(0)
        if search_action in ["build", "BUILD", "Build", "Собрать", "сборка", "собрать", "билд", "сбилди"]:
            search_arm = re.search(r"hook-asset-publisher|asset|hook-asset|asset-publisher|hook-search|inspinia-theme|inspinia|languagePackRU|languagePack|language|login-hook|login|логин|mainpageGEO|GEO|geo|ГЕО|гео|notification-portlet|notification|npa-loader|npa|нпа|portal-iframe|iframe|reports-display-portlet|reports-display|reports|display|slider|слайдер|subsystem-search|subsystem|сабсистем|support-mail-portlet|support-mail|support|mail|urc-theme|urc", message.text)
            if search_arm != None:
                arm = search_arm.group(0)
                if arm in ["hook-asset-publisher", "asset", "hook-asset", "asset-publisher"]:
                    arm = "hook-asset-publisher"
                if arm in ["hook-search"]:
                    arm = "hook-search"
                if arm in ["inspinia-theme", "inspinia"]:
                    arm = "inspinia-theme"
                if arm in ["languagePackRU", "languagePack", "language"]:
                    arm = "languagePackRU"
                if arm in ["login-hook", "login", "логин"]:
                    arm = "login-hook"
                if arm in ["mainpageGEO", "GEO", "ГЕО", "гео", "geo"]:
                    arm = "mainpageGEO"
                if arm in ["notification-portlet", "notification"]:
                    arm = "notification-portlet"
                if arm in ["npa-loader", "npa", "нпа"]:
                    arm = "npa-loader"
                if arm in ["portal-iframe", "iframe"]:
                    arm = "portal-iframe"
                if arm in ["reports-display-portlet", "reports-display", "display", "reports"]:
                    arm = "reports-display-portlet"
                    bot.send_message(message.chat.id, "reports-display-portlet для сборки лучше в будущем указать стенд, а пока соберу для ПП")
                if arm in ["slider", "слайдер"]:
                    arm = "slider"
                if arm in ["subsystem-search", "subsystem", "сабсистем"]:
                    arm = "subsystem-search"
                if arm in ["support-mail-portlet", "support-mail", "support", "mail"]:
                    arm = "support-mail-portlet"
                if arm in ["urc-theme", "urc"]:
                    arm = "urc-theme"
                if arm == "reports-display-portlet": # ищем стенд для особых случаев
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
                        stand = "REA_TEST"
                    params = {"stand": stand}
                    jenkins.build_job('GISTEK_Portal/' + arm, params)
                else: # обычная сборка без указания теста
                    jenkins.build_job('GISTEK_Portal/' + arm)
                text = "{} собирает приложение {} для портала".format(name_user, arm)
                logging.warning( u"%s", text)
                text = "..еще минута приложение {} для портала соберется".format(arm)
                bot.send_message(message.chat.id, text)
                job = jenkins.get_job('GISTEK_Portal/' + arm)
                test_run(message, arm, "без параметров", 60, job)
            else: # если АРМ не указан
                bot.send_message(message.chat.id, "Я хоть и умный, но мне всё таки нужено знать, что собирать ((")
                # отправить стикер
                sti = random.choice(os.listdir("error_sti"))
                sti = "error_sti/{}".format(sti)
                sti = open(sti, 'rb')
                bot.send_sticker(message.chat.id, sti)
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
            # проверка на открытую \ закрытую часть
            search_open_close = re.search(r"public|open|close|internal|открытая|ОЧ|оч|закрытая|ЗЧ|зч", message.text)
            if search_open_close != None:
                search_open_close = search_open_close.group(0)
            if search_open_close in ["public", "open", "открытая", "ОЧ", "оч"]:
                open_close = "public"
            elif search_open_close in ["internal", "close", "закрытая", "ЗЧ", "зч"]:
                open_close = "internal"
            else:
                open_close = None
                bot.send_message(message.chat.id, "открытая? закрытая? без этого не буду это обновлять")
            # проверка на тег
            search_version = re.search(r"[0-9].[0-9].[0-9]{2}|[0-9].[0-9].[0-9]", message.text)
            if search_version != None:
                search_version = search_version.group(0)
                tag = search_version
            else:
                tag = None
                bot.send_message(message.chat.id, "Тег не задан(( я не буду это обновлять")
            # проверка на приложение
            search_arm = re.search(r"hook-asset-publisher|asset|hook-asset|asset-publisher|hook-search|inspinia-theme|inspinia|languagePackRU|languagePack|language|login-hook|login|логин|mainpageGEO|GEO|geo|ГЕО|гео|notification-portlet|notification|npa-loader|npa|нпа|portal-iframe|iframe|reports-display-portlet|reports-display|reports|display|slider|слайдер|subsystem-search|subsystem|сабсистем|support-mail-portlet|support-mail|support|mail|urc-theme|urc", message.text)
            if search_arm != None:
                arm = search_arm.group(0)
                if arm in ["hook-asset-publisher", "asset", "hook-asset", "asset-publisher"]:
                    arm = "hook-asset-publisher"
                if arm in ["hook-search"]:
                    arm = "hook-search"
                if arm in ["inspinia-theme", "inspinia"]:
                    arm = "inspinia-theme"
                if arm in ["languagePackRU", "languagePack", "language"]:
                    arm = "languagePackRU"
                if arm in ["login-hook", "login", "логин"]:
                    arm = "login-hook"
                if arm in ["mainpageGEO", "GEO", "ГЕО", "гео", "geo"]:
                    arm = "mainpageGEO"
                if arm in ["notification-portlet", "notification"]:
                    arm = "notification-portlet"
                if arm in ["npa-loader", "npa", "нпа"]:
                    arm = "npa-loader"
                if arm in ["portal-iframe", "iframe"]:
                    arm = "portal-iframe"
                if arm in ["reports-display-portlet", "reports-display", "display", "reports"]:
                    arm = "reports-display-portlet"
                if arm in ["slider", "слайдер"]:
                    arm = "slider"
                if arm in ["subsystem-search", "subsystem", "сабсистем"]:
                    arm = "subsystem-search"
                if arm in ["support-mail-portlet", "support-mail", "support", "mail"]:
                    arm = "support-mail-portlet"
                if arm in ["urc-theme", "urc"]:
                    arm = "urc-theme"
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
            if arm != None and tag != None and open_close != None:
                if search_issue != None:
                    params = {"stand": stand, "version": tag, "public_internal": open_close, "TARGET_TAGS": arm, "issue_id": issue_id}
                else:
                    params = {"stand": stand, "version": tag, "public_internal": open_close, "TARGET_TAGS": arm}
                jenkins.build_job('GISTEK_Portal/Update_App', params)
                text = "..еще 2 минуты и на портале {} на {} обновится {} до версии {}, задача {}".format(open_close, stand, arm, tag, issue_id)
                bot.send_message(message.chat.id, text)
                job = jenkins.get_job('GISTEK_Poib/Update_App')
                test_run(message, "poib", params, 120, job)
            else: # не указан тег \ приложение \ ОЧ\ЗЧ портала
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
