import pandas as pd
import numpy as np

import requests

from bs4 import BeautifulSoup

from selenium import webdriver
import re

import warnings; warnings.filterwarnings('ignore')

df = pd.read_excel(r"C:/Users/Admin/Desktop/GREGMAT PREP/GregMat_list_with_meaning.xlsx","Sheet1")
renamer = [[0,1],[9,10],[17,18]]

df_words = pd.DataFrame()
for i in range(len(renamer)):
    print(renamer[i])
    df_temp = df.iloc[:,renamer[i]].dropna(how='all')
    df_temp.columns = ['WORD', 'MEANING']
    df_words = df_words.append(df_temp)
    

df_words['GROUP'] = df_words['WORD'].apply(lambda x: x if 'Group ' in str(x) else np.nan)
df_words[['WORD','GROUP']] = df_words[['WORD','GROUP']].fillna(method = 'ffill')
df_words = df_words[df_words['WORD'].apply(lambda x: x.split()[0] not in ['Group','Take','Word'])]
df_words2 = df_words.dropna(how = 'any').groupby(['GROUP','WORD'])['MEANING'].apply(lambda x: "\n".join(x)).reset_index()
df_words2['GROUP NO'] = df_words2['GROUP'].apply(lambda x: int(x.split()[-1]))
df_words2['GROUP'].value_counts()

#%%
df_words2['WORD'] = df_words2['WORD'].apply(lambda x: str(x).strip().lower())
main_list = df_words2['WORD'].unique()
final_dict = {}
for k,word in enumerate(main_list):
    print(k+1, ") " + word)
    final_dict[word] = []
    
    url = f'https://www.google.com/search?q={word}%20word%20meaning#dobc=en'
    # driver = webdriver.Chrome("C:/Users/Admin/Desktop/GREGMAT PREP/chromedriver.exe")
    # driver.get(url)
    # text = driver.find_element_by_tag_name('body').text


    response = requests.get(url)
    a = response.text
    soup = BeautifulSoup(a, 'html.parser')
    text = soup.get_text()
    
    final = [a for a in text.split("synonyms:")[1:]]
    for vaakya in final:
        for sent in vaakya.split(","):
            sent = sent.strip()
            if sent == "": continue
            cap = re.sub("[^A-Z]","",sent[1:])
            if len(cap)>0:
                final_dict[word].append(sent.split(cap)[0])
                break
            final_dict[word].append(sent)
        if 'People also ask' in vaakya: break
    
    final_dict[word] = [i for i in final_dict[word] if len(i)<45]
    
    
#%%
final_dict2 = {k:", ".join(v) for k,v in final_dict.items()}
final_df = pd.DataFrame(final_dict2, index = [0]).T.reset_index()
final_df.columns = ['WORD','SYNONYMS']


df2 = df_words2.merge(final_df, on = 'WORD', indicator = True, how='outer')

