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

map mouse to human in h5ad file
```bash
python make_cpdb_meta_from_h5ad.py \
  --h5ad .../your_file.h5ad \
  --cluster-col cluster \
  --out /root/autodl-tmp/BGI/STOmics/cpdb_inputs/meta_A40.txt
```








