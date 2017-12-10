# -*- coding: utf-8 -*-

def pizi_action(bot, errors, jenkins, test_run, message):
    # try:
    search_action = re.search("build", message.text)
    if search_action != None:
        try:
            jenkins.build_job('GISTEK_Pizi/Build_App')
        except Exception:
            bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
            authentication(0)
            jenkins.build_job('GISTEK_Pizi/Build_App')
        bot.send_message(message.chat.id, "..еще минута и приложения для Cбора соберутся")
        job = jenkins.get_job('GISTEK_Pizi/Build_App')
        test_run(message, var.arm, "Без оных", 55, job)
    else:
        search_action = re.search("deploy", message.text)
        if search_action != None:
            search_stand = re.search(r"ПП|ПИ|ПК|PP|PI|PK|REA_TEST", message.text)
            if search_stand == "ПК" or search_stand == "PK":
                params = {"stand": "PK"}
            elif search_stand == "ПИ" or search_stand == "PI":
                params = {"stand": "PK"}
            else
                params = {"stand": "REA_TEST"}
            try:
                jenkins.build_job('GISTEK_Pizi/Update_App', params)
            except Exception:
                bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
                authentication(0)
                jenkins.build_job('GISTEK_Pizi/Update_App', params)
            job = jenkins.get_job('GISTEK_Pizi/Update_App')
            test_run(message, var.arm, params, 120, job)
    # except Exception as e:
    #     errors(message)



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
            version_for_pizi(message, "gttechnologist", "monitor")
            version_for_pizi(message, "gtonl", "formfillonline")
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
            bot.send_message(message.chat.id, "Cходи, завари чайку пока этот сбор деплоится))")
            params = {"TAG_GTAFO": gtafo, "TAG_GTARM": gtarm, "TAG_GTTECHNOLOGIST": gttechnologist, "TAG_GTONL": gtonl, "TAG_GTIMPXML": gtimpxml, "TAG_GTXML": gtxml, "TAG_GTTRANSPORT": gttransport, "TAG_GTCONTROL": gtcontrol, "TAG_GTEXPGISEE": gtexpgisee, 	"TAG_GTDOWNLOAD": gtdownload, "TAG_GTCLASSIFIER": gtclassifier, "TAG_CLASSIFIER_VIEW": classifier_view, "TAG_TICKET": ticket, "TAG_SSO_SERVER": sso_server, "TAG_REGISTRATION": registration, "TAG_LOADSSB": loadssb, "stand": stand}
            text = "{} cтучится в jenkins чтобы обновить приложения Сбора".format(name_user)
            logging.warning( u"%s", text)
            try:
                jenkins.build_job('GISTEK_Pizi/Build_and_Deploy', params)
            except Exception:
                bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
                authentication(0)
                jenkins.build_job('GISTEK_Pizi/Build_and_Deploy', params)
            text = "{} собирает приложения для Сбора".format(name_user)
            logging.warning( u"%s", text)
            bot.send_message(message.chat.id, "..еще 7 минут и обновим приложения Сбора")
            job = jenkins.get_job('GISTEK_Pizi/Build_and_Deploy')
            test_run(message, "Build_and_Deploy", params, 420, job)
            menu_help(message)
        else:
            bot.send_message(message.chat.id, "Нету апрува от начальника, в другой раз.")
    except Exception as e:
        errors(message)
