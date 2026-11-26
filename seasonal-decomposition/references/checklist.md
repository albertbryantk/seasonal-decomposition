# Seasonal Decomposition Readiness Checklist

Use this checklist before fitting. Calculate numerical checks in R and record the findings that affect preparation, method choice, or interpretation. Use information already supplied, and ask one focused question at a time when an unresolved choice materially affects the analysis.

## 1 Identify the series and question

- Establish the numeric target, units, group or entity, date range, and time index. The index may come from a timestamp column, documented timing metadata, or an R time-series object. Check that the meaning of the measurement is consistent over time.
- Use a clear question already supplied. If the goal is open, finish the initial data check and use [decision-tree.md](decision-tree.md) to offer dataset-specific questions, a general report, and a free-text option. Analyze each selected series separately unless a meaningful aggregation is defined.
- Keep the analysis focused on historical patterns. Future forecasts, forecast accuracy, and causal effects are outside scope. Internal modeling and series extensions used by X-13 are part of decomposition.

## 2 Check time and measurement quality

- Verify that dates or timestamps parse correctly. Check ordering, the intended observation interval, duplicate timestamps, and missing periods. Apply the relevant calendar, time zone, and daylight-saving convention. Monthly or quarterly observations can be regular on a calendar even when their durations differ.
- Distinguish absent periods from missing values at recorded times. Check for nonnumeric values, infinities, zeros, negative values, unusual observations, and documented changes in units or collection. Investigate unusual values before changing them.

## 3 Prepare the series

- Use documented missing-value handling when appropriate. Keep missing values distinct from genuine zeros. Resolve duplicates or irregular sampling according to what the measurement represents. For example, sales totals may be summed over a period, while a temperature series may call for an average.
- Ask for agreement when a consequential preparation choice is unresolved, such as combining entities or treating absent records as zero. Preserve the original series and index. Record the changes, affected dates and counts, and any shifts in date range or coverage. Keep adjusted, imputed, or excluded observations identifiable.

## 4 Check seasonal evidence and coverage

- Express each candidate period in observations and practical terms, such as 7 observations for a weekly cycle in daily data. Use domain context and plots across cycles to assess whether the pattern recurs. Check for multiple periods and whether the seasonal shape or size changes over time.
- Record how many cycles the grid spans, how many are fully observed, and whether some seasonal phases have limited coverage. Mark partial cycles and concentrated gaps. Filled positions count toward the grid span but do not add observed seasonal evidence. A method can meet its minimum input length even when the evidence is weak.

## 5 Check the chosen method

Use [decision-tree.md](decision-tree.md) to recommend eligible methods and record the user's choice or delegation. Honor a suitable method already chosen. Fit only after the objective, method, and necessary preparation are settled. For a general report, limit the plan to at most three distinct methods. Use [methods.md](methods.md) for fitting details.

| Method | Checks before fitting |
| --- | --- |
| Classical additive | One integer period greater than 1, at least two complete cycles on a regular grid, finite prepared values, and a stable pattern with roughly constant swings in the original units. |
| Classical multiplicative | Same grid and history requirements as classical additive. Require strictly positive values and check whether the swings are roughly proportional to the level. |
| STL | One integer period greater than 1, more than two cycles, and complete finite input for standard `stats::stl()`. Choose fixed or changing seasonality and decide whether robust fitting is suitable. |
| MSTL | Several meaningful periods on the same grid. Check the installed implementation's support for each period. For `forecast::mstl()`, the series must span more than two cycles of each intended period for it to be retained. Account for any native interpolation. |
| X-11 | Monthly or quarterly observations with the correct calendar start and a working X-13 executable. Check the available history and selected mode, transformation, and any calendar or outlier adjustments. |
| SEATS | Monthly, every two months, quarterly, or twice-yearly observations through X-13. Check the calendar start, executable, and whether the history supports the intended seasonal ARIMA model. Check decomposition warnings and any model substitution after fitting. |
| STR | Check that the history supports each seasonal structure and that any predictors align with the target. Use suitable `ts` or `msts` inputs for `AutoSTR()`, or define an explicit STR specification for complex calendar structures or predictors. |

Check R and the selected method's dependencies before fitting. Verify transformation domains and the exact input requirements of the installed implementation. Record automatic choices, warnings, and retained components after fitting as described in [methods.md](methods.md).

## 6 Record readiness and next action

| Outcome | Action |
| --- | --- |
| Ready | Proceed and record the series, preparation, seasonal periods, method, and rationale. |
| Usable with limitations | State what the data can support, explain the limitation, and proceed when necessary choices are settled. |
| Clarification required | Ask a focused question before the affected step, such as which target column to use or what a missing period represents. |
| Requirements unmet | Explain the specific issue. Consider suitable preparation, additional history, or another supported method. If there is no defensible seasonal pattern to analyze, report the descriptive findings the data support. |

Keep a short record of the data source, what each observation and variable means, units, date and clock conventions, settings, assumptions, and outstanding decisions. Use it to introduce the dataset and explain why the selected method fits. Use [report-spec.md](report-spec.md) for the report structure and final checks.
