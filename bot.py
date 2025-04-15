import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os

# Токен бота и ID администратора
TOKEN = os.getenv("TELEGRAM_TOKEN", "7218177880:AAFUJtHajmMhSDTpHjrsVD8-tcejC3oZgkM")
ADMIN_CHAT_ID = "982825858"  # ID чата администратора

# Команда /start
def start(update, context):
    keyboard = [[telegram.KeyboardButton("🎣 Хищная рыба")],
                [telegram.KeyboardButton("🎣 Мирная рыба")]]
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text("Привет! Это бот для покупки рыболовных товаров. Выбери категорию:", reply_markup=reply_markup)

# Обработка сообщений и кнопок
def handle_message(update, context):
    text = update.message.text
    if text == "🎣 Хищная рыба":
        keyboard = [[telegram.KeyboardButton("🐟 Судак")],
                    [telegram.KeyboardButton("🐟 Щука")],
                    [telegram.KeyboardButton("🐟 Окунь")],
                    [telegram.KeyboardButton("⬅️ Назад")]]
        reply_markup = telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text("🐟 Выберите рыбу:", reply_markup=reply_markup)
    elif text == "🎣 Мирная рыба":
        keyboard = [[telegram.KeyboardButton("🐟 Карась")],
                    [telegram.KeyboardButton("🐟 Карп")],
                    [telegram.KeyboardButton("⬅️ Назад")]]
        reply_markup = telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text("🐟 Выберите рыбу:", reply_markup=reply_markup)
    elif text == "⬅️ Назад":
        keyboard = [[telegram.KeyboardButton("🎣 Хищная рыба")],
                    [telegram.KeyboardButton("🎣 Мирная рыба")]]
        reply_markup = telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text("Выбери категорию:", reply_markup=reply_markup)
    elif text in ["🐟 Судак", "🐟 Щука", "🐟 Окунь", "🐟 Карась", "🐟 Карп"]:
        order_data = {
            "client": update.message.from_user.first_name,
            "item": text,
            "quantity": 1  # Количество пока фиксированное
        }
        notify_admin(context, order_data)
        update.message.reply_text(f"Заказ на {text} оформлен! Спасибо!")

# Уведомление администратора
def notify_admin(context, order_data):
    message = f"Новый заказ!\nКлиент: {order_data['client']}\nТовар: {order_data['item']}\nКоличество: {order_data['quantity']}"
    context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message)

# Основная функция
def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Настройка вебхука
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-render-app.onrender.com/")
    PORT = int(os.environ.get("PORT", 5000))
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN,
                          webhook_url=WEBHOOK_URL + TOKEN)
    updater.idle()

if __name__ == "__main__":
    main()
