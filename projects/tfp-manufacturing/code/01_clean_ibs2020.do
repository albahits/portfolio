* ============================================================
* 01_clean_ibs2020.do
* Productivity in Indonesian Manufacturing (IBS 2017-2022)
* Step 1: Clean and deflate one survey year (2020 shown).
*         Repeat for 2017-2022, adjusting the year-specific
*         variable suffixes (e.g. *20 -> *19) and deflators.
* Software: Stata 18
* Input : ibs2020.dta  (BPS Industri Besar dan Sedang; not shared)
* Output: ibs 2020.dta (cleaned)
* ============================================================

use "ibs2020.dta", clear

**# Firm ID
gen double firm_id = real(Kipb)
format firm_id %12.0f
la var firm_id "Firm ID"

**# Year
rename year annual_operation
gen year = 2020
la var year "Year of the Observation"

**# Sector (ISIC)
gen disic5 = disic520
destring disic5, replace
la var disic5 "ISIC Code 5 Digit"

gen disic2 = substr(disic520, 1, 2)
destring disic2, replace force
la var disic2 "ISIC 2 Digit"

* ============================================================
* 1. Firm Output
* ============================================================
**# Firm Income & Output Deflation
local RUN_INCOME_BLOCK 1
if `RUN_INCOME_BLOCK' == 1 {

    * 0. Destring raw inputs (yprvcu20 = nominal income)
    destring yprvcu20, replace

    * 1. Base nominal output (preserves raw survey data)
    gen output = yprvcu20

    * 2. Drop non-producing firms and firms missing a sector code
    drop if output == 0 | missing(output)
    drop if missing(disic2)

    * 3. Sector-specific producer price deflator (IHP, 2010 = 100, BPS)
    gen ihp2020 = .
    replace ihp2020 = 150.43 if disic2 == 10
    replace ihp2020 = 163.93 if inlist(disic2, 11, 12)
    replace ihp2020 = 153.81 if disic2 == 13
    replace ihp2020 = 165.41 if inlist(disic2, 14, 15)
    replace ihp2020 = 164.88 if disic2 == 16
    replace ihp2020 = 145.55 if inlist(disic2, 17, 18)
    replace ihp2020 = 128.78 if disic2 == 19
    replace ihp2020 = 138.43 if inlist(disic2, 20, 21)
    replace ihp2020 = 123.61 if disic2 == 22
    replace ihp2020 = 150.01 if disic2 == 23
    replace ihp2020 = 118.50 if disic2 == 24
    replace ihp2020 = 130.14 if disic2 == 25
    replace ihp2020 = 152.09 if inlist(disic2, 26, 27, 28)
    replace ihp2020 = 141.04 if inlist(disic2, 29, 30)
    replace ihp2020 = 162.53 if inlist(disic2, 31, 32, 33)

    * 4. Deflate: (Nominal / Deflator) * 100
    gen real_output = (output / ihp2020) * 100

    * 5. Log of real output
    gen log_output = ln(real_output)

    la var output      "Firm Total Output Nominal (Rp)"
    la var ihp2020     "IHP 2020 Deflator (Base 2010=100, by disic2)"
    la var real_output "Firm Total Output Real (Deflated by Sector IHP)"
    la var log_output  "Firm Total Output Real (in Log)"
}

* ============================================================
* 2. Labor
* ============================================================
**# Labor (Production vs Non-Production)
local RUN_LABOR_BLOCK 1
if `RUN_LABOR_BLOCK' == 1 {

    * 1. Destring raw inputs (l = Indonesian, f = foreign workers)
    destring lprnol20 lprnof20 lnpnol20 lnpnof20, replace force

    * 2. Headcounts
    gen prodlab     = lprnol20 + lprnof20
    gen non_prodlab = lnpnol20 + lnpnof20
    gen labor       = prodlab + non_prodlab

    * Keep firms with 20+ workers (IBS definition of medium/large)
    drop if labor == 0 | missing(labor)
    drop if labor < 20

    * 3. Logs (ln(0) -> missing for firms with no non-production staff)
    gen log_labor      = ln(labor)
    gen log_prodlab    = ln(prodlab)
    gen log_nonprodlab = ln(non_prodlab)

    la var labor          "Total Labor"
    la var log_labor      "Total Labor (in Log)"
    la var prodlab        "Labor: Production Workers"
    la var log_prodlab    "Labor: Production Workers (in Log)"
    la var non_prodlab    "Labor: Non-Production/Other Workers"
    la var log_nonprodlab "Labor: Non-Production/Other Workers (in Log)"

    * 4. Firm size
    gen size = .
    replace size = 0 if labor >= 20 & labor <= 99
    replace size = 1 if labor >= 100
    la def lbl_size 0 "Medium Firm" 1 "Large Firm"
    la val size lbl_size
    la var size "Firm Size (Categorical)"

    * 5. Wage bill
    destring zpdvcu20 zndvcu20 zptvcu20 zntvcu20, replace force
    replace zpdvcu20 = 0 if missing(zpdvcu20)
    replace zndvcu20 = 0 if missing(zndvcu20)

    gen labor_cost      = zpdvcu20 + zndvcu20
    gen log_labor_cost  = ln(labor_cost + 1)
    gen prod_cost       = zptvcu20
    gen log_prodcost    = ln(prod_cost)
    gen nonprod_cost    = zntvcu20
    gen log_nonprodcost = ln(nonprod_cost)

    la var labor_cost      "Total Labor Cost Nominal (Rp 000)"
    la var log_labor_cost  "Total Labor Cost Nominal (in Log)"
    la var prod_cost       "Labor Cost, Production Workers (Rp 000)"
    la var nonprod_cost    "Labor Cost, Non-Production Workers (Rp 000)"
    la var log_prodcost    "Labor Cost, Production Workers (in Log)"
    la var log_nonprodcost "Labor Cost, Non-Production Workers (in Log)"
}

* ============================================================
* 3. Capital
* ============================================================
**# Capital
local RUN_CAPITAL_BLOCK 1
if `RUN_CAPITAL_BLOCK' == 1 {

    // Flow: (1) impute missing start-of-year capital with end-of-year value (v1115)
    //       (2) impute firms that lease capital from rent paid (ibrvcu20 / 0.10)
    //       (3) drop if still zero  (4) deflate with IHPB (general)  (5) log

    destring ctfpcu20 v1115 ibrvcu20, replace force

    gen capital = ctfpcu20
    replace capital = v1115          if capital == 0 & v1115 > 0    & !missing(v1115)
    replace capital = ibrvcu20 / 0.10 if capital == 0 & ibrvcu20 > 0 & !missing(ibrvcu20)

    drop if capital == 0 | missing(capital)

    gen real_capital = (capital / 103.55) * 100
    gen log_capital  = ln(real_capital)

    la var capital      "Firm Capital (Rp)"
    la var real_capital "Firm Capital (Deflated with IHPB Umum)"
    la var log_capital  "Firm Capital (in Log)"
}

* ============================================================
* 4. Raw Materials and Energy
* ============================================================
**# Raw Materials & Input
local RUN_INPUT_BLOCK 1
if `RUN_INPUT_BLOCK' == 1 {

    destring rtlvcu20 eplvcu20, replace force

    gen raw_material = rtlvcu20
    drop if raw_material == 0 | missing(raw_material)

    * Deflate with wholesale price index (IHPB), 2020 value = 104.30
    gen real_materials = (raw_material / 104.30) * 100
    gen log_material   = ln(real_materials)

    la var raw_material   "Raw Materials (Rp)"
    la var real_materials "Raw Materials (Deflated with IHPB)"
    la var log_material   "Raw Materials (in Log)"

    gen electricity     = eplvcu20
    gen log_electricity = ln(electricity)
    la var electricity     "Electricity Cost (Rp)"
    la var log_electricity "Electricity Cost (in Log)"
}

save "ibs 2020.dta", replace
