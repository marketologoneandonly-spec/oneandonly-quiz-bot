import asyncio
import json
import logging
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, FSInputFile

# ==================== НАСТРОЙКИ ====================
BOT_TOKEN = "8645459843:AAHPX3bqbSDMDiR17in1r2yjhvS90JmLOcs"

PROMO_CODE = "QUIZ20"
CATALOG_URL = "https://oneandonly-perfumer.com/catalog?utm_source=tg&utm_medium=bot&utm_campaign=open"
HOW_TO_URL = "https://oneandonly-perfumer.com/?utm_source=tg&utm_medium=bot&utm_campaign=open2"
TG_CHANNEL = "https://t.me/oneandonly_perfumer"

ADMIN_ID = 77429602
USERS_FILE = "users.json"

# Папка с фото отзывов
REVIEWS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reviews")


# ==================== БАЗА ПОЛЬЗОВАТЕЛЕЙ ====================
def load_users() -> dict:
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_users(users: dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def save_user(user: types.User, quiz_data: dict):
    users = load_users()
    uid = str(user.id)
    users[uid] = {
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "quiz_data": quiz_data,
        "completed_at": datetime.now().isoformat(),
        "quiz_count": users.get(uid, {}).get("quiz_count", 0) + 1,
    }
    save_users(users)


# ==================== FOLLOW-UP ЦЕПОЧКА ====================
async def send_followup_chain(user_id: int):
    """Отправляет цепочку сообщений: 30 мин, 6 часов, 12 часов"""

    # --- Через 30 минут ---
    await asyncio.sleep(30 * 60)
    try:
        await bot.send_message(
            user_id,
            "👋 У меня есть закрытый уникальный канал про парфюм, "
            "на котором я рассказываю о новинках, делюсь уникальными дропами, "
            "даю скидки и запускаю розыгрыши на парфюм.\n\n"
            "Обязательно подпишись на него 👇",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📱 Подписаться на канал", url=TG_CHANNEL)],
            ]),
        )
        logging.info(f"Follow-up 30min sent to {user_id}")
    except Exception as e:
        logging.warning(f"Follow-up 30min failed for {user_id}: {e}")

    # --- Через 6 часов (5.5 часов после первого) ---
    await asyncio.sleep(5 * 60 * 60 + 30 * 60)
    try:
        text_6h = (
            "⭐ У моей линейки парфюмов более 1000 реальных отзывов "
            "довольных клиентов!\n\nВот некоторые из них 👇"
        )

        # Собираем фото из папки reviews
        review_files = sorted([
            os.path.join(REVIEWS_DIR, f)
            for f in os.listdir(REVIEWS_DIR)
            if f.endswith((".png", ".jpg", ".jpeg"))
        ]) if os.path.exists(REVIEWS_DIR) else []

        if review_files:
            # Telegram позволяет до 10 фото в альбоме
            media = []
            for i, filepath in enumerate(review_files[:10]):
                photo = FSInputFile(filepath)
                if i == 0:
                    media.append(InputMediaPhoto(media=photo, caption=text_6h))
                else:
                    media.append(InputMediaPhoto(media=photo))
            await bot.send_media_group(user_id, media)
        else:
            await bot.send_message(user_id, text_6h)

        logging.info(f"Follow-up 6h sent to {user_id}")
    except Exception as e:
        logging.warning(f"Follow-up 6h failed for {user_id}: {e}")

    # --- Через 12 часов (6 часов после второго) ---
    await asyncio.sleep(6 * 60 * 60)
    try:
        await bot.send_message(
            user_id,
            f"🔥 Не забудь воспользоваться промокодом *{PROMO_CODE}* на сайте, "
            f"чтобы сделать заказ со скидкой — переходи по ссылке 👇",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🛒 Заказать со скидкой", url=CATALOG_URL)],
            ]),
            parse_mode="Markdown",
        )
        logging.info(f"Follow-up 12h sent to {user_id}")
    except Exception as e:
        logging.warning(f"Follow-up 12h failed for {user_id}: {e}")


# ==================== КАТАЛОГ АРОМАТОВ ====================
PERFUMES = {
    "obsidian": {
        "name": "OBSIDIAN", "notes": ["leather_tobacco"], "hours": 60,
        "tags": ["durability", "attractiveness", "status"],
        "desc": "🎯 *OBSIDIAN*\n\nГлубокие смолистые ноты, насыщенный табак и соблазнительный ром. Чувственный и мистический.\n\n✅ Стойкость: 60+ часов\n💰 Цена: от 1990₽\n🎁 С промокодом: от 1592₽",
    },
    "elyxion": {
        "name": "ELYXION", "notes": ["woody"], "hours": 72,
        "tags": ["durability", "universal", "compliments"],
        "desc": "🎯 *ELYXION*\n\nМужественные древесные ноты, чистота зелёных оттенков и энергичность цитрусов. Для тех, кто любит быть на вершине.\n\n✅ Стойкость: 72+ часа\n💰 Цена: от 1990₽\n🎁 С промокодом: от 1592₽",
    },
    "citronex": {
        "name": "CITRONEX", "notes": ["citrus"], "hours": 48,
        "tags": ["universal", "compliments", "attractiveness"],
        "desc": "🎯 *CITRONEX*\n\nВзрыв цитрусов и древесная база. Свежий, энергичный, дерзкий. Идеально для работы, свиданий, тусовок.\n\n✅ Стойкость: 48+ часов\n💰 Цена: от 1990₽\n🎁 С промокодом: от 1592₽",
    },
    "terranex": {
        "name": "TERRANEX", "notes": ["leather_tobacco"], "hours": 50,
        "tags": ["status", "attractiveness"],
        "desc": "🎯 *TERRANEX*\n\nДымные аккорды с благородной кожей и фруктовыми нотами. Композиция силы и уверенности.\n\n✅ Стойкость: 50+ часов\n💰 Цена: от 1990₽\n🎁 С промокодом: от 1592₽",
    },
    "drakonis": {
        "name": "DRAKONIS", "notes": ["leather_tobacco"], "hours": 50,
        "tags": ["status", "attractiveness", "durability"],
        "desc": "🎯 *DRAKONIS*\n\nКожаные ноты с лёгкой сладостью. Дерзкий, брутальный, статусный. Пахнет кожаным салоном роскошного автомобиля.\n\n✅ Стойкость: 50+ часов\n💰 Цена: от 1990₽\n🎁 С промокодом: от 1592₽",
    },
    "outlion": {
        "name": "OUTLION", "notes": ["oriental"], "hours": 60,
        "tags": ["durability", "attractiveness", "status"],
        "desc": "🎯 *OUTLION*\n\nИнтенсивный уд, восточные специи и благородная древесина. Для тех, кто не боится доминировать.\n\n✅ Стойкость: 60+ часов\n💰 Цена: от 1990₽\n🎁 С промокодом: от 1592₽",
    },
    "zephyron": {
        "name": "ZEPHYRON", "notes": ["spicy", "woody"], "hours": 55,
        "tags": ["compliments", "status"],
        "desc": "🎯 *ZEPHYRON*\n\nСложный многогранный аромат. Свежие цитрусы с тёплыми древесными аккордами и пряными оттенками.\n\n✅ Стойкость: 55+ часов\n💰 Цена: от 1990₽\n🎁 С промокодом: от 1592₽",
    },
    "chronis": {
        "name": "CHRONIS", "notes": ["spicy"], "hours": 72,
        "tags": ["durability", "attractiveness", "universal"],
        "desc": "🎯 *CHRONIS*\n\nЯркий цитрус, пряности и древесина. Мощный, энергичный аромат для настоящих мужчин.\n\n✅ Стойкость: 72+ часа\n💰 Цена: от 1990₽\n🎁 С промокодом: от 1592₽",
    },
    "verdantis": {
        "name": "VERDANTIS", "notes": ["woody"], "hours": 50,
        "tags": ["status", "compliments"],
        "desc": "🎯 *VERDANTIS*\n\nГлубокий, слегка пряный с тёплыми древесными и табачными нотами. Благородство без слов.\n\n✅ Стойкость: 50+ часов\n💰 Цена: от 1990₽\n🎁 С промокодом: от 1592₽",
    },
    "solvion": {
        "name": "SOLVION", "notes": ["citrus"], "hours": 55,
        "tags": ["universal", "attractiveness"],
        "desc": "🎯 *SOLVION*\n\nСочный лимон, морской бриз и тёплая древесина. Энергия Средиземноморья в одном флаконе.\n\n✅ Стойкость: 55+ часов\n💰 Цена: от 1990₽\n🎁 С промокодом: от 1592₽",
    },
    "vortexium": {
        "name": "VORTEXIUM", "notes": ["spicy"], "hours": 50,
        "tags": ["status", "universal"],
        "desc": "🎯 *VORTEXIUM*\n\nПряности, глубокая древесина и тёплая амбра. Аромат успеха и стабильности.\n\n✅ Стойкость: 50+ часов\n💰 Цена: от 1990₽\n🎁 С промокодом: от 1592₽",
    },
    "oceanix": {
        "name": "OCEANIX", "notes": ["citrus"], "hours": 60,
        "tags": ["durability", "attractiveness", "universal"],
        "desc": "🎯 *OCEANIX*\n\nСвежесть океанского бриза. Морские аккорды с сочными цитрусовыми нотами.\n\n✅ Стойкость: 60+ часов\n💰 Цена: от 1990₽\n🎁 С промокодом: от 1592₽",
    },
    "alcibiades": {
        "name": "ALCIBIADES", "notes": ["oriental"], "hours": 48,
        "tags": ["attractiveness", "compliments"],
        "desc": "🎯 *ALCIBIADES*\n\nСладкая ваниль с тёплыми специями. Действует на женщин как магнит. Оружие соблазнения.\n\n✅ Стойкость: 48+ часов\n💰 Цена: от 1990₽\n🎁 С промокодом: от 1592₽",
    },
    "aquatis": {
        "name": "AQUATIS", "notes": ["citrus"], "hours": 50,
        "tags": ["compliments", "quality"],
        "desc": "🎯 *AQUATIS*\n\nПрохлада мокрого кипариса, лёгкая древесная основа. Благородная свежесть, которая не сливается с толпой.\n\n✅ Стойкость: 50+ часов\n💰 Цена: от 1990₽\n🎁 С промокодом: от 1592₽",
    },
}

NOTES_MAP = {
    "spicy": ["chronis", "vortexium", "zephyron"],
    "citrus": ["citronex", "solvion", "oceanix", "aquatis"],
    "oriental": ["alcibiades", "outlion"],
    "woody": ["elyxion", "verdantis", "zephyron"],
    "leather_tobacco": ["obsidian", "drakonis", "terranex"],
}

IMPORTANCE_OPTIONS = {
    "durability": "⏱ Стойкость",
    "attractiveness": "💋 Привлекательность",
    "status": "👑 Статус и впечатление",
    "compliments": "💬 Комплименты",
    "quality": "💰 Цена и качество",
    "universal": "🔄 Универсальность",
}

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


class BroadcastStates(StatesGroup):
    waiting_message = State()


# ==================== ИНИЦИАЛИЗАЦИЯ ====================
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# ==================== ХЕЛПЕРЫ ====================
def make_kb(buttons, row_width=2):
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


def make_multiselect_kb(options, selected, prefix):
    keyboard = []
    for key, label in options.items():
        check = "✅ " if key in selected else ""
        keyboard.append([InlineKeyboardButton(text=f"{check}{label}", callback_data=f"{prefix}_{key}")])
    if selected:
        keyboard.append([InlineKeyboardButton(text="➡️ Готово", callback_data=f"{prefix}_done")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_recommendations(selected_notes, selected_importance, count=3):
    seen = set()
    candidates = []
    for note in selected_notes:
        for pid in NOTES_MAP.get(note, []):
            if pid not in seen:
                seen.add(pid)
                candidates.append(PERFUMES[pid] | {"id": pid})

    def score(p):
        tag_matches = sum(1 for imp in selected_importance if imp in p.get("tags", []))
        return (tag_matches, p["hours"])

    candidates.sort(key=score, reverse=True)
    return candidates[:count]


# ==================== АДМИН-КОМАНДЫ ====================
@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    users = load_users()
    await message.answer(f"📊 *Статистика бота*\n\nПрошли квиз: *{len(users)}* чел.", parse_mode="Markdown")


@dp.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    users = load_users()
    if not users:
        await message.answer("База пуста — рассылать некому.")
        return
    await message.answer(
        f"📤 *Рассылка*\n\nВ базе *{len(users)}* чел.\n"
        f"Отправь мне сообщение для рассылки (текст, фото, видео — что угодно).\n\n"
        f"Для отмены напиши /cancel",
        parse_mode="Markdown",
    )
    await state.set_state(BroadcastStates.waiting_message)


@dp.message(BroadcastStates.waiting_message, Command("cancel"))
async def cancel_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.clear()
    await message.answer("Рассылка отменена.")


@dp.message(BroadcastStates.waiting_message)
async def process_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.clear()
    users = load_users()
    total = len(users)
    sent = 0
    failed = 0
    status_msg = await message.answer(f"⏳ Рассылаю... 0/{total}")

    for uid_str in users:
        uid = int(uid_str)
        try:
            await message.copy_to(chat_id=uid)
            sent += 1
        except Exception as e:
            logging.warning(f"Не удалось отправить {uid}: {e}")
            failed += 1
        if (sent + failed) % 10 == 0:
            try:
                await status_msg.edit_text(f"⏳ Рассылаю... {sent + failed}/{total}")
            except Exception:
                pass
        await asyncio.sleep(0.05)

    await status_msg.edit_text(
        f"✅ *Рассылка завершена*\n\nОтправлено: *{sent}*\nНе доставлено: *{failed}*\nВсего в базе: *{total}*",
        parse_mode="Markdown",
    )


@dp.message(Command("users"))
async def cmd_users(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    users = load_users()
    if not users:
        await message.answer("База пуста.")
        return
    sorted_users = sorted(users.values(), key=lambda x: x.get("completed_at", ""), reverse=True)[:20]
    text = "👥 *Последние прошедшие квиз:*\n\n"
    for u in sorted_users:
        username = f"@{u['username']}" if u.get("username") else u.get("first_name", "Без имени")
        date = u.get("completed_at", "")[:10]
        count = u.get("quiz_count", 1)
        text += f"• {username} — {date} (×{count})\n"
    text += f"\n📊 Всего в базе: *{len(users)}*"
    await message.answer(text, parse_mode="Markdown")


# ==================== КВИЗ ====================
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
    kb = make_kb([("👨 Мужчина", "gender_male"), ("👩 Девушка", "gender_female")])
    await callback.message.edit_text("❓ *Вопрос 1 из 4*\n\nВаш пол?", reply_markup=kb, parse_mode="Markdown")
    await state.set_state(QuizStates.gender)


@dp.callback_query(QuizStates.gender, F.data.startswith("gender_"))
async def process_gender(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(gender=callback.data.replace("gender_", ""))
    kb = make_kb([("18-24", "age_18"), ("25-34", "age_25"), ("35-44", "age_35"), ("45+", "age_45")])
    await callback.message.edit_text("❓ *Вопрос 2 из 4*\n\nВаш возраст?", reply_markup=kb, parse_mode="Markdown")
    await state.set_state(QuizStates.age)


@dp.callback_query(QuizStates.age, F.data.startswith("age_"))
async def process_age(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(age=callback.data.replace("age_", ""), selected_importance=[])
    kb = make_multiselect_kb(IMPORTANCE_OPTIONS, set(), "imp")
    await callback.message.edit_text(
        "❓ *Вопрос 3 из 4*\n\nЧто для вас важно при покупке парфюма?\n_Можно выбрать несколько вариантов_",
        reply_markup=kb, parse_mode="Markdown",
    )
    await state.set_state(QuizStates.importance)


@dp.callback_query(QuizStates.importance, F.data.startswith("imp_"))
async def process_importance(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.replace("imp_", "")
    data = await state.get_data()
    selected = set(data.get("selected_importance", []))

    if action == "done":
        if not selected:
            await callback.answer("Выберите хотя бы один вариант", show_alert=True)
            return
        await callback.answer()
        await state.update_data(selected_importance=list(selected), selected_notes=[])
        kb = make_multiselect_kb(NOTES_OPTIONS, set(), "note")
        await callback.message.edit_text(
            "❓ *Вопрос 4 из 4*\n\nКакие ноты вам нравятся?\n_Можно выбрать несколько вариантов_",
            reply_markup=kb, parse_mode="Markdown",
        )
        await state.set_state(QuizStates.notes)
        return

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

        importance_list = data.get("selected_importance", [])
        notes_list = list(selected)
        recs = get_recommendations(notes_list, importance_list, count=3)

        # Сохраняем пользователя
        save_user(callback.from_user, {
            "gender": data.get("gender"),
            "age": data.get("age"),
            "importance": importance_list,
            "notes": notes_list,
            "recommendations": [p["name"] for p in recs],
        })

        result_text = "🎉 *Ваша персональная подборка готова!*\n\n"
        for i, perfume in enumerate(recs, 1):
            result_text += f"*{i}.* {perfume['desc']}\n\n"
        result_text += f"━━━━━━━━━━━━━━━\n\n🎁 *Ваш промокод на скидку 20%:* `{PROMO_CODE}`\n⏰ Действует 24 часа!\n\n"

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Перейти в каталог", url=CATALOG_URL)],
            [InlineKeyboardButton(text="📺 Как пользоваться сайтом", url=HOW_TO_URL)],
            [InlineKeyboardButton(text="🔄 Пройти заново", callback_data="start_quiz")],
        ])
        await callback.message.edit_text(result_text, reply_markup=kb, parse_mode="Markdown")
        await state.clear()

        # Запускаем follow-up цепочку в фоне
        asyncio.create_task(send_followup_chain(callback.from_user.id))

        return

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
