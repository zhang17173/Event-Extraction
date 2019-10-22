import csv
import numpy as np
from random import shuffle


def data_split(data_csv):
    """
    将原始数据分割成训练集和测试集
    :param data_csv:原始数据
    :return:
    """
    with open(data_csv) as f:
        f_csv = csv.reader(f)
        rows = list()
        for row in f_csv:
            rows.append(row)
        del (rows[0])  # 去除表头
        # 打乱顺序
        # shuffle(rows)
        rows_train = rows[:13000]
        rows_test = rows[13000:]
        with open("train16.csv", "w") as f_train:
            f_train_csv = csv.writer(f_train)
            f_train_csv.writerows(rows_train)
        with open("test16.csv", "w") as f_test:
            f_test_csv = csv.writer(f_test)
            f_test_csv.writerows(rows_test)


def patterns_weight(csv_file, new_csv_file):
    """
    给特征加权，然后将16个特征变为5个特征，以减轻数据的稀疏性
    :param csv_file: 不带表头的源文件，16个特征
    :param new_csv_file:加权之后的文件，5个特征
    :return:
    """
    f1 = np.loadtxt(csv_file, delimiter=',', dtype=np.int)
    new_csv_list = []
    for i in range(len(f1)):
        origin_patterns = f1[i]
        temp_dict = dict()
        temp_dict["01伤亡情况"] = origin_patterns[0] * 100 + origin_patterns[1] * 70  # 死亡人数+重伤人数
        temp_dict["02责任认定"] = 10 if origin_patterns[2] == 1 else 8
        # 酒后驾驶、吸毒后驾驶、无证驾驶、无牌驾驶、不安全驾驶、超载、逃逸
        temp_dict["03违章情况"] = origin_patterns[3] * 120 + origin_patterns[4] * 130 + origin_patterns[5] * 100 + \
                              origin_patterns[6] * 100 + origin_patterns[7] * 90 + origin_patterns[8] * 100 + \
                              origin_patterns[9] * 130
        # 抢救伤者、报警、现场等待、赔偿、认罪
        temp_dict["04案后表现"] = origin_patterns[10] * (-90) + origin_patterns[11] * (-90) + origin_patterns[12] * (-90) + \
                              origin_patterns[13] * (-120) + origin_patterns[14] * (-90)
        temp_dict["05初犯偶犯"] = 120 if origin_patterns[15] == 0 else -90
        temp_dict["06判决结果"] = origin_patterns[-1]
        new_csv_list.append(temp_dict)
    # 将新特征写回文件
    headers = ["01伤亡情况", "02责任认定", "03违章情况", "04案后表现", "05初犯偶犯", "06判决结果"]
    with open(new_csv_file, "w", newline="")as f2:
        f_csv = csv.DictWriter(f2, headers)
        # f_csv.writeheader()
        f_csv.writerows(new_csv_list)


def remove_error(csv_file1, csv_file2):
    """
    暴力消除数据的噪声
    :param csv_file1:
    :param csv_file2:
    :return:
    """
    with open(csv_file1) as f1:
        f1_csv = csv.reader(f1)
        d = dict()
        rows = list()
        # 将原来的csv文件提炼成字典，key为特征，value为对应的判决结果组成的list
        for row in f1_csv:
            rows.append(row)
            data = tuple(row[:-1])
            label = row[-1]
            if data in d:
                d[data].append(label)
            else:
                d[data] = []
                d[data].append(label)
        # 生成正确的数据（每种特征组合对应的判决结果，取众数）
        correct = []
        # f3 = open(csv_file1)
        # f3_csv = csv.reader(f3)
        for row in rows:
            new_row = row[:-1]
            labels = d[tuple(new_row)]
            true_label = max(labels, key=labels.count)
            new_row.append(true_label)
            correct.append(new_row)
        # for key, value in d.items():
        #     true_label = max(value, key=value.count)
        #     new_row = list(key)
        #     new_row.append(true_label)
        #     correct.append(new_row)
        with open(csv_file2, "w", newline="")as f2:
            f2_csv = csv.writer(f2)
            f2_csv.writerows(correct)


# remove_error("/home/zhangshiwei/Event-Extraction/06判决结果预测/特征提取/data.csv", "data_without_error.csv")
data_split("/home/zhangshiwei/Event-Extraction/06判决结果预测/特征提取/data.csv")
patterns_weight("train16.csv", "train5.csv")
patterns_weight("test16.csv", "test5.csv")
