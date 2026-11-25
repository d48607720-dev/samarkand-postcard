import os, asyncio, logging
from datetime import datetime, timedelta, timezone
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ["BOT_TOKEN"]
DAVID_ID = int(os.environ["DAVID_ID"])
ALBINA_ID = int(os.environ["ALBINA_ID"])

bot = Bot(TOKEN)
dp = Dispatcher()

# ---------- ТЕКСТЫ ----------

LIGHT = [
    "Привет, Альбина. Это Давид. Сделал небольшого бота, чтобы написать тебе. Нажимай «Дальше», когда будет время.",
    "Мы учимся в одном классе, а общаемся в основном по учёбе.",
    "Подумал, что можно иногда говорить и о других вещах.",
    "Например, чем ты любишь заниматься в свободное время?",
    "Или какую музыку слушаешь, что смотришь?",
    "Есть ли в Самарканде места, куда тебе нравится ходить?",
    "У меня тоже есть несколько мест, которые мне нравятся.",
    "Думаю, нам было бы о чём поговорить.",
    "Пока это просто общий интерес, ничего более.",
    "Дальше будет ещё несколько сообщений.",
]

DISCLAIMER = (
    "Уточнение.\n\n"
    "Дальше я скажу более прямо. Это не давление, и любой ответ нормальный. "
    "Если тебе неинтересно, напиши /stop, бот остановится."
)

SERIOUS = [
    "Если говорить прямо, ты мне симпатична.",
    "Мы не так давно общаемся, поэтому я ничего не жду заранее.",
    "Мне хотелось бы встретиться вне школы и пообщаться в спокойной обстановке.",
    "Ниже несколько вариантов, как это могло бы выглядеть.",
    "Это просто идеи, ничего обязательного.",
]

DATES = [
    "Прогулка по Регистану вечером, когда включается подсветка.",
    "Сиабский базар: попробовать самсу и лепёшки.",
    "Кофе или ужин в кафе, например Platan или Karimbek. Место можно выбрать любое.",
    "Гур-Эмир и Биби-Ханум днём, затем чай где-нибудь рядом.",
    "Обсерватория Улугбека и вид на город на закате.",
]

FINAL = (
    "Как ты относишься к тому, чтобы как-нибудь сходить куда-то из этого? "
    "Можешь ответить как есть.\n\n— Давид"
)

BTN_NEXT = "Дальше"
BTN_YES = "Да, можно"
BTN_THINK = "Нужно подумать"
BTN_BACK = "Другой день"

TXT_PICK_DAY = "Выбери день, когда у тебя свободно."
TXT_PICK_TIME = "Выбери удобное время."
TXT_THINK = "Хорошо, без спешки."
TXT_STOP = "Хорошо, останавливаю. Спасибо, что уделила время."
TXT_DONE = "Записал: {day}, {time}.\nНапишу тебе, обсудим место."

# ---------- ЛОГИКА ----------

STEPS = LIGHT + [DISCLAIMER] + SERIOUS + DATES
TOTAL = len(STEPS)
DISCLAIMER_IDX = len(LIGHT)
SERIOUS_IDX = DISCLAIMER_IDX + 1
DATES_IDX = SERIOUS_IDX + len(SERIOUS)

ANSWER_TEXT = {
    "yes": "согласна встретиться",
    "think": "нужно подумать",
}

ANSWER_KB = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=BTN_YES, callback_data="a:yes")],
    [InlineKeyboardButton(text=BTN_THINK, callback_data="a:think")],
])


def next_kb(i):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=BTN_NEXT, callback_data=f"n:{i}")]])


async def notify(text):
    try:
        await bot.send_message(DAVID_ID, text)
    except Exception as e:
        logging.warning("notify failed: %s", e)


async def send_step(chat_id, i):
    if i >= TOTAL:
        await bot.send_message(chat_id, FINAL, reply_markup=ANSWER_KB)
        await notify("Альбина дошла до финального вопроса")
        return
    await bot.send_message(chat_id, STEPS[i], reply_markup=next_kb(i + 1))
    marks = {
        DISCLAIMER_IDX: "уточнения",
        SERIOUS_IDX: "более прямой части",
        DATES_IDX: "вариантов мест",
    }
    if i in marks:
        await notify(f"Альбина дошла до {marks[i]}")


@dp.message(Command("start"))
async def start(m: Message):
    if m.from_user.id == ALBINA_ID:
        await notify("Альбина запустила бота")
        await send_step(m.chat.id, 0)
    elif m.from_user.id == DAVID_ID:
        await m.answer(
            "Бот работает. Альбина должна сама нажать /start у бота, "
            "иначе Telegram не даст ему писать ей. После этого можно отправить /push."
        )


@dp.message(Command("push"))
async def push(m: Message):
    if m.from_user.id != DAVID_ID:
        return
    try:
        await send_step(ALBINA_ID, 0)
        await m.answer("Отправлено Альбине")
    except Exception as e:
        await m.answer(f"Не вышло: {e}\nПроверь, что Альбина нажала /start у бота.")


@dp.message(Command("stop"))
async def stop(m: Message):
    if m.from_user.id == ALBINA_ID:
        await m.answer(TXT_STOP)
        await notify("Альбина остановила бота")


@dp.callback_query(F.data.startswith("n:"))
async def on_next(c: CallbackQuery):
    if c.from_user.id != ALBINA_ID:
        return await c.answer()
    await c.answer()
    await c.message.edit_reply_markup(reply_markup=None)
    await send_step(c.message.chat.id, int(c.data.split(":")[1]))


# ---------- КАЛЕНДАРЬ ----------

TZ = timezone(timedelta(hours=5))  # Самарканд, UTC+5
WD = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
TIMES = ["12:00", "14:00", "16:00", "18:00", "19:30"]


def calendar_kb():
    today = datetime.now(TZ).date()
    days = [today + timedelta(days=i) for i in range(1, 15)]
    rows, row = [], []
    for d in days:
        row.append(InlineKeyboardButton(
            text=f"{WD[d.weekday()]} {d.strftime('%d.%m')}",
            callback_data=f"d:{d.isoformat()}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def times_kb(day):
    rows, row = [], []
    for t in TIMES:
        row.append(InlineKeyboardButton(text=t, callback_data=f"t:{day}|{t}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text=BTN_BACK, callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def fmt_day(iso):
    d = datetime.fromisoformat(iso).date()
    return f"{WD[d.weekday()]}, {d.strftime('%d.%m.%Y')}"


@dp.callback_query(F.data.startswith("a:"))
async def on_answer(c: CallbackQuery):
    if c.from_user.id != ALBINA_ID:
        return await c.answer()
    key = c.data.split(":")[1]
    await c.answer()
    await c.message.edit_reply_markup(reply_markup=None)
    await notify(f"Ответ Альбины: {ANSWER_TEXT[key]}")
    if key == "yes":
        await c.message.answer(TXT_PICK_DAY, reply_markup=calendar_kb())
    else:
        await c.message.answer(TXT_THINK)


@dp.callback_query(F.data == "back")
async def on_back(c: CallbackQuery):
    if c.from_user.id != ALBINA_ID:
        return await c.answer()
    await c.answer()
    await c.message.edit_text(TXT_PICK_DAY, reply_markup=calendar_kb())


@dp.callback_query(F.data.startswith("d:"))
async def on_day(c: CallbackQuery):
    if c.from_user.id != ALBINA_ID:
        return await c.answer()
    await c.answer()
    day = c.data[2:]
    await c.message.edit_text(
        f"{fmt_day(day)}\n{TXT_PICK_TIME}", reply_markup=times_kb(day)
    )


@dp.callback_query(F.data.startswith("t:"))
async def on_time(c: CallbackQuery):
    if c.from_user.id != ALBINA_ID:
        return await c.answer()
    await c.answer()
    day, t = c.data[2:].split("|")
    await c.message.edit_text(TXT_DONE.format(day=fmt_day(day), time=t))
    await notify(
        f"Альбина выбрала время: {fmt_day(day)}, {t}.\n"
        "Напиши ей и обсуди место."
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
