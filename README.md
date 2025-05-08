Телеграм-бот с обращением к нейросети Kandinsky для генерации изображения.

Перед первым запуском убедитесь, что установлены необходимые библиотеки Python:

```pip install -r requirements.txt```

## Получение ключей API
Перед использованием необходимо получить ключи API для телеграм-бота и для нейросети, и разместить их в файле `src/config.py`.

Телеграм-бот:

`https://t.me/BotFather`

Нейросеть:

`https://fusionbrain.ai/editor`

## Запуск

```run.sh```

Или:

```PYTHONPATH=src python src/main.py```

## Запуск тестов

```PYTHONPATH=src python -m pytest --cov src --cov-report term-missing tests```