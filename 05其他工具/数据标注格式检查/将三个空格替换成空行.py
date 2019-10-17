# -*- coding:utf-8 -*-
# author:ZHANG SHIWEI
# datetime:2019/6/5 0005

with open("test.data", "r", encoding="utf-8") as f1:
    contents = f1.read().splitlines()
    f2 = open("new_test.data", "a", encoding="utf-8")
    for i in range(len(contents)):
        if contents[i] == "   ":
            f2.writelines(contents[i].replace("   ", "") + "\n")
        else:
            f2.writelines(contents[i] + "\n")
    f2.close()
