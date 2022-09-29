import logging
from textwrap import dedent

import redis
from environs import Env
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)

from moltin_api import Moltin

_database = None

logger = logging.getLogger('fish-shop')


def start(bot, update):
    """
    Хэндлер для состояния START.

    Бот отвечает пользователю фразой "Привет!" и переводит его в состояние ECHO.
    Теперь в ответ на его команды будет запускаеться хэндлер echo.
    """

    moltin = Moltin()

    moltin.get_or_create_cart(update.effective_user.id)

    products = moltin.get_products()

    keyboard = []

    for product in products:
        keyboard.append(
            [
                InlineKeyboardButton(
                    product.get('name'),
                    callback_data=product.get('id')
                )
            ]
        )

    keyboard.append(
        [InlineKeyboardButton(
            '🛒 Корзина',
            callback_data='SHOW_CART'
        )]
    )

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        update.message.reply_text('Please choose:', reply_markup=reply_markup)
    else:
        chat_id = update.effective_chat.id
        bot.deleteMessage(chat_id=chat_id,
                          message_id=update.effective_message.message_id)

        bot.send_message(chat_id=chat_id,
                         text='Please choose:',
                         reply_markup=reply_markup)

    return 'HANDLE_MENU'


def get_image_url(product):
    """Получает ссылку на URL изображения."""
    moltin = Moltin()

    try:
        if file_id := (product.get('relationships')
                       .get('main_image')
                       .get('data')
                       .get('id')):

            if file_url := (moltin.get_file_url(file_id)
                            .get('data')
                            .get('link')
                            .get('href')):

                return file_url
    except Exception:
        return open('no_image.jpg', 'rb')


def handle_menu(bot, update):
    """Обработка кнопок меню."""
    query = update.callback_query
    item_id = query.data

    moltin = Moltin()

    product = moltin.get_product(item_id)

    image_url = get_image_url(product)

    price = product.get('price')[0]
    price = f'{float(price["amount"]) / 100} {price["currency"]}'

    message_text = dedent(
        f'''
            *{product.get('name')}*

            *Цена:*:
            `{price}`

            Описание:
            `{product.get('description')}`

        '''
    )

    bot.deleteMessage(chat_id=update.effective_chat.id,
                      message_id=update.effective_message.message_id)

    quantity_button = []

    for quantity in [1, 5, 10]:
        quantity_button.append(
            InlineKeyboardButton(
                f'{quantity} кг.',
                callback_data=f'{item_id}#{quantity}',
            )
        )

    keyboard = [
        quantity_button,
        [InlineKeyboardButton('🛒 Корзина', callback_data='SHOW_CART')],
        [InlineKeyboardButton('В меню', callback_data='BACK')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=image_url,
        caption=message_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup)

    return 'HANDLE_DESCRIPTION'


def handle_description(bot, update):
    """Обработка вывода описания."""
    user_id = update.effective_user.id
    query = update.callback_query

    item_id, quantity = query.data.split('#')

    moltin = Moltin()
    moltin.add_cart_item(user_id, item_id=item_id, quantity=quantity)

    return 'HANDLE_DESCRIPTION'


def show_cart(bot, update):
    """Отображение корзины."""
    chat_id = update.effective_chat.id
    message_id = update.effective_message.message_id
    user_id = update.effective_user.id

    moltin = Moltin()
    cart = moltin.get_cart(user_id)
    cart_items = moltin.get_cart_items(user_id).get('data', [])

    cost = (cart.get('data')
                .get('meta')
                .get('display_price')
                .get('with_tax')
                .get('formatted'))

    keyboard = []
    description_items = []

    for item in cart_items:
        quantity = item.get('quantity', 0)
        price = item.get('unit_price', 0).get('amount', 0) / 100

        description_items.append(
            dedent(
                f'''
                    *{item.get('name')}*
                    *Цена:*
                    `{price}`
                    Количество:
                    `{quantity}`
                '''
            )
        )

        keyboard.append(
            [
                InlineKeyboardButton(
                    f'Убрать из корзины: {item.get("name")}',
                    callback_data=f'{item.get("id")}',
                )
            ]
        )

    description_items.append(
        dedent(
            f'''
                Стоимость:
                `{cost}`
            '''
        )
    )

    message_text = dedent(
        f'''
            🛒 *Товары в корзине:*
            {''.join(description_items)}
        '''
    )

    keyboard.append(
        [InlineKeyboardButton('Оплатить', callback_data='WAITING_EMAIL')]
    )

    keyboard.append(
        [InlineKeyboardButton('В меню', callback_data='BACK')]
    )

    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.deleteMessage(chat_id=chat_id,
                      message_id=message_id)

    bot.send_message(chat_id=chat_id,
                     text=message_text,
                     reply_markup=reply_markup,
                     parse_mode=ParseMode.MARKDOWN)

    return 'HANDLE_CART'


def handle_cart(bot, update):
    """Обработка кнопок корзины."""
    user_id = update.effective_user.id

    query = update.callback_query
    item_id = query.data

    moltin = Moltin()
    moltin.remove_cart_item(user_id, item_id)

    return show_cart(bot, update)


def waiting_email(bot, update):
    """Получение email покупателя."""
    chat_id = update.effective_chat.id
    message_id = update.effective_message.message_id
    user_id = update.effective_user.id

    if update.message:
        email = update.message.text

        update.message.reply_text(f'Ваш e-mail: {email}')

        moltin = Moltin()
        moltin.create_customer(user_id, email)

        return show_cart(bot, update)
    else:
        bot.deleteMessage(chat_id=chat_id,
                          message_id=message_id)

        bot.send_message(chat_id=chat_id,
                         text='Пожалуйста, введите свой e-mail:')

        return 'WAITING_EMAIL'


def handle_users_reply(bot, update):
    """
    Функция, которая запускается при любом сообщении от пользователя и решает как его обработать.

    Эта функция запускается в ответ на эти действия пользователя:
        * Нажатие на inline-кнопку в боте
        * Отправка сообщения боту
        * Отправка команды боту
    Она получает стейт пользователя из базы данных и запускает соответствующую функцию-обработчик (хэндлер).
    Функция-обработчик возвращает следующее состояние, которое записывается в базу данных.
    Если пользователь только начал пользоваться ботом, Telegram форсит его написать "/start",
    поэтому по этой фразе выставляется стартовое состояние.
    Если пользователь захочет начать общение с ботом заново, он также может воспользоваться этой командой.
    """
    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start' or user_reply == 'BACK':
        user_state = 'START'
    elif user_reply == 'SHOW_CART':
        user_state = 'SHOW_CART'
    elif user_reply == 'WAITING_EMAIL':
        user_state = 'WAITING_EMAIL'
    else:
        user_state = db.get(chat_id).decode('utf-8')

    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
        'SHOW_CART': show_cart,
        'HANDLE_CART': handle_cart,
        'WAITING_EMAIL': waiting_email
    }
    state_handler = states_functions[user_state]
    # Если вы вдруг не заметите, что python-telegram-bot перехватывает ошибки.
    # Оставляю этот try...except, чтобы код не падал молча.
    # Этот фрагмент можно переписать.
    try:
        next_state = state_handler(bot, update)
        db.set(chat_id, next_state)
    except Exception as err:
        logger.error(err)


def get_database_connection():
    """
    Возвращает конекшн с базой данных Redis, либо создаёт новый, если он ещё не создан.
    """
    global _database
    if _database is None:
        env = Env()
        env.read_env()

        database_host = env.str('REDIS_HOST', 'localhost')
        database_port = env.str('REDIS_PORT', 6379)
        database_username = env.str('REDIS_USERNAME', '')
        database_password = env.str('REDIS_PASSWORD', '')

        _database = redis.Redis(
            host=database_host,
            port=database_port,
            username=database_username,
            password=database_password
        )

    return _database


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
    )

    env = Env()
    env.read_env()

    token = env.str('TELEGRAM_TOKEN')
    moltin_client_id = env.str('MOLTIN_CLIENT_ID')

    Moltin(moltin_client_id)

    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()


if __name__ == '__main__':
    main()
