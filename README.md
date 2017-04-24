--Info:

Телеграм бот для управления дженкиинсом на GISTEK

--Files:

README.md
telegram_henkins.py
config.py
test.py

--Setup:

Установить: python3 и pip3

Необходимые библиотеки:
pip3 install pytelegrambotapi
pip3 install cherrypy
pip3 install jenkinsapi

Добавить в крон:
*/15 * * * * cd /home/derokhin/GISTEK/DevOps/work/rest_api_jenkins && ./telegram_jenkins.py >> log

--History:

---1.0

Старт

Реализовано:

Сборка:
ПИЗИ АРМ
ПИЗИ App
ПИЗИ Робот
Портал портлеты
ПОИБ приложение
Пентахо плагины
Интеграционная подсистема
Мобильное приложение

Деплой:
Сбор
Робот
