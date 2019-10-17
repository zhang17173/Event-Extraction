#!/usr/bin/env python
# _*_coding:utf-8 _*_
# @Author:Zhang Shiwei
# @Date  :2019-07-21


# 去除列表中重复元素，同时保持相对顺序不变
def remove_duplicate_elements(l):
    new_list = []
    for i in l:
        if i not in new_list:
            new_list.append(i)
    return new_list


# 将属于同一事件要素的词语合并

def func(file_name):
    words = []
    element_type = []
    with open(file_name, "r", encoding='utf-8') as f1:
        contents = f1.readlines()
        new_contents = []
        # 将文本转换成list，方便后续处理
        for content in contents:
            new_contents.append(content.strip("\n").split(" "))

        for index, content in enumerate(new_contents):
            if "S" in content[-1]:
                # 处理由一个单词组成的事件要素
                words.append(content[0])
                element_type.append(content[-1])

            elif "B" in content[-1]:
                # 处理由多个单词组成的事件要素
                words.append(content[0])
                element_type.append(content[-1])
                j = index + 1
                while "I" in new_contents[j][-1] or "E" in new_contents[j][-1]:
                    words[-1] = words[-1] + new_contents[j][0]
                    j += 1
                    if j == len(new_contents):
                        break
        T = []
        K = []
        D = []
        P = []
        N = []
        R = []

        for i in range(len(element_type)):
            if element_type[i][-1] == "T":
                T.append(words[i])
            elif element_type[i][-1] == "K":
                K.append(words[i])
            elif element_type[i][-1] == "D":
                D.append(words[i])
            elif element_type[i][-1] == "P":
                P.append(words[i])
            elif element_type[i][-1] == "N":
                N.append(words[i])
            elif element_type[i][-1] == "R":
                R.append(words[i])
        # 整理抽取结果
        result = dict()
        result["事故类型"] = remove_duplicate_elements(T)
        result["罪名"] = remove_duplicate_elements(K)
        result["主次责任"] = remove_duplicate_elements(D)
        result["减刑因素"] = remove_duplicate_elements(P)
        result["加刑因素"] = remove_duplicate_elements(N)
        result["判决结果"] = remove_duplicate_elements(R)

        #   打印出完整的事件要素
        # for key, value in result.items():
        #    print(key, value)

    return result


func("元数据/1.txt")
