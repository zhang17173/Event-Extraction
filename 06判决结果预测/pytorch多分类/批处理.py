import os

# 执行01数据预处理
os.system("python /home/zhangshiwei/Event-Extraction/01数据预处理/data_preprocess.py")

# 执行02分词
os.system("/home/zhangshiwei/Event-Extraction/02分词/分词算法/05LTP分词/LTP分词_词性标注_命名实体识别.py")

# # 执行03 CRF事件抽取
# os.remove("/home/zhangshiwei/CRF++-0.58/data/result.txt")
# os.system(
#     "/home/zhangshiwei/CRF++-0.58/crf_test -m /home/zhangshiwei/CRF++-0.58/model /home/zhangshiwei/Event-Extraction/02分词/分词算法/05LTP分词/分词_词性标注_命名实体识别_结果.txt >> /home/zhangshiwei/CRF++-0.58/data/result.txt")
#
# # 执行特征提取
# os.system("python /home/zhangshiwei/Event-Extraction/06判决结果预测/特征提取/特征提取.py")
#
# # 执行数据预处理
# os.system("/home/zhangshiwei/Event-Extraction/06判决结果预测/特征提取/data/切割完整数据.py")
# os.system("/home/zhangshiwei/Event-Extraction/06判决结果预测/pytorch多分类/数据预处理.py")
