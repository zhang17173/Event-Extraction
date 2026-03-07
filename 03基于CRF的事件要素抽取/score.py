# -*- coding:utf-8 -*-
# author:ZHANG SHIWEI
# datetime:2019/6/10 0010

with open("output05.txt", "r", encoding="utf-8") as f1:
    contents = f1.read().splitlines()
    tp = 0
    fp = 0
    fn = 0
    tn = 0

    for line in contents:
        if len(line) <= 1:
            continue
        parts = line.split("\t")
        gold = parts[-2]
        pred = parts[-1]
        if gold != "O":
            if pred == gold:
                tp += 1
            else:
                fn += 1
        elif pred != "O":
            fp += 1
        else:
            tn += 1

    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
    print("P=" + str(precision))
    print("R=" + str(recall))
    print("F1=" + str(f1))
