import asyncio
import json
import os
import threading
from datetime import datetime
from flask import Flask

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    CallbackQuery,
)

# ============ SOZLAMALAR ============
BOT_TOKEN = "8843105986:AAGn1GNZKf748_hGOZWhri7A2lJF8q0pIbU"
ADMIN_ID = 8374511835
ADMIN_USERNAME = "alphauzff"
CARD_NUMBER = "9860 1666 5545 7637"
CARD_OWNER = "U.M"
REQUIRED_CHANNEL = "alpha02uz"

DB_FILE = "database.json"

# Virtual nomerlar (10 davlat)
VIRTUAL_NUMBERS = {
    "🇿🇦 Janubiy Afrika": 8000,
    "🇮🇩 Indonesiya": 7000,
    "🇨🇱 Chili": 8000,
    "🇲🇦 Marokko": 7000,
    "🇨🇦 Kanada": 9000,
    "🇺🇸 Amerika": 10000,
    "🇬🇧 Britaniya": 9000,
    "🇦🇪 BAA": 12000,
    "🇵🇱 Polsha": 6000,
    "🇸🇬 Singapur": 8000,
}

# Premium Telegram nomerlar (5 davlat)
PREMIUM_NUMBERS = {
    "🇿🇦 Janubiy Afrika": 15000,
    "🇮🇩 Indonesiya": 18000,
    "🇨🇱 Chili": 20000,
    "🇲🇦 Marokko": 17000,
    "🇨🇦 Kanada": 25000,
}

# YouTube/Google verification nomerlar
YOUTUBE_NUMBERS = {
    "🎬 Anonim Nomer 1": 3000,
    "🎬 Anonim Nomer 2": 4000,
    "🎬 Anonim Nomer 3": 3500,
    "🎬 Anonim Nomer 4": 4500,
    "🎬 Anonim Nomer 5": 5000,
}

# Tayor Telegram akkauntlar
READY_ACCOUNTS = {
    "📱 Oddiy Akkaunt (Uzbek)": 10000,
    "📱 Oddiy Akkaunt (Random)": 12000,
    "📱 Premium Akkaunt (Uzbek)": 25000,
    "📱 Premium Akkaunt (Random)": 30000,
    "📱 Old Akkaunt (Uzbek)": 15000,
    "📱 Old Akkaunt (Random)": 18000,
}

# =====================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# ---------- JSON baza ----------
def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def get_user(db, user_id):
    uid = str(user_id)
    if uid not in db["users"]:
        db["users"][uid] = {"balance": 0, "history": []}
    return db["users"][uid]


# ---------- FSM holatlari ----------
class TopUp(StatesGroup):
    waiting_check = State()


class AdminHelp(StatesGroup):
    waiting_message = State()


class AdminCustomAmount(StatesGroup):
    waiting_amount = State()


# ---------- Kanal tekshirish ----------
async def check_channel_subscription(user_id):
    try:
        member = await bot.get_chat_member(f"@{REQUIRED_CHANNEL}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# ---------- Klaviaturalar ----------
def main_menu():
    kb = [
        [InlineKeyboardButton(text="💳 Hisob to'ldirish", callback_data="topup")],
        [InlineKeyboardButton(text="📱 Tayor Telegram Akkauntlar", callback_data="ready_accounts")],
        [InlineKeyboardButton(text="🔢 Virtual Nomerlar", callback_data="virtual_numbers")],
        [InlineKeyboardButton(text="👑 Premium Telegram Nomerlar", callback_data="premium_numbers")],
        [InlineKeyboardButton(text="🎬 YouTube/Google Nomerlar", callback_data="youtube_numbers")],
        [InlineKeyboardButton(text="🆘 Admin Yordam", callback_data="admin_help")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def back_button():
    kb = [[InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_main")]]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def subscribe_button():
    kb = [
        [InlineKeyboardButton(text="✅ Kanalga a'zo bo'ldim", callback_data="check_subscribe")],
        [InlineKeyboardButton(text="📢 Kanalni ochish", url=f"https://t.me/{REQUIRED_CHANNEL}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def create_items_menu(items, callback_prefix):
    kb = []
    for name, price in items.items():
        label = f"{name} — {price:,} so'm"
        kb.append([InlineKeyboardButton(text=label, callback_data=f"{callback_prefix}_{name}")])
    kb.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


# ---------- /start ----------
@dp.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    
    is_subscribed = await check_channel_subscription(message.from_user.id)
    
    if not is_subscribed:
        await message.answer(
            f"👋 Assalomu alaykum, {message.from_user.full_name}!\n\n"
            "🔔 Botdan foydalanish uchun avval kanalimizga a'zo bo'lishingiz kerak:",
            reply_markup=subscribe_button(),
        )
        return
    
    db = load_db()
    user = get_user(db, message.from_user.id)
    save_db(db)
    
    await message.answer(
        f"👋 Assalomu alaykum, {message.from_user.full_name}!\n\n"
        f"💰 Balansingiz: {user['balance']:,} so'm\n\n"
        "🎯 Quyidagi menyudan birini tanlang:",
        reply_markup=main_menu(),
    )


@dp.callback_query(F.data == "check_subscribe")
async def check_subscribe(callback: CallbackQuery, state: FSMContext):
    is_subscribed = await check_channel_subscription(callback.from_user.id)
    
    if not is_subscribed:
        await callback.answer("❌ Siz kanalga a'zo bolmadingiz. Iltimos qayta urinib ko'ring.", show_alert=True)
        return
    
    await state.clear()
    db = load_db()
    user = get_user(db, callback.from_user.id)
    save_db(db)
    
    await callback.message.edit_text(
        f"✅ A'zosiz foydalanish uchun ruxsat berildi!\n\n"
        f"💰 Balansingiz: {user['balance']:,} so'm\n\n"
        "🎯 Quyidagi menyudan birini tanlang:",
        reply_markup=main_menu(),
    )
    await callback.answer("✅ Xush kelibsiz!")


@dp.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    db = load_db()
    user = get_user(db, callback.from_user.id)
    await callback.message.edit_text(
        f"💰 Balansingiz: {user['balance']:,} so'm\n\n🎯 Menyu:",
        reply_markup=main_menu(),
    )
    await callback.answer()


# ---------- 1-BO'LIM: Hisob to'ldirish ----------
@dp.callback_query(F.data == "topup")
async def topup_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TopUp.waiting_check)
    await callback.message.edit_text(
        f"💳 💰 HISOB TO'LDIRISH 💰\n\n"
        f"🏦 Karta: <b>{CARD_NUMBER}</b>\n"
        f"👤 Egasi: <b>{CARD_OWNER}</b>\n"
        f"💼 Xizmat: <b>Humo</b>\n\n"
        "✅ To'lovni amalga oshirgach, chek skrinshotini yuboring 👇",
        parse_mode="HTML",
        reply_markup=back_button(),
    )
    await callback.answer()


@dp.message(TopUp.waiting_check, F.photo)
async def receive_check(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "✅ Chekingiz qabul qilindi!\n"
        "Admin tekshiruvidan so'ng 5–10 daqiqa ichida hisobingiz to'ldiriladi.",
        reply_markup=main_menu(),
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ 1 000", callback_data=f"add_{message.from_user.id}_1000"),
            InlineKeyboardButton(text="➕ 5 000", callback_data=f"add_{message.from_user.id}_5000"),
            InlineKeyboardButton(text="➕ 10 000", callback_data=f"add_{message.from_user.id}_10000"),
        ],
        [
            InlineKeyboardButton(text="➕ 20 000", callback_data=f"add_{message.from_user.id}_20000"),
            InlineKeyboardButton(text="✍️ Boshqa summa", callback_data=f"addcustom_{message.from_user.id}"),
        ],
    ])
    await bot.send_photo(
        ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=(
            f"💳 💰 YANGI CHEK!\n"
            f"👤 {message.from_user.full_name} (ID: {message.from_user.id})\n"
            f"🕐 Vaqt: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            "Qancha balans qo'shamiz?"
        ),
        reply_markup=kb,
    )


@dp.callback_query(F.data.startswith("add_"))
async def admin_add_balance(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
    parts = callback.data.split("_")
    user_id = parts[1]
    amount = int(parts[2])
    db = load_db()
    user = get_user(db, user_id)
    user["balance"] += amount
    user["history"].append({"type": "topup", "amount": amount, "time": str(datetime.now())})
    save_db(db)
    await callback.message.edit_caption(
        caption=callback.message.caption + f"\n\n✅ {amount:,} so'm qo'shildi."
    )
    await bot.send_message(
        int(user_id),
        f"✅ Hisobingizga <b>{amount:,} so'm</b> qo'shildi!\n"
        f"💰 Joriy balans: <b>{user['balance']:,} so'm</b>",
        parse_mode="HTML",
    )
    await callback.answer("✅ Balans qo'shildi")


@dp.callback_query(F.data.startswith("addcustom_"))
async def admin_custom_amount_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
    user_id = callback.data.replace("addcustom_", "")
    await state.update_data(target_user_id=user_id)
    await state.set_state(AdminCustomAmount.waiting_amount)
    await callback.message.answer(f"✍️ {user_id} uchun qo'shilayotgan summani kiriting:")
    await callback.answer()


@dp.message(AdminCustomAmount.waiting_amount)
async def admin_custom_amount_finish(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    user_id = data.get("target_user_id")
    try:
        amount = int(message.text.replace(" ", "").replace(",", ""))
    except ValueError:
        await message.answer("❌ Noto'g'ri format. Faqat raqam kiriting.")
        return
    await state.clear()
    db = load_db()
    user = get_user(db, user_id)
    user["balance"] += amount
    user["history"].append({"type": "topup", "amount": amount, "time": str(datetime.now())})
    save_db(db)
    await message.answer(f"✅ {user_id} ga {amount:,} so'm qo'shildi.")
    await bot.send_message(
        int(user_id),
        f"✅ Hisobingizga <b>{amount:,} so'm</b> qo'shildi!\n"
        f"💰 Joriy balans: <b>{user['balance']:,} so'm</b>",
        parse_mode="HTML",
    )


# ---------- 2-BO'LIM: Tayor Telegram Akkauntlar ----------
@dp.callback_query(F.data == "ready_accounts")
async def ready_accounts_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "📱 📱 TAYOR TELEGRAM AKKAUNTLAR 📱 📱\n\n"
        "💎 Tanlang:",
        reply_markup=create_items_menu(READY_ACCOUNTS, "ready")
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("ready_"))
async def buy_ready_account(callback: CallbackQuery):
    account = callback.data[6:]
    price = READY_ACCOUNTS.get(account)

    if price is None:
        await callback.answer("❌ Akkaunt topilmadi", show_alert=True)
        return

    db = load_db()
    user = get_user(db, callback.from_user.id)

    if user["balance"] < price:
        await callback.answer(
            f"❌ Balansingiz yetarli emas!\nKerak: {price:,} so'm\nMavjud: {user['balance']:,} so'm",
            show_alert=True,
        )
        return

    user["balance"] -= price
    user["history"].append({"type": "ready_account", "account": account, "amount": price, "time": str(datetime.now())})
    save_db(db)

    await callback.message.edit_text(
        f"✅ Buyurtma qabul qilindi!\n{account}\n"
        f"💵 {price:,} so'm\n\n"
        f"💰 Qolgan balansingiz: {user['balance']:,} so'm\n\n"
        "📩 Admin tez orada akkauntni @alphauzff ga yuboradi!",
        reply_markup=main_menu(),
    )
    await bot.send_message(
        ADMIN_ID,
        f"📱 YANGI AKKAUNT BUYURTMASI!\n"
        f"👤 {callback.from_user.full_name} (ID: {callback.from_user.id})\n"
        f"📱 {account}\n"
        f"💵 {price:,} so'm\n\n"
        f"Akkauntni yuboring: @{ADMIN_USERNAME}",
    )
    await callback.answer()


# ---------- 3-BO'LIM: Virtual Nomerlar ----------
@dp.callback_query(F.data == "virtual_numbers")
async def virtual_numbers_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "🔢 🔢 VIRTUAL NOMERLAR 🔢 🔢\n\n"
        "🌍 10 ta davlatdan tanlang:",
        reply_markup=create_items_menu(VIRTUAL_NUMBERS, "vnum")
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("vnum_"))
async def buy_virtual_number(callback: CallbackQuery):
    country = callback.data[5:]
    price = VIRTUAL_NUMBERS.get(country)

    if price is None:
        await callback.answer("❌ Davlat topilmadi", show_alert=True)
        return

    db = load_db()
    user = get_user(db, callback.from_user.id)

    if user["balance"] < price:
        await callback.answer(
            f"❌ Balansingiz yetarli emas!\nKerak: {price:,} so'm\nMavjud: {user['balance']:,} so'm",
            show_alert=True,
        )
        return

    user["balance"] -= price
    user["history"].append({"type": "virtual_number", "country": country, "amount": price, "time": str(datetime.now())})
    save_db(db)

    await callback.message.edit_text(
        f"✅ Buyurtma qabul qilindi!\n{country}\n"
        f"💵 {price:,} so'm\n\n"
        f"💰 Qolgan balansingiz: {user['balance']:,} so'm\n\n"
        "Admin tez orada nomerni sizga yuboradi. ⏳",
        reply_markup=main_menu(),
    )
    await bot.send_message(
        ADMIN_ID,
        f"🔢 YANGI VIRTUAL NOMER BUYURTMASI!\n"
        f"👤 {callback.from_user.full_name} (ID: {callback.from_user.id})\n"
        f"🌍 {country}\n"
        f"💵 {price:,} so'm",
    )
    await callback.answer()


# ---------- 4-BO'LIM: Premium Telegram Nomerlar ----------
@dp.callback_query(F.data == "premium_numbers")
async def premium_numbers_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "👑 👑 PREMIUM TELEGRAM NOMERLAR 👑 👑\n\n"
        "✨ 5 ta davlatdan tanlang:\n"
        "🎁 100% Premium tarifi bor!\n"
        "🔓 Barcha stikerlari va funksiyalari ochiq!",
        reply_markup=create_items_menu(PREMIUM_NUMBERS, "pnum")
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("pnum_"))
async def buy_premium_number(callback: CallbackQuery):
    country = callback.data[5:]
    price = PREMIUM_NUMBERS.get(country)

    if price is None:
        await callback.answer("❌ Davlat topilmadi", show_alert=True)
        return

    db = load_db()
    user = get_user(db, callback.from_user.id)

    if user["balance"] < price:
        await callback.answer(
            f"❌ Balansingiz yetarli emas!\nKerak: {price:,} so'm\nMavjud: {user['balance']:,} so'm",
            show_alert=True,
        )
        return

    user["balance"] -= price
    user["history"].append({"type": "premium_number", "country": country, "amount": price, "time": str(datetime.now())})
    save_db(db)

    await callback.message.edit_text(
        f"✅ Buyurtma qabul qilindi!\n{country}\n"
        f"💵 {price:,} so'm\n"
        f"✨ Premium tarifi bilan!\n\n"
        f"💰 Qolgan balansingiz: {user['balance']:,} so'm\n\n"
        "Admin tez orada nomerni sizga yuboradi. ⏳",
        reply_markup=main_menu(),
    )
    await bot.send_message(
        ADMIN_ID,
        f"👑 YANGI PREMIUM NOMER BUYURTMASI!\n"
        f"👤 {callback.from_user.full_name} (ID: {callback.from_user.id})\n"
        f"🌍 {country}\n"
        f"💵 {price:,} so'm\n"
        f"✨ Premium tarifi bilan",
    )
    await callback.answer()


# ---------- 5-BO'LIM: YouTube/Google Nomerlar ----------
@dp.callback_query(F.data == "youtube_numbers")
async def youtube_numbers_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎬 🎬 YOUTUBE/GOOGLE NOMERLAR 🎬 🎬\n\n"
        "🔐 YouTube Live va Google tastiqlash uchun\n"
        "🔒 Anonim nomerlar",
        reply_markup=create_items_menu(YOUTUBE_NUMBERS, "ynum")
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("ynum_"))
async def buy_youtube_number(callback: CallbackQuery):
    number_type = callback.data[5:]
    price = YOUTUBE_NUMBERS.get(number_type)

    if price is None:
        await callback.answer("❌ Nomer topilmadi", show_alert=True)
        return

    db = load_db()
    user = get_user(db, callback.from_user.id)

    if user["balance"] < price:
        await callback.answer(
            f"❌ Balansingiz yetarli emas!\nKerak: {price:,} so'm\nMavjud: {user['balance']:,} so'm",
            show_alert=True,
        )
        return

    user["balance"] -= price
    user["history"].append({"type": "youtube_number", "number_type": number_type, "amount": price, "time": str(datetime.now())})
    save_db(db)

    await callback.message.edit_text(
        f"✅ Buyurtma qabul qilindi!\n{number_type}\n"
        f"💵 {price:,} so'm\n\n"
        f"💰 Qolgan balansingiz: {user['balance']:,} so'm\n\n"
        "Admin tez orada nomerni sizga yuboradi. ⏳",
        reply_markup=main_menu(),
    )
    await bot.send_message(
        ADMIN_ID,
        f"🎬 YANGI YOUTUBE/GOOGLE NOMER BUYURTMASI!\n"
        f"👤 {callback.from_user.full_name} (ID: {callback.from_user.id})\n"
        f"🎬 {number_type}\n"
        f"💵 {price:,} so'm",
    )
    await callback.answer()


# ---------- Admin yordam ----------
@dp.callback_query(F.data == "admin_help")
async def admin_help_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminHelp.waiting_message)
    await callback.message.edit_text(
        "🆘 🆘 ADMIN YORDAM 🆘 🆘\n\n"
        "✍️ Muammoingizni yozing, admin tez orada javob beradi:",
        reply_markup=back_button(),
    )
    await callback.answer()


@dp.message(AdminHelp.waiting_message)
async def forward_to_admin(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("✅ Xabaringiz adminga yuborildi.", reply_markup=main_menu())
    await bot.send_message(
        ADMIN_ID,
        f"🆘 YANGI YORDAM SO'ROVI!\n"
        f"👤 {message.from_user.full_name} (ID: {message.from_user.id})\n"
        f"📝 Xabar: {message.text}",
    )


@dp.message(F.text.startswith("/reply_"))
async def admin_reply(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = message.text.split(" ", 1)
        user_id = int(parts[0].replace("/reply_", ""))
        text = parts[1]
        await bot.send_message(user_id, f"📩 <b>Admindan javob:</b>\n\n{text}", parse_mode="HTML")
        await message.answer("✅ Javob yuborildi.")
    except (IndexError, ValueError):
        await message.answer("❌ Format: /reply_USERID javob matni")


@dp.message(F.text.startswith("/balance_"))
async def admin_check_balance(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        user_id = message.text.replace("/balance_", "").strip()
        db = load_db()
        user = get_user(db, user_id)
        await message.answer(f"👤 ID: {user_id}\n💰 Balans: {user['balance']:,} so'm\n📊 Tarixi: {len(user['history'])} ta operatsiya")
    except Exception:
        await message.answer("❌ Foydalanuvchi topilmadi.")


# ---------- Flask veb-server ----------
app = Flask(__name__)


@app.route("/")
def home():
    return "✅ Bot ishlayapti 24/7"


def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


async def main():
    print("✅ Bot ishga tushdi — 24/7 rejimda...")
    print(f"📢 Majburiy kanal: @{REQUIRED_CHANNEL}")
    print(f"👤 Admin: {ADMIN_ID}")
    threading.Thread(target=run_flask, daemon=True).start()
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
