"""Create the two report sources from the verified R output."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(name):
    with (ROOT / f"{name}.csv").open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def n(value, digits=2):
    return f"{float(value):,.{digits}f}".replace("-", "−")


def billion(value):
    return n(float(value) / 1000)


def table(headings, rows):
    return (
        "| " + " | ".join(headings) + " |\n"
        "| " + " | ".join("---" for _ in headings) + " |\n"
        + "\n".join("| " + " | ".join(map(str, row)) + " |" for row in rows) + "\n"
    )


stats = read("method-summary")
examples = read("worked-example")
profiles = read("seasonal-profiles")
sensitivity = read("whole-cycle-check")
summary_table = table(
    ["Method", "Highest month", "Contribution, US$ billion", "Lowest month", "Contribution, US$ billion"],
    [(s["method"], s["highest_month"], billion(s["highest_million"]), s["lowest_month"],
      billion(s["lowest_million"])) for s in stats],
)
diagnostics = table(
    ["Method", "Complete months", "Maximum reconstruction error, US$ million", "Remainder RMSE, US$ billion", "12-month correlation"],
    [(s["method"], s["complete_components"], f'{float(s["max_reconstruction_error"]):.2g}',
      billion(s["common_rmse_million"]), n(s["lag12_correlation"])) for s in stats],
)
examples_table = table(
    ["Method", "Trend, US$ million", "Seasonal contribution or factor", "Remainder or factor", "Adjusted sales, US$ million"],
    [(s["method"], n(s["trend_million"]),
      n(s["seasonal_native"], 6 if s["method"] == "Classical multiplicative" else 2),
      n(s["remainder_native"], 6 if s["method"] == "Classical multiplicative" else 2),
      n(s["adjusted_million"])) for s in examples],
)
calculations = []
for e in examples:
    name = e["method"]
    t, seasonal, remainder = [float(e[k]) for k in ("trend_million", "seasonal_native", "remainder_native")]
    if name == "Classical multiplicative":
        text = (
            f"**{name}.** The trend is {n(t)} million dollars. The seasonal factor "
            f"{n(seasonal,6)} gives a May contribution of ({n(seasonal,6)} − 1) × 100 ≈ "
            f"{n((seasonal-1)*100)}%. The seasonal baseline is "
            f"{n(t)} × {n(seasonal,6)} ≈ {n(e['fitted_million'])} million dollars. "
            f"Dividing sales by that baseline gives the remainder factor {n(remainder,6)}, "
            f"about {n(abs(remainder-1)*100)}% below the baseline. Multiplying "
            f"{n(t)} × {n(seasonal,6)} × {n(remainder,6)} ≈ 76,125.00 reconstructs observed sales. "
            f"The adjusted value is 76,125.00 ÷ {n(seasonal,6)} ≈ {n(e['adjusted_million'])} million dollars."
        )
    else:
        text = (
            f"**{name}.** The trend is {n(t)} million dollars and the May seasonal term adds "
            f"{n(seasonal)} million. Their sum is {n(e['fitted_million'])} million dollars. "
            f"Observed sales were {n(abs(remainder))} million below that seasonal baseline. "
            f"The reconstruction is {n(t)} + {n(seasonal)} − {n(abs(remainder))} ≈ 76,125.00. "
            f"Adjusted sales are 76,125.00 − {n(seasonal)} ≈ {n(e['adjusted_million'])} million dollars."
        )
    calculations.append(text)
worked = "\n\n".join(calculations)
title = "Seasonal patterns in U.S. restaurant sales"
body = f"""A comparison of classical additive, classical multiplicative, STL, and STR using September 2021–September 2026.

## Dataset and question

How do four methods describe the same seasonal pattern? We compare the underlying direction, the typical high and low months, the size of their contributions, and the movement each fit leaves unexplained.

The uploaded **MRTSSM7225USN.csv** has **61 consecutive monthly observations** of U.S. restaurants and other eating-place sales. The U.S. Census Bureau produces these estimates, distributed through FRED, the Federal Reserve Bank of St. Louis's economic database. Values are in **millions of U.S. dollars** and are unadjusted for seasonality. Each row is a calendar month's sales total. [Dataset source](https://fred.stlouisfed.org/series/MRTSSM7225USN).

Dates such as 9/1/2021 mean September 2021. We parsed the file as month/day/year. Every month from September 2021 to September 2026 is present, ordered and unique. All measurements are positive and finite. All 61 observations were fitted, with no filled or excluded rows.

The history spans five annual cycles plus one month. The four complete calendar years are 2022–2025. Every calendar month has five or six observations. We use one **12-month seasonal period**. One billion dollars equals 1,000 million dollars. The sales are nominal, so changes include price changes and changes in restaurant activity.

## What each method does and why it fits

### Classical additive

The trend is a centered 12-month moving average. The method averages sales minus trend for each calendar month, centers the twelve seasonal terms around zero, and repeats them. The remainder is observed sales minus trend minus seasonality.

This gives a straightforward fixed seasonal pattern measured in dollars. Its usefulness depends on whether seasonal swings remain reasonably stable in those units. The centered average requires data on both sides, leaving six unavailable trend and remainder values at each end. [R classical decomposition documentation](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/decompose.html).

### Classical multiplicative

This uses the same trend, averages sales-to-trend ratios by calendar month, and normalizes the twelve seasonal factors around one. The remainder is observed sales divided by trend times seasonal factor. It describes a fixed percentage effect whose dollar contribution increases with the underlying level.

All sales are positive, so the ratio calculations are feasible. Comparing the two classical fits helps assess a dollar effect versus a proportional effect. Their trend estimates coincide, and both have the same end gaps. [R classical decomposition documentation](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/decompose.html).

### STL

**STL** means **Seasonal-Trend Decomposition Using LOESS**. LOESS is local smoothing using nearby observations. STL alternates between smoothing each calendar month's readings across years and smoothing the trend after removing seasonality.

It allows the annual shape to evolve smoothly. We fitted the original dollar values with seasonal window 7. The resulting trend window was 23 months and low-pass window 13. Robust fitting was disabled for this standard comparison. The seasonal window uses neighboring occurrences of the same calendar month. This five-year history provides limited evidence of long-term changes. [R STL documentation](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/stl.html).

### STR

**STR** means **Seasonal-Trend Decomposition Using Regression**. It fits trend and seasonality jointly, using penalties to control their smoothness. AutoSTR selected those penalties automatically, using five-fold internal cross-validation with a reported gap setting of 11 observations.

This supplies a regression-based comparison with one annual seasonal component. We used the original dollar values, standard fitting, and no additional predictors. The seasonal shape can vary. Actual settings and selected penalties are saved with the report. [AutoSTR documentation](https://pkg.robjhyndman.com/stR/reference/AutoSTR.html).

## Findings and figures

### Underlying sales level

![Observed monthly sales and the four estimated trends.](sales-and-trend.png)

**Purpose and axes.** Both panels cover September 2021–September 2026. January year labels appear on the lower horizontal axis, and pale vertical year guides appear in both panels. The top vertical axis shows observed sales in billions of U.S. dollars. The bottom shows trend in the same units with a different range. Pale horizontal lines align with the tick values.

**Lines and panels.** The upper solid gray line connects observed monthly sales. Below, solid blue shows classical additive, dashed orange classical multiplicative, dotted green STL (Seasonal-Trend Decomposition Using LOESS), and dot-dashed purple STR (Seasonal-Trend Decomposition Using Regression). LOESS means local smoothing. The classical trends overlap because both use the same moving average. Those lines run from March 2022 to March 2026 because the first and last six trend values are unavailable.

**What it shows.** Every method estimates an upward underlying level alongside a recurring annual rise and fall. On the common March 2022–March 2026 interval, the fitted trend increase is **19.7%–20.5%**. Observed sales reached **85.23 billion dollars in May 2026**, the highest reading in this file.

### Typical seasonal profile

![The four methods' estimated contributions by calendar month.](seasonal-profiles.png)

**Purpose and axes.** The horizontal axis lists January through December. The vertical axis shows seasonal contributions in billions of U.S. dollars. The dotted gray zero line marks no seasonal contribution. Pale horizontal lines align with the ticks. The profiles average January 2022–December 2025, so each month contributes four fitted values. All methods were fitted to the full 61 months.

**Lines and markers.** Solid blue with squares is classical additive. Dashed orange with circles is classical multiplicative. Dotted green with triangles is STL (Seasonal-Trend Decomposition Using LOESS, or local smoothing). Dot-dashed purple with diamonds is STR (Seasonal-Trend Decomposition Using Regression). Lines trace the profile, and small horizontal marker offsets keep them visible. Multiplicative factors are converted to dollars at a common reference trend of **{billion(stats[0]['reference_million'])} billion dollars**, using reference × (factor − 1). This is the average classical trend over March 2022–March 2026. The other methods already give dollar contributions.

**What it shows.** All four methods put the highest recurring contribution in **May** and the lowest in **February**. May contributes **4.82–5.10 billion dollars** and February contributes **−5.95 to −6.15 billion dollars** on this comparison scale. The multiplicative factors are about **1.067459 in May**, or 6.75% above trend, and **0.915898 in February**, or 8.41% below trend.

{summary_table}

The highest observed month was July in 2022–2023 and May in 2024–2025. The seasonal profile averages across years after allowing for different underlying levels, giving May the strongest recurring contribution.

### Variation left after fitting

![Remainders for the four methods on the same dollar scale.](remainders.png)

**Purpose and axes.** Each panel covers September 2021–September 2026, with years along the horizontal axis and pale January guides. All four vertical axes use the same range, in billions of U.S. dollars. The dotted gray line marks zero remainder and pale horizontal lines align with the ticks.

**Lines and panels.** Upper left is classical additive in solid blue. Upper right is classical multiplicative in dashed orange. Lower left is STL (Seasonal-Trend Decomposition Using LOESS, or local smoothing) in dotted green. Lower right is STR (Seasonal-Trend Decomposition Using Regression) in dot-dashed purple. Positive values mean sales exceeded the fitted seasonal baseline. Negative values mean sales fell below it. The multiplicative panel shows observed sales minus trend × seasonal factor in dollars. Its native remainder is a unitless ratio. Both classical panels have gaps in September 2021–February 2022 and April–September 2026.

**What it shows.** The fits leave some individual months above or below their baseline. In the common interval, the largest absolute classical remainders occur in February 2024. The largest absolute STL and STR remainders occur in January 2023. The models divide short movements differently between their components.

## Worked calculations for May 2024

Observed sales were **76,125 million dollars**. For additive fits, observed sales equal trend + seasonal contribution + remainder. For the multiplicative fit, observed sales equal trend × seasonal factor × remainder factor.

Trend and adjusted sales retain the sales units. Additive seasonal and remainder terms are in millions of dollars. Multiplicative seasonal and remainder factors are unitless, with one representing no effect. The table uses native scales. Displayed rounding can affect the last decimal of the arithmetic.

{examples_table}

{worked}

These examples show how the extracted components combine. The complex fitting stages use alternating local smooths for STL and regression with selected smoothness penalties for STR.

## Verification and diagnostics

Every complete set of components passed reconstruction at a tolerance of **0.000001 million dollars**, or one dollar. Each classical method reconstructed 49 positions and had 12 unavailable trend and remainder positions. STL and STR reconstructed all 61.

For a common diagnostic comparison, we use **49 months from March 2022 through March 2026**. RMSE means root mean squared error, the typical size of the fitted dollar deviations. The 12-month correlation uses **37 complete pairs** and measures whether deviations one year apart have similar signs and sizes. There were no filled values.

{diagnostics}

The annual remainder correlations are modest and negative. These checks alone cannot establish that every recurring feature has been captured. In-sample RMSE ranges from about 0.96 to 1.08 billion dollars. Small differences in that statistic do not establish how the methods will work on other data. AutoSTR returned no fitting warnings.

We also checked the partial annual cycle by refitting the classical methods to the first 60 months, September 2021–August 2026. The largest seasonal change was **{n(sensitivity[0]['max_seasonal_difference_million'])} million dollars** for additive decomposition and **{n(sensitivity[1]['max_seasonal_difference_million'])} million dollars** for multiplicative decomposition at the same reference trend. The latter is a maximum factor change of **{n(float(sensitivity[1]['max_factor_difference'])*100)} percentage points**. The exact seasonal figures depend partly on the fitting span.

## Limitations

- About five years of data provide limited evidence of long-term seasonal change. The classical fits fix the seasonal shape across the span.
- Monthly totals reflect month length, weekday composition, holidays, and other conditions alongside seasonal patterns. These fits include no separate calendar or weather variables. February's low total partly reflects its shorter duration.
- The sales are in current dollars. Changes can reflect prices, the mix of purchases, and restaurant activity. These results describe historical sales patterns.
- The classical trend and remainder have end gaps. STL and STR use less information on one side near the ends and may revise when more data arrive. Calendar years 2021 and 2026 are partial in the uploaded file.

## Conclusion

**All four methods agree on May as the strongest seasonal month, February as the weakest, and roughly 20% growth in the underlying sales level from March 2022 to March 2026.** The May–February seasonal difference is about **10.88–11.16 billion dollars** on the common dollar comparison scale.

Classical additive expresses fixed dollar contributions. Classical multiplicative expresses percentage effects, here about +6.75% in May and −8.41% in February. STL and STR allow smoother changes across years and agree on these high and low months. The precise contributions depend on the method and fitting span.

## Reproducibility

The folder includes the input CSV, the R analysis and plots, all components, and the numerical checks. Classical decomposition and STL use base R. STR requires the stR package. The settings file records R and package versions, STR penalties and actual STL windows.

Run these commands from the report folder after installing the R dependencies. The R script regenerates the analysis and plots. The Python builder reads the resulting tables to update the two report sources. Quarto renders the saved report text and figures.

```text
Rscript analyze.R
python build-report.py
quarto render report.qmd --to html
```

- [Input data](MRTSSM7225USN.csv)
- [R analysis](analyze.R) and [R plotting code](plots.R)
- [Report source builder](build-report.py) and [HTML styling](report.css)
- [Monthly components and status flags](components.csv)
- [Seasonal profiles](seasonal-profiles.csv), [method summaries and checks](method-summary.csv), and [worked example](worked-example.csv)
- [Whole-cycle check](whole-cycle-check.csv) and [actual settings and software versions](settings.txt)

## References

- U.S. Census Bureau, distributed through FRED. [Retail Sales: Restaurants and Other Eating Places, MRTSSM7225USN](https://fred.stlouisfed.org/series/MRTSSM7225USN).
- R stats documentation. [Classical decomposition by moving averages](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/decompose.html).
- R stats documentation. [Seasonal decomposition by LOESS](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/stl.html).
- Dokumentov and Hyndman. [STR: Seasonal-Trend Decomposition Using Regression](https://arxiv.org/abs/2009.05894).
- R stR documentation. [AutoSTR](https://pkg.robjhyndman.com/stR/reference/AutoSTR.html).
"""
header = (
    f'---\ntitle: "{title}"\ndate: "2026-11-27"\n'
    "format:\n  html:\n    toc: true\n    toc-depth: 2\n"
    "    embed-resources: true\n    css: report.css\n"
    "    mainfont: 'Segoe UI, system-ui, sans-serif'\n---\n\n"
)
(ROOT / "report.md").write_text(f"# {title}\n\n{body}", encoding="utf-8")
(ROOT / "report.qmd").write_text(header + body, encoding="utf-8")
