# -*- coding:utf-8 -*-
# author:ZHANG SHIWEI
# datetime:2019/6/5 0005

with open("test.data", "r", encoding="utf-8") as f1:
    contents = f1.read().splitlines()
    with open("new_test.data", "w", encoding="utf-8") as f2:
        for line in contents:
            if line == "   ":
                f2.write("\n")
            else:
                f2.write(line + "\n")
