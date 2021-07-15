# -*- coding:utf-8 -*-
# author:ZHANG SHIWEI
# datetime:2019/4/15

import re
from random import shuffle

# 定义标点符号和特殊字母
punctuation = '''，。、:；（）ＸX×xa"“”,<《》'''

# 裁判文书原始文件路径
original_file = "original_data.txt"
processed_file = "processed_data.txt"


def data_process():
    # 对原始数据进行预处理
    f1 = open(original_file, "r", encoding='utf-8')
    processed_cases = []  # 存储处理后的案件
    for line in f1.readlines():
        try:
            location, content = line.strip().split("\t")  # 存储案件对应的地区、内容
        except ValueError:
            continue
        else:
            line1 = re.sub(u"（.*?）", "", content)  # 去除括号内注释
            line2 = re.sub("[%s]+" % punctuation, "", line1)  # 去除标点、特殊字母
            # 去除冗余词
            line3 = re.sub(
                "本院认为|违反道路交通管理法规|驾驶机动车辆|因而|违反道路交通运输管理法规|违反交通运输管理法规|缓刑考.*?计算|刑期.*?止|依照|《.*?》|第.*?条|第.*?款|的|了|其|另|已|且",
                "",
                line2)
            # 删除内容过少或过长的文书，删除包含’保险‘的文书，只保留以’被告人‘开头的文书
            if 100 < len(line3) < 400 and line3.startswith(
                    "被告人") and "保险" not in line3:
                processed_cases.append(location + '\t' + line3)
    f1.close()

    # 打乱数据
    shuffle(processed_cases)

    # 将预处理后的案件写到文本中
    f2 = open(processed_file, "w", encoding='utf-8')
    for idx, case in enumerate(processed_cases):
        f2.write(str(idx + 1) + "\t" + case + "\n")
    f2.close()
    print("数据预处理完成！")


if __name__ == '__main__':
    data_process()
