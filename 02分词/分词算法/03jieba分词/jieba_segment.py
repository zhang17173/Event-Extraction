#!/usr/bin/env python
# _*_coding:utf-8 _*_
# @Author:Zhang Shiwei
import jieba
with open("test.txt", "r", encoding='utf-8') as f1:
    text = f1.read()
    seg_list = jieba.cut(text)
    f2 = open("result.txt", "a", encoding='utf-8')
    for word in seg_list:
        f2.write(word + " ")
    f2.close()

