#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import pandas as pd
import anndata as ad
import os

def load_mgi_rpt(path):
    df = pd.read_csv(path, sep="\t", header=None, dtype=str, comment="#", low_memory=False)
    df.columns = [f"col{i}" for i in range(df.shape[1])]
    # 假设：col0 = group_id, col1 = organism, col3 = symbol
    df2 = df[[ "col0", "col1", "col3" ]].copy()
    df2.columns = ["group_id", "organism", "symbol"]
    df2["organism"] = df2["organism"].str.lower()
    return df2

def build_mm2hs(df):
    mm = df[df["organism"].str.contains("mouse")][["group_id","symbol"]].rename(columns={"symbol":"mouse_symbol"})
    hs = df[df["organism"].str.contains("human")][["group_id","symbol"]].rename(columns={"symbol":"human_symbol"})
    merged = pd.merge(mm, hs, on="group_id", how="inner")
    cnt_mm = merged.groupby("group_id")["mouse_symbol"].nunique()
    cnt_hs = merged.groupby("group_id")["human_symbol"].nunique()
    valid = cnt_mm[(cnt_mm==1) & (cnt_hs==1)].index
    o2o = merged[merged["group_id"].isin(valid)].drop_duplicates(["mouse_symbol","human_symbol"])
    return o2o[["mouse_symbol","human_symbol"]]

def main():
    ap = argparse.ArgumentParser(description="Map mouse → human symbols using MGI orthology table")
    ap.add_argument("--mgi_rpt", required=True, help="Path to MGI HOM_MouseHumanSequence.rpt file")
    ap.add_argument("--in_h5ad", required=True, help="Input .h5ad (mouse genes)")
    ap.add_argument("--out_h5ad", required=True, help="Output .h5ad (human‐symbol version)")
    ap.add_argument("--map_csv", required=True, help="CSV mapping table output")
    ap.add_argument("--drop_unmapped", action="store_true", help="Drop genes not mapped")
    args = ap.parse_args()

    print(f"[Info] Loading MGI report: {args.mgi_rpt}")
    mp = build_mm2hs(load_mgi_rpt(args.mgi_rpt))
    print(f"[Info] One‐to‐one mapped pairs: {mp.shape[0]}")

    lut = dict(zip(mp.mouse_symbol.astype(str), mp.human_symbol.astype(str)))

    print(f"[Info] Reading h5ad: {args.in_h5ad}")
    adata = ad.read_h5ad(args.in_h5ad)
    ms = adata.var_names.astype(str)
    hs = [lut.get(x) for x in ms]

    var = adata.var.copy()
    var["mouse_symbol"] = ms
    var["human_symbol"] = hs

    # 修正：清除 var.index.name 避免与列名冲突
    var.index.name = "_orig_var_index"  # 重命名索引名，避免冲突

    if args.drop_unmapped:
        keep = pd.notna(var["human_symbol"])
        adata = adata[:, keep.values].copy()
        adata.var = var.loc[keep].copy()
        adata.var_names = adata.var["human_symbol"].astype(str)
        # 关键修复：强制重置索引名为 None
        adata.var.index.name = None
    else:
        fill = [h if h is not None else m for m,h in zip(ms, hs)]
        adata.var = var
        adata.var_names = pd.Index(fill).astype(str)
        # 关键修复：强制重置索引名为 None
        adata.var.index.name = None

    mp.to_csv(args.map_csv, index=False)
    print(f"[Info] Mapping table written: {args.map_csv}")

    out_dir = os.path.dirname(os.path.abspath(args.out_h5ad))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    adata.write_h5ad(args.out_h5ad, compression="gzip")
    print(f"[OK] wrote: {args.out_h5ad}")
    print(f"[Stats] n_genes={adata.n_vars}")

if __name__ == "__main__":
    main()
