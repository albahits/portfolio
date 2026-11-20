import pandas as pd
import matplotlib.pyplot as plt
from style import *

def load(db):
    v = pd.read_csv(rf"results\csv\{db}\validation_elec_2025.csv", index_col=0)
    v = v.drop(index="TOTAL", errors="ignore")
    if "rooftop_pv" in v.index:
        v.loc["solar"] = v.loc["solar"] + v.loc["rooftop_pv"]
        v = v.drop(index="rooftop_pv")
    return v

def get(df, t, col):
    return df.loc[t, col] if t in df.index else 0.0

unadj = load("db_ref_updated")
align = load("db_ref_aligned")

LABELS = {"coal": "Coal", "gas": "Gas", "hydro": "Hydro", "geothermal": "Geothermal",
          "biomass": "Biomass", "refined liquids": "Oil products",
          "solar": "Solar (incl. rooftop)", "wind": "Wind", "nuclear": "Nuclear"}
BIG = ["coal", "gas", "hydro", "geothermal", "biomass", "refined liquids"]
SMALL = ["solar", "wind", "nuclear"]

C_UNADJ = "#B5654A"   # terracotta: unadjusted model
C_ALIGN = INK           # dark: aligned model
C_BAND = "#BCC9BF"    # HEESI range

fig, (axL, axR) = plt.subplots(1, 2, figsize=(11, 5.4),
                               gridspec_kw={"width_ratios": [1.6, 1]})
setup(fig, [axL, axR])
title(fig, "Calibrating to HEESI's result corrects GCAM’s 2025 power mix")

fig.text(0.04, 0.865, "▬ HEESI 2025 range", color="#93A396", fontsize=9.5, fontweight="bold")
fig.text(0.19, 0.865, "○ Unadjusted model", color=C_UNADJ, fontsize=9.5, fontweight="bold")
fig.text(0.34, 0.865, "● Aligned baseline", color=C_ALIGN, fontsize=9.5, fontweight="bold")

for ax, techs, xmax in [(axL, BIG, 350), (axR, SMALL, 36)]:
    for i, t in enumerate(techs):
        lo, hi = get(unadj, t, "heesi_on_grid"), get(unadj, t, "heesi_all")
        u, a = get(unadj, t, "gcam_2025"), get(align, t, "gcam_2025")

        
        ax.hlines(i, lo, max(hi, lo + xmax * 0.008), color=C_BAND, linewidth=14, zorder=1)

        
        if abs(u - a) > xmax * 0.02:
            ax.annotate("", xy=(a, i), xytext=(u, i),
                        arrowprops=dict(arrowstyle="-|>", color=C_UNADJ, lw=1.2,
                                        shrinkA=7, shrinkB=6), zorder=2)

       
        ax.scatter(u, i, s=130, facecolors="none", edgecolors=C_UNADJ, linewidths=1.8, zorder=3)
        ax.scatter(a, i, s=45, color=C_ALIGN, zorder=4)

    ax.set_yticks(range(len(techs)))
    ax.set_yticklabels([LABELS[t] for t in techs], color=INK)
    ax.set_ylim(len(BIG) - 0.5, -0.5)          
    ax.set_xlim(-xmax * 0.03, xmax)
    ax.grid(axis="x", color=GRID)
    ax.grid(axis="y", visible=False)

panel_label(axL, "Major sources, TWh in 2025")
panel_label(axR, "Smaller sources (zoomed), TWh in 2025")

s_u, s_h = get(unadj, "solar", "gcam_2025"), get(unadj, "solar", "heesi_all")
w_u, w_h = get(unadj, "wind", "gcam_2025"), get(unadj, "wind", "heesi_all")
axR.text(0, 4.2,
         f"Without calibration, the model shows\n"
         f"solar at {s_u / s_h:.0f}× and wind at {w_u / w_h:.0f}× actual output,\n"
         f"plus nuclear power Indonesia does not have.",
         fontsize=9.5, color=C_UNADJ, va="center")

note(fig, "HEESI range: lower bound = PLN and PLN purchases (on-grid); upper bound = all categories including captive and private generation.\n"
          "Unadjusted = updated population and GDP only; aligned = 2025 solar, wind and nuclear fixed to HEESI. Arrows show the calibration change. "
          "Source: HEESI 2025 (ESDM); author's GCAM v9.1 runs.")
plt.subplots_adjust(left=0.11, right=0.97, top=0.78, bottom=0.2, wspace=0.42)
save(fig, "fig02_calibration")
plt.show()