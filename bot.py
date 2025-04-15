import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
import re

# Токен бота
TOKEN = os.getenv("TELEGRAM_TOKEN", "7218177880:AAFUJtHajmMhSDTpHjrsVD8-tcejC3oZgkM")
ADMIN_CHAT_ID = "982825858"  # ID чата администратора
CONSULTANT_CONTACTS = "TG: @pjvjcx\n📞 Телефон: 8 950 792-01-70"

# Структура данных товаров
fish_data = {
    "predatory": {
        "🐟 Судак": {
            "products": {
                "🎣 Спиннинг": { 
                    "price": 500, 
                    "deposit": 3000,
                    "description": "🎣 Спиннинг для ловли судака\n💸 Цена: 500 руб./день\n🔒 Залог: 3000 руб."
                },
                "🎣 Воблеры": {
                    "price": 200,
                    "deposit": 1500,
                    "description": "🎣 Набор воблеров\n💸 Цена: 200 руб./день\n🔒 Залог: 1500 руб."
                }
            },
            "backMenu": "predatory"
        },
        "🐟 Щука": {
            "products": {
                "🎣 Спиннинг": {
                    "price": 600,
                    "deposit": 3500,
                    "description": "🎣 Спиннинг для ловли щуки\n💸 Цена: 600 руб./день\n🔒 Залог: 3500 руб."
                },
                "🎣 Блесны": {
                    "price": 250,
                    "deposit": 1200,
                    "description": "🎣 Набор блесен\n💸 Цена: 250 руб./день\n🔒 Залог: 1200 руб."
                }
            },
            "backMenu": "predatory"
        },
        "🐟 Окунь": {
            "products": {
                "🎣 Ультралайт": {
                    "price": 400,
                    "deposit": 2500,
                    "description": "🎣 Ультралайт спиннинг\n💸 Цена: 400 руб./день\n🔒 Залог: 2500 руб."
                },
                "🎣 Микроколебалки": {
                    "price": 150,
                    "deposit": 800,
                    "description": "🎣 Набор микроколебалок\n💸 Цена: 150 руб./день\n🔒 Залог: 800 руб."
                }
            },
            "backMenu": "predatory"
        }
    },
    "peaceful": {
        "🐟 Карась": {
            "products": {
                "🎣 Поплавочная удочка": {
                    "price": 300,
                    "deposit": 1500,
                    "description": "🎣 Поплавочная удочка\n💸 Цена: 300 руб./день\n🔒 Залог: 1500 руб."
                },
                "🎣 Наживка": {
                    "price": 50,
                    "deposit": 0,
                    "description": "🎣 Наживка (опарыш)\n💸 Цена: 50 руб./упаковка"
                }
            },
            "backMenu": "peaceful"
        },
        "🐟 Карп": {
            "products": {
                "🎣 Донная снасть": {
                    "price": 700,
                    "deposit": 5000,
                    "description": "🎣 Донная снасть\n💸 Цена: 700 руб./день\n🔒 Залог: 5000 руб."
                },
                "🎣 Бойлы": {
                    "price": 200,
                    "deposit": 0,
                    "description": "🎣 Бойлы для карпа\n💸 Цена: 200 руб./пакет"
                }
            },
            "backMenu": "peaceful"
        }
    },
    "additional": {
        "🛠️ Дополнительное оборудование": {
            "products": {
                "🛠️ Подставки": {
                    "price": 50,
                    "deposit": 150,
                    "description": "🛠️ Подставки под удочки\n💸 Цена: 50 руб./шт\n🔒 Залог: 150 руб."
                },
                "🛠️ Стул": {
                    "price": 300,
                    "deposit": 1500,
                    "description": "🛠️ Раскладной стул\n💸 Цена: 300 руб./день\n🔒 Залог: 1500 руб."
                },
                "🛠️ Лодка": {
                    "price": 500,
                    "deposit": 25000,
                    "description": "🛠️ Надувная лодка\n💸 Цена: 500 руб./день\n🔒 Залог: 25000 руб."
                }
            },
            "backMenu": "main"
        }
    }
}

# Меню
menus = {
    "main": {
        "reply_markup": telegram.ReplyKeyboardMarkup([
            ["🎣 Хищная рыба", "🎣 Мирная рыба"],
            ["📋 Общий каталог", "❓ Впервые на рыбалке"],
            ["📞 Контакты"]
        ], resize_keyboard=True)
    },
    "predatory": {
        "reply_markup": telegram.ReplyKeyboardMarkup([
            ["🐟 Судак", "🐟 Щука", "🐟 Окунь"],
            ["⬅️ Назад"]
        ], resize_keyboard=True)
    },
    "peaceful": {
        "reply_markup": telegram.ReplyKeyboardMarkup([
            ["🐟 Карась", "🐟 Карп"],
            ["⬅️ Назад"]
        ], resize_keyboard=True)
    }
}

# Состояние пользователей
user_state = {}

# Парсер заказов
def parse_order(text, selected_product):
    patterns = {
        "name": r"(?:имя|name)[:\-\s]*(.+)",
        "phone": r"(?:тел|phone|телефон)[:\-\s]*(.+)",
        "address": r"(?:адрес|address)[:\-\s]*(.+)",
        "quantity": r"(?:количество|кол-во|quantity)[:\-\s]*(\d+)"
    }

    lines = text.split("\n")
    result = {}
    errors = []

    # Извлечение данных по регулярным выражениям
    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        result[field] = match.group(1).strip() if match else None

    # Простой разбор, если регулярки не сработали
    if not result["name"] and len(lines) > 0:
        result["name"] = lines[0].strip()
    if not result["phone"] and len(lines) > 1:
        result["phone"] = lines[1].strip()
    if not result["address"] and len(lines) > 2:
        result["address"] = lines[2].strip()
    if not result["quantity"] and len(lines) > 3:
        result["quantity"] = lines[3].strip()

    # Проверка обязательных полей
    if not result["name"]:
        errors.append("Имя")
    if not result["phone"]:
        errors.append("Телефон")
    if not result["address"]:
        errors.append("Адрес")

    # Нормализация телефона
    if result["phone"]:
        result["phone"] = re.sub(r"[^\d+]", "", result["phone"])
        if not re.match(r"^\+?\d{10,15}$", result["phone"]):
            errors.append("Некорректный телефон")

    if errors:
        error_message = "🚫 Не заполнены или некорректны поля:\n" + "\n".join(errors)
        raise ValueError(error_message)

    return {
        "name": result["name"],
        "phone": result["phone"],
        "address": result["address"],
        "product": selected_product,
        "quantity": int(result["quantity"]) if result["quantity"] else 1
    }

# Уведомление администратора
def notify_admin(context, order_data, username):
    username_text = f"@{username}" if username else "не указан"
    message = (
        f"📬 Новый заказ!\n\n"
        f"👤 Имя: {order_data['name']}\n"
        f"📞 Телефон: {order_data['phone']}\n"
        f"🏠 Адрес: {order_data['address']}\n"
        f"🎣 Товар: {order_data['product']}\n"
        f"🔢 Количество: {order_data['quantity']}\n"
        f"🆔 Telegram: {username_text}"
    )
    print(f"Sending message to admin (ID: {ADMIN_CHAT_ID}): {message}")  # Отладка
    context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message)
    print("Message sent to admin.")  # Отладка

# Обработчики команд
def start(update, context):
    chat_id = update.message.chat.id
    user_state[chat_id] = {}
    welcome_text = f"Приветствую, {update.message.from_user.first_name}! 🎣\nЯ помогу подобрать снасти для рыбалки.\n\nВыберите интересующий раздел:"
    update.message.reply_text(welcome_text, reply_markup=menus["main"]["reply_markup"])

def handle_menu_navigation(chat_id, menu_type, context):
    user_state[chat_id] = {"currentMenu": menu_type}
    context.bot.send_message(chat_id=chat_id, text="🐟 Выберите рыбу:", reply_markup=menus[menu_type]["reply_markup"])

def handle_back_navigation(update, context):
    chat_id = update.message.chat.id
    state = user_state.get(chat_id, {})
    
    if "currentFish" in state:
        category = state["currentCategory"]
        context.bot.send_message(chat_id=chat_id, text="🐟 Выберите рыбу:", reply_markup=menus[category]["reply_markup"])
        del state["currentFish"]
        del state["currentCategory"]
    else:
        context.bot.send_message(chat_id=chat_id, text="🏠 Главное меню:", reply_markup=menus["main"]["reply_markup"])
    if chat_id in user_state:
        del user_state[chat_id]

def show_products(chat_id, category, fish, context):
    fish_key = f"🐟 {fish}"
    fish_data_category = fish_data[category]
    if fish_key not in fish_data_category:
        context.bot.send_message(chat_id=chat_id, text="🚫 Рыба не найдена.", reply_markup=menus["main"]["reply_markup"])
        return
    products = fish_data_category[fish_key]["products"]
    product_list = "\n\n".join(product["description"] for product in products.values())
    
    keyboard = telegram.ReplyKeyboardMarkup(
        [[product] for product in products.keys()] + [["⬅️ Назад"]],
        resize_keyboard=True
    )
    context.bot.send_message(
        chat_id=chat_id,
        text=f"🐟 Для {fish} доступны:\n\n{product_list}\n\nВыберите что желаете приобрести:",
        reply_markup=keyboard
    )

def handle_general_catalog(update, context):
    chat_id = update.message.chat.id
    all_products = []
    for category in ["predatory", "peaceful"]:
        for fish in fish_data[category].values():
            all_products.extend(fish["products"].values())
    for additional in fish_data["additional"]["🛠️ Дополнительное оборудование"]["products"].values():
        all_products.append(additional)

    product_list = "\n\n".join(product["description"] for product in all_products)
    
    keyboard = telegram.ReplyKeyboardMarkup(
        [[product] for category in ["predatory", "peaceful"] for fish in fish_data[category].values() for product in fish["products"].keys()] +
        [[product] for product in fish_data["additional"]["🛠️ Дополнительное оборудование"]["products"].keys()] +
        [["⬅️ Назад"]],
        resize_keyboard=True
    )
    context.bot.send_message(
        chat_id=chat_id,
        text=f"📋 Полный каталог снастей:\n\n{product_list}\n\nВыберите что желаете приобрести:",
        reply_markup=keyboard
    )
    user_state[chat_id] = {"inGeneralCatalog": True}

def handle_first_time(update, context):
    chat_id = update.message.chat.id
    text = f"❓ Если вы новичок:\n{CONSULTANT_CONTACTS}\n\nМы поможем с выбором снастей!"
    context.bot.send_message(chat_id=chat_id, text=text)

def handle_contacts(update, context):
    chat_id = update.message.chat.id
    context.bot.send_message(chat_id=chat_id, text=f"📞 Наши контакты:\n{CONSULTANT_CONTACTS}")

def request_order_details(chat_id, product_name, context):
    context.bot.send_message(
        chat_id=chat_id,
        text=(
            f"📝 Для оформления аренды {product_name} введите:\n\n"
            "👤 Имя:\n📞 Телефон:\n🏠 Адрес:\n🔢 Количество:\n\n"
            "Пример:\nИмя: Иван\nТелефон: +79123456789\nАдрес: Москва\nКоличество: 1"
        )
    )

# Обработка текстовых сообщений
def handle_message(update, context):
    chat_id = update.message.chat.id
    text = update.message.text
    state = user_state.get(chat_id, {})

    # Обработка меню
    if text == "🎣 Хищная рыба":
        handle_menu_navigation(chat_id, "predatory", context)
        return
    elif text == "🎣 Мирная рыба":
        handle_menu_navigation(chat_id, "peaceful", context)
        return
    elif text == "📋 Общий каталог":
        handle_general_catalog(update, context)
        return
    elif text == "❓ Впервые на рыбалке":
        handle_first_time(update, context)
        return
    elif text == "📞 Контакты":
        handle_contacts(update, context)
        return
    elif text == "⬅️ Назад":
        handle_back_navigation(update, context)
        return

    # Обработка выбора рыбы
    if text in ["🐟 Судак", "🐟 Щука", "🐟 Окунь", "🐟 Карась", "🐟 Карп"]:
        fish = text.replace("🐟 ", "")
        category = "predatory" if text in ["🐟 Судак", "🐟 Щука", "🐟 Окунь"] else "peaceful"
        user_state[chat_id] = {"currentFish": fish, "currentCategory": category}
        show_products(chat_id, category, fish, context)
        return

    # Обработка выбора товара
    products = [
        "🎣 Спиннинг", "🎣 Воблеры", "🎣 Блесны", "🎣 Ультралайт", "🎣 Микроколебалки",
        "🎣 Поплавочная удочка", "🎣 Наживка", "🎣 Донная снасть", "🎣 Бойлы",
        "🛠️ Подставки", "🛠️ Стул", "🛠️ Лодка"
    ]
    if text in products:
        clean_product_name = text.replace("🎣 ", "").replace("🛠️ ", "")
        if text in ["🛠️ Подставки", "🛠️ Стул", "🛠️ Лодка"]:
            user_state[chat_id] = {"selectedProduct": text}
        else:
            user_state[chat_id]["selectedProduct"] = text
        request_order_details(chat_id, clean_product_name, context)
        return

    # Обработка данных заказа
    if "selectedProduct" in state:
        try:
            clean_product_name = state["selectedProduct"].replace("🎣 ", "").replace("🛠️ ", "")
            print(f"Parsing order for product: {clean_product_name}, text: {text}")  # Отладка
            order_data = parse_order(text, clean_product_name)
            print(f"Order parsed successfully: {order_data}")  # Отладка
            order_data["chat_id"] = chat_id
            order_data["username"] = update.message.from_user.username
            print("Notifying admin...")  # Отладка
            notify_admin(context, order_data, update.message.from_user.username)
            print("Sending confirmation to user...")  # Отладка
            context.bot.send_message(
                chat_id=chat_id,
                text=f"✅ Заказ принят!\n🎣 {order_data['product']}\n🔢 Количество: {order_data['quantity']}\n📞 С вами свяжется менеджер.",
                reply_markup=menus["main"]["reply_markup"]
            )
            print("Confirmation sent to user.")  # Отладка
            del user_state[chat_id]
        except ValueError as e:
            print(f"Error in order parsing: {e}")  # Отладка
            context.bot.send_message(chat_id=chat_id, text=str(e))

# Основная функция
# Основная функция
def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    # Регистрация обработчиков
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Настройка вебхука
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://fishingokbot.onrender.com/")
    PORT = int(os.environ.get("PORT", 10000))
    updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=WEBHOOK_URL + TOKEN
    )
    updater.idle()

if __name__ == "__main__":
    main()
