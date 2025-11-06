#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import zipfile
from cellphonedb.src.core.methods import cpdb_statistical_analysis_method

def get_db_zip_path(cpdb_dir, cpdb_version):
    """获取 CellPhoneDB 数据库 ZIP 文件路径"""
    # 标准路径: {cpdb_dir}/releases/{version}/cellphonedb.zip
    standard_path = os.path.join(cpdb_dir, "releases", cpdb_version, "cellphonedb.zip")
    
    if os.path.exists(standard_path):
        return standard_path
    
    # 备用路径: {cpdb_dir}/cellphonedb.zip
    direct_path = os.path.join(cpdb_dir, "cellphonedb.zip")
    if os.path.exists(direct_path):
        return direct_path
    
    # 检查其他可能的 ZIP 文件
    for file in os.listdir(cpdb_dir):
        if file.endswith(".zip") and "cellphonedb" in file.lower():
            return os.path.join(cpdb_dir, file)
    
    raise FileNotFoundError(f"CellPhoneDB database ZIP file not found in {cpdb_dir}")

def main():
    ap = argparse.ArgumentParser(description="Run CellPhoneDB statistical analysis")
    ap.add_argument("--h5ad", required=True, help="Input h5ad file path")
    ap.add_argument("--meta", required=True, help="Cell type annotation file")
    ap.add_argument("--cpdb_dir", required=True, help="CellPhoneDB database directory")
    ap.add_argument("--cpdb_version", default="v5.0.0", help="Database version")
    ap.add_argument("--outdir", required=True, help="Output directory")
    ap.add_argument("--counts_data", default="hgnc_symbol", 
                   choices=["ensembl", "gene_name", "hgnc_symbol"],
                   help="Gene identifier type")
    ap.add_argument("--iterations", type=int, default=1000, help="Number of permutations")
    ap.add_argument("--threshold", type=float, default=0.1, help="Gene expression threshold")
    ap.add_argument("--threads", type=int, default=8, help="Number of threads")
    ap.add_argument("--microenvs", default=None, help="Optional: microenvs.txt path")
    ap.add_argument("--score_interactions", action="store_true", help="Calculate interaction scores")
    args = ap.parse_args()

    # 创建输出目录
    os.makedirs(args.outdir, exist_ok=True)
    
    # 获取并验证数据库 ZIP 文件路径
    try:
        db_zip_path = get_db_zip_path(args.cpdb_dir, args.cpdb_version)
        print(f"[Info] Using CellPhoneDB DB from: {db_zip_path}")
        
        # 验证 ZIP 文件内容
        with zipfile.ZipFile(db_zip_path, 'r') as zip_ref:
            required_files = [
                'protein_table.csv', 
                'gene_table.csv',
                'interaction_table.csv'
            ]
            missing = [f for f in required_files if f not in zip_ref.namelist()]
            if missing:
                raise ValueError(f"Database ZIP is missing required files: {', '.join(missing)}")
            print(f"[Info] Database validation OK. Contains {len(zip_ref.namelist())} files.")
    except Exception as e:
        print(f"[ERROR] Database validation failed: {str(e)}")
        print("[INFO] Available files in database directory:")
        for root, _, files in os.walk(args.cpdb_dir):
            for file in files:
                print(f"  - {os.path.join(root, file)}")
        raise
    
    print(f"[Info] Starting statistical analysis for {args.h5ad} ...")
    
    try:
        # 执行统计分析
        cpdb_statistical_analysis_method.call(
            cpdb_file_path=db_zip_path,
            meta_file_path=args.meta,
            counts_file_path=args.h5ad,
            counts_data=args.counts_data,
            iterations=args.iterations,
            threshold=args.threshold,
            microenvs_file_path=args.microenvs,
            score_interactions=args.score_interactions,
            threads=args.threads,
            output_path=args.outdir
        )
        print(f"[OK] Analysis completed. Results saved in: {args.outdir}")
    except Exception as e:
        print(f"[ERROR] Analysis failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
