import os
import time
import xml.etree.ElementTree as ET
from xml.dom import minidom

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class AvitoParser:
    """Парсинг недвижимости на Avito для ЮФО."""

    REGIONS = [
        'krasnodarskiy_kray',
        'rostovskaya_oblast',
        'volgogradskaya_oblast',
        'astrahan',
        'sevastopol',
        'respublika_krym',
    ]

    def __init__(self, output_dir='avito_data'):
        self.output_dir = output_dir
        self.ads_buffer = []
        self.file_index = 1

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def save_to_xml(self, ads, index):
        """Сохранение в xml-файл."""
        try:
            root = ET.Element('data')

            for ad in ads:
                ad_el = ET.SubElement(root, 'ad')
                for key, value in ad.items():
                    child = ET.SubElement(ad_el, key)
                    child.text = str(value)

            xml_str = ET.tostring(root, encoding='utf-8')
            pretty_xml = minidom.parseString(xml_str).toprettyxml(indent='  ')

            filename = os.path.join(self.output_dir, f'avito_ads_{index}.xml')
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(pretty_xml)
            print(f'Сохранил {len(ads)} объявлений в {filename}')
        except Exception as e:
            print(f'Ошибка при сохранении XML: {str(e)}')

    def add_ad(self, ad):
        """Разбитие по 2000 объявлений в xml-файле."""
        self.ads_buffer.append(ad)
        if len(self.ads_buffer) >= 2000:
            self.save_to_xml(self.ads_buffer, self.file_index)
            self.ads_buffer = []
            self.file_index += 1
        else:
            self.save_to_xml(self.ads_buffer, self.file_index)

    def get_page(self, url):
        """Загрузка страницы с обработкой ошибок."""
        ua = UserAgent()
        headers = {'User-Agent': ua.random}

        try:
            response = requests.get(url=url, headers=headers, timeout=30)
            response.raise_for_status()
            time.sleep(15)
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f'Ошибка при загрузке страницы {url}: {str(e)}')
            time.sleep(15)
            return None
        except Exception as e:
            print(f'Неожиданная ошибка при загрузке страницы {url}: {str(e)}')
            time.sleep(15)
            return None

    def parse_home_page(self, url):
        """Парсинг страницы с объявлением."""
        soup = self.get_page(url)
        if not soup:
            return None

        try:
            ad = {}
            title = soup.find(
                'h1',
                'styles-module-root-W_crH styles-module-root-o3j6a styles-module-size_xxxl-GRUMY styles-module-size_xxxl-qNkZW stylesMarningNormal-module-root-_BXZU stylesMarningNormal-module-header-3xl-cSW1i',
            )
            ad['title'] = title.get_text() if title else 'Нет названия'

            price = soup.find('span', 'styles-module-size_xxxl-GRUMY')
            ad['price'] = price.get_text() if price else 'Нет цены'

            address = soup.find('span', 'style-item-address__string-wt61A')
            ad['address'] = address.get_text() if address else 'Нет адреса'

            area_elements = soup.find_all(
                'li', 'params-paramsList__item-_2Y2O'
            )
            ad['area'] = area_elements[1].get_text().replace('\xa0', ' ')
            ad['link'] = url.split('?context=')[0]

            return ad
        except Exception as e:
            print(f'Ошибка при парсинге объявления {url}: {str(e)}')
            return None

    def get_homes(self, url):
        """Загрузка страницы с недвижимостью."""
        print(f'Загрузка страницы {url}...')
        soup = self.get_page(url)
        if not soup:
            return

        try:
            homes = soup.find_all(
                'div',
                'iva-item-titleStep-zichc iva-item-ivaItemRedesign-u3mVt',
            )

            for home in homes:
                try:
                    url_kv = home.find(
                        'a',
                        'styles-module-root-m3BML styles-module-root_noVisited-HHF0s styles-module-root_preset_black-ydSp2',
                    ).get('href')
                    full_url = 'https://www.avito.ru' + url_kv

                    ad = self.parse_home_page(full_url)
                    if ad:
                        self.add_ad(ad)
                except Exception as e:
                    print(f'Ошибка при обработке объявления: {str(e)}')
                    continue
        except Exception as e:
            print(f'Ошибка при парсинге списка объявлений: {str(e)}')

    def run(self):
        """Основной метод для запуска парсера."""
        try:
            for region in self.REGIONS:
                self.get_homes(
                    f'https://www.avito.ru/{region}/kvartiry/prodam'
                )

        except KeyboardInterrupt:
            print('\nПарсер остановлен пользователем')
        except Exception as e:
            print(f'Критическая ошибка: {str(e)}')
            if self.ads_buffer:
                self.save_to_xml(self.ads_buffer, self.file_index)


if __name__ == '__main__':
    parser = AvitoParser()
    parser.run()
