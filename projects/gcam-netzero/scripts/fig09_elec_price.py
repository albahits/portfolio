import pandas as pd
import matplotlib.pyplot as plt
from style import *

SCENS = ["Reference_aligned", "NZE2060", "NZE2050"]
PANELS = {"elect_td_bld": "Buildings and transport", "elect_td_ind": "Industry"}

d = pd.read_csv(r"results\csv\combined\elec_price.csv")
d = d[(d["Year"] >= 2020) & (d["Year"] <= 2070)].copy()
d["cents_kwh"] = to_usd_mwh(d["value"]) / 10

fig, axes = plt.subplots(1, 2, figsize=(11, 5.2), sharey=True)
setup(fig, axes)
title(fig, "Net zero keeps electricity costs near today's level instead of letting them fall")

for j, scen in enumerate(SCENS):
    name, color = SCENARIO[scen]
    fig.text(0.04 + j * 0.11, 0.865, f"━ {name}", color=color, fontsize=9.5, fontweight="bold")
fig.text(0.04, 0.82, "Delivered electricity price, 2024 US cents per kWh",
         fontsize=9.5, style="italic", color=MUTED)

for ax, (code, label) in zip(axes, PANELS.items()):
    piv = d[d["fuel"] == code].pivot(index="Year", columns="scenario", values="cents_kwh")

    hi = piv[["NZE2060", "NZE2050"]].max(axis=1)
    ax.fill_between(piv.index, piv["Reference_aligned"], hi, where=piv.index >= 2030,
                    color=SCENARIO["NZE2060"][1], alpha=0.10, zorder=1)

    for scen in SCENS:
        name, color = SCENARIO[scen]
        style = "--" if scen == "Reference_aligned" else "-"
        ax.plot(piv.index, piv[scen], color=color, linewidth=2.2, linestyle=style, zorder=2)

    gap = (piv.loc[2040:2060, ["NZE2060", "NZE2050"]].mean(axis=1)
           - piv.loc[2040:2060, "Reference_aligned"]).mean()
    mid = (piv.loc[2050, "Reference_aligned"] + piv.loc[2050, "NZE2060"]) / 2
    ax.text(2050, mid, f"≈ +{gap:.1f}¢ per kWh\nvs baseline, 2040–2060", ha="center", va="center",
            fontsize=9.5, color=SCENARIO["NZE2060"][1], fontweight="bold")

    ax.set_title(label, loc="left", fontsize=10.5, fontweight="bold", color=INK, pad=8)
    ax.set_xlim(2020, 2070)
    ax.set_xticks(range(2030, 2071, 10))
    ax.set_ylim(10, 22)

note(fig, "Model cost of delivered electricity (cost-based), not PLN's regulated and subsidised tariffs. GCAM prices "
          "buildings (households and commercial) and transport identically.\nThe 2030 dip reflects fast solar deployment "
          "after 2025 (see power mix). Converted from 1975 US$/GJ using the US GDP deflator (BEA via FRED). "
          "Source: author's GCAM v9.1 runs.")
plt.subplots_adjust(left=0.07, right=0.97, top=0.74, bottom=0.18, wspace=0.1)
save(fig, "fig09_elec_price")
plt.show()