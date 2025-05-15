# Телеграм-бот для генерации изображений с помощью нейросети Kandinsky

Этот проект реализует Телеграм-бота, который принимает от пользователя текстовые запросы и отправляет их в нейросеть Kandinsky для генерации изображений.

---

## Установка зависимостей

Перед первым запуском убедитесь, что установлены необходимые библиотеки для Python версии не ниже 3.8:

```bash
pip install -r requirements.txt
```

---

## Получение ключей API

Для работы бота понадобятся два ключа:

1. **Телеграм-бот**
   Создайте бота через [`@BotFather`](https://t.me/BotFather) и получите `BOT_API`.

2. **Нейросеть Kandinsky**
   Зарегистрируйтесь на [https://fusionbrain.ai/editor](https://fusionbrain.ai/editor) и получите `KANDINSKY_API_KEY` и `KANDINSKY_SECRET_KEY`.

### Файл `.env`

В корне проекта создайте файл `.env` со следующим содержимым (без угловых скобок):

```dotenv
BOT_API=<ваш_телеграм_token>
KANDINSKY_API_KEY=<ваш_api_key>
KANDINSKY_SECRET_KEY=<ваш_secret_key>
```

Не забудьте добавить `.env` в ваш `.gitignore`, чтобы ключи не попали в репозиторий.

---

## Запуск бота

* Через скрипт оболочки:

```bash
./run.sh
```

* Или напрямую:

```bash
PYTHONPATH=src python src/main.py
```

---

## Тестирование

Для запуска тестов используйте `pytest`:

```bash
PYTHONPATH=src python -m pytest --cov src --cov-report term-missing tests
```