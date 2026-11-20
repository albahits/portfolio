import pandas as pd
import matplotlib.pyplot as plt
from style import *

C = 44 / 12  # carbon -> CO2

# ---------- data ----------
co2 = pd.read_csv(r"results\csv\combined\co2.csv")
co2["mt"] = co2["value"] * C
co2 = co2[(co2["Year"] >= 2005) & (co2["Year"] <= 2070)]

def sector_group(s):
    s = s.lower()
    if s.startswith("elec") or s == "electricity":
        return "Power"
    if s.startswith("trn"):
        return "Transport"
    if s.startswith(("resid", "comm")):
        return "Buildings"
    if s.startswith(("refining", "gas processing", "gas pipeline", "delivered", "h2", "lh2")):
        return "Fuel supply"
    return "Industry & other"

sec = pd.read_csv(r"results\csv\combined\co2_sector.csv")
sec["group"] = sec["sector"].apply(sector_group)
res = pd.read_csv(r"results\csv\combined\co2_resource.csv")
res["group"] = "Fuel supply"

both = pd.concat([sec[["scenario", "Year", "group", "value"]],
                  res[["scenario", "Year", "group", "value"]]])
y2060 = both[both["Year"] == 2060].groupby(["scenario", "group"])["value"].sum() * C
cuts = (y2060["Reference_aligned"] - y2060["NZE2060"]).sort_values(ascending=False)

# ---------- figure ----------
fig, (axL, axR) = plt.subplots(1, 2, figsize=(11, 5.4),
                               gridspec_kw={"width_ratios": [2.3, 1]})
setup(fig, [axL, axR])
title(fig, "Net zero means bending a rising path")

# ----- left panel: CO2 paths -----
piv = co2.pivot(index="Year", columns="scenario", values="mt")

# shaded abatement gap (baseline vs NZE 2060), from 2030
axL.fill_between(piv.index, piv["NZE2060"], piv["Reference_aligned"],
                 where=piv.index >= 2030, color=SCENARIO["NZE2060"][1], alpha=0.12)


hist = piv[piv.index <= 2030]
axL.plot(hist.index, hist["Reference_aligned"], color=INK, linewidth=2.4)
axL.text(2017.5, 640, "Historical and\ncalibrated", color=INK, fontsize=9, ha="center")

# scenarios: from 2030 onward
fut = piv[piv.index >= 2030]
for scen in ["Reference_aligned", "NZE2060", "NZE2050"]:
    name, color = SCENARIO[scen]
    style = "--" if scen == "Reference_aligned" else "-"
    axL.plot(fut.index, fut[scen], color=color, linewidth=2.4, linestyle=style)
    label_end(axL, fut.index[-1], fut[scen].iloc[-1], name, color,
              dy={"NZE2060": 95, "NZE2050": 40}.get(scen, 0))

axL.text(2048, 620, "Abatement needed\nunder NZE 2060", color=SCENARIO["NZE2060"][1],
         fontsize=9.5, ha="center")
axL.set_ylim(0, 1200)
axL.set_xlim(2005, 2083)
panel_label(axL, "Energy and industry CO2, MtCO2 per year")

# ----- right panel: where the 2060 cuts come from -----
colors = {"Power": "#2F6F8F", "Industry & other": "#8C6D46", "Transport": "#7F93A8",
          "Buildings": "#E3B04B", "Fuel supply": "#7A8B3C"}

items = list(cuts.items())
centers, bottom = [], 0
for grp, val in items:
    axR.bar(0, val, bottom=bottom, color=colors[grp], width=0.55)
    centers.append(bottom + val / 2)
    bottom += val

ys = centers[:]
for i in range(1, len(ys)):
    ys[i] = max(ys[i], ys[i - 1] + 60)

for (grp, val), y, c in zip(items, ys, centers):
    axR.annotate(f"{grp}  {val:,.0f}", xy=(0.28, c), xytext=(0.36, y),
                 va="center", fontsize=9.5, fontweight="bold", color=colors[grp],
                 arrowprops=dict(arrowstyle="-", color=colors[grp], lw=0.8)
                 if abs(y - c) > 5 else None)

axR.set_ylim(0, max(bottom, ys[-1]) + 60)
axR.set_xlim(-0.4, 1.4)
axR.set_xticks([0])
axR.set_xticklabels([f"Total reduction\nin 2060 ({bottom:,.0f} Mt)"], color=MUTED)
axL.set_xticks(range(2010, 2071, 10))
axL.axvline(2060, color=MUTED, linewidth=0.8, linestyle=":", zorder=0)
axL.text(2060, 1150, "2060 →", color=MUTED, fontsize=8.5, ha="center")
panel_label(axR, "Reduction vs baseline in 2060, MtCO2")

# ----- note -----
note(fig, "The shaded area shows the gap between the baseline and the NZE 2060 path. "
          "The right panel splits the 2060 gap by sector; power includes negative emissions from bioenergy with CCS.\n"
          "Source: author's GCAM v9.1 runs, calibrated to UN population, OECD GDP and HEESI 2025.")

plt.subplots_adjust(left=0.06, right=0.97, top=0.82, bottom=0.2, wspace=0.18)
save(fig, "fig03_co2_headline")
plt.show()