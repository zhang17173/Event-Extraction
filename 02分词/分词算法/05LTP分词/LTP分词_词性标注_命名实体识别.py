# -*- coding: utf-8 -*-
from pyltp import NamedEntityRecognizer
from pyltp import Postagger
from pyltp import Segmentor
import os

LTP_DATA_DIR = '/home/zhangshiwei/ltp_data_v3.4.0/'  # ltp模型目录的路径，根据实际情况修改
cws_model_path = os.path.join(LTP_DATA_DIR,
                              'cws.model')  # 分词模型路径，模型名称为`cws.model`
pos_model_path = os.path.join(LTP_DATA_DIR,
                              'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
ner_model_path = os.path.join(LTP_DATA_DIR,
                              'ner.model')  # 命名实体识别模型路径，模型名称为`ner.model`

with open("/home/zhangshiwei/Event-Extraction/01数据预处理/preprocessed_data.txt", "r", encoding='utf-8') as f1:
    content = f1.read()

    # 分词
    segmentor = Segmentor()  # 初始化分词实例
    segmentor.load_with_lexicon(cws_model_path, 'dict')  # 加载分词模型，以及自定义词典
    seg_list = segmentor.segment(content)  # 分词
    seg_list = list(seg_list)  # 返回值并不是list类型，因此需要转换为list

    # LTP不能很好地处理回车，因此需要去除回车给分词带来的干扰。
    # LTP也不能很好地处理数字，可能把一串数字分成好几个单词，因此需要连接可能拆开的数字
    i = 0
    while i < len(seg_list):
        # 如果单词里包含回车，则需要分三种情况处理
        if '\n' in seg_list[i] and len(seg_list[i]) > 1:
            idx = seg_list[i].find('\n')
            # 回车在单词的开头，如\n被告人
            if idx == 0:
                remains = seg_list[i][1:]
                seg_list[i] = '\n'
                seg_list.insert(i + 1, remains)
            # 回车在单词末尾，如被告人\n
            elif idx == len(seg_list[i]) - 1:
                remains = seg_list[i][:-1]
                seg_list[i] = remains
                seg_list.insert(i + 1, '\n')
            # 回车在单词中间，如被告人\n张某某
            else:
                remains1 = seg_list[i].split('\n')[0]
                remains2 = seg_list[i].split('\n')[-1]
                seg_list[i] = remains1
                seg_list.insert(i + 1, '\n')
                seg_list.insert(i + 2, remains2)
        # 将拆开的数字连接起来
        if seg_list[i].isdigit() and seg_list[i + 1].isdigit():
            seg_list[i] = seg_list[i] + seg_list[i + 1]
            del seg_list[i + 1]

        i += 1

    # 词性标注
    postagger = Postagger()  # 初始化词性标注实例
    postagger.load(pos_model_path)  # 加载模型
    postags = postagger.postag(seg_list)  # 词性标注

    # 命名实体识别
    recognizer = NamedEntityRecognizer()  # 初始化命名实体识别实例
    recognizer.load(ner_model_path)  # 加载模型
    netags = recognizer.recognize(seg_list, postags)  # 命名实体识别

    # 写入结果
    if os.path.exists("分词_词性标注_命名实体识别_结果.txt"):
        os.remove("分词_词性标注_命名实体识别_结果.txt")

    f2 = open("分词_词性标注_命名实体识别_结果.txt", "a", encoding='utf-8')
    for word, postag, netag in zip(seg_list, postags, netags):
        if word == '\n':
            f2.write('\n')
        else:
            f2.write(word + " " + postag + " " + netag + "\n")
    f2.close()

    # 释放模型
    segmentor.release()
    postagger.release()
    recognizer.release()
