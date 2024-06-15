import sqlite3
from datetime import datetime, timedelta
import threading

def send_daily_reminders(bot):
    conn = sqlite3.connect('habits.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM habits')
    habits = cursor.fetchall()
    for habit in habits:
        user_id = habit[1]
        habit_name = habit[2]
        bot.send_message(user_id, f"Напоминание о привычке: {habit_name}")
    conn.close()

def schedule_daily_reminders(bot):
    now = datetime.now()
    next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)
    if next_run < now:
        next_run += timedelta(days=1)
    delay = (next_run - now).total_seconds()
    threading.Timer(delay, lambda: send_daily_reminders(bot)).start()
