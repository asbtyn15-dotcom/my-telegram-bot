import os
import random
import time

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

users = {}

QUESTIONS = [
    ("ما عاصمة العراق؟", "بغداد", 100),
    ("كم يوم في الأسبوع؟", "7", 100),
    ("ما الكوكب المعروف بالكوكب الأحمر؟", "المريخ", 150),
    ("كم شهر في السنة؟", "12", 100),
    ("ما أكبر محيط في العالم؟", "الهادئ", 200),
]

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "money": 0,
            "points": 0,
            "question": None,
            "last_gift": 0,
            "last_salary": 0,
        }
    return users[user_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_user(update.effective_user.id)

    await update.message.reply_text(
        "🎮 أهلاً بك في اللعبة!\n\n"
        "💵 /رصيدي\n"
        "❓ /سؤال\n"
        "🎁 /هدية\n"
        "💼 /راتب\n"
        "📈 /استثمار"
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    await update.message.reply_text(
        f"💵 الدولار: {user['money']}$\n"
        f"⭐ النقاط: {user['points']}"
    )

async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    q, answer, reward = random.choice(QUESTIONS)

    user["question"] = {
        "answer": answer.lower(),
        "reward": reward
    }

    await update.message.reply_text(
        f"❓ السؤال:\n{q}\n\n"
        f"💰 الجائزة: {reward}$\n"
        "اكتب جوابك."
    )

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    if not user["question"]:
        return

    text = update.message.text.strip().lower()

    if text == user["question"]["answer"]:
        reward = user["question"]["reward"]
        user["money"] += reward
        user["points"] += 1
        user["question"] = None

        await update.message.reply_text(
            f"✅ صحيح!\n"
            f"💵 +{reward}$\n"
            f"⭐ +1 نقطة"
        )
    else:
        await update.message.reply_text("❌ جواب خطأ!")

async def gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    now = time.time()

    if now - user["last_gift"] < 86400:
        await update.message.reply_text("🎁 أخذت هديتك اليوم بالفعل!")
        return

    user["money"] += 1000
    user["last_gift"] = now

    await update.message.reply_text("🎁 هديتك: +1000$")

async def salary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    now = time.time()

    if now - user["last_salary"] < 3600:
        await update.message.reply_text("💼 الراتب لم يحن موعده بعد!")
        return

    user["money"] += 1000
    user["last_salary"] = now

    await update.message.reply_text("💼 نزل راتبك: +1000$")

async def invest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    if user["money"] <= 0:
        await update.message.reply_text("📉 ما عندك فلوس للاستثمار.")
        return

    percent = random.randint(-20, 30)
    change = int(user["money"] * percent / 100)
    user["money"] += change

    if change >= 0:
        await update.message.reply_text(
            f"📈 استثمار ناجح!\n"
            f"💵 الربح: +{change}$"
        )
    else:
        await update.message.reply_text(
            f"📉 الاستثمار خسر!\n"
            f"💵 الخسارة: {abs(change)}$"
        )

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN غير موجود")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("رصيدي", balance))
    app.add_handler(CommandHandler("سؤال", question))
    app.add_handler(CommandHandler("هدية", gift))
    app.add_handler(CommandHandler("راتب", salary))
    app.add_handler(CommandHandler("استثمار", invest))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, answer)
    )

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
