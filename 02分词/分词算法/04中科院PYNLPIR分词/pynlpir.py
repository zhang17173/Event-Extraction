# -*- coding: utf-8 -*-
"""
Created on Mon May  6 19:00:50 2019

@author: 92111
"""

import pynlpir


def main():
    pynlpir.open()
    try:
        with open("test.txt", "r", encoding="utf-8") as f1:
            text = f1.read()
        seg_list = pynlpir.segment(text, 0)
        with open("result.txt", "w", encoding="utf-8") as f2:
            for word in seg_list:
                f2.write(str(word) + " ")
    finally:
        pynlpir.close()


if __name__ == "__main__":
    main()
