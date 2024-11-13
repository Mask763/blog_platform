# Блог-платформа для публикации постов

Публикация постов на различные тематики с возможностью их сортировки и комментирования.

## Возможности и реализованные задачи

- Регистрация пользователей;
- Восстановление пароля через почту;
- Создание, редактирование и удаление постов;
- Создание и удаление комментариев;
- Тестирование при помощи pytest.

## Требования

Для запуска проекта вам понадобятся: 

- Python 3.9

## Стек используемых технологий

- Django
- СУБД SQLite3

## Установка и запуск

### 1. Клонирование репозитория

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Mask763/blog_platform.git
```

```
cd blog_platform/
```

### 2. Установка зависимостей

Создайте виртуальное окружение и установите зависимости:

```
python -m venv venv
```
```
source venv/bin/activate  # Для Linux/MacOS
```
или
```
source venv/Scripts/activate  # Для Windows
```
```
pip install -r requirements.txt
```

### 3. Сбор статики и выполнение миграций

```
cd blogicum/
```
```
python manage.py collectstatic
```
```
python manage.py migrate
```

### 4. Запуск

```
python manage.py runserver
```

Проект будет доступен локально по адресу - http://127.0.0.1:8000

## Автор проекта

[Mask763](https://github.com/Mask763)
