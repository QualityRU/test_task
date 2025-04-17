import xml.etree.ElementTree as ET
from django.db import transaction  # Пример для Django ORM

def load_xml(file_path):
    """Загрузка xml-файла и обработка ошибок парсинга"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Ошибка парсинга XML: {e}")
        return
    except FileNotFoundError:
        print("Файл не найден")
        return

    ads = []
    for ad in root.findall('ad'):
        ad_data = {
            'id': ad.find('id').text,  # Пример поля
            'title': ad.find('title').text,
            # ... другие поля
        }
        ads.append(ad_data)

    with transaction.atomic():
        for ad in ads:
            # Проверка дубликата (пример для Django)
            if not Ad.objects.filter(id=ad['id']).exists():
                Ad.objects.create(**ad)