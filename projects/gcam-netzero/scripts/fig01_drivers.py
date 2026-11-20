import pandas as pd
import matplotlib.pyplot as plt
from style import *

d = pd.read_csv(r"data\clean\drivers_idn.csv")

# GDP: million 1990 US$ -> trillion 2024 US$; population: thousand -> million
d["gdp_upd"] = to_2024usd(d["gdp_updated"], 1990) / 1e6
d["gdp_def"] = to_2024usd(d["gdp_gcam_default"], 1990) / 1e6
d["pop_upd"] = d["pop_updated"] / 1e3
d["pop_def"] = d["pop_gcam_default"] / 1e3

fig, (axL, axR) = plt.subplots(1, 2, figsize=(11, 5))
setup(fig, [axL, axR])
title(fig, "Updated drivers: a larger economy, a later population peak")

panels = [
    (axL, "gdp_upd", "gdp_def", "GDP, trillion 2024 US$ (market exchange rates)",
     "OECD-based", "GCAM default", (0, None), (2040, 1.10)),
    (axR, "pop_upd", "pop_def", "Population, million",
     "UN WPP", "GCAM default", (250, 335), (2072, 1.025)),
]

for ax, upd, dft, label, name_upd, name_def, ylim, (ax_x, ax_yf) in panels:
    ax.plot(d["year"], d[dft], color=SCENARIO["Reference_aligned"][1], linewidth=2.2, linestyle="--")
    ax.plot(d["year"], d[upd], color=INK, linewidth=2.4)
    last = d.iloc[-1]
    label_end(ax, last["year"], last[upd], name_upd, INK, dy=0)
    label_end(ax, last["year"], last[dft], name_def, SCENARIO["Reference_aligned"][1], dy=0)

    
    r = d[d["year"] == 2060].iloc[0]
    diff = (r[upd] / r[dft] - 1) * 100
    ax.annotate(f"{diff:+.1f}% in 2060", xy=(2060, r[upd]), xytext=(ax_x, r[upd] * ax_yf),
                fontsize=9.5, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))

    ax.set_xlim(2025, 2118)
    ax.set_xticks(range(2030, 2101, 10))
    ax.set_ylim(*ylim)
    panel_label(ax, label)

note(fig, "Updated paths keep GCAM's 2021 calibration and apply observed growth to 2025, then OECD (GDP) and UN WPP medium-variant "
          "(population) projections.\nGDP converted from 1990 US$ using the US GDP deflator (BEA via FRED). "
          "Source: author's calculations; GCAM v9.1 defaults (SSP2).")
plt.subplots_adjust(left=0.06, right=0.97, top=0.82, bottom=0.18, wspace=0.22)
save(fig, "fig01_drivers")
plt.show()