# -*- coding:utf-8 -*-
# author:ZHANG SHIWEI
# datetime:2019/5/16 0016
import os
import time

with open("new_train.data", "r", encoding='utf-8') as f1:
    contents = f1.read().splitlines()
    len_contents = len(contents)  # train.data的行数
    lines_with_error = []   # 存储存在错误的行号
    blanks_count = 0
    j = 0
    file_name = "train" + str(j) + ".data"  # 将train.data拆分成若干个文件

    for i in range(len_contents):
        f2 = open(file_name, "a", encoding='utf-8')
        f2.write(contents[i] + '\n')
        if contents[i] == '' or contents[i] == '   ':
            contents[i] == ''
            blanks_count += 1
            if blanks_count % 2 == 0:   # f2已包含两段，对其进行训练检测
                j += 1  # 文件索引增1
                os.popen("crf_learn template01 " + file_name + " model")
                print("Start...", end='')
                time.sleep(2)
                if os.path.exists("model"):
                    print("Success!!!")
                    os.remove("model")
                else:
                    lines_with_error.append(i)
                file_name = "train" + str(j) + ".data"  # 新创建文件
        f2.close()
print(lines_with_error)

for k in range(0, j + 1):   # 清除中间文件
    os.remove("train" + str(k) + ".data")
