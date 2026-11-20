import pandas as pd

WB = r"D:\Project\Portfolio Website\projects\gcam-netzero\data\Updated Datasheet for GCAM.xlsx"

gdp = pd.read_excel(
    WB,
    sheet_name="GDP Growth (OECD)",
    usecols="A:D",   
    skiprows=3,      
    nrows=23,        
)
print(gdp.head(25))

# ---- GDP (OECD) ----
gdp_clean = gdp.rename(columns={
    "Year": "year",
    "GDP (million USD, 2021 PPP)": "gdp_musd_ppp2021",
    "growth_rate (%)": "growth_annual",
    "Basis of growth": "basis",
})

gdp_clean.to_csv(r"data\clean\gdp_idn.csv", index=False)
print("saved data\\clean\\gdp_idn.csv")

# ---- Population (UN) ----
pop = pd.read_excel(WB, sheet_name="Pop Gr (UN)", skiprows=3, nrows=23)

pop_clean = pop.iloc[:, [0, 1, 3, 5]]
pop_clean.columns = ["year", "pop_thousand", "growth_annual", "pop_koneksi_thousand"]

pop_clean.to_csv(r"data\clean\population_idn.csv", index=False)
print("saved data\\clean\\population_idn.csv")

heesi = pd.read_excel(WB, sheet_name="HEESI_Raw", skiprows=3)
gen = heesi[heesi["Variable"] == "Generation"]

print(gen.groupby(["Year", "Owner / category"])["Value"].sum().round(0))
print(gen[gen["Year"] == 2025][["Owner / category", "HEESI line item", "GCAM group", "Value"]].to_string())
