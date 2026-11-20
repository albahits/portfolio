import pandas as pd
import matplotlib.pyplot as plt
from style import *

YEAR = 2050
TECHS = {   
    "coal (conv pul)": "Coal",
    "coal (conv pul CCS)": "Coal + CCS",
    "gas (CC)": "Gas combined cycle",
    "gas (CC CCS)": "Gas + CCS",
    "biomass (conv CCS)": "Biomass + CCS (BECCS)",
    "geothermal": "Geothermal",
    "wind": "Wind",
    "wind_storage": "Wind + storage",
    "PV": "Solar PV",
    "PV_storage": "Solar PV + storage",
}

d = pd.read_csv(r"results\csv\combined\elec_cost_tech.csv")
d = d[(d["Year"] == YEAR) & (d["technology"].isin(TECHS))]
d = d[d["value"] < 100]                 # drop placeholder costs for unused technologies
d["usd_mwh"] = to_usd_mwh(d["value"])

fig, ax = plt.subplots(figsize=(9, 5.6))
setup(fig, [ax])
title(fig, f"A carbon price reorders the options: generation cost in {YEAR}")

for j, scen in enumerate(["Reference_aligned", "NZE2060", "NZE2050"]):
    name, color = SCENARIO[scen]
    fig.text(0.04 + j * 0.13, 0.865, f"● {name}", color=color, fontsize=9.5, fontweight="bold")

rows = [t for t in TECHS if t in set(d["technology"])]
for i, tech in enumerate(rows):
    g = d[d["technology"] == tech]
    
    ax.hlines(i, g["usd_mwh"].min(), g["usd_mwh"].max(), color=GRID, linewidth=4, zorder=1)
    for scen in ["Reference_aligned", "NZE2060", "NZE2050"]:
        v = g.loc[g["scenario"] == scen, "usd_mwh"]
        if len(v):
            ax.scatter(v.iloc[0], i, color=SCENARIO[scen][1], s=70, zorder=3)

ax.set_yticks(range(len(rows)))
ax.set_yticklabels([TECHS[t] for t in rows], color=INK)
ax.set_ylim(len(rows) - 0.5, -0.5)
ax.set_xlim(0)
ax.grid(axis="x", color=GRID)
ax.grid(axis="y", visible=False)
panel_label(ax, "Generation cost incl. carbon price, 2024 US$ per MWh")

note(fig, "Costs include the carbon price, so fossil options rise under net zero. Coal + CCS has no baseline value "
          "because carbon capture is not used without a carbon price.\n"
          "Source: author's GCAM v9.1 runs; converted from 1975 US$/GJ using the US GDP deflator (BEA via FRED).")
plt.subplots_adjust(left=0.24, right=0.96, top=0.78, bottom=0.17)
save(fig, "fig06_gen_costs")
plt.show()