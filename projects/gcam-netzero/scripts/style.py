import matplotlib.pyplot as plt
import os

# --- color palette ---
BG = "#EEF1EC"        # soft sage-grey panel background
INK = "#2B2F2E"       # main text
MUTED = "#6B7370"     # notes, axes
GRID = "#D5DAD4"

SCENARIO = {
    "Reference_aligned": ("Baseline", "#8A9099"),   # slate grey: business as usual
    "NZE2060": ("NZE 2060", "#2E7D5B"),             # forest green: the official target
    "NZE2050": ("NZE 2050", "#C98A2B"),             # amber: the accelerated ambition
}

FUEL = {
    "coal": "#4A4A48", "refined liquids": "#8C6D46", "oil": "#8C6D46",
    "gas": "#7F93A8", "nuclear": "#8E7CA8", "hydro": "#2F6F8F",
    "geothermal": "#B5654A", "biomass": "#7A8B3C", "solar": "#E3B04B",
    "wind": "#6FB3A8", "rooftop_pv": "#F0CC7A",
}

def setup(fig, axes):
    """Apply the shared look to a figure and its panels."""
    fig.patch.set_facecolor(BG)
    for ax in axes:
        ax.set_facecolor(BG)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color(MUTED)
        ax.tick_params(colors=MUTED, length=0)
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)

def title(fig, text):
    fig.text(0.04, 0.95, text, fontsize=15, fontweight="bold", color=INK, va="top")

def panel_label(ax, text):
    """Small italic axis label above the panel, NBER-style."""
    ax.text(0, 1.04, text, transform=ax.transAxes, fontsize=9.5, style="italic", color=MUTED)

def label_end(ax, x, y, text, color, dy=0):
    """Write a series name at the end of its line instead of using a legend."""
    ax.text(x + 1, y + dy, text, color=color, fontsize=10, fontweight="bold", va="center")

def note(fig, text):
    fig.text(0.96, 0.02, text, fontsize=8, style="italic", color=MUTED, ha="right", va="bottom")

def save(fig, name):
    os.makedirs(r"results\figures", exist_ok=True)
    fig.savefig(rf"results\figures\{name}.png", dpi=200, facecolor=fig.get_facecolor())

# Unit conversion for GDP price deflator, index 2017=100 // Source: BEA via FRED, series A191RD3A086NBEA (retrieved 20 Nov 2026)
DEFLATOR = {1975: 27.800, 1990: 59.305, 2024: 125.428}
GJ_PER_MWH = 3.6
C_TO_CO2 = 44 / 12

def to_2024usd(value, from_year):
    return value * DEFLATOR[2024] / DEFLATOR[from_year]

def to_usd_mwh(v_1975usd_per_gj):
    """GCAM costs and prices: 1975 US$/GJ -> 2024 US$/MWh"""
    return to_2024usd(v_1975usd_per_gj, 1975) * GJ_PER_MWH

def to_usd_tco2(v_1990usd_per_tc):
    """GCAM carbon price: 1990 US$/tC -> 2024 US$/tCO2"""
    return to_2024usd(v_1990usd_per_tc, 1990) / C_TO_CO2

FUEL.update({
    "coal CCS": "#8A8A86",      # lighter charcoal
    "gas CCS": "#AEBCCB",       # lighter slate
    "biomass CCS": "#4E5F22",   # deep olive: BECCS
})
STACK_ORDER = ["coal", "coal CCS", "oil", "gas", "gas CCS", "nuclear", "hydro",
               "geothermal", "biomass", "biomass CCS", "wind", "solar"]
NICE = {"coal": "Coal", "coal CCS": "Coal + CCS", "oil": "Oil", "gas": "Gas",
        "gas CCS": "Gas + CCS", "nuclear": "Nuclear", "hydro": "Hydro",
        "geothermal": "Geothermal", "biomass": "Biomass", "biomass CCS": "BECCS",
        "wind": "Wind", "solar": "Solar"}