
# Проект YaMDb
Проект YaMDb собирает отзывы пользователей на произведения.
Произведению может быть присвоен жанр и категория.
Пользователи оставляют к произведениям текстовые отзывы и ставят произведению оценку в диапазоне от одного до десяти; 
из пользовательских оценок формируется усреднённая оценка произведения — рейтинг. На одно произведение пользователь может оставить только один отзыв.


## Авторы проекта

- [@crocodile-gandhi](https://github.com/crocodile-gandhi)
- [@Senkdar](https://github.com/Senkdar)
- [@Nick](https://github.com/smirnov-nick)


## Как запустить проект (для Windows):
Клонировать репозиторий и перейти в него в командной строке:

```bash
  git clone https://github.com/Senkdar/api_yamdb
  
  cd api_yamdb
```
 
Cоздать и активировать виртуальное окружение:

```bash
python -m venv venv

source Venv/Scripts/activate

```
Установить зависимости из файла requirements.txt:
```bash
pip install -r requirements.txt
```
Выполнить миграции:
```bash
python manage.py migrate
```
Запустить проект:
```bash
python manage.py runserver   
```
## API Reference

К проекту по адресу ```http://127.0.0.1:8000/redoc/```
подключена документация API YaMDb. В ней описаны возможные запросы к API и структура ожидаемых ответов. Для каждого запроса указаны уровни прав доступа: пользовательские роли, которым разрешён запрос.
