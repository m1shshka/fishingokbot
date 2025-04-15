import telegram
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

# Токен бота и другие настройки
TOKEN = os.getenv("TELEGRAM_TOKEN", "7218177880:AAFUJtHajmMhSDTpHjrsVD8-tcejC3oZgkM")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # ID чата администратора
WEBHOOK_URL = "https://your-render-app.onrender.com/"  # Замени на URL от Render после создания

# Настройка Google Таблиц
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("Snasti").sheet1  # Укажи точное название своей таблицы, например "Snasti"

# Функция для сохранения заказа в таблицу
def save_order(order_data):
    sheet.append_row([order_data["client"], order_data["item"], order_data["quantity"]])

# Функция для уведомления администратора
def notify_admin(update, context, order_data):
    message = f"Новый заказ!\nКлиент: {order_data['client']}\nТовар: {order_data['item']}\nКоличество: {order_data['quantity']}"
    context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message)

# Команда /start
def start(update, context):
    keyboard = [[telegram.KeyboardButton("?? Хищная рыба")],
                [telegram.KeyboardButton("?? Мирная рыба")]]
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text("Привет! Это бот для покупки рыболовных товаров. Выбери категорию:", reply_markup=reply_markup)

# Обработка кнопок
def handle_message(update, context):
    text = update.message.text
    if text == "?? Хищная рыба":
        keyboard = [[telegram.KeyboardButton("?? Судак")],
                    [telegram.KeyboardButton("?? Щука")],
                    [telegram.KeyboardButton("?? Окунь")],
                    [telegram.KeyboardButton("?? Назад")]]
        reply_markup = telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text("?? Выберите рыбу:", reply_markup=reply_markup)
    elif text == "?? Мирная рыба":
        keyboard = [[telegram.KeyboardButton("?? Карась")],
                    [telegram.KeyboardButton("?? Карп")],
                    [telegram.KeyboardButton("?? Назад")]]
        reply_markup = telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text("?? Выберите рыбу:", reply_markup=reply_markup)
    elif text == "?? Назад":
        keyboard = [[telegram.KeyboardButton("?? Хищная рыба")],
                    [telegram.KeyboardButton("?? Мирная рыба")]]
        reply_markup = telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text("Выбери категорию:", reply_markup=reply_markup)
    elif text in ["?? Судак", "?? Щука", "?? Окунь", "?? Карась", "?? Карп"]:
        order_data = {
            "client": update.message.from_user.first_name,
            "item": text,
            "quantity": 1  # Можно добавить выбор количества
        }
        save_order(order_data)
        notify_admin(update, context, order_data)
        update.message.reply_text(f"Заказ на {text} оформлен! Спасибо!")

# Основная функция
def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Настройка вебхука
    PORT = int(os.environ.get("PORT", 5000))
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN,
                          webhook_url=WEBHOOK_URL + TOKEN)
    updater.idle()

if __name__ == "__main__":
    main()