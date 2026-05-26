import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# 🔐 TOKEN desde Railway
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("❌ ERROR: BOT_TOKEN no configurado en variables de entorno")

# 📊 Kilatajes
KARATS = {
    "10K": 0.417,
    "14K": 0.583,
    "18K": 0.750,
    "22K": 0.916,
    "24K": 1.000
}

user_data_store = {}

# 💰 Precio oro
def get_gold_price():
    url = "https://api.gold-api.com/price/XAU"
    data = requests.get(url).json()
    ounce_price = data["price"]
    return ounce_price / 31.1035


# 🚀 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton("10K", callback_data="10K"),
            InlineKeyboardButton("14K", callback_data="14K"),
        ],
        [
            InlineKeyboardButton("18K", callback_data="18K"),
            InlineKeyboardButton("22K", callback_data="22K"),
        ],
        [
            InlineKeyboardButton("24K", callback_data="24K"),
        ]
    ]

    await update.message.reply_text(
        "💎 Selecciona el kilataje:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# 🎯 Selección de kilataje
async def karat_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_data_store[query.from_user.id] = {
        "karat": query.data
    }

    await query.message.reply_text(
        f"✅ Seleccionaste {query.data}\n\n"
        "Envía:\npeso ganancia\nEjemplo: 20 25"
    )


# 🧮 Cálculo
async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id

    if user_id not in user_data_store:
        await update.message.reply_text("👉 Usa /start primero")
        return

    try:
        weight, profit = map(float, update.message.text.split())

        karat = user_data_store[user_id]["karat"]
        purity = KARATS[karat]
        spot = get_gold_price()

        real_value = weight * spot * purity
        sell_price = real_value + (real_value * profit / 100)
        buy_price = real_value * 0.85

        await update.message.reply_text(
            f"""
📈 Oro 24K: ${spot:.2f}/g

💍 Kilataje: {karat}
⚖️ Peso: {weight} g

💰 Valor real: ${real_value:.2f}
🛒 Compra: ${buy_price:.2f}
🏷️ Venta: ${sell_price:.2f}
"""
        )

    except:
        await update.message.reply_text("❌ Usa formato: 20 25")


# 🧠 APP
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(karat_selected, pattern="^(10K|14K|18K|22K|24K)$"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calculate))

# ✅ ARRANQUE CORRECTO PARA RAILWAY
if __name__ == "__main__":
    print("✅ Bot activo")
    app.run_polling(drop_pending_updates=True)
