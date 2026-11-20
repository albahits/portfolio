import pandas as pd
import matplotlib.pyplot as plt
from style import *

p = pd.read_csv(r"results\csv\combined\co2_price.csv")
p = p[(p["Year"] >= 2030) & (p["Year"] <= 2070)]
p["usd"] = to_usd_tco2(p["value"])
piv = p.pivot(index="Year", columns="scenario", values="usd")

fig, ax = plt.subplots(figsize=(9, 5.2))
setup(fig, [ax])
title(fig, "Ten years earlier means paying the high price ten years earlier")
fig.text(0.04, 0.865, "Carbon price needed to meet the cap, 2024 US$ per tonne of CO2",
         fontsize=9.5, style="italic", color=MUTED)


span = piv.loc[2035:2050]
ax.fill_between(span.index, span["NZE2060"], span["NZE2050"],
                color=SCENARIO["NZE2050"][1], alpha=0.15)
gap = (span["NZE2050"] / span["NZE2060"] - 1) * 100
ax.text(2042.5, span["NZE2050"].loc[2045] + 18,
        f"NZE 2050 costs {gap.min():.0f}–{gap.max():.0f}%\nmore in 2035–2050",
        color=SCENARIO["NZE2050"][1], fontsize=9.5, ha="center")

for scen, target in [("NZE2060", 2060), ("NZE2050", 2050)]:
    name, color = SCENARIO[scen]
    ax.plot(piv.loc[2030:2035].index, piv.loc[2030:2035, scen], color=color,
        linewidth=1.6, linestyle=":")                     
    ax.plot(piv.loc[2035:].index, piv.loc[2035:, scen], color=color, linewidth=2.4)
    ax.scatter(target, piv.loc[target, scen], color=color, s=60, zorder=3)
    ax.annotate(f"net zero\n{target}", xy=(target, piv.loc[target, scen]),
                xytext=(target, piv.loc[target, scen] + 22), ha="center",
                fontsize=8.5, color=color)
    label_end(ax, piv.index[-1], piv[scen].iloc[-1], name, color,
              dy={"NZE2060": 8, "NZE2050": -8}[scen])

ax.text(2035.6, 22, "caps start in 2035", fontsize=8.5, color=MUTED)
ax.set_xlim(2030, 2076)
ax.set_xticks(range(2030, 2071, 10))
ax.set_ylim(0, piv.max().max() * 1.25)

note(fig, "Shadow price of the CO2 cap for Indonesia's energy and industry emissions. Prices fall after the target year "
          "as clean technologies keep getting cheaper.\n"
          "Converted from 1990 US$ per tC using the US GDP deflator (BEA via FRED) and 44/12. Source: author's GCAM v9.1 runs.")
plt.subplots_adjust(left=0.08, right=0.95, top=0.8, bottom=0.17)
save(fig, "fig08_carbon_price")
plt.show()