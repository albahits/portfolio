import sys
import pandas as pd
import xml.etree.ElementTree as ET

target = sys.argv[1] 

root = ET.parse(rf"D:\GCAM\idn-runs\xml\idn_nze{target}.xml").getroot()
caps = {int(c.get("year")): float(c.text) for c in root.iter("constraint")}

# GCAM's results
co2 = pd.read_csv(rf"results\csv\db_nze{target}\co2.csv").set_index("Year")["value"]
price = pd.read_csv(rf"results\csv\db_nze{target}\co2_price.csv").set_index("Year")["value"]
units = pd.read_csv(rf"results\csv\db_nze{target}\co2_price.csv")["Units"].iloc[0]

print(f"NZE {target}   (emissions in MTC, price in {units})")
for y in range(2025, 2071, 5):
    cap = caps.get(y)
    cap_txt = f"{cap:7.1f}" if cap is not None else "    -  "
    print(f"  {y}: emissions {co2.get(y, float('nan')):7.1f}   cap {cap_txt}  price {price.get(y, 0):8.1f}")