import gcamreader
import pandas as pd
import sys
import os

GCAM = r"D:\GCAM\gcam-v9.1-Windows-Release-Package"


DB = sys.argv[1] if len(sys.argv) > 1 else "database_basexdb"
OUT = rf"results\csv\{DB}"
os.makedirs(OUT, exist_ok=True)

QUERIES = {
    "population": "population by region",
    "gdp": "GDP MER by region",
    "primary_energy": "primary energy consumption by region (direct equivalent)",
    "final_energy": "final energy consumption by sector and fuel",
    "elec_gen": "elec gen by subsector",
    "elec_gen_tech": "elec gen by gen tech and cooling tech (incl cogen)",
    "elec_cost_tech": "elec gen costs by tech",
    "elec_price": "elec prices by sector",
    "co2": "CO2 emissions by region",
    "co2_sector": "CO2 emissions by sector (no bio) (excluding resource production)",
    "co2_price": "CO2 prices", "co2_resource": "CO2 emissions by resource production "
}

conn = gcamreader.LocalDBConn(rf"{GCAM}\output", DB)
all_queries = gcamreader.parse_batch_query(rf"{GCAM}\output\queries\Main_queries.xml")
by_title = {q.title: q for q in all_queries}

for short, title in QUERIES.items():
    if title not in by_title:
        print(f"NOT FOUND: {title}")
        continue

    df = conn.runQuery(by_title[title], regions=["Indonesia"])

    if df is None or df.empty:
        print(f"empty (skipped): {short}")
        continue

    df["scenario"] = df["scenario"].str.split(",").str[0]
    df.to_csv(rf"{OUT}\{short}.csv", index=False)
    print(f"saved {short}: {len(df)} rows")