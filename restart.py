# -*- coding: utf-8 -*-
import re, logging, random, os

def restart_action(bot, errors, jenkins, test_run, message):
    try:
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        # проверка на приложение
        search_arm = re.search(r"pizi|pizi_app|пизи|poib|поиб|portal_open|портал_оч|portal_close|портал_зч|pentaho_all|все пентахи|пентахи|pentaho_oil_gas|пентахо_оил_гас|pentaho_ee|пентахо_ее|pentaho_electro|пентахо_електро|пентахо_электро|pentaho_integr|пентахо_интегр|пентаха_интеграционная|pentaho_coal|пентахо_коал|пентаха_уголь|robot|робот", message.text)
        if search_arm != None:
            arm = search_arm.group(0)
            if arm in ["pizi_app", "pizi", "пизи"]:
                arm = "pizi_app"
            if arm in ["portal_open", "портал_оч"]:
                arm = "portal_open"
            if arm in ["portal_close", "портал_зч"]:
                arm = "portal_close"
            if arm in ["pentaho_all", "все пентахи", "пентахи"]:
                arm = "pentaho_all"
            if arm in ["pentaho_oil_gas"]:
                arm = "pentaho_oil_gas"
            if arm in ["pentaho_ee", "пентахо_ее"]:
                arm = "pentaho_ee"
            if arm in ["pentaho_electro", "пентахо_електро", "пентахо_электро"]:
                arm = "pentaho_electro"
            if arm in ["pentaho_integr", "пентахо_интегр", "пентаха_интеграционная"]:
                arm = "pentaho_integr"
            if arm in ["pentaho_coal", "пентаха_уголь", "пентахо_коал"]:
                arm = "pentaho_coal"
            if arm in ["robot", "робот"]:
                arm = "robot"
        else:
            arm = None
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
            stand = "REA_TEST"
            bot.send_message(message.chat.id, "Стенд не указали, будет тест")
        # проверка на указонное приложение
        if arm != None:
            params = {"stand": stand, "system": arm}
            jenkins.build_job('GISTEK_Restart', params)
            text = "{} перезапускает приложение {} на {}".format(name_user, arm, stand)
            logging.warning( u"%s", text)
            text = "..еще минута приложение {} на {} перезапустится".format(arm, stand)
            bot.send_message(message.chat.id, text)
            sti = random.choice(os.listdir("deploy_sti"))
            sti = "deploy_sti/{}".format(sti)
            sti = open(sti, 'rb')
            bot.send_sticker(message.chat.id, sti)
            job = jenkins.get_job('GISTEK_Restart')
            test_run(message, arm, params, 60, job)
        elif arm == None:
            bot.send_message(message.chat.id, "Я хоть и умный, но мне всё таки нужено знать, что собирать ((")
            # отправить стикер
            sti = random.choice(os.listdir("error_sti"))
            sti = "error_sti/{}".format(sti)
            sti = open(sti, 'rb')
            bot.send_sticker(message.chat.id, sti)
    except Exception as e:
        errors(message)
