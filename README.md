Тестовое задание для Python-разработчика: Парсинг Avito и веб-интерфейс для загрузки XML-файла
---
Задача 1. Парсинг данных с Avito  
---
Для запуска кода потребуется: 
1. Клонировать репозиторий
```
git clone https://github.com/QualityRU/test_task.git
```
2. Установить виртуальное окружени
```
python3 -m venv venv
```
3. Активировать виртуальное окружение
```
. venv/bin/activate
```
4. Установить зависимости
```
pip install requests bs4 fake_useragent
```
5. Запустить код
```
python3 avito-parser.py
```
При написании кода возникала проблема - при частом опросе сайта avito.ru происходит запрос капчи и получение ошибки 429. Обойти это можно при помощи множественного прокси и менять User-Agent и/или использовать обход капчи, например solvecaptcha, 2captcha, anticaptcha
#
Задача 2. Интеграция XML с веб-интерфейсом
---
Для запуска кода также потребуется установить виртуальное окружение и зависимости
1. Установить зависимости
```
pip install flask
```
2. Запустить код
```
python3 upload_xml.py
```
3. Открыть веб-интерфейс
```
В браузере ввести http://127.0.0.1:8000
```
Задача 4. Легаси-код 
---
**Какие проблемы вы видите в этом коде?**

- Отсутствие обработки ошибок: Нет проверки, успешно ли загружен XML-файл.
- Нет валидации данных
- Потенциальные проблемы с памятью: 

**Как бы вы модифицировали его для работы с Python-скриптом?**
- Переписал бы код на Python как в avito_parser.py

**Предложите решение для увеличения производительности при загрузке 10k+ объявлений**

Переписать парсер на Python с использованием
- Многопоточности для быстрых I/O-операций (загрузка страниц)
- Асинхронности (asyncio + aiohttp) для эффективной работы с сетью
- Использовать xml.etree.ElementTree.iterparse() для постепенного чтения данных
- Очищать уже обработанные элементы (elem.clear()) для экономии памяти
- Кэшировать повторяющиеся запросы
- Использовать пул соединений (requests.Session)
- Сохранять данные порциями (например, по 2000 записей)
- Минимизировать sleep-таймеры, где это возможно