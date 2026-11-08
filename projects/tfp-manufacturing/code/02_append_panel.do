* ============================================================
* 02_append_panel.do
* Step 2: Append the cleaned annual files and declare the panel.
* Input : ibs 2017.dta ... ibs 2022.dta (outputs of step 1)
* Output: appended 2017-2022.dta
* ============================================================

clear all
set more off

use "ibs 2017.dta", clear
foreach yr of numlist 2018/2022 {
    append using "ibs `yr'.dta"
}

sort firm_id year
label variable firm_id "Firm Unique Identifier"
label variable year    "Year of Observation"

xtset firm_id year
xtdescribe

save "appended 2017-2022.dta", replace
