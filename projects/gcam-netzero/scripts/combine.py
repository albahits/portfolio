import pandas as pd
from pathlib import Path

DBS = ["db_ref_aligned", "db_nze2060", "db_nze2050"]
OUT = Path(r"results\csv\combined")
OUT.mkdir(exist_ok=True)

names = sorted({f.stem
                for db in DBS
                for f in Path(rf"results\csv\{db}").glob("*.csv")
                if not f.stem.startswith("validation")})

for name in names:
    parts = [pd.read_csv(rf"results\csv\{db}\{name}.csv")
             for db in DBS if Path(rf"results\csv\{db}\{name}.csv").exists()]
    combined = pd.concat(parts, ignore_index=True)
    combined.to_csv(OUT / f"{name}.csv", index=False)
    print(f"{name}: {len(combined)} rows, scenarios {sorted(combined['scenario'].unique())}")