# -*- coding: utf-8 -*-
import re, logging, random, os


def arm_action(bot, errors, jenkins, test_run, message):
    try:
        name_user = "{}({}):".format(message.chat.username, message.chat.id)
        search_arm = re.search(r"admin_kl|kl|admin-kl|admin_net|net|admin-net|all_mak_inf|all-mak-inf|arm_access|access|arm-access|arm_gist_viewer|viewer|arm-gist-viewer|arm_remover|remover|arm-remover|fpi-autoregistration|fpi_autoregistration|fpi|gis_des|des|gis-des|inn_ogrn_corrector|inn-ogrn-corrector|corrector|is_transport|is-transport|transport|kontrol|load_ssb|load-ssb|load|ssb|offline|template_cleaner|template-cleaner|template|cleaner|wmk_gistek|wmk-gistek|wmk", message.text)
        if search_arm != None:
            arm = search_arm.group(0)
            if arm in ["admin_kl", "kl", "admin-kl"]:
                arm = "admin_kl"
            if arm in ["admin_net", "net", "admin-net"]:
                arm = "admin_net"
            if arm in ["all_mak_inf", "all-mak-inf"]:
                arm = "all_mak_inf"
            if arm in ["arm_access", "access", "arm-access"]:
                arm = "arm_access"
            if arm in ["arm_gist_viewer", "viewer", "arm-gist-viewer"]:
                arm = "arm_gist_viewer"
            if arm in ["arm_remover", "remover", "arm-remover"]:
                arm = "arm_remover"
            if arm in ["fpi-autoregistration", "fpi_autoregistration", "fpi"]:
                arm = "fpi-autoregistration"
            if arm in ["gis_des", "des", "gis-des"]:
                arm = "gis_des"
            if arm in ["inn_ogrn_corrector", "inn-ogrn-corrector", "corrector"]:
                arm = "inn_ogrn_corrector"
            if arm in ["is_transport", "is-transport", "transport"]:
                arm = "is_transport"
            if arm in ["kontrol"]:
                arm = "kontrol"
            if arm in ["load_ssb", "load-ssb", "load", "ssb"]:
                arm = "load_ssb"
            if arm in ["offline"]:
                arm = "offline"
            if arm in ["template_cleaner", "template-cleaner", "template", "cleaner"]:
                arm = "template_cleaner"
            if arm in ["wmk_gistek", "wmk-gistek", "wmk"]:
                arm = "wmk_gistek"
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
            search_version = re.search(r"[0-9].[0-9].[0-9].[0-9]{4}|[0-9].[0-9].[0-9].[0-9]{3}|[0-9].[0-9].[0-9]{2}.[0-9]{4}|[0-9].[0-9].[0-9]{2}.[0-9]{3}", message.text)
            if search_version != None:
                search_version = search_version.group(0)
                tag = search_version
            else:
                tag = None
                bot.send_message(message.chat.id, "Тега нету, я соберу по последнему")
            # проверка на номер задачи
            search_issue = re.search(r"#[0-9]{5}", message.text)
            if search_issue != None:
                search_issue = search_issue.group(0)
                issue_id = search_issue
            else:
                issue_id = "отсутствует"
            if arm != None:
                if search_issue != None and tag != None:
                    params = {"stand": stand, "version": tag, "issue_id": issue_id}
                elif search_issue == None and tag != None:
                    params = {"stand": stand, "version": tag}
                elif search_issue != None and tag == None:
                    params = {"stand": stand, "issue_id": issue_id}
                elif search_issue == None and tag == None:
                    params = {"stand": stand}
                jenkins.build_job('GISTEK_Pizi/Build_ARM/' + arm, params)
                text = "{} собирает АРМ {}".format(name_user, arm)
                logging.warning( u"%s", text)
                text = "..еще минута и АРМ {} соберется".format(arm)
                bot.send_message(message.chat.id, text)
                sti = random.choice(os.listdir("deploy_sti"))
                sti = "deploy_sti/{}".format(sti)
                sti = open(sti, 'rb')
                bot.send_sticker(message.chat.id, sti)
                job = jenkins.get_job('GISTEK_Pizi/Build_ARM/' + arm)
                test_run(message, arm, params, 60, job)
            else:
                sti = random.choice(os.listdir("error_sti"))
                sti = "error_sti/{}".format(sti)
                sti = open(sti, 'rb')
                bot.send_sticker(message.chat.id, sti)
        else: # если АРМ не указан
            arm = None
            bot.send_message(message.chat.id, "Я хоть и умный, но мне всё таки нужено знать, что собирать ((")
            sti = random.choice(os.listdir("error_sti"))
            sti = "error_sti/{}".format(sti)
            sti = open(sti, 'rb')
            bot.send_sticker(message.chat.id, sti)

    except Exception as e:
        errors(message)
