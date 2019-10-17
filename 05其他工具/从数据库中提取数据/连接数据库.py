# -*- coding: utf-8 -*-
"""
Created on Mon May  6 19:48:46 2019
@author: ZHANG SHIWEI
"""
import MySQLdb
import os

# 连接数据库
conn = MySQLdb.connect(
    host="127.0.0.1",
    user="root",
    passwd="7473158zhang",
    db="law",
    charset='utf8')
cur = conn.cursor()

# 执行数据库的操作cur.execute
cur.execute('select 法院意见,判决结果 from 裁判文书')
rows = cur.fetchall()

# 将查询结果写入文件
f = open('/Users/zhangshiwei/基于法律裁判文书的事件抽取和应用/01数据预处理/original_data.txt', 'w', encoding='utf-8')
for i in range(len(rows)):
    # 每行加上序号
    # f.write(str(i + 1) + ": ")
    for j in rows[i]:
        f.write(str(j))
    f.write("\n")

f.close()
conn.close()
