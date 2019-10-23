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


def extract_seg(content):
    # 死亡人数、重伤人数、轻伤人数提取
    r1 = re.compile(u'[1234567890一二两三四五六七八九十 ]*人( )*死亡')
    r2 = re.search(r1, content)
    if r2 is None:
        num1 = 0
    else:
        text = r2.group()
        num1 = per_num(text)
    # 重伤人数
    r3 = re.compile(u'[1234567890一二两三四五六七八九十 ]*人( )*重伤')
    r4 = re.search(r3, content)
    if r4 is None:
        num2 = 0
    else:
        text = r4.group()
        num2 = per_num(text)
    # 受伤人数
    r5 = re.compile(u'[1234567890一二两三四五六七八九十 ]*人( )*(轻伤|受伤)')
    r6 = re.search(r5, content)
    if r6 is None:
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

# num = sentence_result(
#     '''被告人张五红发生致一人死亡重大交通事故负事故全部责任行为构成交通肇事罪公诉机关指控被告人张五红犯交通肇事罪罪名成立本院依法予以支持被告人张五红在交通肇事后驾车逃逸依法应在有期徒刑三年以上七年以下量刑幅度内量刑辩护人关于被告人张五红具有坦白情节赔偿被害人亲属经济损失并取得被害人亲属谅解以及被告人张五红系初犯在事故发生之后十多年中没有任何违法犯罪行为建议本院对被告人张五红宣告缓刑意见符合本案事实和法律规定据此本院对张五红予以从轻处罚并宣告缓刑但辩护人建议本院对被告人张五红减轻处罚意见无法律依据本院不予支持为维护交通运输管理秩序保护公民人身权利不受侵犯根据被告人犯罪事实性质情节造成危害后果以及被告人悔罪表现中华人民共和国刑法之规定判决如下被告人张五红犯交通肇事罪判处有期徒刑三年缓刑五年被告人张五红回到社区后应当遵守法律法规服从监督管理接受教育完成公益劳动做一名有益社会公民''')
# print(num)
