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
VIDEO_URL = "https://oneandonly-perfumer.com/"  # видео на главной

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

# Маппинг важности → тег
IMPORTANCE_MAP = {
    "durability": "durability",
    "attractiveness": "attractiveness",
    "status": "status",
    "compliments": "compliments",
    "quality": "quality",
    "universal": "universal",
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
    """Создаёт инлайн-клавиатуру из списка (текст, callback_data)"""
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


def get_recommendations(note: str, importance: str, count: int = 2) -> list[dict]:
    """Подбирает ароматы по нотам и важности"""
    candidates = NOTES_MAP.get(note, [])
    perfume_list = [PERFUMES[pid] | {"id": pid} for pid in candidates]

    # Сортируем: сначала по совпадению тега важности, потом по стойкости
    def score(p):
        tag_match = 1 if importance in p.get("tags", []) else 0
        return (tag_match, p["hours"])

    perfume_list.sort(key=score, reverse=True)
    return perfume_list[:count]


# ==================== ОБРАБОТЧИКИ ====================
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    text = (
        "👋 Привет! Я помогу подобрать идеальный аромат от *One&Only Perfumer*\n\n"
        "Ответь на 4 вопроса — и получи персональную подборку + промокод на скидку 20% 🎁\n\n"
        "Поехали?"
    )
    kb = make_kb([
        ("🚀 Начать подбор", "start_quiz"),
    ], row_width=1)
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")


@dp.callback_query(F.data == "start_quiz")
async def start_quiz(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
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
    await state.update_data(age=age)

    kb = make_kb(
        [
            ("⏱ Стойкость", "imp_durability"),
            ("💋 Привлекательность", "imp_attractiveness"),
            ("👑 Статус и впечатление", "imp_status"),
            ("💬 Комплименты", "imp_compliments"),
            ("💰 Цена и качество", "imp_quality"),
            ("🔄 Универсальность", "imp_universal"),
        ],
        row_width=1,
    )
    await callback.message.edit_text(
        "❓ *Вопрос 3 из 4*\n\nЧто для вас важно при покупке парфюма?",
        reply_markup=kb,
        parse_mode="Markdown",
    )
    await state.set_state(QuizStates.importance)


@dp.callback_query(QuizStates.importance, F.data.startswith("imp_"))
async def process_importance(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    importance = callback.data.replace("imp_", "")
    await state.update_data(importance=importance)

    kb = make_kb(
        [
            ("🌶 Пряные", "note_spicy"),
            ("🍋 Свежие и цитрусовые", "note_citrus"),
            ("🌙 Восточные и сладкие", "note_oriental"),
            ("🌲 Древесные", "note_woody"),
            ("🖤 Кожаные и табачные", "note_leather_tobacco"),
        ],
        row_width=1,
    )
    await callback.message.edit_text(
        "❓ *Вопрос 4 из 4*\n\nКакие ноты вам нравятся?",
        reply_markup=kb,
        parse_mode="Markdown",
    )
    await state.set_state(QuizStates.notes)


@dp.callback_query(QuizStates.notes, F.data.startswith("note_"))
async def process_notes(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    note = callback.data.replace("note_", "")
    data = await state.get_data()
    importance = data.get("importance", "durability")

    recs = get_recommendations(note, importance, count=2)

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


# ==================== ЗАПУСК ====================
async def main():
    logging.info("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
