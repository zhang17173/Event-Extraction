import csv
from collections import Counter
import os

with open("result.csv", "r") as f:
    f_csv = csv.reader(f)
    true_0, true_1, true_2, true_3, true_4 = 0, 0, 0, 0, 0
    false_0, false_1, false_2, false_3, false_4 = 0, 0, 0, 0, 0
    false_pred_0 = []
    false_pred_2 = []
    false_pred_4 = []
    for row in f_csv:
        if row[-2] == '0':
            if row[-1] == row[-2]:
                true_0 += 1
            else:
                false_0 += 1
                false_pred_0.append(row[-1])
        if row[-2] == '1':
            if row[-1] == row[-2]:
                true_1 += 1
            else:
                false_1 += 1
        if row[-2] == '2':
            if row[-1] == row[-2]:
                true_2 += 1
            else:
                false_2 += 1
                false_pred_2.append(row[-1])
        if row[-2] == '3':
            if row[-1] == row[-2]:
                true_3 += 1
            else:
                false_3 += 1
        if row[-2] == '4':
            if row[-1] == row[-2]:
                true_4 += 1
            else:
                false_4 += 1
                false_pred_4.append(row[-1])

true_count = true_0 + true_1 + true_2 + true_3 + true_4
total_count = true_count + false_0 + false_1 + false_2 + false_3 + false_4

print("total:%d" % total_count)
print("true:%d" % true_count)
print("class" + '\t' + "total" + '\t' + "true" + '\t' + "false" + '\t')
print("0" + '\t' + str(true_0 + false_0) + '\t' + str(true_0) + '\t' + str(false_0))
print("1" + '\t' + str(true_1 + false_1) + '\t' + str(true_1) + '\t' + str(false_1))
print("2" + '\t' + str(true_2 + false_2) + '\t' + str(true_2) + '\t' + str(false_2))
print("3" + '\t' + str(true_3 + false_3) + '\t' + str(true_3) + '\t' + str(false_3))
print("4" + '\t' + str(true_4 + false_4) + '\t' + str(true_4) + '\t' + str(false_4))
print(Counter(false_pred_0))
print(Counter(false_pred_2))
print(Counter(false_pred_4))

# 导出错误数据
headers = ['01死亡人数', "02重伤人数", "04全部责任", "05酒后驾驶", "06吸毒后驾驶", "07无证驾驶", "08无牌驾驶", "09不安全驾驶", "10超载",
           "11逃逸", "12抢救伤者", "13报警", "14现场等待", "15赔偿", "16认罪", "18初犯偶犯", "判决结果"]

f1 = open("/home/zhangshiwei/Event-Extraction/01数据预处理/preprocessed_data.txt", "r", encoding="utf-8")
cases = f1.readlines()

f3 = open("test16.csv")
f3_csv = list(csv.reader(f3))

f2 = open("result.csv", "r")
f2_csv = list(csv.reader(f2))

if os.path.exists("analysis.txt"):
    os.remove("analysis.txt")

f5 = open("test5_noises.csv")
f5_csv = list(csv.reader(f5))

f4 = open("analysis.txt", "a", encoding="utf-8")
for i in range(len(f2_csv)):
    if f2_csv[i][1] == '4' and f2_csv[i][-1] != f2_csv[i][1]:
        f4.write(cases[20000 + i])
        f4.write("真实判决结果：" + f5_csv[i][-1] + "\n")
        f4.write("消噪后的类别：" + str(f2_csv[i][1]) + "\n" + "预测类别：" + str(f2_csv[i][-1]) + "\n")
        f4.write("16维特征：" + ' '.join(f3_csv[i]) + '\n')
        for j in range(2, 16):
            if f3_csv[i][j] == '1':
                f4.write(headers[j] + ' ')
        f4.write('\n')
        f4.write("5维特征：" + f2_csv[i][0] + '\n\n\n')
f1.close()
f2.close()
f3.close()
f4.close()
