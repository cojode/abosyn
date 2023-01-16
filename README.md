# Любимые Рецептики

## Введение

Данный проект является лабораторной работой по предмету ООП. Это телеграм бот, написанный на aiogram, который способен генерировать рецепты при помощи двух


## Архитектура проекта

![](/diagram.png)

## Структура проекта

+ ### [Telegram Bot]
  + [bot.py](https://github.com/cojode/abosyn/blob/main/bot.py) - запуск бота
  + [config.json](https://github.com/cojode/abosyn/blob/main/config.json) - конфиг
  + [config_loader.py](https://github.com/cojode/abosyn/blob/main/config_loader.py) - класс для загрузки и обновлений конфига в процессе работы
  + [recipe_model.py](https://github.com/cojode/abosyn/blob/main/recipe_model.py) - класс, для загрузки модели и генерации рецепта

+ ### Training
  + [recipes_parser.py](https://github.com/cojode/abosyn/blob/main/recipes_parser.py) - парсер
  + [train.py](https://github.com/cojode/abosyn/blob/main/train.py) - обучение модели
