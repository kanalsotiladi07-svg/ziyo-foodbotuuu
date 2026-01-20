import os
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("8346475214:AAF61SD2ElIb97ceq4IxO34mfxYaiGEoR5c")
ADMIN_ID = int(os.getenv("7827164632"))

MENU = {
    "🍔 Burger": 30000,
    "🌯 Lavash": 33000,
    "🌭 Hot-dog": 20000,
    "🍗 Tovuq": 45000,
    "🥤 Cola": 10000
}

users = {}
orders = {}
order_id = 1
total_money = 0


def user_menu():
    return ReplyKeyboardMarkup(
        [["🍽 Buyurtma berish"], ["📞 Qo‘llab-quvvatlash"]],
        resize_keyboard=True
    )


def food_menu():
    kb = [[k] for k in MENU]
    kb.append(["✅ Tugatish"])
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid == ADMIN_ID:
        await update.message.reply_text("👮 Admin panel", reply_markup=user_menu())
    else:
        await update.message.reply_text("🍔 Ziyo Food botiga xush kelibsiz!", reply_markup=user_menu())


# ---------- USER FLOW ----------
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global order_id
    uid = update.effective_user.id
    text = update.message.text

    if text == "🍽 Buyurtma berish":
        users[uid] = {"items": [], "sum": 0}
        await update.message.reply_text("🍽 Menyudan tanlang:", reply_markup=food_menu())
        return

    if text in MENU:
        users[uid]["items"].append(text)
        users[uid]["sum"] += MENU[text]
        await update.message.reply_text(
            f"➕ {text} qo‘shildi\n💰 Jami: {users[uid]['sum']} so‘m"
        )
        return

    if text == "✅ Tugatish":
        await update.message.reply_text(
            "📍 Lokatsiyani yuboring:",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("📍 Lokatsiya yuborish", request_location=True)]],
                resize_keyboard=True
            )
        )
        return

    if text == "📞 Qo‘llab-quvvatlash":
        await update.message.reply_text("☎️ Admin bilan bog‘laning")
        return


async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global order_id, total_money
    uid = update.effective_user.id
    loc = update.message.location

    orders[order_id] = {
        "user": uid,
        "items": users[uid]["items"],
        "sum": users[uid]["sum"],
        "lat": loc.latitude,
        "lon": loc.longitude,
        "status": "Qabul qilindi"
    }

    total_money += users[uid]["sum"]

    kb = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🟡 Tayyorlanmoqda", callback_data=f"prep_{order_id}"),
                InlineKeyboardButton("🚚 Yo‘lda", callback_data=f"way_{order_id}")
            ],
            [
                InlineKeyboardButton("✅ Yetkazildi", callback_data=f"done_{order_id}")
            ],
            [
                InlineKeyboardButton("📍 Xarita", url=f"https://maps.google.com/?q={loc.latitude},{loc.longitude}")
            ]
        ]
    )

    msg = (
        f"🆕 BUYURTMA #{order_id}\n\n"
        f"🍽 {', '.join(users[uid]['items'])}\n"
        f"💰 {users[uid]['sum']} so‘m\n"
        f"📍 Lokatsiya yuborildi"
    )

    await context.bot.send_message(ADMIN_ID, msg, reply_markup=kb)
    await update.message.reply_text("✅ Buyurtma qabul qilindi!", reply_markup=user_menu())

    order_id += 1


# ---------- ADMIN CALLBACK ----------
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action, oid = query.data.split("_")
    oid = int(oid)

    if oid not in orders:
        return

    if action == "prep":
        orders[oid]["status"] = "Tayyorlanmoqda"
    elif action == "way":
        orders[oid]["status"] = "Yo‘lda"
    elif action == "done":
        orders[oid]["status"] = "Yetkazildi"

    await context.bot.send_message(
        orders[oid]["user"],
        f"📦 Buyurtma #{oid}\nHolati: {orders[oid]['status']}"
    )


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_text))
    app.add_handler(MessageHandler(filters.LOCATION, location_handler))
    app.add_handler(CallbackQueryHandler(callback_handler))

    app.run_polling()


if __name__ == "__main__":
    main()
