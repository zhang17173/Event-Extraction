import csv
import numpy as np


def data_split(data_csv):
    """
    将原始数据分割成训练集和测试集
    :param data_csv:原始数据
    :return:
    """
    with open(data_csv) as f:
        f_csv = csv.reader(f)
        rows = list(f_csv)
        # 前18000条作为训练集
        rows_train = rows[:20000]
        rows_test = rows[20000:]
        with open("data/train16.csv", "w") as f_train:
            f_train_csv = csv.writer(f_train)
            f_train_csv.writerows(rows_train)
        with open("data/test16.csv", "w") as f_test:
            f_test_csv = csv.writer(f_test)
            f_test_csv.writerows(rows_test)


def patterns_weight(csv_file, new_csv_file):
    """
    给特征加权，然后将16个特征变为6个特征，以缓解数据的稀疏性
    :param csv_file: 源文件，16个特征
    :param new_csv_file:加权合并之后的文件，6个特征
    :return:
    """
    f1 = np.loadtxt(csv_file, delimiter=',', dtype=np.int)
    new_csv_list = []
    for i in range(len(f1)):
        origin_patterns = f1[i]
        temp_dict = dict()
        # headers = ['01死亡人数', "02重伤人数", "04责任认定", "05是否酒后驾驶", "06是否吸毒后驾驶", "07是否无证驾驶", "08是否无牌驾驶", "09是否不安全驾驶", "10是否超载",
        #            "11是否逃逸", "12是否抢救伤者", "13是否报警", "14是否现场等待", "15是否赔偿", "16是否认罪", "18是否初犯偶犯", "判决结果"]
        temp_dict["01伤亡情况"] = origin_patterns[0] * 80 + origin_patterns[1] * 30  # 死亡人数+重伤人数
        temp_dict["02责任认定"] = 30 if origin_patterns[2] == 1 else 10
        # 酒后驾驶、吸毒后驾驶、无证驾驶、无牌驾驶、不安全驾驶、超载、逃逸
        temp_dict["03违章情况"] = origin_patterns[3] * 15 + origin_patterns[4] * 20 + origin_patterns[5] * 10 + \
                              origin_patterns[6] * 10 + origin_patterns[7] * 5 + origin_patterns[8] * 10 + \
                              origin_patterns[9] * 30
        # 抢救伤者、报警、现场等待、赔偿、认罪
        temp_dict["04案后表现"] = origin_patterns[10] * (-15) + origin_patterns[11] * (
            -30) + origin_patterns[12] * (-15) + origin_patterns[13] * (-25) + origin_patterns[14] * (-15)
        temp_dict["05初犯偶犯"] = 30 if origin_patterns[15] == 0 else -15
        temp_dict["06是否逃逸"] = origin_patterns[9] * 100
        temp_dict["07判决结果"] = origin_patterns[-1]
        new_csv_list.append(temp_dict)
    # 将新特征写回文件
    headers = ["01伤亡情况", "02责任认定", "03违章情况", "04案后表现", "05初犯偶犯", "06是否逃逸", "07判决结果"]
    with open(new_csv_file, "w", newline="")as f2:
        f_csv = csv.DictWriter(f2, headers)
        # f_csv.writeheader()
        f_csv.writerows(new_csv_list)


def remove_error(csv_file1, csv_file2):
    """
    暴力消除数据的噪声
    :param csv_file1:源文件
    :param csv_file2:消噪之后的文件
    :return:
    """
    with open(csv_file1) as f1:
        f1_csv = csv.reader(f1)
        d = dict()
        rows = list()
        # 将原来的csv文件提炼成字典，key为特征，value为对应的判决结果组成的list
        for row in f1_csv:
            rows.append(row)
            pattern = tuple(row[:-1])
            label = row[-1]
            if pattern in d:
                d[pattern].append(label)
            else:
                d[pattern] = []
                d[pattern].append(label)

        # 生成去噪的数据（每种特征组合对应的判决结果，取众数）
        cases_without_noises = []

        for row in rows:
            new_row = row[:-1]
            labels = d[tuple(new_row)]
            # 取众数作为正确的label
            true_label = max(labels, key=labels.count)
            new_row.append(true_label)
            cases_without_noises.append(new_row)
        # 写入新的文件
        with open(csv_file2, "w", newline="")as f2:
            f2_csv = csv.writer(f2)
            f2_csv.writerows(cases_without_noises)


remove_error("/home/zhangshiwei/Event-Extraction/06判决结果预测/特征提取/data.csv", "data/data_without_error.csv")
data_split("data/data_without_error.csv")
patterns_weight("data/train16.csv", "data/train6.csv")
patterns_weight("data/test16.csv", "data/test6.csv")

# remove_error("/home/zhangshiwei/Event-Extraction/06判决结果预测/特征提取/data_unlabeled.csv", "data_unlabeled_without_error.csv")
# print("Done!")
# data_split("data_unlabeled_without_error.csv")
# print("Done!")
# patterns_weight("train16.csv", "train5.csv")
# print("Done!")
# patterns_weight("test16.csv", "test5.csv")
# print("Done!")
