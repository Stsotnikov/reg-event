import logging
import sqlite3
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from telegram.ext import CommandHandler
import random

import logging
from config import Config, load_config

config: Config = load_config()
BOT_TOKEN: str = config.tg_bot.token

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Этапы диалога
NAME, PHONE, ADDITIONAL_INFO, PAYMENT = range(4)

# Подключение к базе данных SQLite
conn = sqlite3.connect('user_data.db', check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы, если ее нет
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (nickname TEXT, fio TEXT, phone TEXT, telegram_id TEXT, additional_info TEXT, payment_status TEXT)''')

# Функция начала общения с ботом
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Привет! Пожалуйста, введи своё ФИО:")
    return NAME

# Функция для получения ФИО
def get_name(update: Update, context: CallbackContext) -> int:
    user_fio = update.message.text
    context.user_data['fio'] = user_fio
    update.message.reply_text("Теперь, пожалуйста, введи свой телефон (в формате +X-XXX-XXX-XXXX):")
    return PHONE

# Функция для получения телефона
def get_phone(update: Update, context: CallbackContext) -> int:
    user_phone = update.message.text
    context.user_data['phone'] = user_phone
    update.message.reply_text("Теперь, пожалуйста, введи дополнительные данные:")
    return ADDITIONAL_INFO

# Функция для получения дополнительных данных
def get_additional_info(update: Update, context: CallbackContext) -> int:
    user_additional_info = update.message.text
    context.user_data['additional_info'] = user_additional_info
    update.message.reply_text("Отлично! Теперь вам нужно пройти оплату через Юкассу. Жду подтверждения.")
    
    # Симуляция платежа (в реальности будет интеграция с API Юкассы)
    update.message.reply_text("Оплата прошла успешно. Платеж завершен!")
    context.user_data['payment_status'] = "успешно"
    
    # Сохранение данных в базе
    save_user_data(context.user_data)
    
    update.message.reply_text("Спасибо! Ваша информация была сохранена.")
    return ConversationHandler.END

# Функция для сохранения данных в базе
def save_user_data(user_data):
    nickname = user_data.get('nickname', '')
    fio = user_data['fio']
    phone = user_data['phone']
    telegram_id = user_data['telegram_id']
    additional_info = user_data['additional_info']
    payment_status = user_data['payment_status']
    
    cursor.execute('INSERT INTO users (nickname, fio, phone, telegram_id, additional_info, payment_status) VALUES (?, ?, ?, ?, ?, ?)',
                   (nickname, fio, phone, telegram_id, additional_info, payment_status))
    conn.commit()

# Обработка ошибки или отмены
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Операция отменена. Если захотите попробовать снова, используйте команду /start.")
    return ConversationHandler.END

# Основная функция для настройки бота
def main() -> None:
    updater = Updater("BOT_TOKEN")

    dispatcher = updater.dispatcher

    # Настроим обработчик состояний
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
            PHONE: [MessageHandler(Filters.text & ~Filters.command, get_phone)],
            ADDITIONAL_INFO: [MessageHandler(Filters.text & ~Filters.command, get_additional_info)],
            PAYMENT: [MessageHandler(Filters.text & ~Filters.command, get_additional_info)],  # просто симуляция
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()