biaotou = ['标题', '案号', '案件类型', '庭审程序', '案由', '文书类型', '法院','判决日期','原告', '被告', '第三人', '法官', '审判长', '审判员', '书记员', '头部', '头部2', '当事人',
           '当事人2', '庭审程序说明', '庭审程序说明2', '庭审过程', '庭审过程2', '庭审过程3', '庭审过程4', '庭审过程5', '庭审过程6', '法院意见','法院意见2'
           ,'判决结果','判决结果2','庭后告知','庭后告知2','结尾','结尾2','附录','附录2']
# 在哪里搜索多个表格
filelocation = "/Users/zhangshiwei/OneDrive - Sierra College/交通肇事判决书/"
# 当前文件夹下搜索的文件名后缀
fileform = "xlsx"
# 将合并后的表格存放到的位置
filedestination = "/Users/zhangshiwei/OneDrive - Sierra College/交通肇事判决书/"
# 合并后的表格命名为file
file = "合并"

# 首先查找默认文件夹下有多少文档需要整合
import glob
import numpy

filearray = []
for filename in glob.glob(filelocation + "*." + fileform):
    filearray.append(filename)
# 以上是从pythonscripts文件夹下读取所有excel表格，并将所有的名字存储到列表filearray
print("在当前文件夹下有%d个文档" % len(filearray))
ge = len(filearray)
matrix = [None] * ge
# 实现读写数据

# 下面是将所有文件读数据到三维列表cell[][][]中（不包含表头）
import xlrd


for i in range(ge):
    fname = filearray[i]
    bk = xlrd.open_workbook(fname)
    try:
        sh = bk.sheet_by_name("Sheet0")
    except:
        print("在文件%s中没有找到sheet0，读取该EXCEL文件数据失败" % fname)
    nrows = sh.nrows
    matrix[i] = [0] * (nrows - 1)

    ncols = sh.ncols
    for m in range(nrows - 1):
        matrix[i][m] = ["0"] * ncols

    for j in range(1, nrows):
        for k in range(0, ncols):
            matrix[i][j - 1][k] = sh.cell(j, k).value
        # 下面是写数据到新的表格test.xls中哦
import xlwt

filename = xlwt.Workbook()
sheet = filename.add_sheet("hel")
# 下面是把表头写上
for i in range(0, len(biaotou)):
    sheet.write(0, i, biaotou[i])
# 求和前面的文件一共写了多少行
zh = 1
for i in range(ge):
    for j in range(len(matrix[i])):
        for k in range(len(matrix[i][j])):
            sheet.write(zh, k, matrix[i][j][k])
        zh = zh + 1
filename.save(filedestination + file + ".xls")