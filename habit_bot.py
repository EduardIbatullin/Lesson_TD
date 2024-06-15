import telebot
from telebot import types
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd

TOKEN = '7311839890:AAHdscqIzW2mgF3Uyl-dZf9RmC7-G0V75_Q'
bot = telebot.TeleBot(TOKEN)
user_data = {}


def init_db():
    conn = sqlite3.connect('habits.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        description TEXT,
        frequency TEXT,
        frequency_days INTEGER,
        start_date DATE,
        goal INTEGER
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS habit_tracking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id INTEGER,
        date DATE,
        status BOOLEAN
    )
    ''')
    conn.commit()
    conn.close()


init_db()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я помогу тебе отслеживать твои привычки. Начнем с добавления новой привычки.")


@bot.message_handler(commands=['addhabit'])
def add_habit(message):
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
        msg = bot.reply_to(message,
                           "Введите частоту выполнения привычки (например, ежедневно, раз в неделю, раз в N дней):")
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

        conn = sqlite3.connect('habits.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO habits (user_id, name, description, frequency, frequency_days, start_date, goal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (chat_id, user_data[chat_id]['name'], user_data[chat_id]['description'],
              user_data[chat_id]['frequency'], user_data[chat_id]['frequency_days'], datetime.now().date(),
              user_data[chat_id]['goal']))
        conn.commit()
        conn.close()

        bot.reply_to(message, "Привычка успешно добавлена!")
    except Exception as e:
        bot.reply_to(message, 'Что-то пошло не так.')


@bot.message_handler(commands=['todayhabits'])
def send_today_habits(message):
    chat_id = message.chat.id
    today = datetime.now().date()

    conn = sqlite3.connect('habits.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, name, frequency, frequency_days, start_date FROM habits WHERE user_id = ?
    ''', (chat_id,))
    habits = cursor.fetchall()
    conn.close()

    today_habits = []
    for habit in habits:
        habit_id, habit_name, habit_frequency, habit_frequency_days, start_date = habit
        if habit_frequency == 'ежедневно' or (habit_frequency_days > 0 and (
                today - datetime.strptime(start_date, '%Y-%m-%d').date()).days % habit_frequency_days == 0):
            today_habits.append(habit_name)

    if today_habits:
        bot.send_message(chat_id, "Сегодня вам нужно выполнить следующие привычки:\n" + "\n".join(today_habits))
    else:
        bot.send_message(chat_id, "На сегодня нет запланированных привычек.")


@bot.message_handler(commands=['allhabits'])
def send_all_habits(message):
    chat_id = message.chat.id

    conn = sqlite3.connect('habits.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT name, frequency, frequency_days FROM habits WHERE user_id = ?
    ''', (chat_id,))
    habits = cursor.fetchall()
    conn.close()

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


def generate_report(user_id, period):
    conn = sqlite3.connect('habits.db')
    cursor = conn.cursor()
    if period == 'weekly':
        start_date = datetime.now() - timedelta(days=7)
    elif period == 'monthly':
        start_date = datetime.now() - timedelta(days=30)
    cursor.execute('''
    SELECT habits.name, habit_tracking.date, habit_tracking.status
    FROM habits
    JOIN habit_tracking ON habits.id = habit_tracking.habit_id
    WHERE habits.user_id = ? AND habit_tracking.date >= ?
    ''', (user_id, start_date.date()))
    data = cursor.fetchall()
    conn.close()

    if not data:
        return "Нет данных для отчета."

    df = pd.DataFrame(data, columns=['Habit', 'Date', 'Status'])
    report = df.pivot_table(index='Date', columns='Habit', values='Status', aggfunc='sum').fillna(0)
    report_str = report.to_string()
    return report_str


def create_plot(user_id, period):
    conn = sqlite3.connect('habits.db')
    cursor = conn.cursor()
    if period == 'weekly':
        start_date = datetime.now() - timedelta(days=7)
    elif period == 'monthly':
        start_date = datetime.now() - timedelta(days=30)
    cursor.execute('''
    SELECT habits.name, habit_tracking.date, habit_tracking.status
    FROM habits
    JOIN habit_tracking ON habits.id = habit_tracking.habit_id
    WHERE habits.user_id = ? AND habit_tracking.date >= ?
    ''', (user_id, start_date.date()))
    data = cursor.fetchall()
    conn.close()

    if not data:
        return None

    df = pd.DataFrame(data, columns=['Habit', 'Date', 'Status'])
    report = df.pivot_table(index='Date', columns='Habit', values='Status', aggfunc='sum').fillna(0)

    plt.figure()
    report.plot(kind='bar', stacked=True)
    plt.title(f'{period.capitalize()} Habit Report')
    plt.xlabel('Date')
    plt.ylabel('Completion')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plot_path = f'{user_id}_{period}_report.png'
    plt.savefig(plot_path)
    return plot_path


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


def send_daily_reminders():
    conn = sqlite3.connect('habits.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM habits')
    habits = cursor.fetchall()
    for habit in habits:
        user_id = habit[1]
        habit_name = habit[2]
        bot.send_message(user_id, f"Напоминание о привычке: {habit_name}")
    conn.close()


import threading


def schedule_daily_reminders():
    now = datetime.now()
    next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)
    if next_run < now:
        next_run += timedelta(days=1)
    delay = (next_run - now).total_seconds()
    threading.Timer(delay, send_daily_reminders).start()


schedule_daily_reminders()
bot.polling(none_stop=True)
