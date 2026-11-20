import pandas as pd

un = pd.read_csv(r"data\clean\population_idn.csv").set_index("year")
oecd = pd.read_csv(r"data\clean\gdp_idn.csv").set_index("year")

gcam_pop = pd.read_csv(r"results\csv\population.csv").set_index("Year")
gcam_gdp = pd.read_csv(r"results\csv\gdp.csv").set_index("Year")

pop = gcam_pop.loc[2021, "value"]   
gdp = gcam_gdp.loc[2021, "value"]
prev = 2021

rows = []
for year in range(2025, 2101, 5):
    years = year - prev                
    g_pop = un.loc[year, "growth_annual"]
    g_gdp = oecd.loc[year, "growth_annual"]

    pop = pop * (1 + g_pop) ** years
    gdp = gdp * (1 + g_gdp) ** years

    rows.append({
        "year": year,
        "pop_updated": round(pop),
        "pop_gcam_default": gcam_pop.loc[year, "value"],
        "gdp_updated": round(gdp),
        "gdp_gcam_default": gcam_gdp.loc[year, "value"],
        "growth_pop": g_pop,
        "growth_gdp": g_gdp,
    })
    prev = year

drivers = pd.DataFrame(rows)
drivers["gdp_per_capita_updated"] = drivers["gdp_updated"] / drivers["pop_updated"]

print("GDP units in GCAM:", gcam_gdp["Units"].iloc[0])
print(drivers.round(4))
drivers.to_csv(r"data\clean\drivers_idn.csv", index=False)