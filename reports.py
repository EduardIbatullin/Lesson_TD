import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from database import get_habit_tracking


def generate_report(user_id, period):
    if period == 'weekly':
        period_days = 7
    elif period == 'monthly':
        period_days = 30
    data = get_habit_tracking(user_id, period_days)

    if not data:
        return "Нет данных для отчета."

    df = pd.DataFrame(data, columns=['Habit', 'Date', 'Status'])
    report = df.pivot_table(index='Date', columns='Habit', values='Status', aggfunc='sum').fillna(0)
    report_str = report.to_string()
    return report_str


def create_plot(user_id, period):
    if period == 'weekly':
        period_days = 7
    elif period == 'monthly':
        period_days = 30
    data = get_habit_tracking(user_id, period_days)

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
