import pandas as pd

co2 = pd.read_csv(r"results\csv\db_ref_aligned\co2.csv").set_index("Year")
start = co2.loc[2030, "value"]          
years = list(range(2035, 2101, 5))       

for target in [2050, 2060]:
    steps = (target - 2030) // 5          
    caps = {}
    for y in years:
        if y < target:
            caps[y] = start * (1 - (y - 2030) / (target - 2030))
        else:
            caps[y] = 0.0

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             "<scenario>", "  <world>", '    <region name="Indonesia">',
             '      <ghgpolicy name="CO2">',
             "        <market>Indonesia</market>"]
    for y, v in caps.items():
        lines.append(f'        <constraint year="{y}">{v:.2f}</constraint>')
    lines += ["      </ghgpolicy>", "    </region>", "  </world>", "</scenario>"]

    out = rf"D:\GCAM\idn-runs\xml\idn_nze{target}.xml"
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nNZE {target}: {steps} steps from {start:.1f} MTC in 2030")
    for y, v in caps.items():
        if y <= target + 5:
            print(f"  {y}: {v:6.1f} MTC  ({v * 44 / 12:6.0f} MtCO2)")
    print(f"  written {out}")