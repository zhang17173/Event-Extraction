from __future__ import annotations

import argparse
from pathlib import Path

import glob
import xlrd
import xlwt

BIAOTOU = [
    '标题', '案号', '案件类型', '庭审程序', '案由', '文书类型', '法院', '判决日期', '原告', '被告', '第三人', '法官', '审判长',
    '审判员', '书记员', '头部', '头部2', '当事人', '当事人2', '庭审程序说明', '庭审程序说明2', '庭审过程', '庭审过程2',
    '庭审过程3', '庭审过程4', '庭审过程5', '庭审过程6', '法院意见', '法院意见2', '判决结果', '判决结果2', '庭后告知',
    '庭后告知2', '结尾', '结尾2', '附录', '附录2'
]


def main() -> None:
    parser = argparse.ArgumentParser(description="合并同一目录下的 Excel 文件。")
    parser.add_argument("--input-dir", default=".", help="待合并的 Excel 所在目录。")
    parser.add_argument("--pattern", default="*.xlsx", help="文件匹配模式。")
    parser.add_argument("--output", default="合并.xls", help="输出文件名。")
    parser.add_argument("--sheet-name", default="Sheet0", help="读取的工作表名称。")
    args = parser.parse_args()

    input_dir = Path(args.input_dir).resolve()
    files = sorted(glob.glob(str(input_dir / args.pattern)))
    print(f"在当前文件夹下有{len(files)}个文档")

    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("merged")
    for column, header in enumerate(BIAOTOU):
        sheet.write(0, column, header)

    row_index = 1
    for file_path in files:
        book = xlrd.open_workbook(file_path)
        try:
            sh = book.sheet_by_name(args.sheet_name)
        except Exception:
            print(f"在文件{file_path}中没有找到 {args.sheet_name}，跳过该文件")
            continue

        for r in range(1, sh.nrows):
            for c in range(sh.ncols):
                sheet.write(row_index, c, sh.cell(r, c).value)
            row_index += 1

    output_path = Path(args.output).resolve()
    workbook.save(str(output_path))
    print(f"合并完成: {output_path}")


if __name__ == "__main__":
    main()
