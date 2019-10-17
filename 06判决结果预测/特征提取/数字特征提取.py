#!/usr/bin/env python
# _*_coding:utf-8 _*_
# @Author:Zhang Shiwei
# @Date  :2019/9/12

import re


def text2num(text):
    num = 0
    # 将text序列连接成字符串
    text = "".join(text)
    digit = {
        '一': 1,
        '二': 2,
        '两': 2,
        '三': 3,
        '四': 4,
        '五': 5,
        '六': 6,
        '七': 7,
        '八': 8,
        '九': 9}
    if text:
        idx_q, idx_b, idx_s = text.find('千'), text.find('百'), text.find('十')
        if idx_q != -1:
            num += digit[text[idx_q - 1:idx_q]] * 1000
        if idx_b != -1:
            num += digit[text[idx_b - 1:idx_b]] * 100
        if idx_s != -1:
            # 十前忽略一的处理
            num += digit.get(text[idx_s - 1:idx_s], 1) * 10
        if text[-1] in digit:
            num += digit[text[-1]]
    return num


def per_num(text):
    string = re.findall(r"\d+", text)
    if len(string) == 0:
        r1 = re.compile(u'[一二两三四五六七八九十]{1,}')
        r2 = r1.findall(text)
        if len(r2) == 0:
            num = 1
        else:
            num = text2num(r2)
    else:
        num = string[0]
    return num


# 分词
def extract_seg(content):
    # 死亡人数
    r1 = re.compile(u'[1234567890一二两三四五六七八九十 ]*人( )*死亡')
    r2 = re.search(r1, content)
    if r2 == None:
        num1 = 0
    else:
        text = r2.group()
        num1 = per_num(text)
    # 重伤人数
    r3 = re.compile(u'[1234567890一二两三四五六七八九十 ]*人( )*重伤')
    r4 = re.search(r3, content)
    if r4 == None:
        num2 = 0
    else:
        text = r4.group()
        num2 = per_num(text)
    # 受伤人数
    r5 = re.compile(u'[1234567890一二两三四五六七八九十 ]*人( )*(轻伤|受伤)')
    r6 = re.search(r5, content)
    if r6 == None:
        num3 = 0
    else:
        text = r6.group()
        num3 = per_num(text)
    return num1, num2, num3


# num1, num2, num3 = extract_seg("8	被告人宋慧勇发生重大事故导致两人死亡被告人负事故全部责任行为经构成交通肇事罪应予惩处公诉机关指控罪名成立鉴于被告人案发后能够自动投案如实供述自己罪行依法应当认定为自首可以从轻处罚经本院告知并释明被害人家属明确表示案提起民事诉讼意愿本院予以尊重被告人系初犯于本案庭审前主动预交赔偿款人民币30000元有悔罪表现可酌定从轻处罚并适用缓刑综上中华人民共和国刑法最高人民法院关于处理自首和立功具体应用法律若干问题解释及最高人民法院关于审理交通肇事刑事案件具体应用法律若干问题解释[[5dc0c97d590d4210b8ee4b79f84bff82Article1Prgrph-1List|第㈠项]]之规定判决如下被告人宋慧勇犯交通肇事罪判处有期徒刑一年六个月缓刑二年")
# print(num1, num2, num3)

# 提取出判决结果，单位为月份
def sentence_result(text):
    text = text.strip(" ")  # 去除每行首尾可能出现的多余空格
    text = text.replace(" ", "")  # 去除所有空格
    if text.find("判决如下") != -1:
        result = text.split('判决如下')[-1]
    elif text.find("判处如下") != -1:
        result = text.split('判处如下')[-1]
    else:
        result = text
    r1 = re.compile(u'(有期徒刑|拘役)[一二三四五六七八九十又年零两]{1,}(个月|年)')
    r2 = re.search(r1, result)
    if r2 is None:
        num = 0
    else:
        text = r2.group()
        r3 = re.compile(u'[一二三四五六七八九十两]{1,}')
        r4 = r3.findall(text)
        if len(r4) > 1:
            num1 = text2num(r4[0])
            num2 = text2num(r4[1])
            num = 12 * num1 + num2
        elif text.find(u"年") != -1:
            num = 12 * text2num(r4)
        else:
            num = text2num(r4)
    return num


# num = sentence_result('''7 被告人 周某 违反 中华人民共和国 道路 交通 安全法 规定 发生 交通事故 致 一 人 死亡 一人 受伤 并 负 事故 主要责任 行为
#             构成 交通肇事罪 公诉机关 指控 罪名成立 关于 民事赔偿 部分 被告人 周某 所在 单位 与 被害人 解某 亲属 达成 赔偿 协议 赔偿
#             被害人 解某 亲属 362000 元 被告人 周某 认罪 态度 尚 好 综合 被告人 犯罪 性质 情节 及 社会 危害 程度 等 因素 对
#             被告人 周某 可 适用 缓刑 中华人民共和国 刑法 之 规定 判决如下 被告人 周某 犯 交通肇事罪 判处 有期徒刑五年三个月  缓刑 二年''')
# print(num)
