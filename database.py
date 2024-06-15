import sqlite3
from datetime import datetime

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

def add_habit(user_id, name, description, frequency, frequency_days, goal):
    conn = sqlite3.connect('habits.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO habits (user_id, name, description, frequency, frequency_days, start_date, goal)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, name, description, frequency, frequency_days, datetime.now().date(), goal))
    conn.commit()
    conn.close()

def get_habits(user_id):
    conn = sqlite3.connect('habits.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, name, frequency, frequency_days, start_date FROM habits WHERE user_id = ?
    ''', (user_id,))
    habits = cursor.fetchall()
    conn.close()
    return habits

def get_all_habits(user_id):
    conn = sqlite3.connect('habits.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT name, frequency, frequency_days FROM habits WHERE user_id = ?
    ''', (user_id,))
    habits = cursor.fetchall()
    conn.close()
    return habits

def get_habit_tracking(user_id, period_days):
    conn = sqlite3.connect('habits.db')
    cursor = conn.cursor()
    start_date = datetime.now() - timedelta(days=period_days)
    cursor.execute('''
    SELECT habits.name, habit_tracking.date, habit_tracking.status
    FROM habits
    JOIN habit_tracking ON habits.id = habit_tracking.habit_id
    WHERE habits.user_id = ? AND habit_tracking.date >= ?
    ''', (user_id, start_date.date()))
    data = cursor.fetchall()
    conn.close()
    return data
