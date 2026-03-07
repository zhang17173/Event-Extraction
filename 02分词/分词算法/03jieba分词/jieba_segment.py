#!/usr/bin/env python
# _*_coding:utf-8 _*_
# @Author:Zhang Shiwei
import jieba


def main():
    with open("test.txt", "r", encoding="utf-8") as f1:
        text = f1.read()
    seg_list = jieba.cut(text)
    with open("result.txt", "w", encoding="utf-8") as f2:
        for word in seg_list:
            f2.write(word + " ")


if __name__ == "__main__":
    main()
