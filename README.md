# A40AML_CELLPHONEDB_Analysis
A40(AML)_CELLPHONEDB_Analysis
## 📖 Overview
A40(AML)_CELLPHONEDB_Analysis

## 🚀 How to run

build the cellphonedb env

```bash
conda create -n cpdb python=3.10 -y
conda activate cpdb
```

install cellphonedb
```bash
pip install -U cellphonedb
```

make cpdb_meta from h5ad file
```bash
python make_cpdb_meta_from_h5ad.py \
  --h5ad .../your_file.h5ad \
  --cluster-col cluster \
  --out /root/autodl-tmp/BGI/STOmics/cpdb_inputs/meta_A40.txt
```
download the MGI mouse and human homologs
![step1](images/step1.png)
![step2](images/step2.png)
![step3](images/step3.png)

map mouse to human in h5ad file
```bash
python map_mm_to_hs_from_mgi_v4.py \
  --mgi_rpt /root/autodl-tmp/BGI/mgi/HOM_MouseHumanSequence.rpt.txt \
  --in_h5ad .../your_file.h5ad \
  --out_h5ad .../your_file.h5ad \
  --map_csv .../mm2hs_from_mgi.csv \
  --drop_unmapped
```

download cpdb datasets
```bash
python download_cpdb_db.py --target-dir /root/autodl-tmp/BGI/cpdb_db --version v5.0.0
```

```bash
mkdir -p /root/autodl-tmp/BGI/cpdb_db/releases/v5.0.0
```

```bash
mv /root/autodl-tmp/BGI/cpdb_db/cellphonedb.zip /root/autodl-tmp/BGI/cpdb_db/releases/v5.0.0/
```

```bash
rm -f /root/autodl-tmp/BGI/cpdb_db/*.csv
rm -rf /root/autodl-tmp/BGI/cpdb_db/sources
```

run cpdb stat_analysis
```bash
python run_cpdb_stat.py \
  --h5ad /root/autodl-tmp/BGI/STOmics/spatial_data/bin20_h5ad_10.30/BM26_A40_C05094F1_hs_symbol.h5ad \
  --meta /root/autodl-tmp/BGI/STOmics/cpdb_inputs/meta_A40.txt \
  --cpdb_dir /root/autodl-tmp/BGI/cpdb_db \
  --cpdb_version v5.0.0 \
  --outdir /root/autodl-tmp/BGI/STOmics/cpdb_out/A40 \
  --counts_data hgnc_symbol \
  --iterations 1000 \
  --threshold 0.1 \
  --threads 64 \
  --score_interactions
```









