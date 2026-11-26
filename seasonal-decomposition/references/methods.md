# Seasonal Decomposition Methods Reference

Use [checklist.md](checklist.md) to review the data, [decision-tree.md](decision-tree.md) to choose a method, and [report-spec.md](report-spec.md) to present findings. Run the example for the selected method with built-in or simulated data, then adapt the inputs and settings to the user's series.

## Prepare the inputs once

- Keep one ordered numeric series `y` per target and group, with a parallel time index `index`. Check for invalid values, gaps, and duplicate timestamps before constructing an R `ts` or `msts` object. Preserve the original observations, the prepared grid, and any imputation or exclusion flags. Match outputs back to dates or timestamps rather than inferring them from row positions after a fit changes the span.
- Express each period in observations and calendar terms. For example, `48` half-hour observations represents one day on a regular grid. State the clock convention before assigning labels such as “6 p.m.” Check actual phase coverage, particularly when daylight saving, leap days, or partial cycles matter.
- A usable seasonal grid and a successful fit do not establish meaningful seasonality. Check repeated patterns in the observed series, the history available for each period, and whether the results address the user's question. Use documented missing-value handling where appropriate. The examples below use complete, finite inputs.

The following monthly example supplies `x`, `y`, and `index` for methods 1, 2, 3, 5, 6, and 7. To use your own data, construct `x <- stats::ts(y, start = c(first_year, first_month_or_quarter), frequency = period)` after verifying the ordered observations and their start. For a noncalendar `ts`, retain its original time index separately. Method 4 has its own input example.

```r
x <- datasets::AirPassengers
y <- as.numeric(x)
index <- seq(as.Date("1949-01-01"), by = "month", length.out = length(x))
m <- stats::frequency(x)
stopifnot(length(y) == length(index), all(is.finite(y)))

check_reconstruction <- function(observed, reconstructed) {
  stopifnot(length(observed) == length(reconstructed))
  keep <- is.finite(observed) & is.finite(reconstructed)
  stopifnot(any(keep))
  error <- max(abs(observed[keep] - reconstructed[keep]))
  tolerance <- 1e-8 * max(1, max(abs(observed[keep])))
  stopifnot(error <= tolerance)
  c(max_error = error, checked = sum(keep), omitted = sum(!keep))
}
```

## 1 Classical additive decomposition

Use for one stable seasonal pattern with roughly constant swings in the measurement's units. Use a regular series with integer period `m > 1` and at least two complete cycles. Whole cycles give better phase coverage. Centered moving averages leave trend and remainder undefined near both ends. `fit$figure` gives the repeating effect for each phase in the original units.

```r
stopifnot(m > 1, m == round(m), length(x) >= 2 * m)
fit <- stats::decompose(x, type = "additive")
T <- as.numeric(fit$trend)
S <- as.numeric(fit$seasonal)
R <- as.numeric(fit$random)
adjusted <- y - S
check_reconstruction(y, T + S + R)
```

## 2 Classical multiplicative decomposition

Use for one stable seasonal pattern whose swings grow roughly in proportion to the level. Use the same grid and history checks as method 1 and require strictly positive observations. The trend retains the measurement's units, while the seasonal and remainder components are factors centered conceptually around one. The same edge gaps apply.

```r
stopifnot(m > 1, m == round(m), length(x) >= 2 * m, all(y > 0))
fit <- stats::decompose(x, type = "multiplicative")
T <- as.numeric(fit$trend)
S <- as.numeric(fit$seasonal)
R <- as.numeric(fit$random)
adjusted <- y / S
check_reconstruction(y, T * S * R)
```

Use `100 * (S - 1)` to express the seasonal contribution as a percentage relative to trend. Use `T * (S - 1)` to express it in measurement units at each date. For example, a factor of `1.15` means the fitted seasonal baseline is 15% above trend before the remainder is applied.

## 3 STL

Use for one integer seasonal period when the trend needs flexible smoothing or the seasonal shape may change. Standard `stats::stl()` needs more than two full cycles and complete observations. `s.window = "periodic"` fixes the seasonal shape. To allow change, choose an odd seasonal window of at least 7 and justify it using the available history and the question. Larger windows smooth more across cycles. `robust = TRUE` reduces the influence of unusual observations.

```r
stopifnot(m > 1, m == round(m), length(x) > 2 * m)
fit <- stats::stl(x, s.window = 7, robust = TRUE)
parts <- fit$time.series
adjusted <- y - parts[, "seasonal"]
check_reconstruction(y, rowSums(parts))
```

STL adds components on the analyzed scale. For strictly positive data, fitting to `log(x)` yields multiplicative components after exponentiation. Back-transform sums of components for other justified transformations and label the resulting scale. Save the actual windows and robust setting.

## 4 MSTL

Use for several supported seasonal periods on the same grid. The example uses `forecast::mstl()` with complete data and two integer periods. Check that the installed version retains every intended period. The usual implementation can drop periods at least half the series length and can interpolate missing values. Document these behaviors if they occur. Use a different specification when a fractional period matters and the selected STL implementation cannot represent it faithfully.

```r
# Four weeks of simulated hourly data with daily and weekly patterns.
t <- seq_len(24 * 28)
periods <- c(24, 168)
y_multi <- 100 + t / 40 + 8 * sin(2 * pi * t / 24) +
  3 * sin(2 * pi * t / 168)
index_multi <- as.POSIXct("2024-01-01", tz = "UTC") + (t - 1) * 3600
stopifnot(length(y_multi) > 2 * max(periods))
x_multi <- forecast::msts(y_multi, seasonal.periods = periods)
parts <- forecast::mstl(x_multi, lambda = NULL, iterate = 2,
                        s.window = c(11, 15), robust = TRUE)
seasonal_names <- paste0("Seasonal", periods)
stopifnot(all(seasonal_names %in% colnames(parts)))
seasonal_total <- rowSums(parts[, seasonal_names, drop = FALSE])
adjusted <- y_multi - seasonal_total
check_reconstruction(y_multi, parts[, "Trend"] + seasonal_total +
                       parts[, "Remainder"])
```

Save one column per retained period. Interpret each pattern in the presence of the others, especially when one period is a multiple of another. If fitting with a Box-Cox transformation, verify reconstruction on the transformed scale and use the documented inverse for reported values.

## 5 X-11

Use for filter-based seasonal adjustment of monthly or quarterly data. Set `frequency(x)` to 12 or 4 with the correct calendar start. Check history and data limits for the X-13 specifications in use. Choose and record the decomposition mode and any regARIMA preparation. For signed data, evaluate whether additive adjustment is suitable. The example uses a positive series with a log transformation and multiplicative mode.

```r
seasonal::checkX13(fail = TRUE)
stopifnot(m %in% c(4, 12), all(y > 0))
x11 <- seasonal::seas(
  x, x11 = "", x11.mode = "mult", transform.function = "log",
  regression.aictest = NULL, outlier = NULL, na.action = stats::na.fail,
  x11.save = c("d10", "d11", "d12", "d13"), out = TRUE
)
x11_parts <- seasonal::series(x11, c("d10", "d11", "d12", "d13"),
                              reeval = FALSE)
summary(x11)
```

The four tables give seasonal effects, adjusted observations, trend-cycle, and irregular component, respectively. Use the definitions and scales of the actual tables. Keep calendar and other regression effects separately when the model estimates them. Review residual seasonal signals, endpoint sensitivity, and the stability of the adjustment.

## 6 SEATS

Use for model-based seasonal adjustment and signal extraction from a fitted seasonal ARIMA model. X-13 supports 12, 6, 4, or 2 observations per year for seasonal adjustment. Check the installed interface, calendar alignment, and enough history for the chosen model and settings. Fit and check a suitable model before interpreting its components. Inspect messages for convergence problems or use of an alternative model when the fitted model cannot be decomposed.

```r
seasonal::checkX13(fail = TRUE)
stopifnot(m %in% c(2, 4, 6, 12), all(y > 0))
seats <- seasonal::seas(
  x, seats.noadmiss = "yes", transform.function = "log",
  regression.aictest = NULL, outlier = NULL, na.action = stats::na.fail,
  seats.save = c("s10", "s11", "s12", "s13"), out = TRUE
)
seats_parts <- seasonal::series(seats, c("s10", "s11", "s12", "s13"),
                                reeval = FALSE)
summary(seats)
```

`seas()` uses SEATS by default when X-11 is not requested. The four tables give seasonal effects, adjusted observations, trend-cycle, and irregular component, respectively. Check whether the chosen model supplies any additional modeled components. Keep ARIMA model residuals separate from the final irregular component and review both when assessing fit and adjustment quality.

**Checks for both X-13 methods.** The examples turn off automatic trading-day and Easter testing and automatic outlier detection for illustration. Assess these effects on the user's actual data and record what was included, removed, or restored. Use the saved X-13 output to verify the actual specification and relevant diagnostics. Use `seasonal::na.x13` only when the specification supports native missing-value estimation and that treatment is appropriate. Preserve the missing flags and the reported estimates. For reconstruction, match calendar periods and compare documented table identities on the relevant scale and span. Allow for output rounding, transformations, prior adjustments, and additional effects. A simple sum or product may correspond to an adjusted input rather than the raw series. Inspect residual seasonality in the adjusted series and note that endpoint estimates can revise as data arrive. Use `seasonal::static()` and save the final fit and output when documenting automatic settings.

## 7 STR

Use Seasonal-Trend Decomposition Using Regression when multiple or fractional periods, distinct calendar patterns, or predictors are central to the question. Use `stR::AutoSTR()` with a suitable `ts` or `msts` input for standard trend and seasonal components. For predictors or a custom calendar, use an explicit `stR::STR()` specification and define times, seasonal positions or structures, and any predictor values on the same grid. Check history, smoothing choices, fitting warnings, and whether the data distinguish the specified effects.

```r
fit <- stR::AutoSTR(x)
effects <- vapply(fit$output$predictors,
                  function(term) as.numeric(term$data),
                  numeric(length(x)))
remainder <- as.numeric(fit$output$random$data)
check_reconstruction(y, rowSums(effects) + remainder)
```

Use the fitted predictor definitions to label trend, seasonal, and other contributions. Sum only the seasonal columns when computing a series with those effects removed. Record the estimated smoothing parameters and whether the robust option was used. If requested and supported by the fit, label component confidence intervals and their assumptions. Predictor contributions describe associations in the fitted model.

## Check and interpret the results

For the report's worked calculation, select a fitted row with available estimates and extract its values in R. Show how the relevant components combine on their actual scale. For X-13 output, identify the corresponding raw or adjusted reference series and its documented table relationship. Record labels, units, and transformations with the plotting data so the report can explain each figure using [report-spec.md](report-spec.md).

| User question | What to compute or inspect in R |
| --- | --- |
| Is the underlying level rising or falling? | Compare trend estimates over the requested dates. State the dates, units, and any endpoint limitations. |
| When is the series usually high or low? | Summarize seasonal effects by phase, using the actual calendar or clock labels. For a changing pattern, compare agreed time spans and report the size of changes. |
| How large is the seasonal difference? | Report the high and low phase effects and their difference in units for additive fits. For factors, report percentages relative to a stated baseline. Identify which period is summarized for multiple cycles. |
| Was this observation unusual? | Compare it with the fitted baseline and inspect the dated remainder. Check data quality and context before attaching an explanation. |
| Is anything still repeating after adjustment? | Inspect remainder or irregular plots and a lag plot or ACF at relevant lags. Preserve the grid through gaps. Assess X-13 adjustment diagnostics where available. |

Save aligned observed data, trend, every seasonal component, remainder, relevant adjusted series, and any separate effects. Keep missing edge values visible. Record the scale, method, periods, code, actual settings, package versions, and material warnings. Plot the original series and relevant components. Use reconstruction to check arithmetic and alignment. Use seasonal evidence and diagnostics to assess whether the decomposition answers the question.

## Sources

- [Forecasting Principles and Practice, Chapter 3](https://otexts.com/fpp3/decomposition.html), [R classical decomposition](https://search.r-project.org/R/refmans/stats/html/decompose.html), and [R STL](https://search.r-project.org/R/refmans/stats/html/stl.html).
- [MSTL paper](https://robjhyndman.com/publications/mstl/) and [forecast MSTL documentation](https://pkg.robjhyndman.com/forecast/reference/mstl.html).
- [U.S. Census X-13 reference manual](https://www2.census.gov/software/x-13arima-seats/x13as/unix-linux/documentation/docx13ashtml.pdf), [seasonal fitting interface](https://search.r-project.org/CRAN/refmans/seasonal/html/seas.html), and [X-13 table extraction](https://search.r-project.org/CRAN/refmans/seasonal/html/series.html).
- [STR paper](https://arxiv.org/abs/2009.05894), [AutoSTR](https://pkg.robjhyndman.com/stR/reference/AutoSTR.html), and [explicit STR specifications](https://pkg.robjhyndman.com/stR/reference/STR.html).
