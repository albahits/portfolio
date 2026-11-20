import pandas as pd

drivers = pd.read_csv(r"data\clean\drivers_idn.csv")

pop = pd.read_csv(r"results\csv\db_ref_updated\population.csv")
gdp = pd.read_csv(r"results\csv\db_ref_updated\gdp.csv")

for name, gcam, col in [("population", pop, "pop_updated"), ("GDP", gdp, "gdp_updated")]:
    out = gcam[gcam["scenario"] == "Reference_updated"][["Year", "value"]]
    comp = drivers[["year", col]].merge(out, left_on="year", right_on="Year")
    comp["diff_pct"] = (comp["value"] / comp[col] - 1) * 100
    print(f"\n{name}: GCAM output vs our input")
    print(comp[["year", col, "value", "diff_pct"]].round(2))