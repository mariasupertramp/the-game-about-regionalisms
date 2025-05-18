import telebot
import webbrowser
from telebot import types
import os
from dotenv import load_dotenv

load_dotenv()

botik = telebot.TeleBot(os.getenv('token'))
@botik.message_handler(commands=['site'])
def site(message):
    webbrowser.open('https://yandex.ru/company/researches/2021/local-words')

@botik.message_handler(commands=['start'])
def main(message):

    markup = types.InlineKeyboardMarkup()
    com1 = types.InlineKeyboardButton("Начать угадывать", callback_data='startgame')
    com2 = types.InlineKeyboardButton("Правила игры", callback_data='rules')
    com3 = types.InlineKeyboardButton("До свидания", callback_data='goodbye')
    com4 = types.InlineKeyboardButton("Сайт-источник", callback_data='site')
    markup.add(com1, com2, com3, com4)
    botik.send_message(message.chat.id,f'Привет, {message.from_user.first_name}. Это бот для игры-угадайки регионализмов. '
                                       f'Испытай свое лингвистическое чутье и попробуй определить, какое из значений верное. '
                                       f'Чтобы начать играть, нажми <b>Начать угадывать</b>. '
                                       f'Если ты здесь в первый раз, сначала ознакомься с правилами, нажав <b>Правила игры</b>. '
                                       f'Если у тебя нет желания играть, нажми <b>До свидания</b>. '
                                       f'За основу были взяты слова с сайта исследований Яндекса (куда можно попасть, нажав <b>Сайт-источник</b>), '
                                       f'но не рекомендую заходить на него до игры, '
                                       f'потому что тогда в ней не будет смысла.', parse_mode='html', reply_markup=markup)
@botik.callback_query_handler(func=lambda call: True)
def call_black(call):
    if call.data == 'startgame':
        botik.send_message(call.message.chat.id, "Запускаю игру!")
    elif call.data == 'rules':
        markup = types.InlineKeyboardMarkup()
        com1 = types.InlineKeyboardButton("Начать угадывать", callback_data='startgame')
        com3 = types.InlineKeyboardButton("До свидания", callback_data='goodbye')
        markup.add(com1,com3)
        botik.send_message(call.message.chat.id, "Правила игры:\n 1. Тебе рандомно выпадут слово-регионализм и 4 варианта ответа"
                                                 " – возможные значения этого слова.\n 2. У тебя будет три попытки угадать значение "
                                                 "слова.\n 3. Когда отгадаешь значения или у тебя закончатся попытки, ты получишь пример употребления регионализма и "
                                                 "место его распространения,.\n 4. В любой момент ты можешь завершить игру, нажав "
                                                 "“До свидания”.\n", reply_markup=markup)

    elif call.data == 'goodbye':
        botik.send_message(call.message.chat.id, "Хорошего дня! Приходи, когда надумаешь играть \U0001F609")
    elif call.data == 'site':
        webbrowser.open('https://yandex.ru/company/researches/2021/local-words')
botik.polling(none_stop=True)

