"""Build the report from the verified R output tables."""

import csv
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def read(name):
    with (ROOT / f"{name}.csv").open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def n(value, digits=0):
    return f"{float(value):,.{digits}f}"


def gw(value, digits=2):
    return n(float(value) / 1000, digits)


def pct(value):
    return n(value, 1) + "%"


def signed(value):
    return f"{float(value):+,.2f}".replace("-", "−")


def time_label(half_hour):
    hour, minute = map(int, half_hour.split(":"))
    return f"{hour % 12 or 12}:{minute:02d} {'p.m.' if hour >= 12 else 'a.m.'}"


def row(label, *columns):
    return "<tr><th scope='row'>" + escape(label) + "</th>" + "".join(
        f"<td>{escape(str(val))}</td>" for val in columns
    ) + "</tr>"


early, recent, latest = read("winter-summary")
latest_detail = read("winter-summer-by-year")[-1]
x, s = read("monthly-example")
xcheck, scheck = read("monthly-checks")
half = read("half-hour-example")[0]
hcheck = read("half-hour-checks")[0]
gap = read("weekday-gap")[0]
peaks = {(part["span"], part["weekend"]): part for part in read("peak-times")}
weekdays = peaks[("All", "FALSE")]
weekends = peaks[("All", "TRUE")]
comparison = "".join(
    row(label, gw(item["raw_mw"]), pct(item["raw_pct"]), 
        gw(item["x11.mw"]), pct(item["x11.pct"]), gw(item["seats.mw"]), pct(item["seats.pct"]))
    for label, item in zip(("2016–2018 average", "2024–2026 average", "2026"), (early, recent, latest))
)
profile_rows = "".join(
    row(label, *(
        f"{time_label(peaks[(name, flag)]['clock'])} · {gw(peaks[(name, flag)]['fit_mw'], 1)} GW"
        for flag in ("FALSE", "TRUE")
    ))
    for label, name in (("All fitted days", "All"), ("January 2026", "January"), ("July 2026", "July"))
)
monthly_example = "".join(
    row(label, n(x[field], digits), n(s[field], digits)) for label, field, digits in [
        ("Observed demand (MW)", "observed_mw", 2), ("Pure seasonal factor", "seasonal_factor", 6),
        ("Calendar factor", "calendar_factor", 6), ("Combined factor", "combined_factor", 6),
        ("Adjusted demand (MW)", "adjusted_mw", 2), ("Trend (MW)", "trend_mw", 2),
        ("Irregular factor", "irregular_factor", 6),
    ]
)
half_example = "".join(
    row(label, n(half[field], 2)) for label, field in [
        ("Trend", "trend_mw"), ("Daily effect", "daily_mw"), ("Weekly effect", "weekly_mw"),
        ("Fitted demand", "fit_mw"), ("Remainder", "remainder_mw"), ("Observed demand", "observed_mw"),
    ]
)
half_equation = n(half["trend_mw"], 2) + " " + " ".join(
    signed(half[field]) for field in ("daily_mw", "weekly_mw", "remainder_mw")
)
reconstruction = "".join(
    row(chk["method"], chk["positions"], f"{float(chk['raw_error']):.2g}",
        f"{float(chk['adjusted_error']):.2g}")
    for chk in (xcheck, scheck)
) + row("MSTL", hcheck["positions"], f"{float(hcheck['error']):.2g}", "—")
annual_pct = sorted((float(latest["x11.pct"]), float(latest["seats.pct"])))
annual_gw = sorted((float(latest["x11.mw"]), float(latest["seats.mw"])))
trend_x = read("monthly-components")
x_2015 = sum(float(r["trend_mw"]) for r in trend_x if r["method"] == "X-11" and r["month"][:4] == "2015") / 12
x_2025 = sum(float(r["trend_mw"]) for r in trend_x if r["method"] == "X-11" and r["month"][:4] == "2025") / 12

page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Winter and daily peaks in Great Britain’s electricity demand</title>
  <style>
    :root {{color-scheme:light;--ink:#182b43;--accent:#185d93;--warm:#a54424;--muted:#496278;--line:#dce5ec;--tint:#eaf2f8}}
    * {{box-sizing:border-box}}
    body {{margin:0;background:#f6f8fa;color:var(--ink);font:1rem/1.62 "Segoe UI",system-ui,sans-serif}}
    .wrap {{width:min(calc(100% - 2rem),68rem);margin-inline:auto}}
    header {{background:var(--ink);color:white;padding:clamp(2rem,6vw,4.3rem) 0 2.4rem}}
    header p {{color:#dce9f6}}
    .kicker {{font-size:.9rem;font-weight:650}}
    h1,h2 {{font-family:Georgia,serif;line-height:1.14;letter-spacing:-.023em}}
    h1 {{font-size:clamp(2.2rem,6vw,4.3rem);max-width:20ch;margin:0}}
    h2 {{font-size:clamp(1.65rem,3.6vw,2.35rem);margin:0 0 .7rem}}
    h3 {{font-size:1.04rem;margin:.75rem 0 .4rem}}
    p {{max-width:80ch;margin:.45rem 0 .9rem}}
    .intro {{margin:.9rem 0 0}}
    nav {{background:white;border-bottom:1px solid var(--line)}}
    nav .wrap {{display:flex;flex-wrap:wrap;gap:.4rem 1.25rem;padding-block:.7rem}}
    a {{color:var(--accent);text-underline-offset:.18em}}
    a:focus-visible {{outline:2px solid var(--accent);outline-offset:.2rem}}
    main {{padding-block:.7rem 3rem}}
    section {{padding:1.45rem 0}}
    section + section {{border-top:1px solid var(--line)}}
    .key {{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,16rem),1fr));gap:.8rem;margin-top:1rem}}
    .key div {{padding:.7rem .9rem;border:1px solid var(--line);border-top:4px solid var(--accent);background:white}}
    .key div:last-child {{border-top-color:var(--warm)}}
    .key strong {{display:block;font:600 1.7rem/1.25 Georgia,serif}}
    .key span {{font-size:.91rem;color:var(--muted)}}
    figure {{background:white;margin:1rem 0 0;padding:.7rem;border:1px solid var(--line);border-radius:.32rem .32rem 0 0}}
    figure a {{display:block;cursor:zoom-in}}
    img {{width:100%;height:auto;display:block}}
    figcaption {{padding:.35rem .35rem 0;font-weight:650}}
    .guide {{background:var(--tint);padding:.58rem 1rem .4rem;border:1px solid var(--line);border-top:none;margin-bottom:1.3rem}}
    .guide p {{margin:.25rem 0 .65rem}}
    .table-wrap {{overflow-x:auto;margin:.95rem 0}}
    table {{width:100%;border-collapse:collapse;background:white;font-variant-numeric:tabular-nums}}
    caption {{text-align:left;font-weight:650;padding-bottom:.38rem}}
    th,td {{padding:.45rem .6rem;text-align:left;border-bottom:1px solid var(--line)}}
    thead {{background:var(--tint)}}
    td {{white-space:nowrap}}
    .callout {{padding:.72rem .95rem;background:var(--tint);border-left:4px solid var(--accent)}}
    code {{font-family:Consolas,monospace;font-size:.92em}}
    pre {{padding:.7rem;background:var(--tint);overflow:auto}}
    ul {{padding-left:1.24rem}}
    li + li {{margin-top:.24rem}}
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <p class="kicker">Great Britain · 2015–2026</p>
      <h1>Winter demand and daily electricity peaks</h1>
      <p class="intro">How much higher is demand in winter, has that gap changed, and how do weekday peaks compare with weekends?</p>
    </div>
  </header>
  <nav aria-label="Report sections">
    <div class="wrap">
      <a href="#data">Dataset</a><a href="#methods">Methods</a><a href="#winter">Winter increase</a>
      <a href="#clock">Daily peaks</a><a href="#worked">Worked examples</a><a href="#checks">Checks</a>
      <a href="#conclusion">Conclusion</a><a href="#references">References</a>
    </div>
  </nav>
  <main class="wrap">
    <section id="data">
      <h2>The dataset</h2>
      <p>The National Energy System Operator (NESO) reports Great Britain's National Demand, abbreviated <code>ND</code>, in megawatts (MW) for each half-hour settlement interval. A gigawatt (GW) is 1,000 MW. This series measures metered generation needed to meet National Demand under NESO's definition. It excludes station load, pumped-storage pumping, and interconnector exports. <a href="https://www.neso.energy/data-portal/historic-demand-data/historic_demand_data_2026">Dataset and column definitions</a>.</p>
      <p>We combined the official 2015–2025 annual files with the uploaded 2026 file. The upload has {n(hcheck["positions"])} actual half-hours from 1 January to 4 November. R checked settlement dates and periods against the UK time zone, including the 46-interval spring day and the 50-interval autumn day. The input contains no gaps, duplicates or invalid demand values. All 2026 readings went into the half-hour fit. Monthly fits use {xcheck["positions"]} complete months from January 2015 through October 2026. Each monthly value is the mean of its half-hour power readings. The four November days have no monthly mean in the fit. <a href="https://www.neso.energy/data-portal/historic-demand-data">NESO historical archive</a>.</p>
      <div class="key">
        <div><strong>{gw(latest["raw_mw"], 1)} GW</strong><span>Observed winter–summer gap in 2026</span></div>
        <div><strong>{pct(annual_pct[0])}–{pct(annual_pct[1])}</strong><span>Estimated winter increase from the seasonal component in 2026</span></div>
        <div><strong>{time_label(weekdays["clock"])}</strong><span>Weekday peak of the pooled 2026 fitted profile</span></div>
      </div>
    </section>

    <section id="methods">
      <h2>How the three methods work</h2>
      <p><strong>X-11</strong> uses repeated moving averages to estimate the underlying level, recurrence within a year, and irregular changes. The filters can let the seasonal shape change as newer annual cycles enter the series.</p>
      <p><strong>SEATS</strong>, or <strong>Signal Extraction in ARIMA Time Series</strong>, extracts the seasonal, trend and irregular components implied by a fitted seasonal autoregressive integrated moving average (ARIMA) model. This gives a model-based comparison with X-11. Both methods use the same 12-month period, log transformation, and calendar covariate measuring the share of weekdays in each month. The X-13 software selected the same seasonal ARIMA model, order (1 0 0)(0 1 1), in both fits. The seasonal moving-average coefficient was close to 1. SEATS was run with alternative-model substitution disabled. <a href="https://www.census.gov/data/software/x13as/seasonal-adjustment-questions-answers.html">U.S. Census Bureau seasonal adjustment guide</a>.</p>
      <p><strong>MSTL</strong>, or <strong>Multiple Seasonal-Trend Decomposition Using LOESS</strong>, fits repeated local smooths to estimate several cycles on the same timeline. LOESS is a technique for smoothing nearby data. We used periods of 48 and 336 elapsed half-hours, or one day and one week. We fitted the original MW values with robustness enabled to reduce the influence of unusual readings. The fit uses a regular Coordinated Universal Time (UTC) grid. We converted its times back to the UK clock for the peak comparisons. <a href="https://pkg.robjhyndman.com/forecast/reference/mstl.html">R MSTL documentation</a>.</p>
    </section>

    <section id="winter">
      <h2>How much higher is winter demand?</h2>
      <p>Winter is December–February and is labelled by the year it ends. Summer is June–August in that year. Observed averages and seasonal factors are weighted by the number of readings in each month. To isolate the recurring winter–summer gap, we divide the average winter seasonal factor by the average summer factor, subtract 1, and convert to percent. In GW, we multiply the difference in the two factors by one shared baseline, the fitted trend averaged across those six months.</p>
      <figure aria-describedby="figure-1">
        <a href="monthly-demand.png"><img src="monthly-demand.png" width="1450" height="670" alt="Open the full-size chart of observed monthly power demand and the X-11 and SEATS trend estimates."></a>
        <figcaption>Figure 1. Monthly electricity demand and trend</figcaption>
      </figure>
      <div class="guide" id="figure-1">
        <p><strong>Axes.</strong> The horizontal axis shows calendar months from January 2015 to October 2026. Pale vertical guides mark January. The vertical axis shows average power demand in gigawatts (GW), with pale guides at the tick values.</p>
        <p><strong>Lines.</strong> Solid gray is observed monthly demand. Solid blue is the underlying trend estimated by the X-11 moving-average method. Dashed orange is the underlying trend estimated by SEATS, short for Signal Extraction in ARIMA Time Series. ARIMA means autoregressive integrated moving average.</p>
        <p><strong>What it shows.</strong> The observed line rises in winter and falls in summer around a generally declining trend. The annual average of the X-11 trend fell from {gw(x_2015, 1)} GW in 2015 to {gw(x_2025, 1)} GW in 2025. Both trends tell a similar broad story.</p>
      </div>
      <figure aria-describedby="figure-2">
        <a href="winter-gap.png"><img src="winter-gap.png" width="1450" height="660" alt="Open the full-size chart comparing the observed and model-estimated winter increase by year, in percent and gigawatts."></a>
        <figcaption>Figure 2. Winter–summer difference by year</figcaption>
      </figure>
      <div class="guide" id="figure-2">
        <p><strong>Axes.</strong> Both panels use the year winter ends on the horizontal axis, from 2016 to 2026. The left vertical axis shows how much higher winter demand was relative to summer, in percent. The right vertical axis shows the winter increase in gigawatts (GW). Pale lines mark axis ticks.</p>
        <p><strong>Lines and markers.</strong> Dotted gray with open circles is the observed difference. Solid blue with filled circles shows the seasonal difference estimated with the X-11 moving-average method. Dashed orange with triangles is the estimate from SEATS, or Signal Extraction in ARIMA Time Series. ARIMA means autoregressive integrated moving average. The fitted lines use seasonal factors to hold the underlying power level constant for each winter–summer comparison.</p>
        <p><strong>What it shows.</strong> In the latest comparison, observed winter demand averaged {gw(latest_detail["winter_mean"])} GW and summer demand {gw(latest_detail["summer_mean"])} GW. The recurring winter increase at a shared power level was {gw(annual_gw[0])}–{gw(annual_gw[1])} GW across the two methods. On the left, the X-11 estimate rises gradually and the SEATS estimate stays near 34.5%.</p>
      </div>
      <div class="table-wrap" role="region" tabindex="0" aria-label="Winter and summer comparisons">
        <table>
          <caption>Observed and fitted winter increases over summer</caption>
          <thead><tr><th scope="col">Year winter ends</th><th scope="col">Observed GW</th><th scope="col">Observed %</th>
            <th scope="col">X-11 GW</th><th scope="col">X-11 %</th><th scope="col">SEATS GW</th><th scope="col">SEATS %</th></tr></thead>
          <tbody>{comparison}</tbody>
        </table>
      </div>
      <p>The observed percentage gap increased from {pct(early["raw_pct"])} to {pct(recent["raw_pct"])} across the two three-year groups. X-11's fitted seasonal gap moved from {pct(early["x11.pct"])} to {pct(recent["x11.pct"])}. SEATS moved from {pct(early["seats.pct"])} to {pct(recent["seats.pct"])}. The fitted differences in GW also reflect the decline in underlying demand, because the conversion from a factor to GW uses that period's trend level.</p>
    </section>

    <section id="clock">
      <h2>When demand peaks during the day</h2>
      <figure aria-describedby="figure-3">
        <a href="half-hour-components.png"><img src="half-hour-components.png" width="1450" height="1080" alt="Open the full-size four-panel chart of the observed demand, fit, daily component, weekly component, and remainder for one July week."></a>
        <figcaption>Figure 3. One week of the half-hour decomposition</figcaption>
      </figure>
      <div class="guide" id="figure-3">
        <p><strong>Axes.</strong> The four panels share the UK local timeline from 13 to 19 July 2026. Vertical guides mark local midnight and horizontal guides mark the power ticks. All vertical scales are in gigawatts (GW), with a separate range for each panel. This week illustrates the fit to all 2026 readings.</p>
        <p><strong>Lines and panels.</strong> In the first panel, solid gray is observed demand. Dashed blue is fitted demand from Multiple Seasonal-Trend Decomposition Using LOESS (MSTL), the trend plus the daily and weekly effects. Dotted green is the underlying trend. The second panel's solid blue line is the daily effect over 48 half-hours. The third panel's solid orange line shows the weekly effect over 336 half-hours, including deviations from the daily shape. In the bottom panel solid gray is the remainder, the reading minus its fitted value. The dotted gray zero line in each of the three lower panels marks no contribution or no remaining difference.</p>
        <p><strong>What it shows.</strong> The daily effect repeats the evening rise and overnight fall. The weekly effect dips well below zero on the mornings of Saturday 18 July and Sunday 19 July, lowering fitted demand on those days. The gray gaps from zero in the bottom panel show how much the fitted weekday and weekend patterns leave unexplained.</p>
      </div>
      <figure aria-describedby="figure-4">
        <a href="clock-demand.png"><img src="clock-demand.png" width="1450" height="675" alt="Open the full-size chart of weekday and weekend power profiles for the whole upload, January, and July."></a>
        <figcaption>Figure 4. Fitted weekday and weekend profiles</figcaption>
      </figure>
      <div class="guide" id="figure-4">
        <p><strong>Axes.</strong> All three panels use UK clock hours from midnight through 11:30 p.m. The vertical axis shows fitted power demand in gigawatts (GW). All panels share the same scale. Pale lines mark each axis's labelled ticks.</p>
        <p><strong>Lines and markers.</strong> Solid blue averages fitted demand at each half-hour for Monday–Friday. Dashed orange averages Saturday–Sunday. A blue circle and an orange triangle show the highest half-hour for each group. Fitted demand is the trend plus the daily and weekly effects. The left panel pools all dates from the upload, the center panel shows January, and the right panel shows July.</p>
        <p><strong>What it shows.</strong> Pooling the full span, the fitted weekday peak is around {time_label(weekdays["clock"])} at {gw(weekdays["fit_mw"], 1)} GW and the fitted weekend peak is around {time_label(weekends["clock"])} at {gw(weekends["fit_mw"], 1)} GW. Comparing the daily-plus-weekly components alone, the largest weekday–weekend gap was {gw(gap["max_mw"], 1)} GW at {time_label(gap["clock"])}. The profiles shift later in July than in January.</p>
      </div>
      <div class="table-wrap" role="region" tabindex="0" aria-label="Half-hour peak times">
        <table><caption>Peak of each fitted average profile, UK local time</caption>
          <thead><tr><th scope="col">Span</th><th scope="col">Weekdays</th><th scope="col">Weekends</th></tr></thead>
          <tbody>{profile_rows}</tbody>
        </table>
      </div>
    </section>

    <section id="worked">
      <h2>Worked examples from fitted values</h2>
      <h3>Monthly demand in January 2026</h3>
      <p>X-11 and SEATS return trend and adjusted demand in megawatts. Their seasonal, calendar and irregular factors are unitless, with 1 as neutral. The pure seasonal factor represents the recurring month-of-year effect. The calendar factor represents the weekday mix. Their product gives the combined factor. Divide the observed value by this product to obtain adjusted demand. The adjusted value is also the fitted trend times the irregular factor.</p>
      <div class="table-wrap" role="region" tabindex="0" aria-label="Monthly fitted components">
        <table><caption>January 2026 component values</caption>
          <thead><tr><th scope="col">Component</th><th scope="col">X-11</th><th scope="col">SEATS</th></tr></thead>
          <tbody>{monthly_example}</tbody>
        </table>
      </div>
      <p><strong>X-11.</strong> {n(x["observed_mw"], 2)} ÷ {n(x["combined_factor"], 6)} ≈ {n(x["adjusted_mw"], 2)} MW. Multiplying the trend of {n(x["trend_mw"], 2)} MW by the irregular factor {n(x["irregular_factor"], 6)} gives the same adjusted value. The seasonal factor of {n(x["seasonal_factor"], 6)} implies {pct((float(x["seasonal_factor"]) - 1) * 100)} higher January demand due to the recurring monthly pattern.</p>
      <p><strong>SEATS.</strong> {n(s["observed_mw"], 2)} ÷ {n(s["combined_factor"], 6)} ≈ {n(s["adjusted_mw"], 2)} MW. Multiplying {n(s["trend_mw"], 2)} MW by {n(s["irregular_factor"], 6)} gives the same adjusted value. The pure seasonal factor implies a {pct((float(s["seasonal_factor"]) - 1) * 100)} January increase.</p>
      <h3>Half-hour demand at 7:30 p.m. on 15 July 2026</h3>
      <p>For MSTL, the components add on the original MW scale. The trend is the smoothed underlying level. The daily and weekly terms show the recurring contributions at this half-hour. The remainder is the difference between observed and fitted demand.</p>
      <div class="table-wrap" role="region" tabindex="0" aria-label="Half-hour fitted components">
        <table><caption>15 July 2026 at 7:30 p.m. British Summer Time</caption>
          <thead><tr><th scope="col">Component</th><th scope="col">MW</th></tr></thead>
          <tbody>{half_example}</tbody>
        </table>
      </div>
      <p class="callout">{half_equation} ≈ {n(half["observed_mw"], 2)} MW. R used full precision for both worked examples.</p>
    </section>

    <section id="checks">
      <h2>Verification and diagnostics</h2>
      <div class="table-wrap" role="region" tabindex="0" aria-label="Reconstruction checks">
        <table><caption>Maximum absolute component reconstruction errors in MW</caption>
          <thead><tr><th scope="col">Fit</th><th scope="col">Readings checked</th><th scope="col">Observed</th><th scope="col">Adjusted</th></tr></thead>
          <tbody>{reconstruction}</tbody>
        </table>
      </div>
      <p>Every position passed the 0.000001 MW tolerance. The monthly checks compare observed demand with adjusted demand times the combined factor and adjusted demand with trend times irregular. The half-hour check adds trend, daily effect, weekly effect and remainder to recover the observation. All components were available for the fitted windows.</p>
      <p>Both monthly fits returned a QS seasonal-repetition statistic of {n(xcheck["adjusted_qs"], 2)} on adjusted demand, with a reported p-value of {n(xcheck["adjusted_qs_p"], 2)}. QS looks for positive repetition at seasonal lags. The paired irregular correlation one year apart was {n(xcheck["irregular_lag12"], 2)} in X-11 and {n(scheck["irregular_lag12"], 2)} in SEATS, using {xcheck["lag12_pairs"]} pairs each. X-13 flagged residual calendar-frequency peaks. Those warnings limit confidence in small calendar and seasonal differences. <a href="https://www2.census.gov/software/x-13arima-seats/x13as/unix-linux/documentation/docx13ashtml.pdf">X-13 reference manual</a>.</p>
      <p>MSTL remainder correlations were {n(hcheck["lag48"], 2)} at 48 half-hours (one day, {n(hcheck["pairs48"])} complete pairs) and {n(hcheck["lag336"], 2)} at 336 half-hours (one week, {n(hcheck["pairs336"])} complete pairs). The largest absolute half-hour remainder was {gw(float(hcheck["max_remainder_mw"]))} GW at {escape(hcheck["max_remainder_time"])}. A positive value means observed demand exceeded the fit. GMT is Greenwich Mean Time and BST is British Summer Time.</p>
    </section>

    <section id="limitations">
      <h2>Limitations</h2>
      <ul>
        <li>The analysis estimates recurring patterns in the NESO National Demand measure. It does not estimate how much a particular weather event or change in electricity use caused.</li>
        <li>Late monthly trend and seasonal estimates may revise as more complete months arrive. The 2026 comparison uses the December 2025–February 2026 winter. It contains ten months of 2026 in the monthly fit.</li>
        <li>The 48- and 336-half-hour MSTL periods align in elapsed time. UK clock changes shift the local labels by one hour. Fitted profiles pool holidays with their calendar weekday or weekend and describe the January–November 2026 window.</li>
      </ul>
    </section>

    <section id="conclusion">
      <h2>Conclusion</h2>
      <p class="callout">Observed 2026 winter demand averaged {gw(latest["raw_mw"], 1)} GW above summer. X-11 and SEATS put the recurring increase at {gw(annual_gw[0], 1)}–{gw(annual_gw[1], 1)} GW with the underlying power level held fixed within each fit. Whether the seasonal percentage gap widened depends on the method. X-11 estimates an increase of {n(float(recent["x11.pct"]) - float(early["x11.pct"]), 1)} percentage points. SEATS estimates almost no change.</p>
      <p>Across the full 2026 upload, the fitted weekday and weekend profiles both peak around {time_label(weekdays["clock"])}. The biggest recurring weekday–weekend gap is {gw(gap["max_mw"], 1)} GW at {time_label(gap["clock"])}. The July peaks fall later in the evening than the January peaks.</p>
    </section>

    <section id="references">
      <h2>References and reproducibility</h2>
      <ul>
        <li>National Energy System Operator. <a href="https://www.neso.energy/data-portal/historic-demand-data">Historic Demand Data</a> and <a href="https://www.neso.energy/data-portal/historic-demand-data/historic_demand_data_2026">the 2026 dataset</a>.</li>
        <li>U.S. Census Bureau. <a href="https://www.census.gov/data/software/x13as/seasonal-adjustment-questions-answers.html">Seasonal Adjustment Questions and Answers</a> and <a href="https://www2.census.gov/software/x-13arima-seats/x13as/unix-linux/documentation/docx13ashtml.pdf">X-13 manual</a>.</li>
        <li><a href="https://search.r-project.org/CRAN/refmans/seasonal/html/seas.html">R seasonal documentation</a> and <a href="https://pkg.robjhyndman.com/forecast/reference/mstl.html">R forecast MSTL documentation</a>.</li>
      </ul>
      <p>Use a directory with the 2015–2025 archive CSVs named by year, such as <code>2015.csv</code>. Run from this report folder with R packages <code>seasonal</code>, <code>x13binary</code> and <code>forecast</code> installed. Keep the plots alongside the HTML when moving the report.</p>
      <pre><code>Rscript analyze.R "path/to/archive" "path/to/demanddataupdate_2026.csv"
python build-report.py</code></pre>
      <ul>
        <li><a href="analyze.R">R analysis</a>, <a href="prepare.R">date and data checks</a>, <a href="plots.R">plot code</a> and <a href="build-report.py">HTML builder</a>.</li>
        <li><a href="source-urls.csv">Archive URLs</a>, <a href="downloaded-inputs.csv">input fingerprints and counts</a> and <a href="settings.txt">fit settings, messages and software versions</a>.</li>
        <li><a href="monthly-components.csv">Monthly components</a>, <a href="half-hour-components.csv">half-hour components</a>, <a href="winter-summer-by-year.csv">winter–summer comparisons</a> and <a href="clock-profiles.csv">clock profiles</a>.</li>
        <li><a href="monthly-checks.csv">Monthly diagnostics</a> and <a href="half-hour-checks.csv">half-hour diagnostics</a>.</li>
      </ul>
    </section>
  </main>
</body>
</html>
"""

(ROOT / "report.html").write_text(page, encoding="utf-8")
