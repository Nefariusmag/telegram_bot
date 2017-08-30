--Info:

Телеграм бот для управления дженкиинсом на GISTEK

--Files:

README.md
telegram_henkins.py
config.py

--Setup:

Установить: python3 и pip3

Необходимые библиотеки:
apt-get install python3 python-setuptools
yum install python3 python-setuptools
pip3 install logging pyTelegramBotAPI jenkinsapi python-gitlab

Добавить в крон:
*/15 * * * * cd ~/telegram_bot && ./start.sh start &

--History:

---2.14
Добавил:
В меню переподключение
Возврат в главное меню
Выбор с нуля при сборке АРМ
В ПИЗИ выбор версий приложений

Изменил:
Пароли убраны из приложения
Старт и остановку системы
В ПОИБ время сборки
Текст записи в меню

---2.13
Добавил:
В разных шагах выход в главное меню

Изменил:
Главное меню теперь из кастомной клавиатуры

---2.12
Добавил:
Выгрузку тегов из Gitlab для выбора версии при обновлении

---2.11
Добавил:
Проверку задачи на выполнение и оповещение выполнявшего о результате
Остановку приложения через start.sh stop
Вынес в функцию errors сообщения об ошибках, в котором идет попытка переподключиться к jenkins
Для Клочкова функционал по рестарту и деплою пентахи на DEV
Добавил новый список тру пользователей с урезанными правами

Изменил:
Инициализацию пользователя в боте

---2.10

Добавил:
Запрос на задачу при деплое ПОИБ

---2.9

Добавил:
Проверку по id пользователя для важных вещей
Исправил для ряда подсистем переменные, т.к. изменились переменные в дженкинсе
Изменил стартовый скрипт на start.sh start

---2.8

Добавил:
- деплой интеграционной подсистемы и мобильного приложения
- цикл на переподключение авторизации

---2.7

Временно добавил блокировку через баш, ибо раньше запускалось бесконечное количество процесов питона и сервер падал

Добавил перезапуск серверов основных подсистем

---2.6

Добавил подключение к еще одному дженкинсу jenkins-gistek.dkp.lanit.ru
Встроил выполнеие скриптов синхронизации данных на нем

---2.5

Встроил логирование, теперь не надо париться с выводом логов в какой-то специальный файл

---2.4

Добавлена блокировка от второго запуска

---2.3

В Пентахо и Портале добавлено указвание задачи

---2.2

Добавлено:

Деплой:
Портал

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
