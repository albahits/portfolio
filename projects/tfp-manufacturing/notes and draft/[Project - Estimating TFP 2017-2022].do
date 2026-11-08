// TFP Manufacturing Project


use "D:\Nagoya University\GSID\Master Degree\101 Research\[INDEF] Green Economy\2 - Dataset\Cleaned\[Cleaned] 2017-2022 - V2.dta", clear

cd "D:\Project\Portfolio Website\projects\tfp-manufac\figures_tables"

**# Set-Up
xtset firm_id year 
xtbalance, range (2017 2022)

**# Descriptive Statistics
drop if prodlab <1
drop if log_capital < 1
sum log_output log_labor log_prodlab log_nonprodlab log_capital log_material


// All Industries ==== 
**# Estimate TFP#1 - LP Method 
prodest log_output, free(log_prodlab log_nonprodlab) proxy(log_material) state(log_capital) id(firm_id) t(year)method(lp) fsresiduals(fsr)
predict tfp_lp, omega
sum tfp_lp
la var tfp_lp "TFP LP with Omega"
gen tfp_gr = D.tfp_lp
la var tfp_gr "TFP Growth"

**# Estimate TFP#2 - OLS Residuals
reghdfe log_output log_prodlab log_nonprodlab log_capital log_material, absorb(year disic2) resid vce(robust)
predict ols_res, residuals
gen tfp_ols = ols_res

**# TFP Level (Mean) across the years -- Done
{
preserve

* 1. Collapse to annual Mean and Standard Error components
collapse (mean) mean_tfp = tfp_lp (sd) sd_tfp = tfp_lp (count) n = tfp_lp, by(year)
drop if missing(year)

* 2. Calculate 95% Confidence Intervals for the Mean
gen ci_high = mean_tfp + 1.96 * (sd_tfp / sqrt(n))
gen ci_low  = mean_tfp - 1.96 * (sd_tfp / sqrt(n))

* 3. Generate the Publication-Ready Plot
graph set window fontface "Times New Roman"
set scheme s1mono

twoway ///
    /// 95% CI Error Bars (Plotted first so caps sit behind the marker)
    (rcap ci_low ci_high year, ///
        lcolor(gs7) lwidth(medthick) msize(medium)) ///
    /// Mean Trend Line
    (connected mean_tfp year, ///
        lcolor(black) mcolor(black) msymbol(O) lpattern(solid) lwidth(thick) msize(medium)), ///
    /// Axes Titles and Formatting
    ytitle("Log TFP Level (Levinsohn-Petrin)", size(medium) margin(right)) ///
    xtitle("Year", size(medium) margin(top)) ///
    /// Tightly bound the Y-axis to maximize visibility of the micro-movements
    ylabel(4.65(0.05)4.80, angle(0) nogrid labsize(small) format(%9.2f)) ///
    xlabel(2017(1)2022, nogrid labsize(small)) ///
    /// Legend Box Styling
    legend(order(2 "Mean TFP" 1 "95% Confidence Interval") ///
           rows(1) position(6) region(lstyle(none)) size(small)) ///
    /// Canvas Dimensions & True White Background
    graphregion(color(white) fcolor(white) lcolor(white) margin(medium)) ///
    plotregion(color(white) fcolor(white) lcolor(black) lwidth(medium)) ///
    ysize(5) xsize(7) ///

graph export "Fig - TFP Level 2017-2022.png", replace width(3600)
restore
}

**# Element Elasticities -- Done
sum tfp_lp

**# TFP Dispersion -- Done
{
preserve

* 1. Collapse to annual 90th and 10th percentiles
collapse (p90) p90_tfp = tfp_lp (p10) p10_tfp = tfp_lp, by(year)
drop if missing(year)

* CRITICAL FIX: The dataset must be sorted sequentially for 'rarea' to draw properly
sort year 

* 2. Dynamically extract the coordinates for the 2020 annotation
quietly summarize p90_tfp if year == 2020
local y90 = r(mean)

quietly summarize p10_tfp if year == 2020
local y10 = r(mean)

* Calculate the gap value and the vertical midpoint for the label
local gap_val = `y90' - `y10'
local ymid = (`y90' + `y10') / 2

* Format the gap to 2 decimal places as a string (e.g., "0.64")
local gap_str : display %9.2f `gap_val'
local gap_str = trim("`gap_str'")

* 3. Generate the Publication-Ready Plot
graph set window fontface "Times New Roman"
set scheme s1mono

twoway ///
    /// A. Shaded area representing the productivity gap (Darkened to gs12 for visibility)
    (rarea p90_tfp p10_tfp year, ///
        fcolor(gs12) lcolor(none)) ///
    /// B. The 90th Percentile (Frontier)
    (connected p90_tfp year, ///
        lcolor(black) mcolor(black) msymbol(S) lpattern(solid) lwidth(thick) msize(medium)) ///
    /// C. The 10th Percentile (Laggards)
    (connected p10_tfp year, ///
        lcolor(gs7) mcolor(gs7) msymbol(D) lpattern(dash) lwidth(thick) msize(medium)) ///
    /// D. Vertical dashed connector line specifically for 2020
    (scatteri `y90' 2020 `y10' 2020, ///
        connect(line) msymbol(none) lcolor(black) lpattern(shortdash) lwidth(medthick)), ///
    /// E. Text label inside a white box positioned at the 2020 midpoint
    text(`ymid' 2020 "`gap_str' (Peak)", box fcolor(white) lcolor(black) margin(small) size(small)) ///
    /// Axes Titles and Formatting
    ytitle("Log TFP Level (Levinsohn-Petrin)", size(medium) margin(right)) ///
    xtitle("Year", size(medium) margin(top)) ///
    ylabel(, angle(0) nogrid labsize(small) format(%9.2f)) ///
    xlabel(2017(1)2022, nogrid labsize(small)) ///
    /// Legend Box Styling
    legend(order(2 "90th Percentile (Frontier)" 3 "10th Percentile (Laggards)" 1 "90-10 Gap") ///
           rows(1) position(6) region(lstyle(none)) size(small) colgap(4)) ///
    /// Canvas Dimensions & Enforced White Background
    graphregion(color(white) fcolor(white) lcolor(white) margin(medium)) ///
    plotregion(color(white) fcolor(white) lcolor(black) lwidth(medium)) ///
    ysize(5) xsize(7) ///
    /// Academic Footnote
    note("Notes: The shaded area highlights the productivity gap between frontier and laggard firms." ///
         "The vertical dashed line explicitly denotes the peak dispersion (90th minus 10th percentile) in 2020.", ///
         size(vsmall) margin(top))
		 
graph export "Fig - Dispersion.png", replace width(4000)

restore
}

**# TFP LP vs OLS (Resid)

**# Heterogeneity - Estimate RTS per Industry -- Done
{ 
preserve

* 1. Identify all industries
levelsof disic2, local(sectors)

* 2. Prepare results file
tempname results
tempfile sector_results

postfile `results' ///
    int disic2 ///
    double beta_prodlab beta_nonprodlab ///
    beta_capital beta_material ///
    rts rts_se p_crs ///
    long N ///
    using `sector_results', replace

* 3. Estimate production function by industry
foreach s of local sectors {

    capture drop fsr

    capture quietly prodest log_output ///
        if disic2 == `s', ///
        free(log_prodlab log_nonprodlab) ///
        proxy(log_material) ///
        state(log_capital) ///
        id(firm_id) ///
        t(year) ///
        method(lp) ///
        fsresiduals(fsr)

    if !_rc {

        * Extract coefficients
        local bl1 = _b[log_prodlab]
        local bl2 = _b[log_nonprodlab]
        local bk  = _b[log_capital]
        local bm  = _b[log_material]

        local n = e(N)

        * Calculate RTS and standard error
        quietly lincom ///
            log_prodlab + log_nonprodlab + ///
            log_capital + log_material

        local rts = r(estimate)
        local se  = r(se)

        * Test constant returns to scale
        quietly test ///
            log_prodlab + log_nonprodlab + ///
            log_capital + log_material = 1

        local p = r(p)

        * Store results
        post `results' ///
            (`s') (`bl1') (`bl2') (`bk') (`bm') ///
            (`rts') (`se') (`p') (`n')
    }
}

* 4. Close results file
postclose `results'

* 5. Load results
use `sector_results', clear

* 6. Calculate 95% confidence intervals
gen ci_low  = rts - 1.96*rts_se
gen ci_high = rts + 1.96*rts_se

* 7. Label industries
label define sectorlbl ///
    10 "Food Products" ///
    11 "Beverages" ///
    12 "Tobacco" ///
    13 "Textiles" ///
    14 "Apparel" ///
    15 "Leather" ///
    16 "Wood" ///
    17 "Paper" ///
    18 "Printing and recording media" ///
    19 "Coal and petroleum" ///
    20 "Chemicals" ///
    21 "Pharmaceuticals" ///
    22 "Rubber and plastics" ///
    23 "Non-metallic minerals" ///
    24 "Basic metals" ///
    25 "Fabricated metal products" ///
    26 "Computers and electronics" ///
    27 "Electrical equipment" ///
    28 "Machinery and equipment" ///
    29 "Motor vehicles" ///
    30 "Other transport equipment" ///
    31 "Furniture" ///
    32 "Other manufacturing" ///
    33 "Machinery repair"

label values disic2 sectorlbl

* 8. Visualize sectoral RTS
graph set window fontface "Times New Roman"
set scheme s1mono

twoway ///
    (rcap ci_low ci_high disic2, ///
        horizontal lcolor(gs6) lwidth(medthin) msize(small)) ///
    (scatter disic2 rts, ///
        mcolor(black) msymbol(O) msize(medsmall)), ///
    xline(1, lcolor(gs8) lpattern(dash) lwidth(thin)) ///
    /// ADJUSTMENT 1: Restrict X-axis to zoom in on the actual point estimates
    xscale(range(0.75 1.25)) ///
    xlabel(0.75(0.1)1.25, labsize(small) format(%4.2f) grid gstyle(smalldash) glcolor(gs14)) ///
    ///
    yscale(reverse range(9.5 33.5)) ///
    ylabel(10(1)33, valuelabel angle(0) labsize(vsmall) nogrid) ///
    xtitle("Estimated Returns to Scale ({&gamma})", size(small) margin(top)) ///
    ytitle("") ///
    legend(off) ///
    /// ADJUSTMENT 2: Force a wide left margin (l=18) so long industry names fit
    graphregion(color(white) fcolor(white) margin(l=18 r=5 t=5 b=5)) ///
    plotregion(lcolor(black) fcolor(white) lwidth(medium)) ///
    /// ADJUSTMENT 3: Make the canvas wider/more horizontal (e.g., 7 tall by 9 wide)
    ysize(7) xsize(9) ///
    note("Notes: Solid circles denote point estimates from sector-specific Levinsohn-Petrin production function estimations;" ///
         "whiskers display 95% confidence intervals. The vertical dashed line indicates constant returns to scale ({&gamma} = 1).", ///
         size(vsmall) margin(top))

graph export "Fig - Sectoral RTS.png", replace width(3000)

restore

}

**# Heterogeneity - Estimate Elasticities for Labor Intensive vs Capital Intensive Sector'
{
* ==============================================================================
* ELASTICITY COMPARISON: TEXTILES (LABOR) VS. CHEMICALS (CAPITAL)
* ==============================================================================
preserve

* 1. Prepare results file
tempname results
tempfile sector_results

postfile `results' ///
    int disic2 ///
    str25 sector_name ///
    double beta_prodlab beta_nonprodlab beta_capital beta_material ///
    using `sector_results', replace

* 2. Loop specifically over Textiles (13) and Chemicals (20)
foreach s in 14 19 {

    local sname = ""
    if `s' == 14 local sname = "Textile Industry(Labor-Int)"
    if `s' == 19 local sname = "Petroleum Industry(Capital-Int)"

    capture drop fsr

    capture quietly prodest log_output ///
        if disic2 == `s', ///
        free(log_prodlab log_nonprodlab) ///
        proxy(log_material) ///
        state(log_capital) ///
        id(firm_id) ///
        t(year) ///
        method(lp) ///
        fsresiduals(fsr)

    if !_rc {
        * Store coefficients
        local bl1 = _b[log_prodlab]
        local bl2 = _b[log_nonprodlab]
        local bk  = _b[log_capital]
        local bm  = _b[log_material]

        post `results' (`s') ("`sname'") (`bl1') (`bl2') (`bk') (`bm')
    }
}

postclose `results'

* 3. Load results back into memory
use `sector_results', clear

* 4. Reshape long for grouped bar chart formatting
rename beta_prodlab    b_1_prodlab
rename beta_nonprodlab b_2_nonprodlab
rename beta_capital    b_3_capital
rename beta_material   b_4_material

reshape long b_, i(disic2 sector_name) j(input) string
rename b_ elasticity

gen input_id = .
replace input_id = 1 if input == "1_prodlab"      // <-- Removed leading underscore
replace input_id = 2 if input == "2_nonprodlab"   // <-- Removed leading underscore
replace input_id = 3 if input == "3_capital"      // <-- Removed leading underscore
replace input_id = 4 if input == "4_material"     // <-- Removed leading underscore

label define inputlbl 1 "Production Labor" 2 "Non-Production Labor" 3 "Capital Stock" 4 "Intermediate Materials"
label values input_id inputlbl

* 5. Generate the Publication-Ready Grouped Bar Chart
graph set window fontface "Times New Roman"
set scheme s1mono

graph hbar (mean) elasticity, ///
    over(sector_name, label(labsize(small))) ///
    over(input_id, label(labsize(medium))) ///
    asyvars ///
    bar(1, fcolor(gs13) lcolor(black) lwidth(thin)) /// Textiles (Light Gray)
    bar(2, fcolor(black) lcolor(black) lwidth(thin)) /// Chemicals (Solid Black)
    blabel(bar, format(%9.3f) size(vsmall)) ///
    ytitle("Output Elasticity ({&beta})", size(medium) margin(top)) ///
    ylabel(0(0.2)0.8, nogrid labsize(small) format(%3.1f)) ///
    legend(order(1 "Textile Industry (ISIC 14)" 2 "Petroleum Industry (ISIC 24)") ///
           rows(1) position(6) region(lstyle(none)) size(small)) ///
    graphregion(color(white) fcolor(white) margin(medium)) ///
    plotregion(lcolor(black) fcolor(white) lwidth(medium)) ///
    ysize(5) xsize(7) ///
    note("Notes: Bars represent Levinsohn-Petrin input elasticities estimated via sector-specific regressions.", size(vsmall) margin(top))


graph export "Fig - Elasticities for Labor vs Capital Intensive.png", replace width(3600)
restore

}

**# Heterogeneity - TFP for Foreign Company
{
	tab foreign year
	sum tfp_lp if foreign == 1
}
