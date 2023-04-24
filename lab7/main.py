import telebot
from telebot import types

token = "6199890693:AAF1FUQzeSnfX_8xOfyg6-2RxIZQO1IU6ic"
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row("Хочу", "Не хочу", "/compliment", "/help")
    bot.send_message(message.chat.id, 'Привет! Хочешь узнать свежую информацию о МТУСИ?', reply_markup=keyboard)

@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id, 'Я умею...')

@bot.message_handler(commands=['compliment'])
def compliment(message):
    bot.send_message(message.chat.id, 'Вы сегодня как никогда прекрасно выглядите!')



@bot.message_handler(content_types=['text'])
def answer(message):
    if message.text.lower() == "хочу":
        bot.send_message(message.chat.id, 'Тогда тебе сюда - https://mtuci.ru/')

bot.polling(none_stop=True)
