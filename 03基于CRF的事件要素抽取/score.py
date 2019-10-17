# -*- coding:utf-8 -*-
# author:ZHANG SHIWEI
# datetime:2019/6/10 0010

with open("output05.txt", "r", encoding="utf-8") as f1:
    contents = f1.read().splitlines()
    count = 0
    real_count = 0
    tp = 0
    fp = 0
    fn = 0
    tn = 0

    for i in range(len(contents)):
        if len(contents[i]) > 1:
            real_count += 1
            if contents[i].split("\t")[-2] != "O":
                if contents[i].split("\t")[-1] == contents[i].split("\t")[-2]:
                    tp += 1
                else:
                    fn += 1
            else:
                if contents[i].split("\t")[-1] != "O":
                    fp += 1
                else:
                    tn += 1
    P = tp / (tp + fp)
    R = tp / (tp + fn)
    F1 = 2 * P * R / (P + R)
    print("P=" + str(P))
    print("R=" + str(R))
    print("F1=" + str(F1))
