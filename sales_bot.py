from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from datetime import datetime
from collections import Counter

# Ваш токен бота
TOKEN = '7070419971:AAEktomm75b0LAGqHvvZhrzbbxqv5PhdbmY'

# ID группы, куда будет отправляться отчет
REPORT_GROUP_ID = '-1002220981682'

# Инициализация словаря для хранения товаров и их цен
products = {
    "10 мл(160 грн)": 160,
    "15 мл(200 грн)": 200,
    "15 мл(220 грн)": 220,
    "Chaser/FL350 30 мл(320 грн)": 320,
    "Chaser MIX 30 мл(340 грн)": 340,
    "Chaser LUX 30 мл(350 грн)": 350,
    "Octobar 30 мл(300 грн)": 300,
    "FL350 LUX 30 мл(350 грн)": 350,
    "InBottle 30 мл(360 грн)": 360,
    "Juni,CrazyJuice 30 мл(280 грн)": 280,
    "Hype,MixBar,JuniSilver 30 мл(320 грн)": 320,
    "LoveIt 30 мл(310 грн)": 310,
    "AromaMax(220 грн)": 220,
    "Nova, M-Jam 30 мл(260 грн)": 260,
    "Punch 30 мл(330 грн)": 330,
    "Органика 120 мл(330 грн)": 330,
    "Органика 60 мл(250 грн)": 250,
    "Никобустер соль(70 грн)": 70,
    "Никобустер органика(25 грн)": 25,
    "Картридж(150 грн)": 150,
    "Картридж(140 грн)": 140,
    "Картридж(135 грн)": 135,
    "Картридж(130 грн)": 130,
    "Картридж(125 грн)": 125,
    "Картридж(120 грн)": 120,
    "Картридж(115 грн)": 115,
    "Картридж(110 грн)": 110,
    "Картридж(100 грн)": 100,
    "Картридж(95 грн)": 95,
    "Аккумулятор(300 грн)": 300
}

# Инициализация словаря для хранения устройств и их цен
pods = {
    "Luxe X(1400 грн)": 1400,
    "OXVA SQ Pro(1350 грн)": 1350,
    "XROS Pro/Argus(1250 грн)": 1250,
    "XROS 4/OXVA(1200 грн)": 1200,
    "SMOK Pro(1080 грн)": 1080,
    "VC30/Luxe Q(1020 грн)": 1020,
    "Novo 5/UrsaPro/Thelema/FeelinX(1000 грн)": 1000,
    "OXVA SE(950 грн)": 950,
    "Wenax Q(900 грн)": 900,
    "XROS 4 Mini(880 грн)": 880,
    "XROS 3 Mini/Feelin A1(800 грн)": 800,
    "XROS MINI(720 грн)": 720,
    "URSA Epoch(750 грн)": 750,
    "Sonder U(600 грн)": 600,
    "URSA Cap/Pagee(650 грн)": 650,
    "NeonBar/Orion/FeelinMini(550 грн)": 550,
    "Freeton(500 грн)": 500,
    "JellyBox/Doric(450 грн)": 450
}

# Инициализация словаря для хранения счетчиков продаж
sales_count = {product: 0 for product in products.keys()}
sales_count.update({pod: 0 for pod in pods.keys()})

# Переменные для хранения общей суммы продаж по способам оплаты
total_sales_card = 0
total_sales_cash = 0

# Константы для этапов разговора
CHOOSING_PRODUCT, SALE_SELECTION, PAYMENT_SELECTION, POD_SELECTION = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [KeyboardButton("/sale"), KeyboardButton("/count"), KeyboardButton("/close_shift")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text('Выберите команду из меню ниже:', reply_markup=reply_markup)

async def sale_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = []
    product_names = list(products.keys())
    for i in range(0, len(product_names), 2):
        row = [KeyboardButton(product_names[i])]
        if i + 1 < len(product_names):
            row.append(KeyboardButton(product_names[i + 1]))
        keyboard.append(row)
    keyboard.append([KeyboardButton("Поды"), KeyboardButton("Завершить продажу"), KeyboardButton("Отменить продажу")])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text('Выберите товары для продажи и затем нажмите "Завершить продажу":', reply_markup=reply_markup)
    return SALE_SELECTION

async def sale(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if 'selected_products' not in context.user_data:
        context.user_data['selected_products'] = []
    if 'total_price' not in context.user_data:
        context.user_data['total_price'] = 0

    selected_products = context.user_data['selected_products']
    total_price = context.user_data['total_price']
    product_name = update.message.text

    if product_name == "Завершить продажу":
        if selected_products:
            keyboard = [[KeyboardButton("Карта"), KeyboardButton("Наличные")]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
            await update.message.reply_text('Выберите способ оплаты:', reply_markup=reply_markup)
            return PAYMENT_SELECTION
        else:
            keyboard = [[KeyboardButton("/sale"), KeyboardButton("/count"), KeyboardButton("/close_shift")]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
            await update.message.reply_text('Вы не выбрали ни одного товара. Возвращение в главное меню...', reply_markup=reply_markup)
            return ConversationHandler.END
    elif product_name == "Отменить продажу":
        context.user_data.clear()
        keyboard = [[KeyboardButton("/sale"), KeyboardButton("/count"), KeyboardButton("/close_shift")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text('Продажа отменена. Возвращение в главное меню...', reply_markup=reply_markup)
        return ConversationHandler.END
    elif product_name == "Поды":
        keyboard = []
        pod_names = list(pods.keys())
        for i in range(0, len(pod_names), 2):
            row = [KeyboardButton(pod_names[i])]
            if i + 1 < len(pod_names):
                row.append(KeyboardButton(pod_names[i + 1]))
            keyboard.append(row)
        keyboard.append([KeyboardButton("Назад к продуктам")])
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text('Выберите устройство для продажи и затем нажмите "Назад к продуктам":', reply_markup=reply_markup)
        return POD_SELECTION
    elif product_name in products:
        selected_products.append(product_name)
        total_price += products[product_name]
        context.user_data['total_price'] = total_price
        await update.message.reply_text(f'- "{product_name}"\nТекущая сумма: {total_price} грн.')
        return SALE_SELECTION
    else:
        await update.message.reply_text('Товар не найден. Пожалуйста, выберите товар из списка или нажмите "Завершить продажу".')
        return SALE_SELECTION

async def pod_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if 'selected_products' not in context.user_data:
        context.user_data['selected_products'] = []
    if 'total_price' not in context.user_data:
        context.user_data['total_price'] = 0

    selected_products = context.user_data['selected_products']
    total_price = context.user_data['total_price']
    pod_name = update.message.text

    if pod_name == "Назад к продуктам":
        await sale_start(update, context)
        return SALE_SELECTION
    elif pod_name in pods:
        selected_products.append(pod_name)
        total_price += pods[pod_name]
        context.user_data['total_price'] = total_price
        await update.message.reply_text(f'- "{pod_name}"\nТекущая сумма: {total_price} грн.')
        return POD_SELECTION
    else:
        await update.message.reply_text('Устройство не найдено. Пожалуйста, выберите устройство из списка или нажмите "Назад к продуктам".')
        return POD_SELECTION

async def payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global total_sales_card, total_sales_cash
    selected_products = context.user_data['selected_products']
    total_price = context.user_data['total_price']
    payment_method = update.message.text

    if payment_method in ["Карта", "Наличные"]:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        product_counts = Counter(selected_products)
        sale_message = '\n'.join([f'- {product} x{count}' for product, count in product_counts.items()])
        for product in selected_products:
            sales_count[product] += 1

        payment_message = "Оплата картой" if payment_method == "Карта" else "Оплата наличными"
        if payment_method == "Карта":
            total_sales_card += total_price
        else:
            total_sales_cash += total_price

        await update.message.reply_text(f'Продажи завершены в {current_time}. Вы продали:\n{sale_message}\nОбщая сумма: {total_price} грн.\n{payment_message}')

        keyboard = [[KeyboardButton("/sale"), KeyboardButton("/count"), KeyboardButton("/close_shift")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text('Возвращение в главное меню...', reply_markup=reply_markup)

        context.user_data.clear()
        return ConversationHandler.END
    else:
        await update.message.reply_text('Неверный способ оплаты. Пожалуйста, выберите "Карта" или "Наличные".')
        return PAYMENT_SELECTION

async def count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    sold_items = {product: count for product, count in sales_count.items() if count > 0}

    if not sold_items:
        await update.message.reply_text('Продаж пока нет.')
    else:
        message = "Общее количество продаж:\n"
        for product, count in sold_items.items():
            message += f'{product}: {count}\n'
        message += f'\nОбщая сумма продаж (Карта): {total_sales_card} грн.'
        message += f'\nОбщая сумма продаж (Наличные): {total_sales_cash} грн.'
        await update.message.reply_text(message)

async def close_shift(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global total_sales_card, total_sales_cash, sales_count

    sold_items = {product: count for product, count in sales_count.items() if count > 0}
    if not sold_items:
        await update.message.reply_text('Продаж пока нет.')
        return

    message = "Закрытие смены:\n"
    for product, count in sold_items.items():
        message += f'{product}: {count}\n'
    message += f'\nОбщая сумма продаж (Карта): {total_sales_card} грн.'
    message += f'\nОбщая сумма продаж (Наличные): {total_sales_cash} грн.'
    message += f'\nОбщая сумма продаж: {total_sales_card + total_sales_cash} грн.'

    await context.bot.send_message(chat_id=REPORT_GROUP_ID, text=message)
    await update.message.reply_text('Смена закрыта. Отчет отправлен в группу.')

    # Сброс счетчиков
    sales_count = {product: 0 for product in products.keys()}
    sales_count.update({pod: 0 for pod in pods.keys()})
    total_sales_card = 0
    total_sales_cash = 0

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("count", count))
    application.add_handler(CommandHandler("close_shift", close_shift))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('sale', sale_start)],
        states={
            SALE_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, sale)],
            POD_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, pod_selection)],
            PAYMENT_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, payment_selection)],
        },
        fallbacks=[]
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
