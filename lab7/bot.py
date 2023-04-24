import telebot
from telebot import types

import psycopg2
import datetime

token = "6286666859:AAFtRNToyMyjECo-FDgVGq__pZlTUCDrv4g"
bot = telebot.TeleBot(token)

conn = psycopg2.connect(database="bot_db",
                        user="postgres",
                        password="05062004liza",
                        host="localhost",
                        port="5432")

cursor = conn.cursor()
if datetime.date.today().isocalendar()[1] % 2 == 0:
    week = 0
    next_week = 1
else:
    week = 1
    next_week = 0


def get_date_by_weekday(weekday, next):
    weekdays = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}
    today = datetime.date.today()
    current_weekday = today.weekday()
    days_diff = weekdays[weekday] - current_weekday
    target_date = today + datetime.timedelta(days=days_diff + next)
    return target_date.strftime('%d.%m')


def get_day(day, week):
    cursor.execute(
        "SELECT * FROM timetable JOIN subject on timetable.subject = subject.id"
        " JOIN teacher on teacher.id = timetable.teacher"
        " WHERE timetable.day=%s and timetable.week=%s ORDER BY timetable.id",
        (day, week))
    weekdays = {1: 'ПОНЕДЕЛЬНИК', 2: 'ВТОРНИК', 3: 'СРЕДА', 4: 'ЧЕТВЕРГ', 5: 'ПЯТНИЦА', 6: 'СУББОТА'}
    answer = f'{weekdays[day]}  {get_date_by_weekday(day, 0)}\n'
    for row in cursor.fetchall():
        if row[3] == 10:
            answer += f'{row[5]}\n{row[8]}\n\n'
        else:
            answer += f'{row[5]}\n{row[8]}\n{row[10]}\n{row[4]}\n\n'
    return answer


def get_week(week, next):
    cursor.execute(
        "SELECT * FROM timetable JOIN subject on timetable.subject = subject.id"
        " JOIN teacher on teacher.id = timetable.teacher"
        " WHERE timetable.week=%s ORDER BY timetable.id",
        (week, ))
    weekdays = {1: 'ПОНЕДЕЛЬНИК', 2: 'ВТОРНИК', 3: 'СРЕДА', 4: 'ЧЕТВЕРГ', 5: 'ПЯТНИЦА', 6: 'СУББОТА'}
    answer = f'ПОНЕДЕЛЬНИК {get_date_by_weekday(1, next)}\n'
    current_day = 1
    for row in cursor.fetchall():
        if current_day != row[2]:
            answer += f'\n{weekdays[row[2]]}  {get_date_by_weekday(row[2], next)}\n'
            current_day = row[2]
        if row[3] == 10:
            answer += f'{row[5]}\n{row[8]}\n\n'
        else:
            answer += f'{row[5]}\n{row[8]}\n{row[10]}\n{row[4]}\n\n'
    return answer

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row("Хочу", "/help", "Расписание")
    bot.send_message(message.chat.id, 'Здравствуйте! Хотите узнать свежую информацию о МТУСИ?', reply_markup=keyboard)


@bot.message_handler(commands=['timetable'])
def get_timetable(message):
    print(1)
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row("Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота")
    keyboard.row('На эту неделю', 'На следующую неделю')
    bot.send_message(message.chat.id, 'Выберите команду', reply_markup=keyboard)


@bot.message_handler(commands=['week'])
def get_week_command(message):
    bot.send_message(message.chat.id, get_week(week, 0))


@bot.message_handler(commands=['next_week'])
def get_next_week_command(message):
    bot.send_message(message.chat.id, get_week(next_week, 7))


@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id, 'Я умею:\n /week - Вывести расписание на текущую неделю\n'
                                      '/next_week - Вывести расписание на следующую неделю\n'
                                      '/timetable - Выбрать день недели')


@bot.message_handler(content_types=['text'])
def answer(message):
    weekdays = {'ПОНЕДЕЛЬНИК': 1, 'ВТОРНИК': 2, 'СРЕДА': 3, 'ЧЕТВЕРГ': 4, 'ПЯТНИЦА': 5, 'СУББОТА': 6}
    if message.text.lower() == "хочу":
        bot.send_message(message.chat.id, 'Тогда тебе сюда - https://mtuci.ru/')
    elif message.text.lower() == "расписание":
        keyboard = types.ReplyKeyboardMarkup()
        keyboard.row("Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота")
        keyboard.row('На эту неделю', 'На следующую неделю')
        bot.send_message(message.chat.id, 'Выбери команду', reply_markup=keyboard)
    elif message.text.upper() in ['ПОНЕДЕЛЬНИК', 'ВТОРНИК', 'СРЕДА', 'ЧЕТВЕРГ', 'ПЯТНИЦА', 'СУББОТА']:
        bot.send_message(message.chat.id, get_day(weekdays[message.text.upper()], week))
    elif message.text.lower() == 'на эту неделю':
        bot.send_message(message.chat.id, get_week(week, 0))
    elif message.text.lower() == 'на следующую неделю':
        bot.send_message(message.chat.id, get_week(next_week, 7))

bot.polling()
