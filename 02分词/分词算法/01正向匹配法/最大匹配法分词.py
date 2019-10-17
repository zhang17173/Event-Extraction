# -*- coding:utf-8 -*-
# author:ZHANG SHIWEI
# datetime:2019/4/18 0018


class MM(object):
    """
        正向最大匹配法
    """

    def __init__(self, dic_path):
        self.dictionary = set()  # 构建字典集合
        self.maximum = 0  # 最长单词的长度
        with open(dic_path, 'r', encoding='utf8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                self.dictionary.add(line)
                if len(line) > self.maximum:
                    self.maximum = len(line)

    def cut(self, text):
        result = []
        index = 0
        while index < len(text):
            word = None
            for size in range(self.maximum, 0, -1):
                if len(text) - index < size:
                    continue
                piece = text[index:(index + size)]
                if piece in self.dictionary:
                    word = piece
                    result.append(word)
                    index += size
                    break
            if word is None:
                result.append(text[index])
                index += 1
        return result


def main():
    with open("test.txt", 'r', encoding='utf-8') as f1:
        text = f1.read()
        tokenizer = MM('dict.txt')
        words = tokenizer.cut(text)
        with open("result.txt", "w", encoding='utf8') as f2:
            for word in words:
                f2.write(word + " ")


main()
