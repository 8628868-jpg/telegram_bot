import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import json
import os

# Токен бота (замените на свой)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8825711808:AAHnjAstjONhPG6VPo1M2bs7OJppCoRKtfg")

# Файл для хранения chat_id
CHAT_IDS_FILE = "chat_ids.json"

# Загрузка сохранённых chat_id
def load_chat_ids():
    if os.path.exists(CHAT_IDS_FILE):
        with open(CHAT_IDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Сохранение chat_id
def save_chat_ids(chat_ids):
    with open(CHAT_IDS_FILE, "w", encoding="utf-8") as f:
        json.dump(chat_ids, f, ensure_ascii=False, indent=2)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    username = update.effective_user.username or "без username"
    
    # Сохраняем chat_id
    chat_ids = load_chat_ids()
    chat_ids[str(chat_id)] = {
        "username": username,
        "first_name": update.effective_user.first_name,
        "last_name": update.effective_user.last_name,
        "added_at": str(update.effective_message.date)
    }
    save_chat_ids(chat_ids)
    
    await update.message.reply_text(
        f"✅ Привет! Я сохранил твой chat_id: `{chat_id}`\n\n"
        f"Теперь я могу отправлять тебе сообщения.\n\n"
        f"Напиши `/send <текст>` чтобы отправить сообщение всем сохранённым пользователям."
    )

# Команда /send
async def send_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Укажите текст сообщения: `/send Привет всем!`")
        return
    
    text = " ".join(context.args)
    chat_ids = load_chat_ids()
    
    if not chat_ids:
        await update.message.reply_text("❌ Нет сохранённых пользователей.")
        return
    
    count = 0
    for chat_id in chat_ids.keys():
        try:
            await context.bot.send_message(chat_id=chat_id, text=text)
            count += 1
        except Exception as e:
            logging.error(f"Ошибка отправки {chat_id}: {e}")
    
    await update.message.reply_text(f"✅ Сообщения отправлены {count} пользователям.")

# Обработка обычных сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    chat_ids = load_chat_ids()
    
    if str(chat_id) in chat_ids:
        await update.message.reply_text(
            f"✅ Ты уже сохранён в базе. Твой chat_id: `{chat_id}`\n\n"
            f"Доступные команды:\n"
            f"`/start` — сохранить chat_id\n"
            f"`/send <текст>` — отправить сообщение всем"
        )

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Создание приложения
app = Application.builder().token(TOKEN).build()

# Добавление обработчиков
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("send", send_all))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Запуск бота
if __name__ == "__main__":
    print("🤖 Бот запущен...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
