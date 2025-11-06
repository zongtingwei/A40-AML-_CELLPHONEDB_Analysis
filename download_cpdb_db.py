#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, os
from cellphonedb.utils import db_utils, db_releases_utils

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target-dir", required=True, help="下载位置，如 /root/autodl-tmp/BGI/cpdb_db")
    ap.add_argument("--version", default="v5.0.0", help="数据库版本(≥4.1.0)，如 v5.0.0")
    args = ap.parse_args()

    os.makedirs(args.target_dir, exist_ok=True)
    print("[Info] 可用版本（片段HTML表）已获取...")
    _ = db_releases_utils.get_remote_database_versions_html(min_version=4.1)
    print(f"[Info] 下载 {args.version} 到 {args.target_dir} ...")
    db_utils.download_database(args.target_dir, args.version)
    path = db_utils.get_db_path(args.target_dir, args.version)
    print(f"[OK] 数据库: {path}")

if __name__ == "__main__":
    main()
