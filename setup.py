"This is a scrapper for Jingdaily"
"Put your search topics in keywords"
"Install find all the require packages in requirements.txt"
"Author: Arnauld Adjovi"

import json
import time
import pandas as pd

from run_scrapping import *
from time import sleep

with open('keywords.txt') as file, open('utilis/summary.json') as json_file:
    data = file.read().split(',')
    summary = json.load(json_file)

logs = []
for i in range(len(summary)):
    logs.append(summary[i]['tag'])

trials = 3
results = None
for index, tag in enumerate(data):
    keywords = tag.strip()
    print(keywords)
    if keywords not in logs:
        while True:
            if trials == 0 : break
            try:
                results = get_summary(keywords=keywords, save_steps=1)
                break
            except:
                sleep(4 - trials)
                trials -= 1
    if results is not None:
        summary.append({'index': index, 'tag': keywords, 'Nb_articles':results[1]})
        with open('summary.json', 'w') as json_file:
            json.dump(summary, json_file)
    print()


### Save to excel #####
df = pd.DataFrame(summary)

df =  df.sort_values(by = ['Nb_articles', 'tag'], ascending=[False, True])
df = df.drop_duplicates(subset='tag', keep='first')
df

##### set groups #########
gk = df.groupby('Nb_articles')
print(gk.groups[0])
gk.get_group(0).sort_values('tag')
df.to_excel(r'tagsExport.xlsx', 'Sheet1', index=False)

