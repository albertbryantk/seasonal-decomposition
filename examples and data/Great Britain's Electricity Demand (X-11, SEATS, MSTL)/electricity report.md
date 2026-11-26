# Winter demand and daily electricity peaks

How much higher is demand in winter, has that gap changed, and how do weekday peaks compare with weekends?

## The dataset

The National Energy System Operator (NESO) reports Great Britain's National Demand, abbreviated `ND`, in megawatts (MW) for each half-hour settlement interval. A gigawatt (GW) is 1,000 MW. This series measures metered generation needed to meet National Demand under NESO's definition. It excludes station load, pumped-storage pumping, and interconnector exports. [Dataset and column definitions](https://www.neso.energy/data-portal/historic-demand-data/historic_demand_data_2026).

We combined the official 2015–2025 annual files with the uploaded 2026 file. The upload has 14,784 actual half-hours from 1 January to 4 November. R checked settlement dates and periods against the UK time zone, including the 46-interval spring day and the 50-interval autumn day. The input contains no gaps, duplicates or invalid demand values. All 2026 readings went into the half-hour fit. Monthly fits use 142 complete months from January 2015 through October 2026. Each monthly value is the mean of its half-hour power readings. The four November days have no monthly mean in the fit. [NESO historical archive](https://www.neso.energy/data-portal/historic-demand-data).

**9.3 GW**Observed winter–summer gap in 2026 **34.5%–36.9%**Estimated winter increase from the seasonal component in 2026 **7:00 p.m.**Weekday peak of the pooled 2026 fitted profile

## How the three methods work

**X-11** uses repeated moving averages to estimate the underlying level, recurrence within a year, and irregular changes. The filters can let the seasonal shape change as newer annual cycles enter the series.

**SEATS**, or **Signal Extraction in ARIMA Time Series**, extracts the seasonal, trend and irregular components implied by a fitted seasonal autoregressive integrated moving average (ARIMA) model. This gives a model-based comparison with X-11. Both methods use the same 12-month period, log transformation, and calendar covariate measuring the share of weekdays in each month. The X-13 software selected the same seasonal ARIMA model, order (1 0 0)(0 1 1), in both fits. The seasonal moving-average coefficient was close to 1. SEATS was run with alternative-model substitution disabled. [U.S. Census Bureau seasonal adjustment guide](https://www.census.gov/data/software/x13as/seasonal-adjustment-questions-answers.html).

**MSTL**, or **Multiple Seasonal-Trend Decomposition Using LOESS**, fits repeated local smooths to estimate several cycles on the same timeline. LOESS is a technique for smoothing nearby data. We used periods of 48 and 336 elapsed half-hours, or one day and one week. We fitted the original MW values with robustness enabled to reduce the influence of unusual readings. The fit uses a regular Coordinated Universal Time (UTC) grid. We converted its times back to the UK clock for the peak comparisons. [R MSTL documentation](https://pkg.robjhyndman.com/forecast/reference/mstl.html).

## How much higher is winter demand?

Winter is December–February and is labelled by the year it ends. Summer is June–August in that year. Observed averages and seasonal factors are weighted by the number of readings in each month. To isolate the recurring winter–summer gap, we divide the average winter seasonal factor by the average summer factor, subtract 1, and convert to percent. In GW, we multiply the difference in the two factors by one shared baseline, the fitted trend averaged across those six months.

![Chart of observed monthly power demand and the X-11 and SEATS trend estimates.](monthly-demand.png)

Figure 1. Monthly electricity demand and trend

**Axes.** The horizontal axis shows calendar months from January 2015 to October 2026. Pale vertical guides mark January. The vertical axis shows average power demand in gigawatts (GW), with pale guides at the tick values.

**Lines.** Solid gray is observed monthly demand. Solid blue is the underlying trend estimated by the X-11 moving-average method. Dashed orange is the underlying trend estimated by SEATS, short for Signal Extraction in ARIMA Time Series. ARIMA means autoregressive integrated moving average.

**What it shows.** The observed line rises in winter and falls in summer around a generally declining trend. The annual average of the X-11 trend fell from 32.5 GW in 2015 to 26.0 GW in 2025. Both trends tell a similar broad story.

![Chart comparing the observed and model-estimated winter increase by year, in percent and gigawatts.](winter-gap.png)

Figure 2. Winter–summer difference by year

**Axes.** Both panels use the year winter ends on the horizontal axis, from 2016 to 2026. The left vertical axis shows how much higher winter demand was relative to summer, in percent. The right vertical axis shows the winter increase in gigawatts (GW). Pale lines mark axis ticks.

**Lines and markers.** Dotted gray with open circles is the observed difference. Solid blue with filled circles shows the seasonal difference estimated with the X-11 moving-average method. Dashed orange with triangles is the estimate from SEATS, or Signal Extraction in ARIMA Time Series. ARIMA means autoregressive integrated moving average. The fitted lines use seasonal factors to hold the underlying power level constant for each winter–summer comparison.

**What it shows.** In the latest comparison, observed winter demand averaged 31.43 GW and summer demand 22.12 GW. The recurring winter increase at a shared power level was 7.80–8.27 GW across the two methods. On the left, the X-11 estimate rises gradually and the SEATS estimate stays near 34.5%.

| Year winter ends  | Observed GW | Observed % | X-11 GW | X-11 % | SEATS GW | SEATS % |
|-------------------|-------------|------------|---------|--------|----------|---------|
| 2016–2018 average | 8.71        | 32.8%      | 8.70    | 32.6%  | 9.12     | 34.5%   |
| 2024–2026 average | 8.96        | 40.5%      | 8.15    | 36.3%  | 7.80     | 34.5%   |
| 2026              | 9.31        | 42.1%      | 8.27    | 36.9%  | 7.80     | 34.5%   |

Observed and fitted winter increases over summer

The observed percentage gap increased from 32.8% to 40.5% across the two three-year groups. X-11's fitted seasonal gap moved from 32.6% to 36.3%. SEATS moved from 34.5% to 34.5%. The fitted differences in GW also reflect the decline in underlying demand, because the conversion from a factor to GW uses that period's trend level.

## When demand peaks during the day

![Open the full-size four-panel chart of the observed demand, fit, daily component, weekly component, and remainder for one July week.](half-hour-components.png)

Figure 3. One week of the half-hour decomposition

**Axes.** The four panels share the UK local timeline from 13 to 19 July 2026. Vertical guides mark local midnight and horizontal guides mark the power ticks. All vertical scales are in gigawatts (GW), with a separate range for each panel. This week illustrates the fit to all 2026 readings.

**Lines and panels.** In the first panel, solid gray is observed demand. Dashed blue is fitted demand from Multiple Seasonal-Trend Decomposition Using LOESS (MSTL), the trend plus the daily and weekly effects. Dotted green is the underlying trend. The second panel's solid blue line is the daily effect over 48 half-hours. The third panel's solid orange line shows the weekly effect over 336 half-hours, including deviations from the daily shape. In the bottom panel solid gray is the remainder, the reading minus its fitted value. The dotted gray zero line in each of the three lower panels marks no contribution or no remaining difference.

**What it shows.** The daily effect repeats the evening rise and overnight fall. The weekly effect dips well below zero on the mornings of Saturday 18 July and Sunday 19 July, lowering fitted demand on those days. The gray gaps from zero in the bottom panel show how much the fitted weekday and weekend patterns leave unexplained.

![Chart of weekday and weekend power profiles for the whole upload, January, and July.](clock-demand.png)

Figure 4. Fitted weekday and weekend profiles

**Axes.** All three panels use UK clock hours from midnight through 11:30 p.m. The vertical axis shows fitted power demand in gigawatts (GW). All panels share the same scale. Pale lines mark each axis's labelled ticks.

**Lines and markers.** Solid blue averages fitted demand at each half-hour for Monday–Friday. Dashed orange averages Saturday–Sunday. A blue circle and an orange triangle show the highest half-hour for each group. Fitted demand is the trend plus the daily and weekly effects. The left panel pools all dates from the upload, the center panel shows January, and the right panel shows July.

**What it shows.** Pooling the full span, the fitted weekday peak is around 7:00 p.m. at 32.1 GW and the fitted weekend peak is around 7:00 p.m. at 29.4 GW. Comparing the daily-plus-weekly components alone, the largest weekday–weekend gap was 6.6 GW at 8:00 a.m.. The profiles shift later in July than in January.

| Span            | Weekdays            | Weekends            |
|-----------------|---------------------|---------------------|
| All fitted days | 7:00 p.m. · 32.1 GW | 7:00 p.m. · 29.4 GW |
| January 2026    | 5:30 p.m. · 42.1 GW | 5:00 p.m. · 39.7 GW |
| July 2026       | 7:30 p.m. · 28.1 GW | 8:00 p.m. · 25.0 GW |

Peak of each fitted average profile, UK local time

## Worked examples from fitted values

### Monthly demand in January 2026

X-11 and SEATS return trend and adjusted demand in megawatts. Their seasonal, calendar and irregular factors are unitless, with 1 as neutral. The pure seasonal factor represents the recurring month-of-year effect. The calendar factor represents the weekday mix. Their product gives the combined factor. Divide the observed value by this product to obtain adjusted demand. The adjusted value is also the fitted trend times the irregular factor.

| Component            | X-11      | SEATS     |
|----------------------|-----------|-----------|
| Observed demand (MW) | 32,887.41 | 32,887.41 |
| Pure seasonal factor | 1.219288  | 1.196328  |
| Calendar factor      | 0.999574  | 0.999574  |
| Combined factor      | 1.218769  | 1.195818  |
| Adjusted demand (MW) | 26,984.12 | 27,502.01 |
| Trend (MW)           | 26,676.65 | 27,072.26 |
| Irregular factor     | 1.011526  | 1.015874  |

January 2026 component values

**X-11.** 32,887.41 ÷ 1.218769 ≈ 26,984.12 MW. Multiplying the trend of 26,676.65 MW by the irregular factor 1.011526 gives the same adjusted value. The seasonal factor of 1.219288 implies 21.9% higher January demand due to the recurring monthly pattern.

**SEATS.** 32,887.41 ÷ 1.195818 ≈ 27,502.01 MW. Multiplying 27,072.26 MW by 1.015874 gives the same adjusted value. The pure seasonal factor implies a 19.6% January increase.

### Half-hour demand at 7:30 p.m. on 15 July 2026

For MSTL, the components add on the original MW scale. The trend is the smoothed underlying level. The daily and weekly terms show the recurring contributions at this half-hour. The remainder is the difference between observed and fitted demand.

| Component       | MW        |
|-----------------|-----------|
| Trend           | 21,625.73 |
| Daily effect    | 5,238.97  |
| Weekly effect   | 1,773.97  |
| Fitted demand   | 28,638.66 |
| Remainder       | 66.34     |
| Observed demand | 28,705.00 |

15 July 2026 at 7:30 p.m. British Summer Time

21,625.73 +5,238.97 +1,773.97 +66.34 ≈ 28,705.00 MW. R used full precision for both worked examples.

## Verification and diagnostics

| Fit   | Readings checked | Observed | Adjusted |
|-------|------------------|----------|----------|
| X-11  | 142              | 1.9e-10  | 1.8e-10  |
| SEATS | 142              | 2.1e-10  | 1.7e-10  |
| MSTL  | 14784            | 1.5e-11  | —        |

Maximum absolute component reconstruction errors in MW

Every position passed the 0.000001 MW tolerance. The monthly checks compare observed demand with adjusted demand times the combined factor and adjusted demand with trend times irregular. The half-hour check adds trend, daily effect, weekly effect and remainder to recover the observation. All components were available for the fitted windows.

Both monthly fits returned a QS seasonal-repetition statistic of 0.00 on adjusted demand, with a reported p-value of 1.00. QS looks for positive repetition at seasonal lags. The paired irregular correlation one year apart was -0.14 in X-11 and -0.13 in SEATS, using 130 pairs each. X-13 flagged residual calendar-frequency peaks. Those warnings limit confidence in small calendar and seasonal differences. [X-13 reference manual](https://www2.census.gov/software/x-13arima-seats/x13as/unix-linux/documentation/docx13ashtml.pdf).

MSTL remainder correlations were 0.15 at 48 half-hours (one day, 14,736 complete pairs) and -0.12 at 336 half-hours (one week, 14,448 complete pairs). The largest absolute half-hour remainder was -12.90 GW at 2026-01-01 09:00 GMT. A positive value means observed demand exceeded the fit. GMT is Greenwich Mean Time and BST is British Summer Time.

## Limitations

- The analysis estimates recurring patterns in the NESO National Demand measure. It does not estimate how much a particular weather event or change in electricity use caused.
- Late monthly trend and seasonal estimates may revise as more complete months arrive. The 2026 comparison uses the December 2025–February 2026 winter. It contains ten months of 2026 in the monthly fit.
- The 48- and 336-half-hour MSTL periods align in elapsed time. UK clock changes shift the local labels by one hour. Fitted profiles pool holidays with their calendar weekday or weekend and describe the January–November 2026 window.

## Conclusion

Observed 2026 winter demand averaged 9.3 GW above summer. X-11 and SEATS put the recurring increase at 7.8–8.3 GW with the underlying power level held fixed within each fit. Whether the seasonal percentage gap widened depends on the method. X-11 estimates an increase of 3.8 percentage points. SEATS estimates almost no change.

Across the full 2026 upload, the fitted weekday and weekend profiles both peak around 7:00 p.m.. The biggest recurring weekday–weekend gap is 6.6 GW at 8:00 a.m.. The July peaks fall later in the evening than the January peaks.

## References and reproducibility

- National Energy System Operator. [Historic Demand Data](https://www.neso.energy/data-portal/historic-demand-data) and [the 2026 dataset](https://www.neso.energy/data-portal/historic-demand-data/historic_demand_data_2026).
- U.S. Census Bureau. [Seasonal Adjustment Questions and Answers](https://www.census.gov/data/software/x13as/seasonal-adjustment-questions-answers.html) and [X-13 manual](https://www2.census.gov/software/x-13arima-seats/x13as/unix-linux/documentation/docx13ashtml.pdf).
- [R seasonal documentation](https://search.r-project.org/CRAN/refmans/seasonal/html/seas.html) and [R forecast MSTL documentation](https://pkg.robjhyndman.com/forecast/reference/mstl.html).

Use a directory with the 2015–2025 archive CSVs named by year, such as `2015.csv`. Run from this report folder with R packages `seasonal`, `x13binary` and `forecast` installed. Keep the plots alongside the HTML when moving the report.

    Rscript analyze.R "path/to/archive" "path/to/demanddataupdate_2026.csv"
    python build-report.py

- [R analysis](analyze.R), [date and data checks](prepare.R), [plot code](plots.R) and [HTML builder](build-report.py).
- [Archive URLs](source-urls.csv), [input fingerprints and counts](downloaded-inputs.csv) and [fit settings, messages and software versions](settings.txt).
- [Monthly components](monthly-components.csv), [half-hour components](half-hour-components.csv), [winter–summer comparisons](winter-summer-by-year.csv) and [clock profiles](clock-profiles.csv).
- [Monthly diagnostics](monthly-checks.csv) and [half-hour diagnostics](half-hour-checks.csv).
