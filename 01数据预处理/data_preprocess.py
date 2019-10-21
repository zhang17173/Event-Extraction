# -*- coding:utf-8 -*-
# author:ZHANG SHIWEI
# datetime:2019/4/15

import re
from random import shuffle

# 标点符号和特殊字母
punctuation = '''，。、:；（）ＸX×xa"“”,<《》'''

# 对原始数据进行处理
f1 = open("original_data.txt", "r", encoding='utf-8')
preprocessed_cases = []  # 存储处理过后的案件
for line in f1.readlines():
    line = line.strip()
    location = line.split("\t")[0]  # 存储案件对应的地区
    line = line.split("\t")[-1]
    line1 = re.sub(u"（.*?）", "", line)  # 去除括号内注释
    line2 = re.sub("[%s]+" % punctuation, "", line1)  # 去除标点、特殊字母
    # 去除冗余词
    line3 = re.sub(
        "本院认为|违反道路交通管理法规|驾驶机动车辆|因而|违反道路交通运输管理法规|违反交通运输管理法规|缓刑考.*?计算|刑期.*?止|依照|《.*?》|第.*?条|第.*?款|的|了|其|另|已|且",
        "",
        line2)
    # 删除内容过少或过长的文书，删除包含’保险‘的文书，只保留以’被告人‘开头的文书
    if 100 < len(line3) < 400 and line3.startswith(
            "被告人") and "保险" not in line3:
        preprocessed_cases.append(location + '\t' + line3)
f1.close()

# 将处理过后的案件写到文本中
f2 = open("preprocessed_data.txt", "w", encoding='utf-8')
# 打乱数据
shuffle(preprocessed_cases)
for idx, preprocessed_case in enumerate(preprocessed_cases):
    f2.write(str(idx + 1) + "\t" + preprocessed_case + "\n")
f2.close()
