# Seasonal Decomposition Report Specification

Write for a reader who is new to time series. Use English by default and follow the user's language preference. Explain the results in ordinary language, then give the detail needed to check them. Calculate and verify reported values in R. Use [methods.md](methods.md) for definitions, computations, and interpretation.

## Report format and design

Save and deliver `report.html` (the main reading copy), `report.md` (plain Markdown), and `report.qmd` (editable Quarto source) together in the same output folder. Generate all three even when the user does not specify a format. This also applies to a completed descriptive report. Link each file in the final response.

Write one report body using headings, Markdown tables, and standard links and images. For `report.md`, put the title in a heading above the body. For `report.qmd`, put the title and `format: html` in Quarto YAML front matter above the same body. Use a table of contents when the length warrants it. Both source files must contain the full verified report, including every plot explanation and worked example. Preserve relative paths to the same figures, results, and R code.

Use `quarto render report.qmd --to html` when Quarto is available. If Quarto is unavailable or rendering fails, build the styled HTML from the same verified content with an available renderer or directly in HTML. Deliver the Markdown and Quarto files either way. The Quarto source should render from the saved results and figures. Include any code or asset needed to render, and link the separate R script and rerun instructions for regenerating the analysis. If a format genuinely cannot be produced or verified, identify it and explain the specific issue in the final response.

Give the HTML a clear title, readable typography, consistent spacing, and a layout that works on narrow screens. Make tables and plots legible, include plot alt text, and use a linked contents list when the report is long enough to need one. Embed figures or deliver their assets with working relative paths. Open the final HTML and check that its figures, explanations, and local links work.

## 1 Dataset introduction

State the question and introduce the dataset before interpreting it. Explain where the data came from, what each observation represents, what was measured and in what units, and which group or entity was analyzed. Introduce the time index, date range, observation interval, and calendar or time-zone convention where relevant. Name the target and any calendar or explanatory variables used and define abbreviations. If the source or a variable's meaning is unknown, say so. For a general analysis, state what the report will examine.

## 2 Data quality and preparation

Distinguish missing measurements, missing periods, duplicates, invalid values, and genuine zeros. Explain how any gaps, duplicates, exclusions, aggregation, or transformations were handled and why. Give affected counts and dates or ranges where useful. Distinguish observed values from values filled by code or by the selected method, and from component estimates that are unavailable at the edges. State the actual fitting span and explain any difference between the observed, prepared, analyzed, and displayed intervals.

## 3 What the chosen method does and why it fits

Give each method used its own short explanation. Spell out acronyms on first use and explain the method's general purpose. Describe how it usually separates underlying movement, recurring effects, and unexplained variation. Explain the particular features of this data and question that support the choice, such as the observation frequency, repeated cycles, stable or changing patterns, proportional swings, calendar effects, or several seasonal periods. State each period in observations and calendar terms. State the actual settings, transformations, separate effects, and any important compromises. If comparing methods, explain why each was included and use a shared period and comparable scales when possible.

## 4 How the components were calculated

For each fitted method, explain what its trend or trend-cycle, each seasonal component, and remainder or irregular component mean in this report. Describe how the method estimates them and how they combine. Explain any separately modeled effects and how the seasonally adjusted series was obtained when reported. Identify the reference series and scale before showing an equation. Define each symbol and give its units or explain when it is a factor.

Use an actual date or seasonal phase and values from the fitted R outputs to work through the calculation. Show the inputs, the arithmetic, the resulting value, and its plain-language meaning. For multiple seasonal periods, show all seasonal terms in the selected row and label each one. Where the fitted algorithm is too complex for a hand calculation, explain the estimation steps in words and show a smaller calculation that readers can verify, such as how extracted components combine on the documented scale. State if displayed rounding affects the arithmetic. If no fit was possible, explain why and report the descriptive findings available.

**Illustration for classical multiplicative decomposition.** The trend is a moving-average estimate of the underlying level. Seasonal factors come from averaging observation-to-trend ratios for each phase and normalizing the factors around 1. The remainder is the observation divided by the trend times the seasonal factor.

For example, suppose a month's observed value is 132 units, its trend is 100 units, and its seasonal factor is 1.20. The trend times the seasonal factor gives a fitted baseline of 120 units. This month is estimated to have a recurring uplift of 20% relative to trend. The remainder factor is 132 / 120 = 1.10, so the observation is 10% above that fitted baseline. Multiplying 100 × 1.20 × 1.10 reconstructs the observed 132 units. Dividing 132 by 1.20 gives a seasonally adjusted observation of 110 units. The seasonal and remainder factors are unitless. These numbers are illustrative. Use verified values from the analyzed dataset in the report.

## 5 Findings and figures

Organize findings around the question. For a general report, summarize the underlying direction, the clearest recurring highs and lows, their size where supported, and notable unusual periods. Use no more than three distinct methods and keep comparisons brief. Use the original time-series plot and a plot of the fitted components when a decomposition was run. Add other figures only when they help answer the question. Explain every figure in full even in a short general report.

**Place a full explanation immediately after every figure.** Apply the same rule to every panel in a multi-panel figure and to diagnostic figures. A caption or legend can help the reader navigate, and the explanation below the figure should guide them through it. Use the following order under each figure.

1. **Purpose and axes.** Say what the plot helps the reader see. Explain what the horizontal and vertical axes measure, their units or factors, the time or phase range shown, and any transformations or scale differences. Explain clock labels or lag units where relevant. Distinguish the displayed interval from the fitting interval when they differ.
2. **Variables and visual elements.** Name what each line, color, marker, bar, shaded area, or reference line represents when present. Explain line styles, bands, gaps, and panels and what the reader should infer from them. Define every variable and abbreviation used in the figure, including labels used in earlier plots. Use names and line styles or symbols as well as color when several series are shown.
3. **What the data show.** Identify the relevant pattern and point to specific dates, phases, changes, or values verified in R. Explain what that pattern means for the question and mention any important uncertainty or feature that may change the interpretation. When there is little clear evidence of a pattern, say so directly.

For example, after an autocorrelation function plot, define ACF as the autocorrelation function and explain that it shows how similar remainder values are at different separations. Explain what one lag means in calendar time, what each bar measures, and how to read any displayed reference bands. Discuss the bars at relevant seasonal lags and what they suggest about remaining repetition, given data gaps and available pairs. In an actual report, use the plot's own marks, scales, and values.

## 6 Diagnostic findings

- State the reconstruction relationship actually checked and the scale and series it applies to. Report maximum error, tolerance, the number of checked positions, and unavailable positions when applicable. Explain any mismatch, output rounding, or pre-adjustment. Reconstruction checks arithmetic and alignment. Use the plots and diagnostics to judge whether the method captured the relevant patterns.
- Describe remaining temporal structure and unusual observations. Explain the lag units, how missing or filled positions were treated, and the number of valid pairs when reporting selected-lag correlations. Distinguish X-13 model residuals from the final irregular component. Explain relevant fitting warnings, sensitivity findings, or model substitutions and how they affect the answer.

## 7 Limitations

Keep a separate limitations section. State which limitations matter here, such as short history, missing phases, time-zone or calendar conventions, preparation choices, fixed seasonal assumptions, transformations, edge gaps, revision of recent estimates, or overlap between seasonal components. Explain the practical effect on what readers can conclude. Treat possible explanations of patterns as hypotheses. Keep conclusions within the historical data and analysis scope.

## 8 Conclusion and direct answer

Keep a separate section headed **Conclusion** in the report. Answer the original question in the first sentence, then summarize the strongest supporting findings, with dates and magnitudes where useful. For a general overview, state the underlying direction and the most important recurring pattern or explain that the available data do not support a clear one. Include any caveat that materially qualifies the answer. Use everyday language and avoid introducing new results in this section.

## 9 Reproducibility and references

Include a separate **References** list in the report. Cite the dataset source when known and the methods and software documentation actually used. Cite contextual sources where they support an interpretation. Supply the report and figures, timestamped numerical outputs with status flags, actual settings and diagnostics, and the R code and environment information needed to repeat the analysis. Include data-location and rerun instructions. Distinguish completed calculations from anything that still awaits execution.

## Final report check

- Confirm that the dataset introduction, method purpose and suitability, worked calculations, diagnostics, limitations, conclusion, and references are present as applicable. Check that the conclusion answers the user's question directly.
- Confirm that each figure is immediately followed by its own explanation. Check every axis, visual element, panel, variable, and abbreviation against the actual figure. Verify dates, units, factors, percentages, and findings against the R outputs.
- Open the HTML and inspect both source files. Verify that all three are present and agree on the results, figures, explanations, limitations, and conclusion. Check that all relative links resolve from the output folder and that the references support the claims.
