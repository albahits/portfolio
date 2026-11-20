import pandas as pd
import matplotlib.pyplot as plt
from style import *
from matplotlib.patches import Patch

SCENS = ["Reference_aligned", "NZE2060", "NZE2050"]
YEARS = (2015, 2060)

def base_fuel(name):
    """Map GCAM fuel/technology names to our categories."""
    n = name.lower()
    ccs = "ccs" in n
    if any(k in n for k in ["gen_ii", "gen_iii", "large reactor", "smr"]):
        return "nuclear"
    for key, cat in [("coal", "coal"), ("natural gas", "gas"), ("gas", "gas"),
                     ("refined liquids", "oil"), ("oil", "oil"),
                     ("biomass", "biomass"), ("nuclear", "nuclear"), ("hydro", "hydro"),
                     ("geothermal", "geothermal"), ("wind", "wind"),
                     ("pv", "solar"), ("csp", "solar"), ("solar", "solar")]:
        if key in n:
            return f"{cat} CCS" if ccs and cat in ("coal", "gas", "biomass") else cat
    return None

def spread(ys, gap):
    ys = list(ys)
    for i in range(1, len(ys)):
        ys[i] = max(ys[i], ys[i - 1] + gap)
    return ys

def stacked_panels(df, unit_label, fig_title, fname, note_text, divide=1):
    df = df[(df["Year"] >= YEARS[0]) & (df["Year"] <= YEARS[1])]
    piv_all = df.pivot_table(index=["scenario", "Year"], columns="cat",
                             values="value", aggfunc="sum").fillna(0) / divide
    cats = [c for c in STACK_ORDER if c in piv_all.columns]
    ymax = piv_all[cats].sum(axis=1).max() * 1.08

    fig, axes = plt.subplots(1, 3, figsize=(12, 5.6), sharey=True)
    setup(fig, axes)
    title(fig, fig_title)

    # legend row under the title: one coloured square per category
    handles = [Patch(facecolor=FUEL[c], label=NICE[c]) for c in cats]
    leg = fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.035, 0.895),
                     ncol=len(cats), frameon=False, fontsize=9.5,
                     handlelength=1.1, handleheight=1.1, columnspacing=1.2)
    for text, c in zip(leg.get_texts(), cats):
        text.set_color(FUEL[c])
        text.set_fontweight("bold")

    # unit label under the legend
    fig.text(0.04, 0.825, unit_label, fontsize=9.5, style="italic", color=MUTED)

    for ax, scen in zip(axes, SCENS):
        p = piv_all.loc[scen][cats]
        ax.stackplot(p.index, [p[c] for c in cats],
                     colors=[FUEL[c] for c in cats], linewidth=0)
        name, color = SCENARIO[scen]
        ax.set_title(name, loc="left", fontsize=11, fontweight="bold", color=color, pad=8)
        ax.set_xlim(YEARS)
        ax.set_xticks(range(2020, 2061, 10))
        ax.set_ylim(0, ymax)

    note(fig, note_text)
    plt.subplots_adjust(left=0.06, right=0.97, top=0.73, bottom=0.15, wspace=0.12)
    save(fig, fname)
    plt.show()

# ---------- Figure 4: primary energy ----------
pe = pd.read_csv(r"results\csv\combined\primary_energy.csv")
pe["cat"] = pe["fuel"].apply(base_fuel)
print("unmapped primary fuels:", sorted(pe.loc[pe["cat"].isna(), "fuel"].unique()))
stacked_panels(pe.dropna(subset=["cat"]), "Primary energy, EJ per year",
               "Net zero rebuilds the energy system around biomass, solar and wind",
               "fig04_primary_energy",
               "Primary energy, direct-equivalent accounting. Source: author's GCAM v9.1 runs.")

# ---------- Figure 5: power generation ----------
eg = pd.read_csv(r"results\csv\combined\elec_gen_tech.csv")
eg["cat"] = eg["technology"].apply(base_fuel)
print("unmapped power technologies:", sorted(eg.loc[eg["cat"].isna(), "technology"].unique()))
eg["value"] = eg["value"] * 277.78          # EJ -> TWh
stacked_panels(eg.dropna(subset=["cat"]), "Electricity generation, TWh per year",
               "Power under net zero: coal exits, solar and BECCS take over",
               "fig05_power_mix",
               "Generation by technology, summed across cooling types. CCS = carbon capture and storage; "
               "BECCS = bioenergy with CCS.\nCalibrated to HEESI in 2025 only; after 2025 GCAM deploys solar at its "
               "techno-economic potential, about twice RUPTL's planned pace by 2030. Source: author's GCAM v9.1 runs.")