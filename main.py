import telebot
from handlers import register_handlers
from reminders import schedule_daily_reminders
import config  # Импортируем конфигурацию

bot = telebot.TeleBot(config.TOKEN)  # Используем токен из config.py

register_handlers(bot)

if __name__ == "__main__":
    schedule_daily_reminders(bot)
    bot.polling(none_stop=True)
