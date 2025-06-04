import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from game_logic import generate_board, render_board, generate_shapes, random_bonus
from database import init_db, get_score, add_score

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_states = {}

@dp.message(F.text.lower() == "/start")
async def start_game(message: types.Message):
    user_id = message.from_user.id
    user_states[user_id] = {
        "board": generate_board(),
        "shapes": generate_shapes(),
        "round": 1,
    }
    await show_game(message.chat.id, user_id)

async def show_game(chat_id, user_id):
    state = user_states[user_id]
    score = get_score(user_id)
    board_text = render_board(state["board"])
    shapes = " | ".join(state["shapes"])
    text = f"🎮 Уровень: {state['round']} | Очки: {score}\n\n{board_text}\n\n🧩 Фигуры: {shapes}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Обновить фигуры", callback_data="refresh")],
        [InlineKeyboardButton(text="🎲 Мини-игра", callback_data="minigame")],
    ])
    await bot.send_message(chat_id, text, reply_markup=kb)

@dp.callback_query(F.data == "refresh")
async def refresh_figures(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_states[user_id]["shapes"] = generate_shapes()
    await show_game(call.message.chat.id, user_id)

@dp.callback_query(F.data == "minigame")
async def minigame(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❓ Вопрос", callback_data="quiz")],
        [InlineKeyboardButton(text="🎁 Сундук", callback_data="bonus")],
    ])
    await call.message.answer("Выбери мини-игру:", reply_markup=kb)

@dp.callback_query(F.data == "quiz")
async def quiz_game(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="42", callback_data="quiz_right"),
         InlineKeyboardButton(text="24", callback_data="quiz_wrong")]
    ])
    await call.message.answer("Сколько будет 6 × 7?", reply_markup=kb)

@dp.callback_query(F.data == "quiz_right")
async def quiz_right(call: types.CallbackQuery):
    user_id = call.from_user.id
    add_score(user_id, 10)
    await call.message.answer("✅ Верно! +10 очков.")
    await show_game(call.message.chat.id, user_id)

@dp.callback_query(F.data == "quiz_wrong")
async def quiz_wrong(call: types.CallbackQuery):
    await call.message.answer("❌ Неправильно. Попробуй позже.")
    await show_game(call.message.chat.id, call.from_user.id)

@dp.callback_query(F.data == "bonus")
async def bonus_game(call: types.CallbackQuery):
    prize = random_bonus()
    user_id = call.from_user.id
    if prize == "+5 очков":
        add_score(user_id, 5)
    elif prize == "+1 фигура":
        user_states[user_id]["shapes"].append(generate_shapes(1)[0])
    await call.message.answer(f"🎁 Ты получил: {prize}")
    await show_game(call.message.chat.id, user_id)

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())