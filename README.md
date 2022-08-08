# Avito_parser
Мониторинг недвижимости на сайте Авито

Программа для парсинга объявлений по продаже недвижимости на сайте Авито. Код программы в Avito to telegram.py

Реализована функция сохранения основных параметров объявления недвижимости (кол-во комнат, площадь, url объявления, дата размещения, адрес) в базу данных SQLite и файл json. При сохранение данных объявления осуществляется проверка уже имеющихся в базе данных записей и добавление новых. 

Реализован бот для отправки новых обявлений в телеграм. Параметры телеграм-бота (id и номер чата) располагаются в отдельном конфигурационном файле config_bot.py.

В программе использованы следующие библиотеки и модули: requests, json, sqlite3, urllib, datetime, BeautifulSoup, hyper.
