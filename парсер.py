# это код для парсера, который я написала ещё в самом начале, но потом выяснилось, что с этого сайта
# так спарсить не получится, потому что там идёт подгрузка данных через джаву скрипт, поэтому пришлось разбираться с селениумом

# import requests
# from bs4 import BeautifulSoup
#
# url = "https://yandex.ru/company/researches/2021/local-words"
#
# h = {
#     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"}  # чтобы сайт не ругался на меня, типа я ботиха :)
# response = requests.get(url, headers=h)
# s = BeautifulSoup(response.text, "html.parser")
# words = []
# blocks = s.find_all("div", class_="word-block")
#
# for block in blocks:
#     word = block.find("span", class_="word-block__title")  # само слово ищу
#     meaning = block.find("span", class_="word-block__description")  # значение слова
#     example = block.find("span", class_="word-block__example")  # пример употребления
#     region = block.find("span", class_="word-block__regions")  # регион
#
#     words.append({
#         "word": word,
#         "meaning": meaning,
#         "example": example,
#         "region": region
#     })


from selenium import webdriver
from selenium.webdriver.chrome.service import Service  # помогает запускать ChromeDriver
from selenium.webdriver.common.by import By  # для выбора элементов на странице
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

options = Options()  # нужно настроить браузер
options.add_argument("--headless")  # запуск в фоновом режиме, т.е. без окна браузера

# эта штука должна скачать драйвер для хрома и запустить браузер с нужными мне настройками, которые выше
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://yandex.ru/company/researches/2021/local-words"
driver.get(url)
time.sleep(5)
blocks = driver.find_elements(By.CLASS_NAME, "word-block")  # ищу все элементы с этим классом

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
