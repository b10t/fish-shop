import logging
from textwrap import dedent

import redis
from environs import Env
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ParseMode)
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

    products = Moltin.get_products()

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

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        message = update.message
    else:
        message = update.callback_query

    message.reply_text('Please choose:', reply_markup=reply_markup)
    return 'HANDLE_MENU'


def get_image_url(product):
    """Получает ссылку на URL изображения."""
    try:
        if file_id := (product.get('relationships')
                    .get('main_image')
                    .get('data')
                    .get('id')):

            if file_url := (Moltin.get_file_url(file_id)
                            .get('data')
                            .get('link')
                            .get('href')):

                return file_url
    except Exception:
        return open('no_image.jpg', 'rb')

def handle_menu(bot, update):
    query = update.callback_query

    item_id = query.data

    product = Moltin.get_product(item_id)

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

    bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=image_url,
        caption=message_text,
        parse_mode=ParseMode.MARKDOWN)

    return 'HANDLE_MENU'


def echo(bot, update):
    """
    Хэндлер для состояния ECHO.

    Бот отвечает пользователю тем же, что пользователь ему написал.
    Оставляет пользователя в состоянии ECHO.
    """
    users_reply = update.message.text
    update.message.reply_text(users_reply)
    return 'ECHO'


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
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode('utf-8')

    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'ECHO': echo
    }
    state_handler = states_functions[user_state]
    # Если вы вдруг не заметите, что python-telegram-bot перехватывает ошибки.
    # Оставляю этот try...except, чтобы код не падал молча.
    # Этот фрагмент можно переписать.
    try:
        next_state = state_handler(bot, update)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)


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
    env = Env()
    env.read_env()

    token = env.str('TELEGRAM_TOKEN')
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    # dispatcher.add_handler(CallbackQueryHandler(handle_menu))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()


if __name__ == '__main__':
    main()
