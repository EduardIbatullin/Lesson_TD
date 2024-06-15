from telebot import types
from datetime import datetime, timedelta
from database import add_habit, get_habits, get_all_habits
from reports import generate_report, create_plot

user_data = {}

def register_handlers(bot):
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(message, "Привет! Я помогу тебе отслеживать твои привычки. Начнем с добавления новой привычки.")

    @bot.message_handler(commands=['addhabit'])
    def add_habit_command(message):
        msg = bot.reply_to(message, "Введите название привычки:")
        bot.register_next_step_handler(msg, process_habit_name_step)

    def process_habit_name_step(message):
        try:
            chat_id = message.chat.id
            habit_name = message.text
            user_data[chat_id] = {'name': habit_name}
            msg = bot.reply_to(message, "Введите описание привычки:")
            bot.register_next_step_handler(msg, process_habit_description_step)
        except Exception as e:
            bot.reply_to(message, 'Что-то пошло не так.')

    def process_habit_description_step(message):
        try:
            chat_id = message.chat.id
            habit_description = message.text
            user_data[chat_id]['description'] = habit_description
            msg = bot.reply_to(message, "Введите частоту выполнения привычки (например, ежедневно, раз в неделю, раз в N дней):")
            bot.register_next_step_handler(msg, process_habit_frequency_step)
        except Exception as e:
            bot.reply_to(message, 'Что-то пошло не так.')

    def process_habit_frequency_step(message):
        try:
            chat_id = message.chat.id
            habit_frequency = message.text
            user_data[chat_id]['frequency'] = habit_frequency
            if "раз в" in habit_frequency:
                msg = bot.reply_to(message, "Введите количество дней для частоты (например, 2 для 'раз в 2 дня'):")
                bot.register_next_step_handler(msg, process_habit_frequency_days_step)
            else:
                user_data[chat_id]['frequency_days'] = 0
                msg = bot.reply_to(message, "Введите цель (например, 30 дней):")
                bot.register_next_step_handler(msg, process_habit_goal_step)
        except Exception as e:
            bot.reply_to(message, 'Что-то пошло не так.')

    def process_habit_frequency_days_step(message):
        try:
            chat_id = message.chat.id
            habit_frequency_days = int(message.text)
            user_data[chat_id]['frequency_days'] = habit_frequency_days
            msg = bot.reply_to(message, "Введите цель (например, 30 дней):")
            bot.register_next_step_handler(msg, process_habit_goal_step)
        except Exception as e:
            bot.reply_to(message, 'Что-то пошло не так.')

    def process_habit_goal_step(message):
        try:
            chat_id = message.chat.id
            habit_goal = int(message.text)
            user_data[chat_id]['goal'] = habit_goal
            add_habit(chat_id, user_data[chat_id]['name'], user_data[chat_id]['description'],
                      user_data[chat_id]['frequency'], user_data[chat_id]['frequency_days'], user_data[chat_id]['goal'])
            bot.reply_to(message, "Привычка успешно добавлена!")
        except Exception as e:
            bot.reply_to(message, 'Что-то пошло не так.')

    @bot.message_handler(commands=['todayhabits'])
    def send_today_habits(message):
        chat_id = message.chat.id
        today = datetime.now().date()
        habits = get_habits(chat_id)

        today_habits = []
        for habit in habits:
            habit_id, habit_name, habit_frequency, habit_frequency_days, start_date = habit
            if habit_frequency == 'ежедневно' or (habit_frequency_days > 0 and (today - datetime.strptime(start_date, '%Y-%m-%d').date()).days % habit_frequency_days == 0):
                today_habits.append(habit_name)

        if today_habits:
            bot.send_message(chat_id, "Сегодня вам нужно выполнить следующие привычки:\n" + "\n".join(today_habits))
        else:
            bot.send_message(chat_id, "На сегодня нет запланированных привычек.")

    @bot.message_handler(commands=['allhabits'])
    def send_all_habits(message):
        chat_id = message.chat.id
        habits = get_all_habits(chat_id)

        if habits:
            response = "Ваши привычки:\n"
            for habit in habits:
                habit_name, habit_frequency, habit_frequency_days = habit
                if habit_frequency_days > 0:
                    frequency_description = f"раз в {habit_frequency_days} дней"
                else:
                    frequency_description = habit_frequency
                response += f"{habit_name}: {frequency_description}\n"
            bot.send_message(chat_id, response)
        else:
            bot.send_message(chat_id, "У вас нет добавленных привычек.")

    @bot.message_handler(commands=['weeklyreport'])
    def send_weekly_report(message):
        chat_id = message.chat.id
        report = generate_report(chat_id, 'weekly')
        bot.send_message(chat_id, report)

    @bot.message_handler(commands=['monthlyreport'])
    def send_monthly_report(message):
        chat_id = message.chat.id
        report = generate_report(chat_id, 'monthly')
        bot.send_message(chat_id, report)

    @bot.message_handler(commands=['weeklyplot'])
    def send_weekly_plot(message):
        chat_id = message.chat.id
        plot_path = create_plot(chat_id, 'weekly')
        if plot_path:
            bot.send_photo(chat_id, photo=open(plot_path, 'rb'))
        else:
            bot.send_message(chat_id, "Нет данных для отчета.")

    @bot.message_handler(commands=['monthlyplot'])
    def send_monthly_plot(message):
        chat_id = message.chat.id
        plot_path = create_plot(chat_id, 'monthly')
        if plot_path:
            bot.send_photo(chat_id, photo=open(plot_path, 'rb'))
        else:
            bot.send_message(chat_id, "Нет данных для отчета.")
