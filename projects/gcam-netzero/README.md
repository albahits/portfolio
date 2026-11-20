# Net zero by 2060 or 2050? Modeling Indonesia's pathways with GCAM

Replication files for a portfolio project that calibrates GCAM v9.1 to Indonesia and compares two net-zero targets: 2060 (the official target) and 2050 (the accelerated ambition).

**Write-up:** the project page in this folder (`index.qmd`), published on the author's website.
**Author:** Al Bahits Annef

## Scenarios

| Scenario | Configuration | What it adds | Role |
|---|---|---|---|
| `Reference_updated` | `config_ref_updated.xml` | UN population and OECD GDP from 2025 | Intermediate run, used only to validate against HEESI 2025 |
| `Reference_aligned` | `config_ref_aligned.xml` | + 2025 power mix fixed to HEESI 2025 | **Baseline** for all comparisons |
| `NZE2060` | `config_nze2060.xml` | + CO2 cap for Indonesia, zero from 2060 | Official target |
| `NZE2050` | `config_nze2050.xml` | + CO2 cap for Indonesia, zero from 2050 | Accelerated target |

Both caps cover energy and industry CO2 only, follow the baseline to a 2030 peak (198.3 MtC), decline linearly to zero in the target year and stay at zero to 2100. Indonesia has its own carbon market; other regions have no policy.

## Folder structure

```
gcam-netzero/
├── index.qmd               project page (Quarto)
├── requirements.txt        Python packages and versions
├── data/
│   ├── Updated Datasheet for GCAM.xlsx   source workbook: GDP, population, HEESI 2025
│   ├── clean/              cleaned inputs and driver table
│   ├── owid_annual_co2.csv          Global Carbon Budget via Our World in Data (Figure 0)
│   └── ne_110m_admin_0_countries.zip  Natural Earth country boundaries (Figure 0)
├── gcam/
│   ├── configs/            one GCAM configuration per scenario
│   └── xml/                add-on input files read by GCAM
├── results/
│   ├── csv/combined/       all three scenarios, one file per output
│   ├── csv/validation_*.csv  2025 generation vs HEESI, before and after calibration
│   ├── figures/            the ten figures used on the page
│   └── query_list.txt      titles of all queries in GCAM v9.1 Main_queries.xml
└── scripts/                pipeline, checks and figures (see below)
```

Per-scenario extracts (`results/csv/db_*`) and the Python environment (`.venv`) are not committed; the scripts regenerate them.

## Requirements

- **GCAM v9.1** Windows release package from [JGCRI/gcam-core releases](https://github.com/JGCRI/gcam-core/releases)
- **Java** (64-bit JDK) for GCAM's output database and for `gcamreader`. Set `JAVA_HOME` and add its `bin` folder to `PATH`.
- **Python 3.12**
- **Disk space:** about 3 GB per scenario database (four runs, about 12 GB)
- **Quarto** only to render the page

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Reproducing the results

There are two levels. Run every command from this folder (`gcam-netzero`) with the environment active.

### A. Rebuild the figures only (minutes)

The combined results are committed, so the figures can be rebuilt without GCAM:

```powershell
python scripts\fig00_co2_map.py
python scripts\fig01_drivers.py
python scripts\fig02_calibration.py
python scripts\fig03_co2_headline.py
python scripts\fig04_05_mix.py
python scripts\fig06_gen_costs.py
python scripts\fig07_co2_sectors.py
python scripts\fig08_carbon_price.py
python scripts\fig09_elec_price.py
```

### B. Rerun the full pipeline (several hours)

**1. Paths.** Several files use absolute paths from the author's machine. Adjust them before running:

| Location | Path to change |
|---|---|
| `gcam/configs/*.xml` | `D:/GCAM/idn-runs/xml/...` (add-on files) and the `xmldb-location` database name |
| `scripts/extract.py` | `GCAM` (the GCAM install folder) |
| `scripts/write_socio_xml.py`, `scripts/build_nze_xml.py` | output folder for the XML files |
| `scripts/check_nze.py` | folder the caps are read from |
| `scripts/prepare_inputs.py` | workbook file name |

The configurations were originally kept in `D:\GCAM\idn-runs\`, outside the GCAM install, so GCAM's own files are never edited.

**2. A launcher that accepts a configuration.** In the GCAM `exe` folder, copy `run-gcam.bat` to `run-idn.bat` and change its last command from `gcam.exe -C configuration.xml` to:

```bat
gcam.exe -C "%~1"
```

Run any scenario from the `exe` folder with:

```powershell
.\run-idn.bat <path to configuration>
```

GCAM runs from `exe`, so relative paths in a configuration (`../input/...`) are read from there. Each run takes about 25 minutes plus a few minutes to save the database; do not close the window or open ModelInterface until it prints "Model exiting successfully".

**3. Drivers (population and GDP).**

```powershell
python scripts\prepare_inputs.py     # workbook -> data/clean/gdp_idn.csv, population_idn.csv
python scripts\build_drivers.py      # GCAM 2021 base x observed/UN/OECD growth -> data/clean/drivers_idn.csv
python scripts\write_socio_xml.py    # -> socioeconomics_idn.xml
```

`build_drivers.py` and the comparison scripts also read GCAM's default population and GDP. Get them by running the unmodified reference configuration once and extracting it (`python scripts\extract.py database_basexdb`).

**4. Updated and aligned baselines.** Run `config_ref_updated.xml`, then `config_ref_aligned.xml`, and after each run:

```powershell
python scripts\extract.py db_ref_updated      # or db_ref_aligned
python scripts\check_drivers.py               # GCAM output equals driver input
python scripts\validate_heesi.py db_ref_updated   # 2025 generation vs HEESI
```

**5. Net-zero scenarios.** The caps are computed from the aligned baseline's 2030 emissions, so step 4 must come first:

```powershell
python scripts\build_nze_xml.py    # -> idn_nze2050.xml, idn_nze2060.xml
```

Run `config_nze2060.xml` and `config_nze2050.xml`, then:

```powershell
python scripts\extract.py db_nze2060
python scripts\extract.py db_nze2050
python scripts\check_nze.py 2060   # emissions vs caps, carbon price
python scripts\check_nze.py 2050
```

**6. Combine and plot.**

```powershell
python scripts\combine.py          # -> results/csv/combined/
```

Then rebuild the figures as in A.

## Scripts

| Script | Reads | Writes / does |
|---|---|---|
| `prepare_inputs.py` | workbook | cleaned GDP and population CSVs |
| `compare_gdp.py`, `compare_pop.py` | cleaned inputs, GCAM defaults | gap between updated and default drivers |
| `build_drivers.py` | cleaned inputs, GCAM defaults | `drivers_idn.csv` |
| `write_socio_xml.py` | `drivers_idn.csv` | `socioeconomics_idn.xml` |
| `build_nze_xml.py` | baseline `co2.csv` | `idn_nze2050.xml`, `idn_nze2060.xml` |
| `extract.py <database>` | a GCAM database | `results/csv/<database>/*.csv` |
| `combine.py` | all scenario folders | `results/csv/combined/*.csv` |
| `check_drivers.py` | drivers and extracted output | confirms the override worked |
| `validate_heesi.py <database>` | workbook, extracted generation | `results/csv/validation_<database>.csv` |
| `check_nze.py <year>` | caps XML, extracted output | emissions vs caps |
| `style.py` | | shared palette, chart helpers, unit conversions |
| `fig00_co2_map.py` … `fig09_elec_price.py` | combined results, data | `results/figures/*.png` |

## Method choices

- **2021 calibration kept.** Population and GDP follow observed growth to 2025, then UN WPP (medium variant) and OECD long-term growth rates, applied to GCAM's 2021 values. Replacing the 2021 values themselves would require rebuilding GCAM's input data (gcamdata).
- **GDP override.** GCAM's macro module recalibrates total factor productivity to reproduce the supplied GDP path; `check_drivers.py` confirms an exact match.
- **2025 power mix.** Solar, wind and nuclear are fixed with `fixedOutput` and `share-weight 0`, the mechanism GCAM uses for hydropower. `fixedOutput` sets new output only; plants built earlier keep running, so new wind is set to 0 and new PV to HEESI minus existing output.
- **HEESI range.** Lower bound: PLN and PLN purchases (on-grid). Upper bound: all categories, including captive and private generation.

## Units

| Quantity | GCAM unit | Shown as |
|---|---|---|
| CO2 | MtC | MtCO2 (× 44/12) |
| Electricity | EJ | TWh (× 277.78) |
| Generation costs, electricity prices | 1975 US$/GJ | 2024 US$/MWh (× 4.512 × 3.6) |
| Carbon price | 1990 US$/tC | 2024 US$/tCO2 (× 2.115 ÷ 3.67) |
| GDP | million 1990 US$ (MER) | trillion 2024 US$ |

Price levels use the US GDP implicit price deflator (BEA via FRED, series A191RD3A086NBEA: 1975 = 27.800, 1990 = 59.305, 2024 = 125.428).

## Limitations

- The caps cover energy and industry CO2, not forestry and land use; about 8 MtCO2 a year from fossil-fuel extraction is outside the cap.
- Calibration fixes 2025 only; after 2025 GCAM deploys solar faster than RUPTL 2025–2034 plans.
- Captive coal for industry is under-represented; the baseline's 2025 CO2 is about 17% below the Global Carbon Budget estimate.
- Indonesia is a single region; electricity prices are model costs, not PLN tariffs.

## Data sources

| Data | Source | Terms |
|---|---|---|
| GCAM v9.1 | JGCRI / Pacific Northwest National Laboratory | ECL-2.0 |
| Population | UN World Population Prospects (medium variant) | see source |
| GDP | OECD long-term GDP projections; World Bank WDI | see source |
| Energy balance | HEESI 2025, Ministry of Energy and Mineral Resources | see source |
| CO2 by country (Figure 0) | Global Carbon Budget (2026), via Our World in Data | CC BY 4.0 |
| Country boundaries (Figure 0) | Natural Earth, 1:110m | public domain |
| Deflator | US Bureau of Economic Analysis, via FRED | public |
