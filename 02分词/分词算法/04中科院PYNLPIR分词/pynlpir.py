# -*- coding: utf-8 -*-
"""
Created on Mon May  6 19:00:50 2019

@author: 92111
"""

import pynlpir
pynlpir.open()
with open("test.txt", "r", encoding='utf-8') as f1:
    text = f1.read()
    seg_list = pynlpir.segment(text, 0)
    f2 = open("result.txt", "a", encoding='utf-8')
    for word in seg_list:
        f2.write(word + " ")
    f2.close()
pynlpir.close()
