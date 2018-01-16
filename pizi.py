# -*- coding: utf-8 -*-
import re, logging, os, random

def pizi_action(bot, errors, jenkins, test_run, message):
    try:
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        search_action = re.search("build|BUILD|Build|Собрать|сборка|собрать|билд|сбилди|deploy|Deploy|обнови|update|Update|UPDATE|Обнови|деплой", message.text)
        if search_action != None:
            search_action = search_action.group(0)
        if search_action in ["build", "BUILD", "Build", "Собрать", "сборка", "собрать", "билд", "сбилди"]:
            jenkins.build_job('GISTEK_Pizi/Build_App')
            text = "{} собирает Сбор".format(name_user)
            logging.warning( u"%s", text)
            bot.send_message(message.chat.id, "..еще пара минут и приложения для Cбора соберутся")
            sti = random.choice(os.listdir("deploy_sti"))
            sti = "deploy_sti/{}".format(sti)
            sti = open(sti, 'rb')
            bot.send_sticker(message.chat.id, sti)
            job = jenkins.get_job('GISTEK_Pizi/Build_App')
            test_run(message, "сбор", "Без оных", 150, job)
        elif search_action in ["deploy", "Deploy", "обнови", "update", "Update", "UPDATE", "Обнови", "деплой"]:
            search_stand = re.search(r"ПИ|пи|PI|pi |ПК|пк|PK|pk|REA_TEST|rea_test|PP|pp|ПП|пп", message.text)
            if search_stand != None:
                search_stand = search_stand.group(0)
            if search_stand in ["ПК", "пк", "PK", "pk"]:
                stand = "PK"
            elif search_stand in ["ПИ", "пи", "PI", "pi "]:
                stand = "PI"
            elif search_stand in ["REA_TEST", "rea_test", "PP", "pp", "ПП", "пп"]:
                stand = "REA_TEST"
            else:
                bot.send_message(message.chat.id, "Вы не указали стенд, но подумал я решил за вас и решил, что это будет тестовый")
                stand = "REA_TEST"
            search_issue = re.search(r"#[0-9]{5}", message.text)
            if search_issue != None:
                search_issue = search_issue.group(0)
                issue_id = search_issue
                params = {"stand": stand, "issue_id": issue_id}
            else:
                params = {"stand": stand}
                issue_id = "отсутствует"
            jenkins.build_job('GISTEK_Pizi/Update_App', params)
            text = "..еще 5 минут и Сбор на {} обновится, задача {}".format(stand, issue_id)
            bot.send_message(message.chat.id, text)
            sti = random.choice(os.listdir("deploy_sti"))
            sti = "deploy_sti/{}".format(sti)
            sti = open(sti, 'rb')
            bot.send_sticker(message.chat.id, sti)
            job = jenkins.get_job('GISTEK_Pizi/Update_App')
            test_run(message, "pizi", params, 120, job)
        else:
            bot.send_message(message.chat.id, "И что мне с этим делать?")
            sti = random.choice(os.listdir("true_sti"))
            sti = "true_sti/{}".format(sti)
            sti = open(sti, 'rb')
            bot.send_sticker(message.chat.id, sti)
    except Exception as e:
        errors(message)

# функция подстановки версии переменным
def version_for_pizi(message, arm_jenkins, arm_git):
    arm_search = "{} .*".format(arm_git)
    search_version = re.search(arm_search, message.text)
    if search_version != None:
        select_version = search_version.group(0).split(" ")[1]
        if select_version == "-": # проверка на внезапные тире
            select_version = search_version.group(0).split(" ")[2]
        exec('%s = "%s"' % (str(arm_jenkins),str(select_version)), globals())
    else:
        exec('%s = "release"' % (str(arm_jenkins)), globals())

def pizi_repost_build_deploy(bot, errors, jenkins, test_run, message):
    name_user = "{}({}):".format(message.chat.username, message.chat.id)
    try:
        try:
            from_whom = str(message.forward_from.id)
        except Exception as e:
            bot.send_message(message.chat.id, "Это не репост от Федорова!")
            from_whom = str(message.chat.id)
        if from_whom == "238305929": # Босс ли?
            # выбор версии приложения
            version_for_pizi(message, "gtafo", "afo")
            version_for_pizi(message, "gtarm", "monitor")
            version_for_pizi(message, "gtarm", "monitor")
            version_for_pizi(message, "gttechnologist", "monitor")
            version_for_pizi(message, "gtonl", "formfillonline")
            version_for_pizi(message, "gtimpxml", "gtimpxml")
            version_for_pizi(message, "gtxml", "gtxml")
            version_for_pizi(message, "gttransport", "transport")
            version_for_pizi(message, "gtcontrol", "gtcontrol")
            version_for_pizi(message, "gtexpgisee", "gtexpgisee")
            version_for_pizi(message, "gtdownload", "gtdownload")
            version_for_pizi(message, "gtclassifier", "gtclassifier")
            version_for_pizi(message, "classifier_view", "classifier-view")
            version_for_pizi(message, "ticket", "ticket")
            version_for_pizi(message, "sso_server", "sso_server")
            version_for_pizi(message, "registration", "registration")
            version_for_pizi(message, "loadssb", "loadssb")
            # выбор стенда
            version = re.search("на ПИ", message.text)
            if version != None:
                stand = "PI"
                text = "На прод деплоим \n---------------- \ngtafo версии - {} \ngtarm версии - {} \ngttechnologist версии - {} \ngtonl версии - {} \ngtimpxml версии - {} \ngtxml версии - {} \ngttransport версии - {} \ngtcontrol версии - {} \ngtexpgisee версии - {} \ngtdownload версии - {} \ngtclassifier версии - {} \nclassifier_view версии - {} \nticket версии - {} \nsso-server версии - {} \nregistration версии - {} \nloadssb версии - {} \n----------------".format(gtafo, gtarm, gttechnologist, gtonl, gtimpxml, gtxml, gttransport, gtcontrol, gtexpgisee, gtdownload, gtclassifier, classifier_view, ticket, sso_server, registration, loadssb)
                bot.send_message(message.chat.id, text)
                bot.send_message(message.chat.id, "Есть 15 секунд на подумать, отмена через jenkins")
                time.sleep(15)
            else:
                stand = "REA_TEST"
            params = {"TAG_GTAFO": gtafo, "TAG_GTARM": gtarm, "TAG_GTTECHNOLOGIST": gttechnologist, "TAG_GTONL": gtonl, "TAG_GTIMPXML": gtimpxml, "TAG_GTXML": gtxml, "TAG_GTTRANSPORT": gttransport, "TAG_GTCONTROL": gtcontrol, "TAG_GTEXPGISEE": gtexpgisee, 	"TAG_GTDOWNLOAD": gtdownload, "TAG_GTCLASSIFIER": gtclassifier, "TAG_CLASSIFIER_VIEW": classifier_view, "TAG_TICKET": ticket, "TAG_SSO_SERVER": sso_server, "TAG_REGISTRATION": registration, "TAG_LOADSSB": loadssb, "stand": stand}
            text = "{} cтучится в jenkins чтобы обновить приложения Сбора".format(name_user)
            logging.warning( u"%s", text)
            jenkins.build_job('GISTEK_Pizi/Build_and_Deploy', params)
            text = "{} собирает приложения для Сбора".format(name_user)
            logging.warning( u"%s", text)
            bot.send_message(message.chat.id, "Cходи, завари чайку пока этот сбор обновляется (минут 7 обычно)")
            job = jenkins.get_job('GISTEK_Pizi/Build_and_Deploy')
            test_run(message, "Build_and_Deploy", params, 420, job)
        else:
            bot.send_message(message.chat.id, "Нету апрува от начальника, в другой раз.")
    except Exception as e:
        errors(message)
