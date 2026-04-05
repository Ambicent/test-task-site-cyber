# Esports Matches Site Generator

Генератор сайта с информацией о киберспортивных матчах за вчера, сегодня и завтра.

## Функционал

- генерация 3 отдельных страниц:
  - `/matches/yesterday`
  - `/matches/today`
  - `/matches/tomorrow`
- получение данных о матчах через PandaScore API
- SEO-поля:
  - `title`
  - `description`
  - `keywords`
  - `canonical`
  - Open Graph
  - Twitter meta tags
- микроразметка Schema.org через JSON-LD
- генерация HTML-страниц по кнопке
- отдельные URL без query-параметров

## Стек

- Python
- Flask
- Jinja2
- Requests
- HTML/CSS
- PandaScore API

## Запуск проекта

1. Создать и активировать виртуальное окружение
2. Установить зависимости:

```bash
pip install -r requirements.txt
```

3. Создать файл .env и указать токен PandaScore:

PANDASCORE_TOKEN=your_token
BASE_URL=https://api.pandascore.co
SITE_NAME=Esports Matches
SITE_URL=http://127.0.0.1:5000
ORG_NAME=Esports Matches Portal
ORG_LOGO=https://dummyimage.com/200x60/111827/ffffff&text=Esports+Matches

4. Запуск приложения:

```bash
python app.py
```

## Основные страницы

- / — страница генератора
- /generate — генерация HTML-страниц
- /matches/yesterday — матчи за вчера
- /matches/today — матчи на сегодня
- /matches/tomorrow — матчи на завтра

## Результат генерации

После нажатия на кнопку генерации создаются файлы:

- generated/yesterday.html
- generated/today.html
- generated/tomorrow.html