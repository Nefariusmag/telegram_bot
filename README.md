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

---2.1

Добавлено:

Деплой:
ПОИБ
ПИЗИ

---2.0

Тоже самое, но теперь при сборке арм можно указывать задачку. И код стал чуть меньше говно кодом.

---1.0

Старт

Реализовано:

Сборка:
ПИЗИ АРМ
ПИЗИ App
Портал портлеты
Пентахо плагины
Интеграционная подсистема
Мобильное приложение

Деплой:
ПИЗИ App
ПИЗИ Робот
