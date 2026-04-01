# One&Only Perfumer — Telegram Quiz Bot

## Что делает бот
1. Приветствует пользователя, предлагает пройти квиз
2. 4 вопроса: пол → возраст → что важно → какие ноты нравятся
3. Подбирает 2 аромата на основе ответов
4. Выдаёт промокод QUIZ20 (20% скидка) + ссылки на сайт, канал, инструкцию

## Быстрый запуск (локально)

```bash
pip install -r requirements.txt
python bot.py
```

## Деплой на Railway.app (бесплатно)

### 1. Подготовка
- Зарегистрируйся на https://railway.app (через GitHub)
- Создай репозиторий на GitHub и загрузи туда файлы:
  - bot.py
  - requirements.txt
  - Procfile

### 2. Создай Procfile
Файл `Procfile` (без расширения) с содержимым:
```
worker: python bot.py
```

### 3. Загрузи на GitHub
```bash
git init
git add .
git commit -m "quiz bot"
git remote add origin https://github.com/ТВОЙ_ЛОГИН/oneandonly-quiz-bot.git
git push -u origin main
```

### 4. Подключи к Railway
1. Зайди на https://railway.app → New Project → Deploy from GitHub repo
2. Выбери репозиторий
3. В настройках проекта добавь переменную окружения (опционально):
   - `BOT_TOKEN` = токен бота
4. Railway автоматически задеплоит

### 5. Готово!
Бот запустится автоматически. Проверь в Telegram — напиши /start

## Настройка
Все настройки в начале файла bot.py:
- `BOT_TOKEN` — токен бота
- `PROMO_CODE` — промокод
- `SITE_URL` — ссылка на сайт
- `TG_CHANNEL` — ссылка на TG-канал
- `VIDEO_URL` — ссылка на видео-инструкцию
