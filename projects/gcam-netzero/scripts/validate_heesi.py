import pandas as pd
import sys

DB = sys.argv[1] if len(sys.argv) > 1 else "db_ref_aligned"

WB = r"D:\Project\Portfolio Website\projects\gcam-netzero\data\Updated Datasheet for GCAM.xlsx"
EJ_TO_TWH = 277.78

# HEESI group -> GCAM subsector
MAP = {
    "Steam (coal-dominated)": "coal", "Coal gasification (IGCC)": "coal",
    "Gas - open cycle": "gas", "Gas - combined cycle": "gas",
    "Gas - engine": "gas", "Gas (all types)": "gas",
    "Diesel": "refined liquids", "Hydro": "hydro", "Geothermal": "geothermal",
    "Wind": "wind", "Solar PV": "solar",
    "Biomass": "biomass", "Biogas & waste": "biomass", "Bioenergy": "biomass",
    "Other": "other",
}
ON_GRID = ["PLN", "PLN purchase (IPP, captive, PPU)"]

# --- HEESI 2025, in TWh ---
heesi = pd.read_excel(WB, sheet_name="HEESI_Raw", skiprows=3)
gen = heesi[(heesi["Variable"] == "Generation") & (heesi["Year"] == 2025)].copy()
gen["subsector"] = gen["GCAM group"].map(MAP)
gen["twh"] = gen["Value"] / 1000

on_grid = gen[gen["Owner / category"].isin(ON_GRID)].groupby("subsector")["twh"].sum()
all_cat = gen.groupby("subsector")["twh"].sum()

# --- GCAM 2025, in TWh ---
gcam = pd.read_csv(rf"results\csv\{DB}\elec_gen.csv")
gcam25 = gcam[gcam["Year"] == 2025].groupby("subsector")["value"].sum() * EJ_TO_TWH

comp = pd.DataFrame({
    "heesi_on_grid": on_grid,
    "heesi_all": all_cat,
    "gcam_2025": gcam25,
}).fillna(0)
comp.loc["TOTAL"] = comp.sum()

print(comp.round(1))
comp.round(2).to_csv(rf"results\csv\{DB}\validation_elec_2025.csv")