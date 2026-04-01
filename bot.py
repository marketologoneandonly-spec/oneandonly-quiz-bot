import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ==================== НАСТРОЙКИ ====================
BOT_TOKEN = "8645459843:AAHPX3bqbSDMDiR17in1r2yjhvS90JmLOcs"

PROMO_CODE = "QUIZ20"
SITE_URL = "https://oneandonly-perfumer.com/"
TG_CHANNEL = "https://t.me/oneandonly_perfumer"
VIDEO_URL = "https://oneandonly-perfumer.com/"

# ==================== КАТАЛОГ АРОМАТОВ ====================
PERFUMES = {
    "obsidian": {
        "name": "OBSIDIAN",
        "notes": ["leather_tobacco"],
        "hours": 60,
        "tags": ["durability", "attractiveness", "status"],
        "desc": (
            "🎯 *OBSIDIAN*\n\n"
            "Глубокие смолистые ноты, насыщенный табак и соблазнительный ром. "
            "Чувственный и мистический.\n\n"
            "✅ Стойкость: 60+ часов\n"
            "💰 Цена: от 1990₽\n"
            "🎁 С промокодом: от 1592₽"
        ),
    },
    "elyxion": {
        "name": "ELYXION",
        "notes": ["woody"],
        "hours": 72,
        "tags": ["durability", "universal", "compliments"],
        "desc": (
            "🎯 *ELYXION*\n\n"
            "Мужественные древесные ноты, чистота зелёных оттенков и "
            "энергичность цитрусов. Для тех, кто любит быть на вершине.\n\n"
            "✅ Стойкость: 72+ часа\n"
            "💰 Цена: от 1990₽\n"
            "🎁 С промокодом: от 1592₽"
        ),
    },
    "citronex": {
        "name": "CITRONEX",
        "notes": ["citrus"],
        "hours": 48,
        "tags": ["universal", "compliments", "attractiveness"],
        "desc": (
            "🎯 *CITRONEX*\n\n"
            "Взрыв цитрусов и древесная база. Свежий, энергичный, дерзкий. "
            "Идеально для работы, свиданий, тусовок.\n\n"
            "✅ Стойкость: 48+ часов\n"
            "💰 Цена: от 1990₽\n"
            "🎁 С промокодом: от 1592₽"
        ),
    },
    "terranex": {
        "name": "TERRANEX",
        "notes": ["leather_tobacco"],
        "hours": 50,
        "tags": ["status", "attractiveness"],
        "desc": (
            "🎯 *TERRANEX*\n\n"
            "Дымные аккорды с благородной кожей и фруктовыми нотами. "
            "Композиция силы и уверенности.\n\n"
            "✅ Стойкость: 50+ часов\n"
            "💰 Цена: от 1990₽\n"
            "🎁 С промокодом: от 1592₽"
        ),
    },
    "drakonis": {
        "name": "DRAKONIS",
        "notes": ["leather_tobacco"],
        "hours": 50,
        "tags": ["status", "attractiveness", "durability"],
        "desc": (
            "🎯 *DRAKONIS*\n\n"
            "Кожаные ноты с лёгкой сладостью. Дерзкий, брутальный, статусный. "
            "Пахнет кожаным салоном роскошного автомобиля.\n\n"
            "✅ Стойкость: 50+ часов\n"
            "💰 Цена: от 1990₽\n"
            "🎁 С промокодом: от 1592₽"
        ),
    },
    "outlion": {
        "name": "OUTLION",
        "notes": ["oriental"],
        "hours": 60,
        "tags": ["durability", "attractiveness", "status"],
        "desc": (
            "🎯 *OUTLION*\n\n"
            "Интенсивный уд, восточные специи и благородная древесина. "
            "Для тех, кто не боится доминировать.\n\n"
            "✅ Стойкость: 60+ часов\n"
            "💰 Цена: от 1990₽\n"
            "🎁 С промокодом: от 1592₽"
        ),
    },
    "zephyron": {
        "name": "ZEPHYRON",
        "notes": ["spicy", "woody"],
        "hours": 55,
        "tags": ["compliments", "status"],
        "desc": (
            "🎯 *ZEPHYRON*\n\n"
            "Сложный многогранный аромат. Свежие цитрусы с тёплыми древесными "
            "аккордами и пряными оттенками.\n\n"
            "✅ Стойкость: 55+ часов\n"
            "💰 Цена: от 1990₽\n"
            "🎁 С промокодом: от 1592₽"
        ),
    },
    "chronis": {
        "name": "CHRONIS",
        "notes": ["spicy"],
        "hours": 72,
        "tags": ["durability", "attractiveness", "universal"],
        "desc": (
            "🎯 *CHRONIS*\n\n"
            "Яркий цитрус, пряности и древесина. Мощный, энергичный аромат "
            "для настоящих мужчин.\n\n"
            "✅ Стойкость: 72+ часа\n"
            "💰 Цена: от 1990₽\n"
            "🎁 С промокодом: от 1592₽"
        ),
    },
    "verdantis": {
        "name": "VERDANTIS",
        "notes": ["woody"],
        "hours": 50,
        "tags": ["status", "compliments"],
        "desc": (
            "🎯 *VERDANTIS*\n\n"
            "Глубокий, слегка пряный с тёплыми древесными и табачными нотами. "
            "Благородство без слов.\n\n"
            "✅ Стойкость: 50+ часов\n"
            "💰 Цена: от 1990₽\n"
            "🎁 С промокодом: от 1592₽"
        ),
    },
    "solvion": {
        "name": "SOLVION",
        "notes": ["citrus"],
        "hours": 55,
        "tags": ["universal", "attractiveness"],
        "desc": (
            "🎯 *SOLVION*\n\n"
            "Сочный лимон, морской бриз и тёплая древесина. "
            "Энергия Средиземноморья в одном флаконе.\n\n"
            "✅ Стойкость: 55+ часов\n"
            "💰 Цена: от 1990₽\n"
            "🎁 С промокодом: от 1592₽"
        ),
    },
    "vortexium": {
        "name": "VORTEXIUM",
        "notes": ["spicy"],
        "hours": 50,
        "tags": ["status", "universal"],
        "desc": (
            "🎯 *VORTEXIUM*\n\n"
            "Пряности, глубокая древесина и тёплая амбра. "
            "Аромат успеха и стабильности.\n\n"
            "✅ Стойкость: 50+ часов\n"
            "💰 Цена: от 1990₽\n"
            "🎁 С промокодом: от 1592₽"
        ),
    },
    "oceanix": {
        "name": "OCEANIX",
        "notes": ["citrus"],
        "hours": 60,
        "tags": ["durability", "attractiveness", "universal"],
        "desc": (
            "🎯 *OCEANIX*\n\n"
            "Свежесть океанского бриза. Морские аккорды с сочными "
            "цитрусовыми нотами.\n\n"
            "✅ Стойкость: 60+ часов\n"
            "💰 Цена: от 1990₽\n"
            "🎁 С промокодом: от 1592₽"
        ),
    },
    "alcibiades": {
        "name": "ALCIBIADES",
        "notes": ["oriental"],
        "hours": 48,
        "tags": ["attractiveness", "compliments"],
        "desc": (
            "🎯 *ALCIBIADES*\n\n"
            "Сладкая ваниль с тёплыми специями. Действует на женщин как магнит. "
            "Оружие соблазнения.\n\n"
            "✅ Стойкость: 48+ часов\n"
            "💰 Цена: от 1990₽\n"
            "🎁 С промокодом: от 1592₽"
        ),
    },
    "aquatis": {
        "name": "AQUATIS",
        "notes": ["citrus"],
        "hours": 50,
        "tags": ["compliments", "quality"],
        "desc": (
            "🎯 *AQUATIS*\n\n"
            "Прохлада мокрого кипариса, лёгкая древесная основа. "
            "Благородная свежесть, которая не сливается с толпой.\n\n"
            "✅ Стойкость: 50+ часов\n"
            "💰 Цена: от 1990₽\n"
            "🎁 С промокодом: от 1592₽"
        ),
    },
}

# Маппинг нот
NOTES_MAP = {
    "spicy": ["chronis", "vortexium", "zephyron"],
    "citrus": ["citronex", "solvion", "oceanix", "aquatis"],
    "oriental": ["alcibiades", "outlion"],
    "woody": ["elyxion", "verdantis", "zephyron"],
    "leather_tobacco": ["obsidian", "drakonis", "terranex"],
}

# Варианты для вопроса 3
IMPORTANCE_OPTIONS = {
    "durability": "⏱ Стойкость",
    "attractiveness": "💋 Привлекательность",
    "status": "👑 Статус и впечатление",
    "compliments": "💬 Комплименты",
    "quality": "💰 Цена и качество",
    "universal": "🔄 Универсальность",
}

# Варианты для вопроса 4
NOTES_OPTIONS = {
    "spicy": "🌶 Пряные",
    "citrus": "🍋 Свежие и цитрусовые",
    "oriental": "🌙 Восточные и сладкие",
    "woody": "🌲 Древесные",
    "leather_tobacco": "🖤 Кожаные и табачные",
}


# ==================== СОСТОЯНИЯ ====================
class QuizStates(StatesGroup):
    gender = State()
    age = State()
    importance = State()
    notes = State()


# ==================== ИНИЦИАЛИЗАЦИЯ ====================
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# ==================== ХЕЛПЕРЫ ====================
def make_kb(buttons: list[tuple[str, str]], row_width: int = 2) -> InlineKeyboardMarkup:
    keyboard = []
    row = []
    for text, data in buttons:
        row.append(InlineKeyboardButton(text=text, callback_data=data))
        if len(row) == row_width:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def make_multiselect_kb(
    options: dict[str, str],
    selected: set,
    prefix: str,
) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру с мультивыбором (✅ для выбранных)"""
    keyboard = []
    for key, label in options.items():
        check = "✅ " if key in selected else ""
        keyboard.append(
            [InlineKeyboardButton(text=f"{check}{label}", callback_data=f"{prefix}_{key}")]
        )
    # Кнопка "Готово" — появляется только если выбран хотя бы 1 вариант
    if selected:
        keyboard.append(
            [InlineKeyboardButton(text="➡️ Готово", callback_data=f"{prefix}_done")]
        )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_recommendations(
    selected_notes: list[str],
    selected_importance: list[str],
    count: int = 3,
) -> list[dict]:
    """Подбирает ароматы по нескольким нотам и приоритетам"""
    # Собираем всех кандидатов из выбранных нот
    seen = set()
    candidates = []
    for note in selected_notes:
        for pid in NOTES_MAP.get(note, []):
            if pid not in seen:
                seen.add(pid)
                candidates.append(PERFUMES[pid] | {"id": pid})

    # Скоринг: количество совпадений по тегам важности + стойкость
    def score(p):
        tag_matches = sum(1 for imp in selected_importance if imp in p.get("tags", []))
        return (tag_matches, p["hours"])

    candidates.sort(key=score, reverse=True)
    return candidates[:count]


# ==================== ОБРАБОТЧИКИ ====================
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    text = (
        "👋 Привет! Я помогу подобрать идеальный аромат от *One&Only Perfumer*\n\n"
        "Ответь на 4 вопроса — и получи персональную подборку + промокод на скидку 20% 🎁\n\n"
        "Поехали?"
    )
    kb = make_kb([("🚀 Начать подбор", "start_quiz")], row_width=1)
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")


@dp.callback_query(F.data == "start_quiz")
async def start_quiz(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    kb = make_kb([
        ("👨 Мужчина", "gender_male"),
        ("👩 Девушка", "gender_female"),
    ])
    await callback.message.edit_text(
        "❓ *Вопрос 1 из 4*\n\nВаш пол?",
        reply_markup=kb,
        parse_mode="Markdown",
    )
    await state.set_state(QuizStates.gender)


@dp.callback_query(QuizStates.gender, F.data.startswith("gender_"))
async def process_gender(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    gender = callback.data.replace("gender_", "")
    await state.update_data(gender=gender)

    kb = make_kb([
        ("18-24", "age_18"),
        ("25-34", "age_25"),
        ("35-44", "age_35"),
        ("45+", "age_45"),
    ])
    await callback.message.edit_text(
        "❓ *Вопрос 2 из 4*\n\nВаш возраст?",
        reply_markup=kb,
        parse_mode="Markdown",
    )
    await state.set_state(QuizStates.age)


@dp.callback_query(QuizStates.age, F.data.startswith("age_"))
async def process_age(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    age = callback.data.replace("age_", "")
    await state.update_data(age=age, selected_importance=set())

    kb = make_multiselect_kb(IMPORTANCE_OPTIONS, set(), "imp")
    await callback.message.edit_text(
        "❓ *Вопрос 3 из 4*\n\n"
        "Что для вас важно при покупке парфюма?\n"
        "_Можно выбрать несколько вариантов_",
        reply_markup=kb,
        parse_mode="Markdown",
    )
    await state.set_state(QuizStates.importance)


@dp.callback_query(QuizStates.importance, F.data.startswith("imp_"))
async def process_importance(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.replace("imp_", "")
    data = await state.get_data()

    # Конвертируем из списка в set (на случай если из JSON)
    selected = set(data.get("selected_importance", []))

    if action == "done":
        if not selected:
            await callback.answer("Выберите хотя бы один вариант", show_alert=True)
            return
        await callback.answer()
        # Переходим к вопросу 4
        await state.update_data(
            selected_importance=list(selected),
            selected_notes=set(),
        )
        kb = make_multiselect_kb(NOTES_OPTIONS, set(), "note")
        await callback.message.edit_text(
            "❓ *Вопрос 4 из 4*\n\n"
            "Какие ноты вам нравятся?\n"
            "_Можно выбрать несколько вариантов_",
            reply_markup=kb,
            parse_mode="Markdown",
        )
        await state.set_state(QuizStates.notes)
        return

    # Тогл выбора
    await callback.answer()
    if action in selected:
        selected.discard(action)
    else:
        selected.add(action)

    await state.update_data(selected_importance=list(selected))
    kb = make_multiselect_kb(IMPORTANCE_OPTIONS, selected, "imp")
    await callback.message.edit_reply_markup(reply_markup=kb)


@dp.callback_query(QuizStates.notes, F.data.startswith("note_"))
async def process_notes(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.replace("note_", "")
    data = await state.get_data()

    selected = set(data.get("selected_notes", []))

    if action == "done":
        if not selected:
            await callback.answer("Выберите хотя бы один вариант", show_alert=True)
            return
        await callback.answer()

        # Получаем результаты
        importance_list = data.get("selected_importance", [])
        notes_list = list(selected)

        recs = get_recommendations(notes_list, importance_list, count=3)

        # Формируем результат
        result_text = "🎉 *Ваша персональная подборка готова!*\n\n"

        for i, perfume in enumerate(recs, 1):
            result_text += f"*{i}.* {perfume['desc']}\n\n"

        result_text += "━━━━━━━━━━━━━━━\n\n"
        result_text += f"🎁 *Ваш промокод на скидку 20%:* `{PROMO_CODE}`\n"
        result_text += "⏰ Действует 24 часа!\n\n"

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🛒 Перейти в каталог", url=SITE_URL)],
                [InlineKeyboardButton(text="📺 Как пользоваться сайтом", url=VIDEO_URL)],
                [InlineKeyboardButton(text="📱 Наш Telegram-канал", url=TG_CHANNEL)],
                [InlineKeyboardButton(text="🔄 Пройти заново", callback_data="start_quiz")],
            ]
        )

        await callback.message.edit_text(
            result_text,
            reply_markup=kb,
            parse_mode="Markdown",
        )
        await state.clear()
        return

    # Тогл выбора
    await callback.answer()
    if action in selected:
        selected.discard(action)
    else:
        selected.add(action)

    await state.update_data(selected_notes=list(selected))
    kb = make_multiselect_kb(NOTES_OPTIONS, selected, "note")
    await callback.message.edit_reply_markup(reply_markup=kb)


# ==================== ЗАПУСК ====================
async def main():
    logging.info("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
