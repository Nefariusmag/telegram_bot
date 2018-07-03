#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import telebot, argparse, random
from telebot import types, apihelper

# API key телеграмовского бота
bot = telebot.TeleBot('357145828:AAHCACe_5lUryOB1MdCGUai2p_-SHs5VFek')

# список прокси серверов
# list_proxy = ('79.129.17.195:5373', '193.112.141.244:1080', 'antimalware:eL2S5JbU@148.251.151.141:1080', '50.4.201.158:10200', '121860960:FO8qJhxT@phobos.public.opennetwork.cc:1090', '121860960:FO8qJhxT@deimos.public.opennetwork.cc:1090', 'userid00wa:ZY1iTEi4@185.36.191.39:6398')
import urllib.request
url = 'http://distr-repo-i.gistek.lanit.ru/repo/proxy_list.py'
urllib.request.urlretrieve(url, './proxy_list.py')
import proxy_list
list_proxy = proxy_list.list_proxy

parser = argparse.ArgumentParser()
parser.add_argument('-w', dest='work', default='false',  help="Проверка на разрешение на отправку сообщения")
parser.add_argument('-m', dest='message', default='Я родился!', help="Сообщение, которое будет отправлено в чат")
parser.add_argument('-t', dest='issue_id', type=int,  default=0, help="Номер задачи для перевода в тестирование, 0 - без задачи")
parser.add_argument('-id', dest='chat_id', default='-216046302', help="id телеграма чата куда будет отправлено сообщение")
args = parser.parse_args()

if args.issue_id > 0:
    issue_text = "Задача http://redmine-energo.dkp.lanit.ru/issues/{}".format(args.issue_id)
    args.message = args.message + "\n\n" + issue_text
    args.chat_id = "-217174145"

if args.work == "true":
    all_ok = None
    while all_ok != "ok":
        try:
            proxy_server = random.choice(list_proxy)
            apihelper.proxy = {'https':'socks5://' + proxy_server}
            bot.send_message(args.chat_id, args.message)
            print("Ниче так: " + proxy_server)
            all_ok = "ok"
        except Exception as e:
            print("Не достаточно быстрый: " + proxy_server)

# запускается с параметрами:
# ./telegram_message.py -w ${telegram_message} -id -217174145 -t ${issue_id} -m "some TEXT"
