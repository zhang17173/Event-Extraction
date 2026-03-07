# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import os
from pathlib import Path

try:
    import MySQLdb as mysql_driver
except ImportError:
    try:
        import pymysql as mysql_driver
    except ImportError as exc:
        raise SystemExit("未安装 MySQL 驱动。请安装 mysqlclient 或 pymysql。") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description="从数据库导出案件原始数据。")
    parser.add_argument("--host", default=os.environ.get("LAW_DB_HOST", "127.0.0.1"))
    parser.add_argument("--user", default=os.environ.get("LAW_DB_USER", "root"))
    parser.add_argument("--password", default=os.environ.get("LAW_DB_PASSWORD", ""))
    parser.add_argument("--database", default=os.environ.get("LAW_DB_NAME", "law"))
    parser.add_argument(
        "--output",
        default=str(Path(__file__).resolve().parents[2] / "01数据预处理" / "original_data.txt"),
        help="导出的原始数据文件。",
    )
    args = parser.parse_args()
    if not args.password:
        raise SystemExit("数据库密码为空。请通过 --password 或环境变量 LAW_DB_PASSWORD 提供密码。")

    connection_kwargs = {
        "host": args.host,
        "user": args.user,
        "db": args.database,
        "charset": "utf8",
    }
    if mysql_driver.__name__ == "MySQLdb":
        connection_kwargs["passwd"] = args.password
    else:
        connection_kwargs["password"] = args.password

    conn = mysql_driver.connect(**connection_kwargs)
    cur = conn.cursor()
    cur.execute("select 法院意见,判决结果 from 裁判文书")
    rows = cur.fetchall()

    output_path = Path(args.output).resolve()
    with output_path.open("w", encoding="utf-8") as f:
        for idx, row in enumerate(rows, start=1):
            opinion, judgment = row
            f.write(f"{idx}\t{str(opinion)} {str(judgment)}\n")

    cur.close()
    conn.close()
    print(f"导出完成，共写入 {len(rows)} 条记录: {output_path}")


if __name__ == "__main__":
    main()
