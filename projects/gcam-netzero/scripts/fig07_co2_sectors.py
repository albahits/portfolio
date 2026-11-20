import pandas as pd
import matplotlib.pyplot as plt
from style import *

def group(s):
    s = s.lower()
    if s.startswith("elec_biomass") and "ccs" in s:
        return "BECCS (power)"
    if s.startswith("elec") or s == "electricity":
        return "Other power"
    if s == "refining":
        return "Refining & biofuels"
    if s.startswith("trn_freight"):
        return "Freight transport"
    if s.startswith("trn"):
        return "Passenger transport & aviation"
    if s.startswith(("resid", "comm")):
        return "Buildings"
    if "cement" in s:
        return "Cement"
    if s.startswith(("gas", "delivered", "h2", "lh2")):
        return "Fuel supply"
    return "Other industry"

sec = pd.read_csv(r"results\csv\combined\co2_sector.csv")
sec["grp"] = sec["sector"].apply(group)
res = pd.read_csv(r"results\csv\combined\co2_resource.csv")
res["grp"] = "Fuel supply"
both = pd.concat([sec[["scenario", "Year", "grp", "value"]],
                  res[["scenario", "Year", "grp", "value"]]])
both["mt"] = both["value"] * C_TO_CO2

cases = [("NZE2060", 2060), ("NZE2050", 2050)]
data = {s: both[(both["scenario"] == s) & (both["Year"] == y)].groupby("grp")["mt"].sum()
        for s, y in cases}


order = pd.concat(data.values(), axis=1).sum(axis=1).sort_values().index.tolist()

fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.4), sharey=True)
setup(fig, axes)
title(fig, "Net zero is not zero: remaining emissions are offset by removals")
fig.text(0.04, 0.865, "CO2 by sector in the target year, MtCO2", fontsize=9.5,
         style="italic", color=MUTED)

lim = max(d.abs().max() for d in data.values()) * 1.25
for ax, (scen, yr) in zip(axes, cases):
    d = data[scen].reindex(order).fillna(0)
    colors = [FUEL["biomass CCS"] if v < 0 else "#8C6D46" for v in d]
    ax.barh(range(len(d)), d.values, color=colors, height=0.62, zorder=2)
    ax.axvline(0, color=INK, linewidth=0.9, zorder=3)
    for i, v in enumerate(d.values):
        if abs(v) >= 1:
            ax.text(v + (lim * 0.015 if v >= 0 else -lim * 0.015), i, f"{v:,.0f}",
                    va="center", ha="left" if v >= 0 else "right", fontsize=8.5, color=INK)
    pos, neg = d[d > 0].sum(), d[d < 0].sum()
    name, color = SCENARIO[scen]
    ax.set_title(f"{name}, in {yr}", loc="left", fontsize=11, fontweight="bold", color=color, pad=8)
    ax.text(0.98, 0.96, f"Emitted: +{pos:,.0f}\nRemoved: {neg:,.0f}\nNet: {pos + neg:,.0f}",
            transform=ax.transAxes, ha="right", va="top", fontsize=9, color=INK)
    ax.set_xlim(-lim, lim)
    ax.grid(axis="x", color=GRID)
    ax.grid(axis="y", visible=False)

axes[0].set_yticks(range(len(order)))
axes[0].set_yticklabels(order, color=INK)
axes[0].set_ylim(len(order) - 0.5, -0.5)

note(fig, "Negative values are CO2 removals, mostly power from biomass with carbon capture (BECCS). "
          "Net includes about 8 MtCO2 from fossil-fuel extraction not covered by the CO2 cap.\n"
          "Source: author's GCAM v9.1 runs.")
plt.subplots_adjust(left=0.2, right=0.97, top=0.78, bottom=0.15, wspace=0.08)
save(fig, "fig07_co2_sectors")
plt.show()