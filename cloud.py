import os
import random
import math
from datetime import datetime
from collections import Counter
import re
import openpyxl
import pandas as pd
from nltk.corpus import stopwords
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet as wn

# 查找常见短语
common_phrases = set()
for syn in wn.all_synsets():
    for lemma in syn.lemmas():
        if '_' in lemma.name():
            common_phrases.add(lemma.name())

# 期刊列表
journals_list = set(['Public Administration Review', 'Public Management Review', 'Policy Sciences', 'Journal of Policy Analysis and Management', 'Journal of European Public Policy', 'Climate Policy', 'Policy and Society', 'Review of Public Personnel Administration', 'Governance-An International Journal of Policy Administration and Institutions', 'Regulation & Governance', 'Social Policy & Administration', 'Public Performance & Management Review'])

# 停用词
stop_words = set(stopwords.words('english'))
title = 1
journal = 4
key_word = 5
max_display_number = 100

# 指定文件夹路径
folder_path = 'lib'
save_path = 'data'
file_names = os.listdir(folder_path)
files = [f for f in file_names if os.path.isfile(os.path.join(folder_path, f))]
sentences = []
unique_key_words = set()

for file in files:
    # 导入 Excel 文件
    filename = os.path.join(folder_path, file)
    print('Processing: '+filename+'...')

    df_list = pd.read_html(filename)  # 返回一个包含所有表格的列表
    # 假设你要处理第一个表格
    if df_list:
        df = df_list[0]  # 获取第一个表格
        # 提取title和key word的所有数据
        column_data = df[title]
        sentences += df[title].tolist()

        # 更新关键词集合
        journal_data = df[journal].tolist()
        key_words = df[key_word].tolist()
        random.shuffle(key_words)

        for i in range(len(key_words)):
            key_word_sentence = key_words[i]
            journal_data_sentence = journal_data[i]
            if journal_data_sentence not in journals_list:
                continue
            elif type(key_word_sentence) == str:
                splited_text = re.split(r'[;()]', key_word_sentence)       
                unique_words = unique_key_words.update(splited_text)

    else:
        print("未找到任何表格。")

print(unique_key_words)
pattern = r'\b(?:' + '|'.join(re.escape(phrase) for phrase in unique_key_words) + r')\b'
# 对句子清洗一下
words = []
for i in range(len(sentences)):
    sentence = sentences[i]
    cleaned_sentence = re.sub(r'\S+\s+pp.*', '', sentence)
    specialized_sentence = re.sub(pattern, lambda x: x.group(0).replace(" ", "_"), cleaned_sentence)
    sentences[i] = specialized_sentence

# 将所有句子合并为一个字符串
all_text = ' '.join(sentences)
# 打散成单词，使用正则表达式去除标点符号并改为小写
words = re.findall(r'\w+(?:-\w+)*', all_text.lower())
unique_key_words = {s.replace(' ', '_') for s in unique_key_words}
words = [word for word in words if word in unique_key_words and word not in stop_words]
# 统计单词频次
word_counts = Counter(words)

# 打印统计结果
for word, count in word_counts.most_common(max_display_number):  # 打印前n个单词及其频次
    print(f'{word}: {count}')

df = pd.DataFrame(word_counts.items(), columns=['Word', 'Count'])
# 保存为 CSV 文件
current_time = datetime.now()
formatted_time = current_time.strftime("%Y-%m-%d_%H-%M-%S")
df = df.sort_values(by='Count', ascending=False)
df.to_csv(os.path.join(save_path, '{}_word_counts.csv'.format(formatted_time)), index=False)


print('Done.')
