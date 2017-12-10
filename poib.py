# -*- coding: utf-8 -*-

def poib_action(bot, errors, jenkins, test_run, message):
    # try:
    search_action = re.search("build", message.text)
    if search_action != None:
        try:
            jenkins.build_job('GISTEK_Poib/Build')
        except Exception:
            bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
            authentication(0)
            jenkins.build_job('GISTEK_Poib/Build')
        text = "{} собирает ПОИБ".format(name_user)
        logging.warning( u"%s", text)
        bot.send_message(message.chat.id, "..еще минута и ПОИБ соберется")
        job = jenkins.get_job('GISTEK_Poib/Build')
        test_run(message, "сборка ПОИБ", "без параметров", 65, job)
    else:
        search_action = re.search("deploy", message.text)
        if search_action != None:
            search_stand = re.search(r"ПП|ПИ|ПК|PP|PI|PK|REA_TEST", message.text)
            if search_stand == "ПК" or search_stand == "PK":
                stand = "PK"
            elif search_stand == "ПИ" or search_stand == "PI":
                stand = "PI"
            else
                stand = "REA_TEST"
            search_version = re.search("[0-9].[0-9].[0-9]", message.text)
            if search_version != None:
                tag = search_version
            else:
                tag = "1.5.13"
            search_issue = re.search("#[0-9]{5}")
            if search_issue != None:
                issue_id = search_issue
                params = {"stand": stand, "version": tag, "issue_id": issue_id}
            else: params = {"stand": stand, "version": tag}
            try:
                jenkins.build_job('GISTEK_Poib/Update_App', params)
            except Exception:
                bot.send_message(message.chat.id, "Это занимает больше времени чем планировалось изначально. Подождите пожалуйста.")
                authentication(0)
                jenkins.build_job('GISTEK_Poib/Update_App', params)
            bot.send_message(message.chat.id, "..еще 2 минуты и приложение ПОИБ обновится")
            job = jenkins.get_job('GISTEK_Poib/Update_App')
            test_run(message, var.arm, params, 120, job)
    # except Exception as e:
    #     errors(message)
