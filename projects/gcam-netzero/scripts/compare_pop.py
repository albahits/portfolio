import pandas as pd

ours = pd.read_csv(r"data\clean\population_idn.csv")
gcam = pd.read_csv(r"results\csv\population.csv")

comp = ours.merge(gcam[["Year", "value"]], left_on="year", right_on="Year", how="left")
comp = comp.rename(columns={"value": "pop_gcam_thousand"})
comp["un_vs_gcam_pct"] = (comp["pop_thousand"] / comp["pop_gcam_thousand"] - 1) * 100

print(comp[["year", "pop_thousand", "pop_gcam_thousand", "un_vs_gcam_pct"]].round(1))
comp.to_csv(r"results\csv\population_comparison.csv", index=False)