* ============================================================
* 03_tfp_and_figures.do
* Step 3: Descriptives (Table 1), Levinsohn-Petrin TFP (Table 2),
*         and Figures 1-4.
* Requires: prodest (ssc install prodest)
* Input   : appended 2017-2022.dta
* ============================================================

use "appended 2017-2022.dta", clear
xtset firm_id year

graph set window fontface "Times New Roman"
set scheme s1mono

**# Table 1: Descriptive statistics
sum log_output log_labor log_prodlab log_nonprodlab log_capital log_material

**# Table 2: Levinsohn-Petrin production function
prodest log_output, free(log_prodlab log_nonprodlab) proxy(log_material) ///
    state(log_capital) id(firm_id) t(year) method(lp) fsresiduals(fsr)

* Returns to scale and Wald test of constant returns
lincom log_prodlab + log_nonprodlab + log_capital + log_material
test   log_prodlab + log_nonprodlab + log_capital + log_material = 1

predict tfp_lp, omega
sum tfp_lp

**# Figure 1: Mean TFP across years
{
preserve
collapse (mean) mean_tfp = tfp_lp (sd) sd_tfp = tfp_lp (count) n = tfp_lp, by(year)
drop if missing(year)
gen ci_high = mean_tfp + 1.96 * (sd_tfp / sqrt(n))
gen ci_low  = mean_tfp - 1.96 * (sd_tfp / sqrt(n))

twoway ///
    (rcap ci_low ci_high year, lcolor(gs7) lwidth(medthick) msize(medium)) ///
    (connected mean_tfp year, lcolor(black) mcolor(black) msymbol(O) ///
        lpattern(solid) lwidth(thick) msize(medium)), ///
    ytitle("Log TFP Level (Levinsohn-Petrin)", size(medium) margin(right)) ///
    xtitle("Year", size(medium) margin(top)) ///
    ylabel(4.65(0.05)4.80, angle(0) nogrid labsize(small) format(%9.2f)) ///
    xlabel(2017(1)2022, nogrid labsize(small)) ///
    legend(order(2 "Mean TFP" 1 "95% Confidence Interval") ///
        rows(1) position(6) region(lstyle(none)) size(small)) ///
    graphregion(color(white) fcolor(white) lcolor(white) margin(medium)) ///
    plotregion(color(white) fcolor(white) lcolor(black) lwidth(medium)) ///
    ysize(5) xsize(7)
graph export "fig1-tfp-level.png", replace width(3600)
restore
}

**# Figure 2: Frontier vs laggard firms (p90 vs p10)
{
preserve
collapse (p90) p90_tfp = tfp_lp (p10) p10_tfp = tfp_lp, by(year)
drop if missing(year)
sort year

quietly summarize p90_tfp if year == 2020
local y90 = r(mean)
quietly summarize p10_tfp if year == 2020
local y10 = r(mean)
local gap_val = `y90' - `y10'
local ymid    = (`y90' + `y10') / 2
local gap_str : display %9.2f `gap_val'
local gap_str = trim("`gap_str'")

twoway ///
    (rarea p90_tfp p10_tfp year, fcolor(gs12) lcolor(none)) ///
    (connected p90_tfp year, lcolor(black) mcolor(black) msymbol(S) ///
        lpattern(solid) lwidth(thick) msize(medium)) ///
    (connected p10_tfp year, lcolor(gs7) mcolor(gs7) msymbol(D) ///
        lpattern(dash) lwidth(thick) msize(medium)) ///
    (scatteri `y90' 2020 `y10' 2020, connect(line) msymbol(none) ///
        lcolor(black) lpattern(shortdash) lwidth(medthick)), ///
    text(`ymid' 2020 "`gap_str' (Peak)", box fcolor(white) lcolor(black) ///
        margin(small) size(small)) ///
    ytitle("Log TFP Level (Levinsohn-Petrin)", size(medium) margin(right)) ///
    xtitle("Year", size(medium) margin(top)) ///
    ylabel(, angle(0) nogrid labsize(small) format(%9.2f)) ///
    xlabel(2017(1)2022, nogrid labsize(small)) ///
    legend(order(2 "90th Percentile (Frontier)" 3 "10th Percentile (Laggards)" 1 "90-10 Gap") ///
        rows(1) position(6) region(lstyle(none)) size(small) colgap(4)) ///
    graphregion(color(white) fcolor(white) lcolor(white) margin(medium)) ///
    plotregion(color(white) fcolor(white) lcolor(black) lwidth(medium)) ///
    ysize(5) xsize(7)
graph export "fig2-dispersion.png", replace width(4000)
restore
}

**# Figure 3: Returns to scale by 2-digit sector
{
preserve
levelsof disic2, local(sectors)

tempname results
tempfile sector_results
postfile `results' int disic2 ///
    double beta_prodlab beta_nonprodlab beta_capital beta_material ///
    rts rts_se p_crs long N using `sector_results', replace

foreach s of local sectors {
    capture drop fsr
    capture quietly prodest log_output if disic2 == `s', ///
        free(log_prodlab log_nonprodlab) proxy(log_material) ///
        state(log_capital) id(firm_id) t(year) method(lp) fsresiduals(fsr)

    if !_rc {
        local bl1 = _b[log_prodlab]
        local bl2 = _b[log_nonprodlab]
        local bk  = _b[log_capital]
        local bm  = _b[log_material]
        local n   = e(N)

        quietly lincom log_prodlab + log_nonprodlab + log_capital + log_material
        local rts = r(estimate)
        local se  = r(se)

        quietly test log_prodlab + log_nonprodlab + log_capital + log_material = 1
        local p = r(p)

        post `results' (`s') (`bl1') (`bl2') (`bk') (`bm') ///
            (`rts') (`se') (`p') (`n')
    }
}
postclose `results'

use `sector_results', clear
gen ci_low  = rts - 1.96*rts_se
gen ci_high = rts + 1.96*rts_se

label define sectorlbl ///
    10 "Food Products" 11 "Beverages" 12 "Tobacco" 13 "Textiles" ///
    14 "Apparel" 15 "Leather" 16 "Wood" 17 "Paper" ///
    18 "Printing and recording media" 19 "Coal and petroleum" ///
    20 "Chemicals" 21 "Pharmaceuticals" 22 "Rubber and plastics" ///
    23 "Non-metallic minerals" 24 "Basic metals" ///
    25 "Fabricated metal products" 26 "Computers and electronics" ///
    27 "Electrical equipment" 28 "Machinery and equipment" ///
    29 "Motor vehicles" 30 "Other transport equipment" ///
    31 "Furniture" 32 "Other manufacturing" 33 "Machinery repair"
label values disic2 sectorlbl

twoway ///
    (rcap ci_low ci_high disic2, horizontal lcolor(gs6) lwidth(medthin) msize(small)) ///
    (scatter disic2 rts, mcolor(black) msymbol(O) msize(medsmall)), ///
    xline(1, lcolor(gs8) lpattern(dash) lwidth(thin)) ///
    xscale(range(0.75 1.25)) ///
    xlabel(0.75(0.1)1.25, labsize(small) format(%4.2f) grid gstyle(smalldash) glcolor(gs14)) ///
    yscale(reverse range(9.5 33.5)) ///
    ylabel(10(1)33, valuelabel angle(0) labsize(vsmall) nogrid) ///
    xtitle("Estimated Returns to Scale ({&gamma})", size(small) margin(top)) ///
    ytitle("") legend(off) ///
    graphregion(color(white) fcolor(white) margin(l=18 r=5 t=5 b=5)) ///
    plotregion(lcolor(black) fcolor(white) lwidth(medium)) ///
    ysize(7) xsize(9)
graph export "fig3-sectoral-rts.png", replace width(3000)
restore
}

**# Figure 4: Input elasticities, Textiles (ISIC 13) vs Motor Vehicles (ISIC 29)
{
preserve
tempname results
tempfile sector_results
postfile `results' int disic2 str25 sector_name ///
    double beta_prodlab beta_nonprodlab beta_capital beta_material ///
    using `sector_results', replace

foreach s in 13 29 {
    local sname = ""
    if `s' == 13 local sname = "Textile Industry"
    if `s' == 29 local sname = "Motor Vehicles Industry"

    capture drop fsr
    capture quietly prodest log_output if disic2 == `s', ///
        free(log_prodlab log_nonprodlab) proxy(log_material) ///
        state(log_capital) id(firm_id) t(year) method(lp) fsresiduals(fsr)

    if !_rc {
        post `results' (`s') ("`sname'") (_b[log_prodlab]) ///
            (_b[log_nonprodlab]) (_b[log_capital]) (_b[log_material])
    }
}
postclose `results'

use `sector_results', clear
rename beta_prodlab    b_1_prodlab
rename beta_nonprodlab b_2_nonprodlab
rename beta_capital    b_3_capital
rename beta_material   b_4_material
reshape long b_, i(disic2 sector_name) j(input) string
rename b_ elasticity

gen input_id = .
replace input_id = 1 if input == "1_prodlab"
replace input_id = 2 if input == "2_nonprodlab"
replace input_id = 3 if input == "3_capital"
replace input_id = 4 if input == "4_material"
label define inputlbl 1 "Production Labor" 2 "Non-Production Labor" ///
    3 "Capital Stock" 4 "Intermediate Materials"
label values input_id inputlbl

graph hbar (mean) elasticity, ///
    over(sector_name, label(labsize(small))) ///
    over(input_id, label(labsize(medium))) ///
    asyvars ///
    bar(1, fcolor(gs13) lcolor(black) lwidth(thin)) ///
    bar(2, fcolor(black) lcolor(black) lwidth(thin)) ///
    blabel(bar, format(%9.3f) size(vsmall)) ///
    ytitle("Output Elasticity ({&beta})", size(medium) margin(top)) ///
    ylabel(0(0.2)0.8, nogrid labsize(small) format(%3.1f)) ///
    legend(order(1 "Textile Industry (ISIC 13)" 2 "Motor Vehicles Industry (ISIC 29)") ///
        rows(1) position(6) region(lstyle(none)) size(small)) ///
    graphregion(color(white) fcolor(white) margin(medium)) ///
    plotregion(lcolor(black) fcolor(white) lwidth(medium)) ///
    ysize(5) xsize(7)
graph export "fig4-elasticities-two-sectors.png", replace width(3600)
restore
}
