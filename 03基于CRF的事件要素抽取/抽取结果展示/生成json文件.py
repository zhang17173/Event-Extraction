#!/usr/bin/env python
# _*_coding:utf-8 _*_
# @Author:Zhang Shiwei
# @Date  :2019-07-21

import 展示每个案件的事件要素
import json

dd = dict()
txt_num = 694 + 1
for i in range(1, txt_num):
    file_name = "元数据/" + str(i) + ".txt"
    dd[i] = 展示每个案件的事件要素.func(file_name)

with open("案件事件要素统计.json", "w", encoding='utf-8') as f:
    json.dump(dd, f, ensure_ascii=False)

# 减刑因素规范化
positive = []
for i in range(1, txt_num):
    positive += dd[i]["减刑因素"]
for i in range(len(positive)):
    if "自首" in positive[i] or "投案" in positive[i]:
        positive[i] = "自首"
    elif "谅解" in positive[i] or "取得" in positive[i]:
        positive[i] = "取得谅解"
    elif "赔偿" in positive[i]:
        positive[i] = "赔偿被害人"
    elif "如实供述" in positive[i] or "坦白" in positive[i]:
        positive[i] = "如实供述"
    elif "认罪" in positive[i]:
        positive[i] = "自愿认罪"


# 加刑因素规范化
negative = []
for i in range(1, txt_num):
    negative += dd[i]["加刑因素"]
for i in range(len(negative)):
    if "逃" in negative[i]:
        negative[i] = "逃逸"
    elif "无证" in negative[i] or "驾驶资格" in negative[i] or "驾驶证" in negative[i] or "无牌" in negative[i]:
        negative[i] = "无牌或无证驾驶"
    elif "酒" in negative[i]:
        negative[i] = "酒后驾驶"
    elif "超速" in negative[i]:
        negative[i] = "超速"
