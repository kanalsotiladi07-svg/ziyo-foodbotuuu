import os
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================== SOZLAMALAR ==================
TOKEN = os.getenv("8346475214:AAF61SD2ElIb97ceq4IxO34mfxYaiGEoR5c")
ADMIN_ID = int(os.getenv("7827164632"))

# ================== MENU ==================
MENU = {
    "🌯 LAVASH": 33000,
    "🍔 NON BURGER": 35000,
    "🌭 XOT-DOG": 20000,
    "☕️ KOFE": 15000,
    "🥤 COCA COLA": 10000,
    "🥤 PEPSI": 10000,
    "🥤 FANTA": 10000,
    "🍗 TANDIR TOVUQ": 50000,
    "🍗 KEFSI": 40000
}

users = {}
orders = []

# ================== KLAVIATURALAR ==================
def main_menu():
    return ReplyKeyboardMarkup(
        [
            ["🛒 Ovqat zakaz qilish"],
            ["📦 Buyurtmalar", "📍 Manzil"],
            ["📊 Statistika", "☎️ Qo‘llab-quvvatlash"]
        ],
        resize_keyboard=True
    )

def food_menu():
    buttons = [[item] for item in MENU.keys()]
    buttons.append(["⬅️ Orqaga"])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# ================== /start ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users[user_id] = {}
    await update.message.reply_text(
        "👋 Assalomu alaykum!\nZiyo Food botiga xush kelibsiz 🍽",
        reply_markup=main_menu()
    )

# ================== XABARLAR ==================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in users:
        users[user_id] = {}

    # ---- OVQAT ZAKAZ ----
    if text == "🛒 Ovqat zakaz qilish":
        users[user_id]["cart"] = []
        await update.message.reply_text(
            "🍽 Ovqat tanlang:",
            reply_markup=food_menu()
        )
        return

    if text in MENU:
        users[user_id]["current"] = text
        await update.message.reply_text("Nechta olasiz? (son yozing)")
        return

    if text.isdigit() and "current" in users[user_id]:
        item = users[user_id]["current"]
        qty = int(text)
        users[user_id]["cart"].append((item, qty))
        del users[user_id]["current"]

        await update.message.reply_text(
            "✅ Qo‘shildi.\nYana tanlaysizmi yoki davom etamizmi?",
            reply_markup=ReplyKeyboardMarkup(
                [["➕ Yana tanlash", "➡️ Davom etish"]],
                resize_keyboard=True
            )
        )
        return

    if text == "➕ Yana tanlash":
        await update.message.reply_text("🍽 Tanlang:", reply_markup=food_menu())
        return

    if text == "➡️ Davom etish":
        await update.message.reply_text(
            "📞 Telefon raqamingizni yuboring:",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("📱 Raqamni yuborish", request_contact=True)]],
                resize_keyboard=True
            )
        )
        return

    # ---- ORQAGA ----
    if text == "⬅️ Orqaga":
        await update.message.reply_text("🏠 Bosh menyu", reply_markup=main_menu())
        return

    # ---- BUYURTMALAR ----
    if text == "📦 Buyurtmalar":
        if not orders:
            await update.message.reply_text("📦 Buyurtmalar yo‘q")
            return

        msg = "📦 Buyurtmalar:\n\n"
        for o in orders:
            msg += f"👤 {o['name']} | {o['phone']}\n"
            for i, q in o["items"]:
                msg += f"- {i} x{q}\n"
            msg += "— — — —\n"

        await update.message.reply_text(msg)
        return

    # ---- MANZIL ----
    if text == "📍 Manzil":
        await update.message.reply_text(
            "📍 Manzilingizni yuboring:",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("📍 Lokatsiyani yuborish", request_location=True)]],
                resize_keyboard=True
            )
        )
        return

    # ---- STATISTIKA (ADMIN) ----
    if text == "📊 Statistika":
        if user_id != ADMIN_ID:
            await update.message.reply_text("⛔️ Siz admin emassiz")
            return

        await update.message.reply_text(
            f"📊 Statistika:\n"
            f"👥 Foydalanuvchilar: {len(users)}\n"
            f"📦 Buyurtmalar: {len(orders)}"
        )
        return

    # ---- QO‘LLAB-QUVVATLASH ----
    if text == "☎️ Qo‘llab-quvvatlash":
        await update.message.reply_text(
            "☎️ Qo‘llab-quvvatlash:\nAdmin bilan bog‘laning:\n@admin"
        )
        return

# ================== CONTACT ==================
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    phone = update.message.contact.phone_number
    users[user_id]["phone"] = phone

    await update.message.reply_text(
        "📍 Endi lokatsiyani yuboring:",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📍 Lokatsiyani yuborish", request_location=True)]],
            resize_keyboard=True
        )
    )

# ================== LOCATION ==================
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    loc = update.message.location

    order = {
        "name": update.effective_user.full_name,
        "phone": users[user_id]["phone"],
        "items": users[user_id]["cart"],
        "lat": loc.latitude,
        "lon": loc.longitude
    }

    orders.append(order)

    # ADMIN GA YUBORAMIZ
    msg = "🆕 YANGI BUYURTMA\n"
    msg += f"👤 {order['name']}\n📞 {order['phone']}\n"
    for i, q in order["items"]:
        msg += f"- {i} x{q}\n"
    msg += f"📍 https://maps.google.com/?q={order['lat']},{order['lon']}"

    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)

    await update.message.reply_text(
        "✅ Buyurtma qabul qilindi!\nTez orada bog‘lanamiz 😊",
        reply_markup=main_menu()
    )

# ================== RUN ==================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
