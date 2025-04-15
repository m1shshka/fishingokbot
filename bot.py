import telegram
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

# ����� ���� � ������ ���������
TOKEN = os.getenv("TELEGRAM_TOKEN", "7218177880:AAFUJtHajmMhSDTpHjrsVD8-tcejC3oZgkM")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # ID ���� ��������������
WEBHOOK_URL = "https://your-render-app.onrender.com/"  # ������ �� URL �� Render ����� ��������

# ��������� Google ������
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("Snasti").sheet1  # ����� ������ �������� ����� �������, �������� "Snasti"

# ������� ��� ���������� ������ � �������
def save_order(order_data):
    sheet.append_row([order_data["client"], order_data["item"], order_data["quantity"]])

# ������� ��� ����������� ��������������
def notify_admin(update, context, order_data):
    message = f"����� �����!\n������: {order_data['client']}\n�����: {order_data['item']}\n����������: {order_data['quantity']}"
    context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message)

# ������� /start
def start(update, context):
    keyboard = [[telegram.KeyboardButton("?? ������ ����")],
                [telegram.KeyboardButton("?? ������ ����")]]
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text("������! ��� ��� ��� ������� ���������� �������. ������ ���������:", reply_markup=reply_markup)

# ��������� ������
def handle_message(update, context):
    text = update.message.text
    if text == "?? ������ ����":
        keyboard = [[telegram.KeyboardButton("?? �����")],
                    [telegram.KeyboardButton("?? ����")],
                    [telegram.KeyboardButton("?? �����")],
                    [telegram.KeyboardButton("?? �����")]]
        reply_markup = telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text("?? �������� ����:", reply_markup=reply_markup)
    elif text == "?? ������ ����":
        keyboard = [[telegram.KeyboardButton("?? ������")],
                    [telegram.KeyboardButton("?? ����")],
                    [telegram.KeyboardButton("?? �����")]]
        reply_markup = telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text("?? �������� ����:", reply_markup=reply_markup)
    elif text == "?? �����":
        keyboard = [[telegram.KeyboardButton("?? ������ ����")],
                    [telegram.KeyboardButton("?? ������ ����")]]
        reply_markup = telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text("������ ���������:", reply_markup=reply_markup)
    elif text in ["?? �����", "?? ����", "?? �����", "?? ������", "?? ����"]:
        order_data = {
            "client": update.message.from_user.first_name,
            "item": text,
            "quantity": 1  # ����� �������� ����� ����������
        }
        save_order(order_data)
        notify_admin(update, context, order_data)
        update.message.reply_text(f"����� �� {text} ��������! �������!")

# �������� �������
def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # ��������� �������
    PORT = int(os.environ.get("PORT", 5000))
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN,
                          webhook_url=WEBHOOK_URL + TOKEN)
    updater.idle()

if __name__ == "__main__":
    main()