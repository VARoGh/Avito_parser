import requests
import json
import sqlite3
from urllib.parse import unquote
from datetime import datetime
from bs4 import BeautifulSoup
from hyper.contrib import HTTP20Adapter
from config_bot import token, chat_id  # настройки для телеграм-бота в отдельном файле

site = 'https://www.avito.ru'


def get_json(data: dict, filename: str = 'data.json') -> None:
    """Сохранение данных по объявлениям в файл json"""
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def get_data(url: str) -> dict:
    """Поиск на сайте и сохранение данных по объявлениям в словарь"""
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0)"
    }
    s = requests.Session()
    s.mount('https://', HTTP20Adapter())
    response = s.get(url, headers=headers)
    html = response.text
    tree = BeautifulSoup(html, 'html.parser')
    scripts = tree.find_all('script')
    for script in scripts:
        if 'window.__initialData__' in script.text:
            s = script.text.split(';')[0].split('=')[-1].strip(' "')
            s = unquote(s)
            data = json.loads(s)
            get_json(data)
            return data


def format_text(offer: dict) -> str:
    """Форматирование объявления в HTML формат для бота"""
    title = offer['title']
    d = offer['date']
    date = f"{d[8:10]}.{d[5:7]} в {d[13:18]}"
    text = f"""{offer['price']} ₽
    <a href='{offer['url']}'>{title}</a>
    {offer['address']}
    {date}"""
    return text


def send_telegram(offer: dict) -> None:
    """Отправка объявлений в телеграм"""
    text = format_text(offer)
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    response = requests.post(url=url, data=data)
    print(response)


def check_database(offer: dict) -> None:
    """Запись объявлений в базу данных"""
    offer_id = offer['offer_id']
    with sqlite3.connect('realty.db') as connection:
        connection = sqlite3.connect('realty.db')
        cursor = connection.cursor()
        cursor.execute("""
        SELECT offer_id FROM offers WHERE offer_id = (?)
        """, (offer_id,))
        result = cursor.fetchone()
        if result is None:
            send_telegram(offer)  # отправка обявления в телеграм
            cursor.execute("""
                            INSERT INTO offers
                            VALUES (NULL, :title, :url, :offer_id, :date, :price, :address)
                        """, offer)
            connection.commit()
            print(f'Объявление {offer_id} добавлено в базу данных')


def get_offers(data: dict) -> list:
    """Обработка словаря json из собранных данных
     и формирование списка выходных данных просмотренных объявлений Авито"""
    offers = []
    for key in data:
        if 'single-page' in key:
            items = data[key]['data']['catalog']['items']
            for item in items:
                if item.get('id'):
                    try:
                        offer = {}
                        offer['offer_id'] = item['id']
                        offer['price'] = item['priceDetailed']['value']
                        offer['title'] = item['title']
                        offer['url'] = site + item['urlPath']
                        timestamp = datetime.fromtimestamp(item['sortTimeStamp'] / 1000)
                        timestamp = datetime.strftime(timestamp, '%Y-%m-%d в %H:%M:%S')
                        offer['date'] = timestamp
                        city = item['geo']['geoReferences'][0]['content'] if item['geo'][
                            'geoReferences'] else 'Отсутствует'
                        address = item['geo']['formattedAddress']
                        offer['address'] = city + ', ' + address
                        offers.append(offer)
                    except IndexError:
                        print('Произошла ошибка индексации списка или словаря json при чтении данных!')
    return offers


def main():
    url = 'https://www.avito.ru/rostov-na-donu/kvartiry/prodam/vtorichka-ASgBAQICAUSSA8YQAUDmBxSMUg?s=104'
    data = get_data(url)
    offers = get_offers(data)

    for offer in offers:
        check_database(offer)


if __name__ == '__main__':
    main()
