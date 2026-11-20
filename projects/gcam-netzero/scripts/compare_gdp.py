import pandas as pd

ours = pd.read_csv(r"data\clean\gdp_idn.csv")
gcam = pd.read_csv(r"results\csv\gdp.csv")

gcam = gcam.sort_values("Year")
gcam["gcam_growth"] = (gcam["value"] / gcam["value"].shift(1)) ** (1 / gcam["Year"].diff()) - 1

comp = ours.merge(gcam[["Year", "gcam_growth"]], left_on="year", right_on="Year", how="left")
comp["gap_pp"] = (comp["growth_annual"] - comp["gcam_growth"]) * 100

print(comp[["year", "growth_annual", "gcam_growth", "gap_pp"]].round(4))

# Comparing GDP starts from a common 2025 start (index 2025 = 100)
fut = comp[comp["year"] >= 2030].copy()
fut["ours_index"] = 100 * (1 + fut["growth_annual"]).pow(5).cumprod()
fut["gcam_index"] = 100 * (1 + fut["gcam_growth"]).pow(5).cumprod()
fut["ours_vs_gcam_pct"] = (fut["ours_index"] / fut["gcam_index"] - 1) * 100

print(fut[["year", "ours_index", "gcam_index", "ours_vs_gcam_pct"]].round(1))

fut.to_csv(r"results\csv\gdp_comparison.csv", index=False)

print("GDP Comparison Saved")
