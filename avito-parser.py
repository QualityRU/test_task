import os
import time
import xml.etree.ElementTree as ET
from xml.dom import minidom

import requests
from bs4 import BeautifulSoup

REGIONS = ['krasnodarskiy_kray', 'rostovskaya_oblast', 'volgogradskaya_oblast', 'astrahan', 'sevastopol']
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
OUTPUT_DIR = 'avito_data'
ads_buffer = []
file_index = 1


def save_to_xml(ads, index):
    """Сохранение в xml-файл."""
    root = ET.Element('data')

    for ad in ads:
        ad_el = ET.SubElement(root, "ad")
        for key, value in ad.items():
            child = ET.SubElement(ad_el, key)
            child.text = str(value)

    xml_str = ET.tostring(root, encoding='utf-8')
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent='  ')

    filename = os.path.join(OUTPUT_DIR, f'avito_ads_{index}.xml')
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    print(f'Сохранил {len(ads)} объявлений в {filename}')


def add_ad(ad):
    """Разбитие по 2000 объявлений в xml-файле."""
    global ads_buffer, file_index

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    ads_buffer.append(ad)
    if len(ads_buffer) >= 2000:
        save_to_xml(ads_buffer, file_index)
        ads_buffer = []
        file_index += 1
    else:
        save_to_xml(ads_buffer, file_index)


def get_homes(url):
    """Загрузка страницы с недвижимостью."""
    print('Загрузка страницы ...')
    response = requests.get(url=url, headers=HEADERS)

    if response.status_code != 200:
        raise Exception(f'Капча {response.status_code}')
    soup = BeautifulSoup(response.text, 'html.parser')
    homes = soup.find_all(
        'div', 'iva-item-titleStep-zichc iva-item-ivaItemRedesign-u3mVt'
    )
    time.sleep(30)

    for home in homes:
        url_kv = home.find(
            'a',
            'styles-module-root-m3BML styles-module-root_noVisited-HHF0s styles-module-root_preset_black-ydSp2',
        ).get('href')
        response = requests.get(
            url='https://www.avito.ru' + url_kv, headers=HEADERS
        )
        if response.status_code != 200:
            raise Exception(f'Капча {response.status_code}')
        soup = BeautifulSoup(response.text, 'html.parser')

        ad = {}
        ad['title'] = soup.find(
            'h1',
            'styles-module-root-W_crH styles-module-root-o3j6a styles-module-size_xxxl-GRUMY styles-module-size_xxxl-qNkZW stylesMarningNormal-module-root-_BXZU stylesMarningNormal-module-header-3xl-cSW1i',
        ).get_text()
        ad['price'] = soup.find(
            'span', 'styles-module-size_xxxl-GRUMY'
        ).get_text()
        ad['address'] = soup.find(
            'span', 'style-item-address__string-wt61A'
        ).get_text()
        ad['area'] = (
            soup.find_all('li', 'params-paramsList__item-_2Y2O')[1]
            .get_text()
            .replace('\xa0', ' ')
        )
        ad['link'] = 'https://www.avito.ru' + url_kv.split('?context=')[0]

        add_ad(ad)
        time.sleep(60)


def get_link_page(soup):
    return soup.find_all(
        'li',
        'styles-module-listItem-dvmc5 styles-module-listItem_notFirst-rRzSy',
    )[0].get('href')


def main():
    for region in REGIONS:
        get_homes(f'https://www.avito.ru/{region}/kvartiry/prodam')


if __name__ == '__main__':
    main()
