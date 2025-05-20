from random import choices
from threading import Timer
from selenium import webdriver
from selenium.webdriver.chrome.service import Service  # помогает запускать ChromeDriver
from selenium.webdriver.common.by import By  # для выбора элементов на странице
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import telebot
import webbrowser
import os
from dotenv import load_dotenv
load_dotenv()
from telebot import types
import pandas as pd
from json import loads, dumps
import random

options = Options()  # нужно настроить браузер
options.add_argument("--headless")  # запуск в фоновом режиме, т.е. без окна браузера

# эта штука должна скачать драйвер для хрома и запустить браузер с нужными мне настройками, которые выше
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://yandex.ru/company/researches/2021/local-words"
driver.get(url)
time.sleep(5)
blocks = driver.find_elements(By.CLASS_NAME, "word-block")  # ищу все элементы с этим классом

botik = telebot.TeleBot(os.getenv('token'))
@botik.message_handler(commands=['site'])
def site(message):
    webbrowser.open('https://yandex.ru/company/researches/2021/local-words')

words = []
for block in blocks:
    words.append({
        "word": block.find_element(By.CLASS_NAME, "word-block__title").text.strip(),
        "meaning": block.find_element(By.CLASS_NAME, "word-block__description").text.strip(),
        "example": block.find_element(By.CLASS_NAME, "word-block__example").text.strip(),
        "region": block.find_element(By.CLASS_NAME, "word-block__regions").text.strip()
    })

driver.quit()

with open("local_words.json", "w", encoding="utf-8") as f:
    json.dump(words, f, ensure_ascii=False, indent=2)

data = pd.read_json("local_words.json", orient="records")
tojson = data.to_json(orient="records")
parsed = loads(tojson)
lst = []
for line in parsed:
    lst.append(line)

@botik.message_handler(commands=['start'])
def main(message):

    markup = types.InlineKeyboardMarkup()
    com1 = types.InlineKeyboardButton("Начать угадывать", callback_data='startgame')
    com2 = types.InlineKeyboardButton("Правила игры", callback_data='rules')
    com3 = types.InlineKeyboardButton("До свидания", callback_data='goodbye')
    com4 = types.InlineKeyboardButton("Сайт-источник", url='https://yandex.ru/company/researches/2021/local-words')
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
    if call.data == 'rules':
        markup = types.InlineKeyboardMarkup()
        com1 = types.InlineKeyboardButton("Начать угадывать", callback_data='startgame')
        com3 = types.InlineKeyboardButton("До свидания", callback_data='goodbye')
        markup.add(com1,com3)
        botik.send_message(call.message.chat.id, "Правила игры:\n 1. В игре 10 раундов, за каждый из "
                                                 "которых ты можешь получить 1 балл.\n 2. Тебе рандомно выпадут "
                                                 "слово-регионализм и 4 варианта ответа – возможные значения этого "
                                                 "слова.\n 3. У тебя будет одна попытка угадать значение слова.\n 4. "
                                                 "Вместе с правильным ответом ты сможешь посмотреть пример употребления регионализма "
                                                 "и место, в котором он распространен.", reply_markup=markup)
    elif call.data == 'goodbye':
        botik.send_message(call.message.chat.id, "Чудесного дня! Приходи, когда надумаешь играть \U0001F609")

    elif call.data == 'startgame':
        chat_id = call.message.chat.id
        game[chat_id] = {
            'gamepoints': 0,
            'rounds': 0,
            'words': lst.copy()
        }
        new_round(chat_id)

    elif call.data.startswith('var'):
        choice_index = int(call.data[-1]) - 1
        chat_id = call.message.chat.id
        user_data = game.get(chat_id)

        if not user_data or 'current_answer' not in user_data:
            botik.send_message(chat_id, "Пожалуйста, начни игру сначала, я не в ресурсе.")
            return

        chosen_meaning = user_data['current_options'][choice_index]
        correct_meaning = user_data['current_answer']

        if chosen_meaning == correct_meaning:
            user_data['gamepoints'] += 1
            botik.send_message(chat_id, "💅Ну крутышка! Поздравляю, это верно :)")
        else:
            botik.send_message(chat_id, f"😋А вот и нет! хихи. На самом деле: {correct_meaning}")

        # Показ примера и региона
        botik.send_message(chat_id, f"Говорят так: {user_data['example']}\nИспользуют тут: {user_data['region']}")
        Timer(5, lambda: new_round(chat_id)).start()


def new_round(chat_id):
    user_data = game[chat_id]
    if user_data['rounds'] >= 10 or len(words) < 4:
        botik.send_message(chat_id, f"Всё! Конец. Вот сколько очков мы тебе насчитали: {user_data['gamepoints']}/10.")
        return
    choices = []
    user_data['rounds'] += 1
    random_word = random.choice(user_data['words'])
    user_data['words'].remove(random_word)
    cor_word = random_word['word']
    cor_mean = random_word['meaning']
    choices.append(cor_mean)
    cor_ex = random_word['example']
    cor_reg = random_word['region']
    while len(choices) < 4:
        wr_mean = random.choice(user_data['words'])['meaning']
        if wr_mean not in choices:
            choices.append(wr_mean)
    random.shuffle(choices)

    text_block = '\n'.join([f'{i + 1}. {opt}' for i, opt in enumerate(choices)])
    markup = types.InlineKeyboardMarkup(row_width=4)
    buttons = [types.InlineKeyboardButton(str(i + 1), callback_data=f'var{i + 1}') for i in range(4)]
    markup.add(*buttons)
    user_data['current_answer'] = cor_mean
    user_data['current_options'] = choices
    user_data['example'] = cor_ex
    user_data['region'] = cor_reg
    botik.send_message(chat_id, f'Как думаешь, что значит <b>{cor_word}</b>?\n\n{text_block}', parse_mode='html',
                       reply_markup=markup)


@botik.message_handler(func=lambda message: not message.text.startswith('/'), content_types=['text'])
def unknown_message(message):
    botik.send_message(message.chat.id, "Нормально же общались, ну чего ты :(. "
                                        "Используй кнопки, чтобы управлять ботом")
botik.polling(none_stop=True)
