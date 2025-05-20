from selenium import webdriver
from selenium.webdriver.chrome.service import Service  # помогает запускать ChromeDriver
from selenium.webdriver.common.by import By  # для выбора элементов на странице
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import telebot
import webbrowser
from telebot import types
import os
from dotenv import load_dotenv
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
        markup = types.InlineKeyboardMarkup()
        points = 0
        botik.send_message(call.message.chat.id, "Запускаю игру!")

        n = random.randint(0, len(lst) - 1)
        word = (lst[n])['word']
        botik.send_message(call.message.chat.id, f"Как думаешь, что значит слово: <b>{word}</b>?", parse_mode='html')

        vallist = []
        correct = (lst[n])['meaning']
        vallist.append(correct)
        lst.remove(lst[n])

        count = 0
        while count != 3:
            n = random.randint(0, len(lst) - 1)
            val = (lst[n])['meaning']
            if val not in vallist:
                vallist.append(val)
                count += 1

        random.shuffle(vallist)

        markup.add(types.InlineKeyboardButton(vallist[0], callback_data='var1'))
        markup.add(types.InlineKeyboardButton(vallist[1], callback_data='var2'))
        markup.add(types.InlineKeyboardButton(vallist[2], callback_data='var3'))
        markup.add(types.InlineKeyboardButton(vallist[3], callback_data='var4'))

        botik.send_message(call.message.chat.id, "Выбери правильный вариант:", reply_markup=markup)


    elif call.data == 'goodbye':
        botik.send_message(call.message.chat.id, "Хорошего дня! Приходи, когда надумаешь играть \U0001F609")
    elif call.data == 'site':
        webbrowser.open('https://yandex.ru/company/researches/2021/local-words')
botik.polling(none_stop=True)

lst = []
for line in parsed:
    lst.append(line)
rounds = 0
while rounds != 10 and len(lst) >= 4:
    dicright = dict()
    vallist = []
    n = random.randint(0, len(lst))
    word = (lst[n])['Слово']
    val = (lst[n])['Значение']
    dicright[word] = val
    vallist.append(val)
    lst.remove(lst[n])
    count = 0
    while count != 3:
        n = random.randint(0, len(lst))
        val = (lst[n])['Значение']
        vallist.append(val)
        count += 1
    random.shuffle(vallist)
    choice = input() #пока не интегрирую в ботовские термины
    if choice == dicright[word]:
        round += 1
    elif choice != dicright[word] and len(vallist) != 1:
        vallist.remove(choice)
        choice = input()
    elif len(vallist) == 1:
        round += 1
