# -*- coding: utf-8 -*-
from pyltp import Segmentor
import os
LTP_DATA_DIR = '/Users/zhangshiwei/ltp_data_v3.4.0/'  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR,
                              'cws.model')  # 分词模型路径，模型名称为`cws.model`


segmentor = Segmentor()  # 初始化实例
segmentor.load_with_lexicon(cws_model_path, 'dict')  # 加载自定义字典
f1 = open("/Users/zhangshiwei/基于法律裁判文书的事件抽取和应用/01数据预处理/preprocessed_data.txt", "r", encoding="utf-8")
if os.path.exists("segment_result.txt"):
    os.remove("segment_result.txt")
f2 = open("segment_result.txt", "a", encoding="utf-8")


texts = f1.readlines()
for text in texts:
    words = segmentor.segment(text.strip())  # 分词
    words_list = list(words)
    for word in words_list:
        f2.write(word + ' ')
    f2.write('\n')
segmentor.release()  # 释放模型
f1.close()
f2.close()
