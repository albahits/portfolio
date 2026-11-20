import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from style import *

co2 = pd.read_csv(r"data\owid_annual_co2.csv")
val = co2.columns[3]   
co2 = co2[co2["Code"].notna() & ~co2["Code"].astype(str).str.startswith("OWID")]
print("countries in file:", co2["Code"].nunique())  

world = gpd.read_file(r"data\ne_110m_admin_0_countries.zip")[["ADM0_A3", "geometry"]]
world = world[world["ADM0_A3"] != "ATA"].to_crs("ESRI:54030")

BINS = [0, 3e6, 1e7, 3e7, 1e8, 3e8, 1e9, 3e9, 1e10, 1e11]
EDGE = ["0", "3M", "10M", "30M", "100M", "300M", "1B", "3B", "10B"]
COLORS = ["#F4ECDF", "#EBD9BD", "#E2C196", "#D9A46C", "#CC8350",
          "#B5654A", "#934634", "#6E3026", "#4A1F1A"]
cmap, norm = ListedColormap(COLORS), BoundaryNorm(BINS, len(COLORS))

def value(code, yr):
    return co2[(co2["Code"] == code) & (co2["Year"] == yr)][val].iloc[0]

def fmt(v):
    return f"{v / 1e9:.1f} Gt" if v >= 1e9 else f"{v / 1e6:,.0f} Mt"

def anchor(geom):
    """A point inside the country's largest landmass (avoids Alaska, outer islands)."""
    if geom.geom_type == "MultiPolygon":
        geom = max(geom.geoms, key=lambda g: g.area)
    return geom.representative_point()


LABELS = {
    "USA": ("United States", (4.6e6, -1.8e6)),   
    "CHN": ("China", (3.2e6, -2.0e6)),           
    "JPN": ("Japan", (2.6e6, 0.5e6)),            
    "IND": ("India", (-2.6e6, -2.2e6)),          
    "IDN": ("Indonesia", (-3.2e6, -3.4e6)),      
}

YEARS = [2001, 2025]
ratio = value("IDN", YEARS[1]) / value("IDN", YEARS[0])

fig, axes = plt.subplots(1, 2, figsize=(12, 5.6))
setup(fig, axes)
title(fig, f"Indonesia's CO2 emissions have grown {ratio:.1f}-fold since {YEARS[0]}")
fig.text(0.04, 0.865, "Annual CO2 emissions from fossil fuels and industry; land-use change not included",
         fontsize=9.5, style="italic", color=MUTED)

for ax, yr in zip(axes, YEARS):
    ax.set_axis_off()
    d = world.merge(co2[co2["Year"] == yr][["Code", val]],
                    left_on="ADM0_A3", right_on="Code", how="left")
    d.plot(ax=ax, color="#DDE1DB", edgecolor="white", linewidth=0.25)
    d[d[val].notna()].plot(ax=ax, column=val, cmap=cmap, norm=norm,
                           edgecolor="white", linewidth=0.25)

    d[d["ADM0_A3"] == "IDN"].plot(ax=ax, facecolor="none", edgecolor=INK,
                                  linewidth=0.6, alpha=0.6)

    for code, (name, off) in LABELS.items():
        p = anchor(d.loc[d["ADM0_A3"] == code, "geometry"].iloc[0])
        text = f"{name}\n{fmt(value(code, yr))}"
        if code == "IDN":
            style = dict(fontsize=10, fontweight="bold", color=INK,
                         bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#B5654A", lw=1.2))
            line = dict(arrowstyle="-", color="#B5654A", lw=1.0)
        else:
            style = dict(fontsize=8, color=INK,
                         bbox=dict(boxstyle="round,pad=0.25", fc=BG, ec="none", alpha=0.85))
            line = dict(arrowstyle="-", color=MUTED, lw=0.7)
        ax.annotate(text, xy=(p.x, p.y), xytext=(p.x + off[0], p.y + off[1]),
                    ha="center", va="center", arrowprops=line, **style)

cax = fig.add_axes([0.22, 0.14, 0.56, 0.028])
for i, c in enumerate(COLORS):
    cax.add_patch(plt.Rectangle((i, 0), 1, 1, color=c))
    cax.text(i, 1.35, EDGE[i], ha="center", fontsize=8.5, color=MUTED)
cax.text(len(COLORS) / 2, -1.1, "Tonnes of CO2 per year", ha="center", fontsize=8.5,
         style="italic", color=MUTED)
cax.set_xlim(0, len(COLORS)); cax.set_ylim(0, 1); cax.set_axis_off()

note(fig, "Data: Global Carbon Budget (2026), via Our World in Data (CC BY). Boundaries: Natural Earth. "
          "Chart: author's own.")
plt.subplots_adjust(left=0.02, right=0.98, top=0.8, bottom=0.22, wspace=0.03)
save(fig, "fig00_co2_map")
plt.show()