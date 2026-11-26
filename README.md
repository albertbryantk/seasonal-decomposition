# Seasonal Decomposition

`seasonal-decomposition` is an R-based skill for understanding historical patterns in dated numeric data. It separates a time series into its **trend** (underlying movement), **seasonality** (patterns that repeat at known intervals), and **remainder** (variation left after accounting for those patterns). Use it to find recurring highs and lows, see whether seasonal swings have changed, or identify observations that were unusual for their time of year.

## Setup and Quick Start

1. Put the `seasonal-decomposition/` folder in your agent's skills directory, keeping `SKILL.md` and `references/` together.
2. Make R available to the agent. Run `Rscript --version` to check. On Windows, you can use the full path to `Rscript.exe` in your R installation's `bin` folder. Classical decomposition and STL use base R. The other methods' dependencies are listed below.
3. Attach a dataset or name a built-in R series, then ask the agent to use `seasonal-decomposition`. Include your question if you have one. For example, “Use `seasonal-decomposition` to find which months typically have the highest sales and whether the underlying sales level is rising.”

For a quick start, attach the 2026 Great Britain electricity demand CSV or give the agent the dataset link. [2026 NESO data page](https://www.neso.energy/data-portal/historic-demand-data/historic_demand_data_2026)

> Use `seasonal-decomposition` on the 2026 NESO data. Fit MSTL to the half-hour National Demand (`ND`) readings using daily and weekly cycles. What time does demand usually peak on weekdays and weekends? Show the times in London local time.

## Example Questions

- Which weekdays usually have the most orders, and how many more orders do they get than the quietest weekday?
- Has website traffic grown over the past year after accounting for the usual weekly pattern?
- Do summer electricity demand peaks sit farther above the underlying trend now than they did earlier in the series?
- Which months had unusually low hotel bookings after accounting for the trend and the usual seasonal pattern?
- Do my hourly transit counts show both a daily cycle and a weekly cycle?
- Can you give me a general report showing the trend, recurring highs and lows, and any unusual observations?

## Example Dataset for Great Britain Electricity Demand

The National Energy System Operator (NESO) publishes Great Britain's historical electricity demand in half-hour intervals. Download the annual CSVs for 2015–2025 and the 2026 CSV. Use `ND` (National Demand, in megawatts) as the measurement. If `FORECAST_ACTUAL_INDICATOR` is present, keep actual observations (`A`). The archive is updated with a publication lag and may be revised. [Annual CSV archive](https://www.neso.energy/data-portal/historic-demand-data) · [2026 CSV and data dictionary](https://www.neso.energy/data-portal/historic-demand-data/historic_demand_data_2026)

| Prepare the data | Seasonal periods | Methods to try |
| --- | --- | --- |
| Average the half-hour readings within each complete calendar month. January 2015 through October 2026 makes a 142-month example. | 12 months per annual cycle | Classical additive and multiplicative, STL, X-11, and SEATS |
| Keep the 2026 half-hour readings. Convert `SETTLEMENT_DATE` and `SETTLEMENT_PERIOD` to a regular UTC timeline using the London clock-change rules. Check for gaps and duplicates before fitting. | 48 half-hours per day and 336 per week | MSTL |

The monthly series is strictly positive, so you can compare the two classical methods and check whether seasonal swings are steadier in megawatts or as a proportion of the underlying level. The half-hour series lets you compare time-of-day and day-of-week patterns. When reporting clock times, state whether they are UTC or London local time.

> Use `seasonal-decomposition` on the attached NESO CSVs. Average `ND` within each complete month from January 2015 through October 2026. Compare X-11 and SEATS to estimate how much higher demand typically was in winter than in summer.

Supported by National Energy SO Open Data. [NESO Open Data Licence](https://www.neso.energy/data-portal/neso-open-licence)

## Data and Workflow

Provide a numeric measurement and a known time index, such as a date column or the timing metadata in an R time-series object. Use a consistent observation interval and enough history to see the proposed cycle repeat. Units, group labels, and time zone information help the skill interpret the series correctly.

1. **Inspect the data.** Check the time grid, gaps, duplicates, and how many seasonal cycles were actually observed. Preserve the original data, ask about consequential preparation choices, and flag any values that are filled or excluded.
2. **Set the objective.** Use the question you provide or choose from questions tailored to the data. A general report covers the underlying direction, recurring highs and lows, and unusual observations when the evidence supports them.
3. **Choose a method.** The skill explains which methods fit the data and the question. You can choose a method, accept the recommendation, or delegate the choice.
4. **Fit and verify in R.** The skill checks timestamp alignment, confirms that the components reconstruct the appropriate series, and examines remaining patterns and fit warnings.
5. **Read the report.** The skill answers your question in plain language and delivers HTML, Markdown, and Quarto together.

When the history or time grid cannot support a seasonal fit, the skill explains the issue and reports what the available observations can support. Conclusions describe patterns in the observed history.

## Supported Methods

| Method | When it fits | R requirement |
| --- | --- | --- |
| Classical additive | One stable cycle with roughly constant swings in the original units | Base R (`stats::decompose()`) |
| Classical multiplicative | One stable cycle with swings that grow roughly in proportion to the level and strictly positive values | Base R (`stats::decompose()`) |
| STL | One cycle with a potentially changing seasonal pattern or a need for robust fitting | Base R (`stats::stl()`) |
| MSTL | Several cycles on the same time grid, such as daily and weekly patterns in hourly data | `forecast` |
| X-11 | Filter-based seasonal adjustment for monthly or quarterly data | `seasonal` and a working X-13 executable |
| SEATS | Seasonal adjustment based on a suitable seasonal ARIMA model at a supported calendar frequency | `seasonal` and a working X-13 executable |
| STR | Flexible seasonal patterns, such as fractional periods, custom calendars, or models with predictors | `stR` |

See the [methods reference](references/methods.md) for runnable R examples, dependency checks, and interpretation details.

## Reports and Reproducibility

- **Three report files in the same folder.** Open `report.html` in a browser, read `report.md` as Markdown, or edit `report.qmd` as Quarto source. All three include the same findings, figures and explanations, worked calculation, diagnostics, limitations, conclusion, and references. Keep the linked assets with the report files. You can render `report.qmd` with Quarto.
- **Analysis files** with timestamped components, preparation flags, fit settings, and diagnostic results for the completed analysis.
- **Reproducibility details** with the R code, software versions, and instructions for rerunning the analysis. If R or a required package is unavailable, the skill provides runnable R code and identifies the pending results.

## Skill Files

| File | Purpose |
| --- | --- |
| [`SKILL.md`](SKILL.md) | Main instructions for the analysis workflow |
| [`references/checklist.md`](references/checklist.md) | Data readiness and method requirements |
| [`references/decision-tree.md`](references/decision-tree.md) | How the skill moves from the user's question to a suitable method |
| [`references/methods.md`](references/methods.md) | R examples and verification checks for all seven methods |
| [`references/report-spec.md`](references/report-spec.md) | Report structure and final checks |

## References

- Hyndman, R. J., & Athanasopoulos, G. (2021). *Forecasting: Principles and Practice* (3rd ed.), chapter 3. OTexts. Covers the components of a time series and both classical methods. [Time series decomposition](https://otexts.com/fpp3/decomposition.html)
- Cleveland, R. B., Cleveland, W. S., McRae, J. E., & Terpenning, I. (1990). STL: A seasonal-trend decomposition procedure based on loess. *Journal of Official Statistics*, 6(1), 3–73. [Original STL paper](https://www.scb.se/contentassets/ca21efb41fee47d293bbee5bf7be7fb3/stl-a-seasonal-trend-decomposition-procedure-based-on-loess.pdf)
- Bandara, K., Hyndman, R. J., & Bergmeir, C. (2025). MSTL: A seasonal-trend decomposition algorithm for time series with multiple seasonal patterns. *International Journal of Operational Research*, 52(1), 79–98. [Published MSTL paper](https://doi.org/10.1504/IJOR.2025.143957)
- Shiskin, J., Young, A. H., & Musgrave, J. C. (1967). *The X-11 Variant of the Census Method II Seasonal Adjustment Program*. U.S. Bureau of the Census, Technical Paper No. 15. [Original X-11 paper](https://www.census.gov/library/working-papers/1967/adrm/shiskin-01.html)
- Gómez, V., & Maravall, A. (1996). *Programs TRAMO and SEATS: Instructions for the User*. Banco de España, Working Paper No. 9628. [Original SEATS documentation](https://www.bde.es/wbe/en/publicaciones/analisis-economico-investigacion/documentos-trabajo/programs-tramo-and-seats-instructions-for-user-beta-version-september-1996.html)
- U.S. Census Bureau. (2017). *X-13ARIMA-SEATS Reference Manual* (version 1.1). Documents the X-11 and SEATS options used by the skill. [X-13ARIMA-SEATS manual](https://www.census.gov/library/working-papers/2017/adrm/docx13ashtml.html)
- Dokumentov, A., & Hyndman, R. J. (2022). STR: Seasonal-trend decomposition using regression. *INFORMS Journal on Data Science*, 1(1), 50–62. [Published STR paper](https://doi.org/10.1287/ijds.2021.0004)
