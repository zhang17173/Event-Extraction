import csv
from collections import Counter

with open("result.csv", "r") as f:
    f_csv = csv.reader(f)
    true_0, true_1, true_2 = 0, 0, 0
    false_0, false_1, false_2 = 0, 0, 0
    pred_1 = []
    for row in f_csv:
        if row[-2] == '0':
            if row[-1] == row[-2]:
                true_0 += 1
            else:
                false_0 += 1
        if row[-2] == '1':
            if row[-1] == row[-2]:
                true_1 += 1
            else:
                false_1 += 1
                pred_1.append(row[-1])
        if row[-2] == '2':
            if row[-1] == row[-2]:
                true_2 += 1
            else:
                false_2 += 1

true_count = true_0 + true_1 + true_2
total_count = true_count + false_0 + false_1 + false_2
print("total:%d" % total_count)
print("true:%d" % true_count)
print("class" + '\t' + "total" + '\t' + "true" + '\t' + "false" + '\t')
print("0" + '\t' + str(true_0 + false_0) + '\t' + str(true_0) + '\t' + str(false_0))
print("1" + '\t' + str(true_1 + false_1) + '\t' + str(true_1) + '\t' + str(false_1))
print("2" + '\t' + str(true_2 + false_2) + '\t' + str(true_2) + '\t' + str(false_2))

headers = ['01死亡人数', "02重伤人数", "04责任认定", "05是否酒后驾驶", "06是否吸毒后驾驶", "07是否无证驾驶", "08是否无牌驾驶", "09是否不安全驾驶", "10是否超载",
           "11是否逃逸", "12是否抢救伤者", "13是否报警", "14是否现场等待", "15是否赔偿", "16是否认罪", "18是否初犯偶犯", "判决结果"]

f1 = open("/home/zhangshiwei/Event-Extraction/01数据预处理/preprocessed_data.txt", "r", encoding="utf-8")
cases = f1.readlines()
f2 = open("result.csv", "r")
f3 = open("test16.csv")
f3_csv = list(csv.reader(f3))
print(f3_csv)
f4 = open("analysis.txt", "a", encoding="utf-8")

f2_csv = list(csv.reader(f2))
for i in range(len(f2_csv)):
    if f2_csv[i][1] == '1':
        f4.write(cases[12000 + i])
        f4.write(' '.join(f3_csv[i]) + '\n')
        for j in range(2, 16):
            if f3_csv[i][j] == '1':
                f4.write(headers[j] + ' ')
        f4.write('\n')
        f4.write(f2_csv[i][0] + '\n\n')
f1.close()
f2.close()
f3.close()
f4.close()
