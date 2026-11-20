import pandas as pd

drivers = pd.read_csv(r"data\clean\drivers_idn.csv")
OUT = r"D:\GCAM\idn-runs\xml\socioeconomics_idn.xml"

lines = []
lines.append('<?xml version="1.0" encoding="UTF-8"?>')
lines.append("<scenario>")
lines.append("  <world>")
lines.append('    <region name="Indonesia">')

# population: thousands, from 2025 onward
lines.append("      <demographics>")
for _, r in drivers.iterrows():
    lines.append(f'        <populationMiniCAM year="{int(r.year)}">')
    lines.append(f"          <totalPop>{int(r.pop_updated)}</totalPop>")
    lines.append("        </populationMiniCAM>")
lines.append("      </demographics>")

# GDP: million 1990$, from 2025 onward (TFP left untouched)
lines.append("      <nationalAccountContainer>")
for _, r in drivers.iterrows():
    lines.append(f'        <nationalAccount year="{int(r.year)}">')
    lines.append(f"          <GDP>{int(r.gdp_updated)}</GDP>")
    lines.append("        </nationalAccount>")
lines.append("      </nationalAccountContainer>")

lines.append("    </region>")
lines.append("  </world>")
lines.append("</scenario>")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"written {OUT} ({len(drivers)} years)")