#!/usr/bin/env python
# _*_coding:utf-8 _*_
# @Author:Zhang Shiwei
# @Date  :2019-07-21

with open("完整数据.data", "r", encoding="utf-8") as f1:
    data = f1.readlines()
    num = 1
    file_name = '元数据/' + str(num) + '.txt'
    for i in range(len(data)):
        f2 = open(file_name, "a", encoding='utf-8')
        if data[i] == '\n':
            num += 1
            file_name = '元数据/' + str(num) + '.txt'
        else:
            f2.writelines(data[i])
