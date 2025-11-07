#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import zipfile
from pathlib import Path

from cellphonedb.src.core.methods import cpdb_statistical_analysis_method

REQUIRED_DB_FILES = {
    "protein_table.csv",
    "gene_table.csv",
    "interaction_table.csv",
}

def log(msg: str):
    print(f"[CPDB] {msg}", flush=True)

def list_dir(p: str):
    for root, _, files in os.walk(p):
        for f in files:
            print("  -", os.path.join(root, f))

def has_required_csvs(dir_path: str) -> bool:
    found = set()
    for root, _, files in os.walk(dir_path):
        for f in files:
            if f in REQUIRED_DB_FILES:
                found.add(f)
    return REQUIRED_DB_FILES.issubset(found)

def make_zip_from_dir(src_dir: str, out_zip: str):
    """把 src_dir 下的 CSV 打包成 cellphonedb.zip（扁平化放入根目录）"""
    log(f"打包 CellPhoneDB CSV 到 ZIP: {out_zip}")
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(src_dir):
            for f in files:
                if f.lower().endswith(".csv"):
                    zf.write(os.path.join(root, f), arcname=f)
    # 校验
    with zipfile.ZipFile(out_zip, "r") as zf:
        names = set(zf.namelist())
    missing = [f for f in REQUIRED_DB_FILES if f not in names]
    if missing:
        raise ValueError(f"打包后的 ZIP 缺少必要文件: {', '.join(missing)}")

def resolve_db_zip(cpdb_dir: str, cpdb_version: str) -> str:
    """
    返回可用的数据库 ZIP 路径。查找顺序：
      1) {cpdb_dir}/releases/{version}/cellphonedb.zip
      2) {cpdb_dir}/cellphonedb.zip
      3) 若 releases/{version} 目录里有 CSV，则就地打包出 cellphonedb.zip
      4) 若 cpdb_dir 目录有 CSV，则就地打包出 cellphonedb.zip
      5) 兜底：在 cpdb_dir 下找任意 *cellphonedb*.zip
    """
    rel_dir = os.path.join(cpdb_dir, "releases", cpdb_version)
    std_zip = os.path.join(rel_dir, "cellphonedb.zip")
    if os.path.isfile(std_zip):
        return std_zip

    direct_zip = os.path.join(cpdb_dir, "cellphonedb.zip")
    if os.path.isfile(direct_zip):
        return direct_zip

    if os.path.isdir(rel_dir) and has_required_csvs(rel_dir):
        os.makedirs(rel_dir, exist_ok=True)
        make_zip_from_dir(rel_dir, std_zip)
        return std_zip

    if os.path.isdir(cpdb_dir) and has_required_csvs(cpdb_dir):
        make_zip_from_dir(cpdb_dir, direct_zip)
        return direct_zip

    for f in os.listdir(cpdb_dir):
        if f.lower().endswith(".zip") and "cellphonedb" in f.lower():
            return os.path.join(cpdb_dir, f)

    raise FileNotFoundError(
        f"未找到可用的 CellPhoneDB 数据库 ZIP，也未检测到可打包的 CSV 目录。\n"
        f"检查路径: {cpdb_dir}\n"
        f"期望包含: {', '.join(sorted(REQUIRED_DB_FILES))}"
    )

def validate_zip(zip_path: str):
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = set(zf.namelist())
    missing = [f for f in REQUIRED_DB_FILES if f not in names]
    if missing:
        raise ValueError(f"数据库 ZIP 缺少必要文件: {', '.join(missing)}")
    log(f"数据库校验通过（{len(names)} 个文件）。")

def main():
    ap = argparse.ArgumentParser(description="Run CellPhoneDB statistical analysis (Method 2)")
    ap.add_argument("--h5ad", required=True, help="Input .h5ad (counts)")
    ap.add_argument("--meta", required=True, help="Meta file (2列: Cell, cell_type)")
    ap.add_argument("--cpdb_dir", required=True, help="CellPhoneDB database directory")
    ap.add_argument("--cpdb_version", default="v5.0.0", help="Database version (e.g. v5.0.0)")
    ap.add_argument("--outdir", required=True, help="Output directory")
    ap.add_argument("--counts_data", default="hgnc_symbol",
                    choices=["ensembl", "gene_name", "hgnc_symbol"],
                    help="Gene ID type used in the counts matrix")
    ap.add_argument("--iterations", type=int, default=1000)
    ap.add_argument("--threshold", type=float, default=0.1)
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--microenvs", default=None,
                    help="Microenvironment file (two columns: cell_type\\tmicroenvironment)")
    ap.add_argument("--score_interactions", action="store_true")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    # 解析并校验数据库 ZIP
    try:
        db_zip_path = resolve_db_zip(args.cpdb_dir, args.cpdb_version)
        log(f"使用数据库 ZIP: {db_zip_path}")
        validate_zip(db_zip_path)
    except Exception as e:
        print(f"[ERROR] 数据库准备/校验失败：{e}", file=sys.stderr)
        print("[INFO] 目录下文件一览：")
        list_dir(args.cpdb_dir)
        sys.exit(2)

    log("开始运行统计分析 ...")
    log(f"Params: iterations={args.iterations}, threshold={args.threshold}, "
        f"threads={args.threads}, counts_data={args.counts_data}, microenvs={args.microenvs}")

    try:
        cpdb_statistical_analysis_method.call(
            cpdb_file_path=db_zip_path,
            meta_file_path=args.meta,
            counts_file_path=args.h5ad,
            counts_data=args.counts_data,
            iterations=args.iterations,
            threshold=args.threshold,
            microenvs_file_path=args.microenvs,          # 关键：微环境文件
            score_interactions=args.score_interactions,
            threads=args.threads,
            output_path=args.outdir
        )
        log(f"完成。结果已保存到: {args.outdir}")
    except Exception as e:
        print(f"[ERROR] 运行失败：{e}", file=sys.stderr)
        raise

if __name__ == "__main__":
    main()
