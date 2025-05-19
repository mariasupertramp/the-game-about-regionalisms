import pandas as pd
from json import loads, dumps
import random


data = pd.read_json("local_words.json", orient="records")
tojson = data.to_json(orient="records")
parsed = loads(tojson)
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
    
