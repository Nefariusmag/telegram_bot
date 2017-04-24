#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def lock_file(fname):
    import fcntl
    _lock_file = open(fname, 'a+')
    try:
        fcntl.flock(_lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        return "Процесс уже используется."
    return _lock_file

lock = lock_file('telegram_jenkins.py')

import jenkinsapi
from jenkinsapi.jenkins import Jenkins

import config
import telebot
from telebot import types

jenkins = Jenkins("http://jenkins.gistek.lanit.ru", username=config.username, password=config.password)
bot = telebot.TeleBot(config.token)

### отладка из-за медленно работающего jenkins'а
# bot.send_message(121860960, "В jenkins авторизовались")
print("В jenkins авторизовались")
###

@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    # msg = bot.reply_to(message, "Вот такой вот стремный /help.")
    text = "{}({}): решил почитать /help".format(message.chat.username, message.chat.id)
    print(text)
    bot.send_message(message.chat.id, "Вот такой вот стремный /help.")
    # bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['helppp'])
def handle_start_help(message):
    text = "{}({}): решил почитать настоящий /help ;-)".format(message.chat.username, message.chat.id)
    print(text)
    bot.send_message(message.chat.id, "Сборка: \n\nАРМ: /gistek_build_arm_pp /gistek_build_arm_pk /gistek_build_arm_pi \n\nРазные подсистемы: /gistek_build_pentaho /gistek_build_portal /gistek_build_mobile /gistek_build_integration \n\nПодсистемы: /gistek_pizi")

@bot.message_handler(commands=['gistek_build_arm_pp', 'gistek_build_arm_pk', 'gistek_build_arm_pi'])
def any_subsystem(message):
    stend = "{}".format(message.text)
    global name_user
    name_user = "{}({}): ".format(message.chat.username, message.chat.id)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    url_button_jenkins = types.InlineKeyboardButton(text="go to jenkins", url="http://jenkins.gistek.lanit.ru/view/GISTEK/job/GISTEK_Pizi/job/Build_ARM/")
    url_button_redmine = types.InlineKeyboardButton(text="go to redmine", url="http://redmine-energo.dkp.lanit.ru/projects/gistek16/wiki/%D0%A1%D1%82%D0%B5%D0%BD%D0%B4%D1%8B")
    if stend == "/gistek_build_arm_pp":
        text = name_user + "АРМы для ПП, выбирай!"
        build_admin_kl = types.InlineKeyboardButton(text="admin_kl", callback_data="build_admin_kl_pp")
        build_admin_net = types.InlineKeyboardButton(text="admin_net", callback_data="build_admin_net_pp")
        build_all_mak_inf = types.InlineKeyboardButton(text="all_mak_inf", callback_data="build_all_mak_inf_pp")
        build_arm_access = types.InlineKeyboardButton(text="arm_access", callback_data="build_arm_access_pp")
        build_fpi_autoregistration = types.InlineKeyboardButton(text="fpi_autoregistration", callback_data="build_fpi_autoregistration_pp")
        build_gis_des = types.InlineKeyboardButton(text="gis_des", callback_data="build_gis_des_pp")
        build_is_transport = types.InlineKeyboardButton(text="is_transport", callback_data="build_is_transport_pp")
        build_kontrol = types.InlineKeyboardButton(text="kontrol", callback_data="build_kontrol_pp")
        build_load_ssb = types.InlineKeyboardButton(text="load_ssb", callback_data="build_load_ssb_pp")
        build_offline = types.InlineKeyboardButton(text="offline", callback_data="build_offline_pp")
        build_template_cleaner = types.InlineKeyboardButton(text="template_cleaner", callback_data="build_template_cleaner_pp")
        build_wmk_gistek = types.InlineKeyboardButton(text="wmk_gistek", callback_data="build_wmk_gistek_pp")
    if stend == "/gistek_build_arm_pk":
        text = name_user + "АРМы для ПК, выбирай!"
        build_admin_kl = types.InlineKeyboardButton(text="admin_kl", callback_data="build_admin_kl_pk")
        build_admin_net = types.InlineKeyboardButton(text="admin_net", callback_data="build_admin_net_pk")
        build_all_mak_inf = types.InlineKeyboardButton(text="all_mak_inf", callback_data="build_all_mak_inf_pk")
        build_arm_access = types.InlineKeyboardButton(text="arm_access", callback_data="build_arm_access_pk")
        build_fpi_autoregistration = types.InlineKeyboardButton(text="fpi_autoregistration", callback_data="build_fpi_autoregistration_pk")
        build_gis_des = types.InlineKeyboardButton(text="gis_des", callback_data="build_gis_des_pk")
        build_is_transport = types.InlineKeyboardButton(text="is_transport", callback_data="build_is_transport_pk")
        build_kontrol = types.InlineKeyboardButton(text="kontrol", callback_data="build_kontrol_pk")
        build_load_ssb = types.InlineKeyboardButton(text="load_ssb", callback_data="build_load_ssb_pk")
        build_offline = types.InlineKeyboardButton(text="offline", callback_data="build_offline_pk")
        build_template_cleaner = types.InlineKeyboardButton(text="template_cleaner", callback_data="build_template_cleaner_pk")
        build_wmk_gistek = types.InlineKeyboardButton(text="wmk_gistek", callback_data="build_wmk_gistek_pk")
    if stend == "/gistek_build_arm_pi":
        text = name_user + "АРМы для ПИ, выбирай!"
        build_admin_kl = types.InlineKeyboardButton(text="admin_kl", callback_data="build_admin_kl_pi")
        build_admin_net = types.InlineKeyboardButton(text="admin_net", callback_data="build_admin_net_pi")
        build_all_mak_inf = types.InlineKeyboardButton(text="all_mak_inf", callback_data="build_all_mak_inf_pi")
        build_arm_access = types.InlineKeyboardButton(text="arm_access", callback_data="build_arm_access_pi")
        build_fpi_autoregistration = types.InlineKeyboardButton(text="fpi_autoregistration", callback_data="build_fpi_autoregistration_pi")
        build_gis_des = types.InlineKeyboardButton(text="gis_des", callback_data="build_gis_des_pi")
        build_is_transport = types.InlineKeyboardButton(text="is_transport", callback_data="build_is_transport_pi")
        build_kontrol = types.InlineKeyboardButton(text="kontrol", callback_data="build_kontrol_pi")
        build_load_ssb = types.InlineKeyboardButton(text="load_ssb", callback_data="build_load_ssb_pi")
        build_offline = types.InlineKeyboardButton(text="offline", callback_data="build_offline_pi")
        build_template_cleaner = types.InlineKeyboardButton(text="template_cleaner", callback_data="build_template_cleaner_pi")
        build_wmk_gistek = types.InlineKeyboardButton(text="wmk_gistek", callback_data="build_wmk_gistek_pi")
    keyboard.add(url_button_redmine, url_button_jenkins, build_admin_kl, build_admin_net, build_all_mak_inf, build_arm_access, build_fpi_autoregistration, build_gis_des, build_is_transport, build_kontrol, build_load_ssb, build_offline, build_template_cleaner, build_wmk_gistek)
    print(text)
    bot.send_message(message.chat.id, text, reply_markup=keyboard)

@bot.message_handler(commands=['gistek_build_pentaho'])
def build_pentaho_subsystem(message):
    stend = "{}".format(message.text)
    global name_user
    name_user = "{}({}): ".format(message.chat.username, message.chat.id)
    text = name_user + "выбирай что будем собирать!"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    url_button_jenkins = types.InlineKeyboardButton(text="go to jenkins", url="http://jenkins.gistek.lanit.ru/view/GISTEK/job/GISTEK_Pentaho/view/Pentaho/")
    url_button_redmine = types.InlineKeyboardButton(text="go to redmine", url="http://redmine-energo.dkp.lanit.ru/projects/gistek16/wiki/%D0%A1%D1%82%D0%B5%D0%BD%D0%B4%D1%8B")
    build_pentaho_fileproperties = types.InlineKeyboardButton(text="fileproperties", callback_data="build_pentaho_fileproperties")
    build_pentaho_integr_clearcache = types.InlineKeyboardButton(text="integr_clearcache", callback_data="build_pentaho_integr_clearcache")
    build_pentaho_integr_readmetadata = types.InlineKeyboardButton(text="integr_readmetadata", callback_data="build_pentaho_integr_readmetadata")
    build_pentaho_languagepack = types.InlineKeyboardButton(text="languagepack", callback_data="build_pentaho_languagepack")
    build_pentaho_cas_tek = types.InlineKeyboardButton(text="cas_tek", callback_data="build_pentaho_cas_tek")
    build_pentaho_plugin = types.InlineKeyboardButton(text="plugin", callback_data="build_pentaho_plugin")
    build_pentaho_quixote_theme = types.InlineKeyboardButton(text="quixote_theme", callback_data="build_pentaho_quixote_theme")
    keyboard.add(url_button_redmine, url_button_jenkins, build_pentaho_fileproperties, build_pentaho_integr_clearcache, build_pentaho_integr_readmetadata, build_pentaho_languagepack, build_pentaho_cas_tek, build_pentaho_plugin, build_pentaho_quixote_theme)
    print(text)
    bot.send_message(message.chat.id, text, reply_markup=keyboard)

@bot.message_handler(commands=['gistek_build_portal'])
def build_portal_subsystem(message):
    stend = "{}".format(message.text)
    global name_user
    name_user = "{}({}): ".format(message.chat.username, message.chat.id)
    text = name_user + "выбирай что будем собирать!"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    url_button_jenkins = types.InlineKeyboardButton(text="go to jenkins", url="http://jenkins.gistek.lanit.ru/view/GISTEK/job/GISTEK_Portal/view/Build/")
    url_button_redmine = types.InlineKeyboardButton(text="go to redmine", url="http://redmine-energo.dkp.lanit.ru/projects/gistek16/wiki/%D0%A1%D1%82%D0%B5%D0%BD%D0%B4%D1%8B")
    build_languagepackru = types.InlineKeyboardButton(text="languagePackRU", callback_data="build_portal_languagepackru")
    build_support_mail_portlet = types.InlineKeyboardButton(text="support-mail-portlet", callback_data="build_portal_support_mail_portlet")
    build_hook_search = types.InlineKeyboardButton(text="hook-search", callback_data="build_portal_hook_search")
    build_subsystem_search = types.InlineKeyboardButton(text="subsystem-search", callback_data="build_portal_subsystem_search")
    build_hook_asset_publisher = types.InlineKeyboardButton(text="hook-asset-publisher", callback_data="build_portal_hook_asset_publisher")
    build_urc_theme = types.InlineKeyboardButton(text="urc-theme", callback_data="build_portal_urc_theme")
    build_mainpageGEO = types.InlineKeyboardButton(text="mainpageGEO", callback_data="build_portal_mainpagegeo")
    build_slider = types.InlineKeyboardButton(text="slider", callback_data="build_portal_slider")
    build_npa_loader = types.InlineKeyboardButton(text="npa-loader", callback_data="build_portal_npa_loader")
    build_inspinia_theme = types.InlineKeyboardButton(text="inspinia-theme", callback_data="build_portal_inspinia_theme")
    build_login_hook = types.InlineKeyboardButton(text="login-hook", callback_data="build_portal_login_hook")
    build_reports_display_portlet = types.InlineKeyboardButton(text="reports-display-portlet", callback_data="build_portal_reports_display_portlet")
    build_iframe = types.InlineKeyboardButton(text="portal-iframe", callback_data="build_portal_iframe")
    keyboard.add(url_button_redmine, url_button_jenkins, build_languagepackru, build_support_mail_portlet, build_hook_search, build_subsystem_search, build_hook_asset_publisher, build_urc_theme, build_mainpageGEO, build_slider, build_npa_loader, build_inspinia_theme, build_login_hook, build_reports_display_portlet, build_iframe)
    print(text)
    bot.send_message(message.chat.id, text, reply_markup=keyboard)

@bot.message_handler(commands=['gistek_build_mobile'])
def build_mobile_subsystem(message):
    stend = "{}".format(message.text)
    global name_user
    name_user = "{}({}): ".format(message.chat.username, message.chat.id)
    text = name_user + "выбирай что будем собирать!"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    url_button_jenkins = types.InlineKeyboardButton(text="go to jenkins", url="http://jenkins.gistek.lanit.ru/view/GISTEK/job/GISTEK_Portal/view/Build/")
    url_button_redmine = types.InlineKeyboardButton(text="go to redmine", url="http://redmine-energo.dkp.lanit.ru/projects/gistek16/wiki/%D0%A1%D1%82%D0%B5%D0%BD%D0%B4%D1%8B")
    build_android = types.InlineKeyboardButton(text="Android", callback_data="build_mobile_android")
    build_tek_portlet = types.InlineKeyboardButton(text="tek-portlet", callback_data="build_mobile_tek_portlet")
    build_web_service_java = types.InlineKeyboardButton(text="web-service-java", callback_data="build_mobile_web_service_java")
    keyboard.add(url_button_redmine, url_button_jenkins, build_android, build_web_service_java, build_tek_portlet)
    print(text)
    bot.send_message(message.chat.id, text, reply_markup=keyboard)

@bot.message_handler(commands=['gistek_build_integration'])
def build_integration_subsystem(message):
    stend = "{}".format(message.text)
    global name_user
    name_user = "{}({}): ".format(message.chat.username, message.chat.id)
    text = name_user + "кликни и соберем!"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    url_button_jenkins = types.InlineKeyboardButton(text="go to jenkins", url="http://jenkins.gistek.lanit.ru/view/GISTEK/job/GISTEK_Integration/")
    url_button_redmine = types.InlineKeyboardButton(text="go to redmine", url="http://redmine-energo.dkp.lanit.ru/projects/gistek16/wiki/%D0%A1%D1%82%D0%B5%D0%BD%D0%B4%D1%8B")
    build_integration = types.InlineKeyboardButton(text="Integration", callback_data="build_integration")
    keyboard.add(url_button_redmine, url_button_jenkins, build_integration)
    print(text)
    bot.send_message(message.chat.id, text, reply_markup=keyboard)

@bot.message_handler(commands=['gistek_pizi'])
def pizi_subsystem(message):
    stend = "{}".format(message.text)
    global name_user
    name_user = "{}({}): ".format(message.chat.username, message.chat.id)
    text = name_user + "Подсистема Сбор, что дальше?!"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    url_button_jenkins = types.InlineKeyboardButton(text="go to jenkins", url="http://jenkins.gistek.lanit.ru/view/GISTEK/job/GISTEK_Pizi/")
    url_button_redmine = types.InlineKeyboardButton(text="go to redmine", url="http://redmine-energo.dkp.lanit.ru/projects/gistek16/wiki/%D0%A1%D1%82%D0%B5%D0%BD%D0%B4%D1%8B")
    build_app = types.InlineKeyboardButton(text="Build Apps", callback_data="build_pizi_app")
    build_db_change_script = types.InlineKeyboardButton(text="Build DB change_script", callback_data="build_pizi_change_script")
    build_db_refresh_db = types.InlineKeyboardButton(text="Build DB refresh_db", callback_data="build_pizi_db_refresh_db")
    update_app_pp = types.InlineKeyboardButton(text="Update App PP", callback_data="update_pizi_app_pp")
    update_app_pi = types.InlineKeyboardButton(text="Update App PI", callback_data="update_pizi_app_pi")
    update_app_pk = types.InlineKeyboardButton(text="Update App PK", callback_data="update_pizi_app_pk")
    update_robot_pp = types.InlineKeyboardButton(text="Update Robot PP", callback_data="update_pizi_robot_pp")
    update_robot_pi = types.InlineKeyboardButton(text="Update Robot PI", callback_data="update_pizi_robot_pi")
    update_robot_pk = types.InlineKeyboardButton(text="Update Robot PK", callback_data="update_pizi_robot_pk")
    keyboard.add(url_button_redmine, url_button_jenkins, build_app, build_db_change_script, build_db_refresh_db, update_app_pp, update_app_pi, update_app_pk, update_robot_pp, update_robot_pi, update_robot_pk)
    print(text)
    bot.send_message(message.chat.id, text, reply_markup=keyboard)

# Попробовать зазбить этого монстра на части!!!

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        def build_arm(arm, stend):
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="пыжимся и тужимся... ")
            params = {"stend": stend}
            print(name_user + "cтучится в jenkins чтобы собрать " + arm + " для " + stend)
            jenkins.build_job('GISTEK_Pizi/Build_ARM/' + arm, params)
            print(name_user + "собирает " + arm + " на " + stend)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="..еще 5 минуточек и " + arm + " , для " + stend + " соберется (если ошибки в jenkins не будет), а пока можно продолжать.")
        # Стенд ПП
        if call.data == "build_admin_kl_pp":
            build_arm("admin_kl", "REA_TEST")
        if call.data == "build_admin_net_pp":
            build_arm("admin_net", "REA_TEST")
        if call.data == "build_all_mak_inf_pp":
            build_arm("all_mak_inf", "REA_TEST")
        if call.data == "build_arm_access_pp":
            build_arm("arm_access", "REA_TEST")
        if call.data == "build_fpi_autoregistration_pp":
            build_arm("fpi_autoregistration", "REA_TEST")
        if call.data == "build_gis_des_pp":
            build_arm("gis_des", "REA_TEST")
        if call.data == "build_is_transport_pp":
            build_arm("is_transport", "REA_TEST")
        if call.data == "build_kontrol_pp":
            build_arm("kontrol", "REA_TEST")
        if call.data == "build_load_ssb_pp":
            build_arm("load_ssb", "REA_TEST")
        if call.data == "build_offline_pp":
            build_arm("offline", "REA_TEST")
        if call.data == "build_template_cleaner_pp":
            build_arm("template_cleaner", "REA_TEST")
        if call.data == "build_wmk_gistek_pp":
            build_arm("wmk_gistek", "REA_TEST")
        # Стенд ПИ
        if call.data == "build_admin_kl_pi":
            build_arm("admin_kl", "PI")
        if call.data == "build_admin_net_pi":
            build_arm("admin_net", "PI")
        if call.data == "build_all_mak_inf_pi":
            build_arm("all_mak_inf", "PI")
        if call.data == "build_arm_access_pi":
            build_arm("arm_access", "PI")
        if call.data == "build_fpi_autoregistration_pi":
            build_arm("fpi_autoregistration", "PI")
        if call.data == "build_gis_des_pi":
            build_arm("gis_des", "PI")
        if call.data == "build_is_transport_pi":
            build_arm("is_transport", "PI")
        if call.data == "build_kontrol_pi":
            build_arm("kontrol", "PI")
        if call.data == "build_load_ssb_pi":
            build_arm("load_ssb", "PI")
        if call.data == "build_offline_pi":
            build_arm("offline", "PI")
        if call.data == "build_template_cleaner_pi":
            build_arm("template_cleaner", "PI")
        if call.data == "build_wmk_gistek_pi":
            build_arm("wmk_gistek", "PI")
        # Стенд ПК
        if call.data == "build_admin_kl_pk":
            build_arm("admin_kl", "PK")
        if call.data == "build_admin_net_pk":
            build_arm("admin_net", "PK")
        if call.data == "build_all_mak_inf_pk":
            build_arm("all_mak_inf", "PK")
        if call.data == "build_arm_access_pk":
            build_arm("arm_access", "PK")
        if call.data == "build_fpi_autoregistration_pk":
            build_arm("fpi_autoregistration", "PK")
        if call.data == "build_gis_des_pk":
            build_arm("gis_des", "PK")
        if call.data == "build_is_transport_pk":
            build_arm("is_transport", "PK")
        if call.data == "build_kontrol_pk":
            build_arm("kontrol", "PK")
        if call.data == "build_load_ssb_pk":
            build_arm("load_ssb", "PK")
        if call.data == "build_offline_pk":
            build_arm("offline", "PK")
        if call.data == "build_template_cleaner_pk":
            build_arm("template_cleaner", "PK")
        if call.data == "build_wmk_gistek_pk":
            build_arm("wmk_gistek", "PK")
        def build_pentaho(app):
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="пыжимся и тужимся... ")
            print(name_user + "стучится в jenkins чтобы собрать " + app)
            jenkins.build_job('GISTEK_Pentaho/Build_' + app)
            print(name_user + "собирает " + app)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="..еще 5 минуточек и " + app + " соберется (если ошибки в jenkins не будет), а пока можно продолжать.")
        if call.data == "build_pentaho_fileproperties":
            build_pentaho("FileProperties")
        if call.data == "build_pentaho_integr_clearcache":
            build_pentaho("integr_clearcache")
        if call.data == "build_pentaho_integr_readmetadata":
            build_pentaho("integr_readmetadata")
        if call.data == "build_pentaho_languagepack":
            build_pentaho("languagePack")
        if call.data == "build_pentaho_cas_tek":
            build_pentaho("pentaho-cas-tek")
        if call.data == "build_pentaho_plugin":
            build_pentaho("Plugin")
        if call.data == "build_pentaho_quixote_theme":
            build_pentaho("quixote-theme")
        def build_portal(app):
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="пыжимся и тужимся... ")
            print(name_user + "стучится в jenkins чтобы собрать портлет " + app)
            jenkins.build_job('GISTEK_Portal/' + app)
            print(name_user + "собирает портлет " + app)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="..еще 5 минуточек и портлет " + app + " соберется (если ошибки в jenkins не будет), а пока можно продолжать.")
        if call.data == "build_portal_languagepackru":
            build_portal("languagePackRU")
        if call.data == "build_portal_support_mail_portlet":
            build_portal("support-mail-portlet")
        if call.data == "build_portal_hook_search":
            build_portal("hook-search")
        if call.data == "build_portal_subsystem_search":
            build_portal("subsystem-search")
        if call.data == "build_portal_hook_asset_publisher":
            build_portal("hook-asset-publisher")
        if call.data == "build_portal_urc_theme":
            build_portal("urc-theme")
        if call.data == "build_portal_mainpagegeo":
            build_portal("mainpageGEO")
        if call.data == "build_portal_slider":
            build_portal("slider")
        if call.data == "build_portal_npa_loader":
            build_portal("npa-loader")
        if call.data == "build_portal_inspinia_theme":
            build_portal("inspinia-theme")
        if call.data == "build_portal_login_hook":
            build_portal("login-hook")
        if call.data == "build_portal_reports_display_portlet":
            build_portal("reports-display-portlet")
        if call.data == "build_portal_iframe":
            build_portal("portal-iframe")
        def build_mobile(app):
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="пыжимся и тужимся... ")
            print(name_user + "стучится в jenkins чтобы собрать " + app)
            jenkins.build_job('GISTEK_MobileApp/Build_' + app)
            print(name_user + "собирает " + app)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="..еще 5 минуточек и " + app + " соберется (если ошибки в jenkins не будет), а пока можно продолжать.")
        if call.data == "build_mobile_android":
            build_mobile("Android")
        if call.data == "build_mobile_tek_portlet":
            build_mobile("tek-portlet")
        if call.data == "build_mobile_web_service_java":
            build_mobile("web-service-java")
        if call.data == "build_integration":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="пыжимся и тужимся... ")
            print(name_user + "стучится в jenkins чтобы собрать интеграционную подсистему")
            jenkins.build_job('GISTEK_Integration/Build')
            print(name_user + "собирает интеграционную подсистему")
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="..еще 5 минуточек и интеграционная подсистема соберется (если ошибки в jenkins не будет), а пока можно продолжать.")
        def build_pizi(app):
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="пыжимся и тужимся... ")
            print(name_user + "стучится в jenkins чтобы собрать " + app)
            jenkins.build_job('GISTEK_Pizi/Build_' + app)
            print(name_user + "собирает " + app)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="..еще 5 минуточек и " + app + " соберется (если ошибки в jenkins не будет), а пока можно продолжать.")
        if call.data == "build_pizi_app":
            build_pizi("App")
        if call.data == "build_pizi_change_script":
            build_pizi("DB_change_script")
        if call.data == "build_pizi_db_refresh_db":
            build_pizi("DB_refresh_db")
        def update_pizi(arm, stend):
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="пыжимся и тужимся... ")
            params = {"stend": stend}
            print(name_user + "стучится в jenkins чтобы обновить " + arm + " для " + stend)
            jenkins.build_job('GISTEK_Pizi/Update_' + arm, params)
            print(name_user + "обновляет " + arm + " на " + stend)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="..еще 5 минуточек и " + arm + ", для " + stend + " обновится (если ошибки в jenkins не будет), а пока можно продолжать.")
        if call.data == "update_pizi_app_pp":
            update_pizi("App", "REA_TEST")
        if call.data == "update_pizi_app_pi":
            update_pizi("App", "PI")
        if call.data == "update_pizi_app_pk":
            update_pizi("App", "PK")
        if call.data == "update_pizi_robot_pp":
            update_pizi("Robot", "REA_TEST")
        if call.data == "update_pizi_robot_pi":
            update_pizi("Robot", "PI")
        if call.data == "update_pizi_robot_pk":
            update_pizi("Robot", "PK")

# повторюшка всего остального
@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    text = "{}({}): {}".format(message.chat.username, message.chat.id, message.text)
    print(text)
    bot.send_message(message.chat.id, message.text)

if __name__ == '__main__':
    bot.polling(none_stop=True)
