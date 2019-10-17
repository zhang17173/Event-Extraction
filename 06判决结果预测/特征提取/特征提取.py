# coding=utf-8
from 数字特征提取 import extract_seg
from 数字特征提取 import sentence_result
import csv
import re


def remove_duplicate_elements(l):
    """
    去除列表中重复元素，同时保持相对顺序不变
    :param l: 可能包含重复元素的列表
    :return: 去除重复元素的新列表
    """
    new_list = []
    for elem in l:
        if elem not in new_list:
            new_list.append(elem)
    return new_list


def find_element(l, *ss):
    """
    查找在l的元素中中是否包含s
    :param l:列表
    :param ss:一个或多个字符串
    :return:
    """
    for s in ss:
        for element in l:
            if s in element:
                return "1"
    return "0"


def get_event_elements(case_file):
    """
    将案件中属于同一事件要素的词语合并，最终返回完整的事件要素
    :param case_file: 记录单个案件的文本文件
    :return result: 返回一个字典，键为事件要素类型，值为对应的单词组成的list
    """
    words = []  # 保存所有属于事件要素的单词
    element_types = []  # 保存上述单词对应的事件要素类型
    with open(case_file, "r", encoding='utf-8') as f1:
        contents = []
        # 将文本转换成list，方便后续处理
        for line in f1.readlines():
            contents.append(line.strip("\n").split("\t"))

        for index, content in enumerate(contents):
            if "S" in content[-1]:
                # S出现在最后一个位置，说明这是一个单独的事件要素，将其加入word列表
                words.append(content[0])
                element_types.append(content[-1][-1])

            elif "B" in content[-1]:
                # 处理由多个单词组成的事件要素
                words.append(content[0])
                element_types.append(content[-1][-1])
                j = index + 1
                while "I" in contents[j][-1] or "E" in contents[j][-1]:
                    words[-1] = words[-1] + contents[j][0]
                    j += 1
                    if j == len(contents):
                        break
        # 将事件要素进行分类（将words列表中的元素按照类别分成6累）
        T = []
        K = []
        D = []
        P = []
        N = []
        R = []

        for i in range(len(element_types)):
            if element_types[i] == "T":
                T.append(words[i])
            elif element_types[i] == "K":
                K.append(words[i])
            elif element_types[i] == "D":
                D.append(words[i])
            elif element_types[i] == "P":
                P.append(words[i])
            elif element_types[i] == "N":
                N.append(words[i])
            elif element_types[i] == "R":
                R.append(words[i])

        # 为了防止CRF未能抽取出全部的事件要素，因此使用规则化的方法，从原始文本中直接提取出事件要素，作为补充
        case = ""  # case是完整的案件内容
        for idx in range(len(contents)):
            case += contents[idx][0]
        if "无证" in case or "驾驶资格" in case:
            N.append("无证驾驶")
        if "无号牌" in case or "牌照" in case or "无牌" in case:
            N.append("无牌驾驶")
        if "吸毒" in case or "毒品" in case or "毒驾" in case:
            N.append("吸毒后驾驶")
        if "超载" in case:
            N.append("超载")
        if "逃逸" in case or "逃离" in case:
            N.append("逃逸")
        if ("有前科" in case or "有犯罪前科" in case) and ("无前科" not in case and "无犯罪前科" not in case):
            N.append("有犯罪前科")

        # 整理抽取结果
        result = dict()  # 用字典存储各类事件要素
        result["事故类型"] = remove_duplicate_elements(T)
        result["罪名"] = remove_duplicate_elements(K)
        result["主次责任"] = remove_duplicate_elements(D)
        result["减刑因素"] = remove_duplicate_elements(P)
        result["加刑因素"] = remove_duplicate_elements(N)
        result["判决结果"] = remove_duplicate_elements(R)

        # 打印出完整的事件要素
        # for key, value in result.items():
        #     print(key, value)
        return result


def get_patterns_from_dict(result):
    """
    将提取出的事件要素转换成特征
    :param result: 字典形式的事件要素
    :return patterns: 字典形式的特征
    """
    patterns = dict()
    # 从事件要素中的"加刑因素"提取出三个特征：01死亡人数、02重伤人数、03轻伤人数
    patterns["01死亡人数"], patterns["02重伤人数"], patterns["03轻伤人数"] = extract_seg(
        "".join(result["加刑因素"]))

    # 从事件要素中的"主次责任"提取出特征：04责任认定
    patterns["04责任认定"] = find_element(result["主次责任"], "全部责任")

    # 从事件要素中的"加刑因素"提取出8个特征
    patterns["05是否酒后驾驶"] = find_element(result["加刑因素"], "酒")
    patterns["06是否吸毒后驾驶"] = find_element(result["加刑因素"], "毒")
    patterns["07是否无证驾驶"] = find_element(result["加刑因素"], "驾驶证", "证")
    patterns["08是否无牌驾驶"] = find_element(result["加刑因素"], "牌照", "牌")
    patterns["09是否不安全驾驶"] = find_element(result["加刑因素"], "安全")
    patterns["10是否超载"] = find_element(result["加刑因素"], "超载")
    patterns["11是否逃逸"] = find_element(result["加刑因素"], "逃逸", "逃离")
    patterns["是否初犯偶犯"] = 1 - int(find_element(result["加刑因素"], "前科"))

    # 从事件要素中的"减刑因素"提取出7个特征
    patterns["12是否抢救伤者"] = find_element(result["减刑因素"], "抢救", "施救")
    patterns["13是否报警"] = find_element(result["减刑因素"], "报警", "自首", "投案")
    patterns["14是否现场等待"] = find_element(result["减刑因素"], "现场", "等候")
    patterns["15是否赔偿"] = find_element(result["减刑因素"], "赔偿")
    patterns["16是否认罪"] = find_element(result["减刑因素"], "认罪")
    patterns["17是否如实供述"] = find_element(result["减刑因素"], "如实")
    if patterns["是否初犯偶犯"] == 0:
        patterns["18是否初犯偶犯"] = "0"
    else:
        patterns["18是否初犯偶犯"] = "1"
    return patterns


# num1 = sentence_result(
#     "7 被告人 周某 违反 中华人民共和国 道路 交通 安全法 规定 发生 交通事故 致 一 人 死亡 一人 受伤 并 负 事故 主要责任 行为 构成 交通肇事罪 公诉机关 指控 罪名成立 关于 民事赔偿 部分 被告人 周某 所在 单位 与 被害人 解某 亲属 达成 赔偿 协议 赔偿 被害人 解某 亲属 362000 元 被告人 周某 认罪 态度 尚 好 综合 被告人 犯罪 性质 情节 及 社会 危害 程度 等 因素 对 被告人 周某 可 适用 缓刑 中华人民共和国 刑法 之 规定 判决如下 被告人 周某 犯 交通肇事罪 判处 有期徒刑两年  缓刑 二年 ")
# num2 = sentence_result(
#     "10	被告人陈华未按照操作规范靠右安全驾驶发生致两人死亡重大交通事故行为构成交通肇事罪公诉机关指控罪名成立被告人陈华在本起事故中致两人死亡负事故全部责任应认定为有他特别恶劣情节被告人陈华在肇事后主动打电话报警并在现场等待公安机关处理归案后能如实供述自己犯罪事实符合自首条件应认定具有自首情节依法可以从轻处罚由于肇事车辆投保被害人损失基本上可以得到赔偿被害人家属也表示对被告人进行谅解请求本院从轻处罚并适用缓刑根据被告人陈华犯罪情节和悔罪表现适用缓刑确实不致再危害社会可以对被告人陈华适用缓刑中华人民共和国刑法第项规定判决如下被告人陈华犯交通肇事罪判处有期徒刑三年缓刑四年")
# print(num1, num2)


def label_case(file, is_label=False):
    """
    给数据打标签
    :param is_label: 是否需要将刑期分类，默认不分类
    :param file: 无标签数据
    :return:
    """
    f = open(file, 'r', encoding='utf-8')
    contents = f.readlines()
    labels = []
    for content in contents:
        num = sentence_result(content)
        labels.append(num)
    # 分类
    if is_label:
        for i in range(len(labels)):
            if 0 <= labels[i] <= 12:
                labels[i] = 0
            elif 13 <= labels[i] <= 35:
                labels[i] = 1
            # elif 25 <= labels[i] <= 35:
            #     labels[i] = 2
            else:
                labels[i] = 2
    f.close()
    return labels


headers = ['01死亡人数', "02重伤人数", "04责任认定", "05是否酒后驾驶", "06是否吸毒后驾驶", "07是否无证驾驶", "08是否无牌驾驶", "09是否不安全驾驶", "10是否超载",
           "11是否逃逸", "12是否抢救伤者", "13是否报警", "14是否现场等待", "15是否赔偿", "16是否认罪", "18是否初犯偶犯", "判决结果"]
rows = []
# 提取标签
labels = label_case("data/preprocessed_data.txt", is_label=True)
num_cases = 21086

f1 = open("data/preprocessed_data.txt", "r", encoding="utf-8")
contents = f1.readlines()
for i in range(1, num_cases + 1):
    file_name = "data/单个案件/" + str(i) + ".txt"
    result = get_event_elements(file_name)
    patterns = get_patterns_from_dict(result)
    # 因为目前CRF提取的效果还不够好，伤亡情况可能没有提取出来
    # 保险起见，对整个案件进行提取死亡人数等3个特征，而非事件抽取的结果
    patterns['01死亡人数'], patterns['02重伤人数'], patterns['03轻伤人数'] = extract_seg(contents[i - 1])
    patterns["判决结果"] = labels[i - 1]
    del patterns["是否初犯偶犯"]
    del patterns["03轻伤人数"]
    del patterns["17是否如实供述"]
    rows.append(patterns)
f1.close()
with open("data.csv", "w", newline='') as f:
    f_csv = csv.DictWriter(f, headers)
    f_csv.writeheader()
    f_csv.writerows(rows)
