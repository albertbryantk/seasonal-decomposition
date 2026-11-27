args <- commandArgs(trailingOnly = TRUE)
input <- if (length(args)) args[1] else "MRTSSM7225USN.csv"
original <- read.csv(input)
dates <- as.Date(original$observation_date, "%m/%d/%Y")
y <- original$MRTSSM7225USN
stopifnot(
  length(y) == 61L, is.numeric(y), all(is.finite(y)), all(y > 0), !anyNA(dates),
  !anyDuplicated(dates),
  identical(dates, seq(as.Date("2021-09-01"), as.Date("2026-09-01"), by = "month"))
)
x <- ts(y, start = c(2021, 9), frequency = 12)
methods <- c("Classical additive", "Classical multiplicative", "STL", "STR")
add <- decompose(x, type = "additive")
mul <- decompose(x, type = "multiplicative")
stl_fit <- stl(x, s.window = 7, robust = FALSE)
str_warnings <- character()
str_fit <- withCallingHandlers(
  stR::AutoSTR(x, robust = FALSE),
  warning = function(w) { str_warnings <<- c(str_warnings, conditionMessage(w)) }
)
term_names <- vapply(str_fit$input$predictors, function(p) p$name, character(1))
stopifnot(identical(term_names, c("Trend", "Seasonality 12")))
str_parts <- vapply(str_fit$output$predictors, function(p) as.numeric(p$data), numeric(length(y)))
values <- list(
  list(trend = as.numeric(add$trend), seasonal = as.numeric(add$seasonal),
       remainder = as.numeric(add$random), factor = FALSE),
  list(trend = as.numeric(mul$trend), seasonal = as.numeric(mul$seasonal),
       remainder = as.numeric(mul$random), factor = TRUE),
  list(trend = as.numeric(stl_fit$time.series[, "trend"]),
       seasonal = as.numeric(stl_fit$time.series[, "seasonal"]),
       remainder = as.numeric(stl_fit$time.series[, "remainder"]), factor = FALSE),
  list(trend = str_parts[, 1], seasonal = str_parts[, 2],
       remainder = as.numeric(str_fit$output$random$data), factor = FALSE)
)
components <- do.call(rbind, Map(function(parts, name) {
  trend <- parts$trend
  seasonal <- parts$seasonal
  remainder <- parts$remainder
  if (parts$factor) {
    adjusted <- y / seasonal
    fitted <- trend * seasonal
    reconstructed <- fitted * remainder
    seasonal_mw <- trend * (seasonal - 1)
    remainder_dollars <- y - fitted
  } else {
    adjusted <- y - seasonal
    fitted <- trend + seasonal
    reconstructed <- fitted + remainder
    seasonal_mw <- seasonal
    remainder_dollars <- remainder
  }
  keep <- is.finite(reconstructed)
  error <- max(abs(y[keep] - reconstructed[keep]))
  stopifnot(error < 1e-6, sum(keep) %in% c(49, 61), all(is.finite(adjusted)))
  data.frame(
    date = dates, method = name, observed_million = y, observation_status = "observed",
    component_status = ifelse(keep, "estimated", "trend_and_remainder_unavailable"),
    trend_million = trend, seasonal_native = seasonal, remainder_native = remainder,
    native_scale = if (parts$factor) "unitless_factors" else "million_USD",
    seasonal_million = seasonal_mw, remainder_million = remainder_dollars,
    fitted_million = fitted, adjusted_million = adjusted,
    reconstruction_error = ifelse(keep, abs(y - reconstructed), NA_real_)
  )
}, values, methods))
common <- dates >= as.Date("2022-03-01") & dates <= as.Date("2026-03-01")
reference <- mean(values[[1]]$trend[common])
profile_span <- dates >= as.Date("2022-01-01") & dates <= as.Date("2025-12-01")
phase <- as.integer(format(dates, "%m"))
profiles <- do.call(rbind, lapply(methods, function(method) {
  parts <- components[components$method == method, ]
  seasonal <- if (method == "Classical multiplicative") {
    reference * (parts$seasonal_native - 1)
  } else {
    parts$seasonal_native
  }
  data.frame(
    method, month_number = 1:12, month_name = month.abb,
    contribution_million = as.numeric(tapply(seasonal[profile_span], phase[profile_span], mean)),
    multiplicative_factor = if (method == "Classical multiplicative") {
      as.numeric(tapply(parts$seasonal_native[profile_span], phase[profile_span], mean))
    } else NA_real_
  )
}))
cor_pairs <- function(z, lag) {
  i <- seq_len(length(z) - lag)
  keep <- is.finite(z[i]) & is.finite(z[i + lag])
  c(correlation = cor(z[i][keep], z[i + lag][keep]), pairs = sum(keep))
}
summary <- do.call(rbind, lapply(methods, function(method) {
  p <- profiles[profiles$method == method, ]
  c <- components[components$method == method, ]
  errors <- c$remainder_million[common]
  stopifnot(length(errors) == 49, all(is.finite(errors)))
  lag12 <- cor_pairs(c$remainder_million[common], 12)
  lag1 <- cor_pairs(c$remainder_million[common], 1)
  i <- which.max(abs(errors))
  data.frame(
    method, highest_month = p$month_name[which.max(p$contribution_million)],
    highest_million = max(p$contribution_million),
    lowest_month = p$month_name[which.min(p$contribution_million)],
    lowest_million = min(p$contribution_million), swing_million = diff(range(p$contribution_million)),
    reference_million = reference, common_rmse_million = sqrt(mean(errors^2)),
    lag1_correlation = lag1[1], lag1_pairs = lag1[2],
    lag12_correlation = lag12[1], lag12_pairs = lag12[2],
    complete_components = sum(c$component_status == "estimated"),
    missing_components = sum(c$component_status != "estimated"),
    max_reconstruction_error = max(c$reconstruction_error, na.rm = TRUE), tolerance_million = 1e-6,
    trend_start_million = c$trend_million[which(common)[1]],
    trend_end_million = c$trend_million[tail(which(common), 1)],
    trend_increase_pct = 100 * (c$trend_million[tail(which(common), 1)] /
                                 c$trend_million[which(common)[1]] - 1),
    largest_common_remainder_date = as.character(dates[common][i]),
    largest_common_remainder_million = errors[i]
  )
}))
write.csv(components, "components.csv", row.names = FALSE, na = "")
write.csv(profiles, "seasonal-profiles.csv", row.names = FALSE, na = "")
write.csv(summary, "method-summary.csv", row.names = FALSE)
full_cycle <- window(x, end = c(2026, 8))
add60 <- decompose(full_cycle, type = "additive")
mul60 <- decompose(full_cycle, type = "multiplicative")
common_add <- as.numeric(add$seasonal)[1:60]
common_mul <- as.numeric(mul$seasonal)[1:60]
sensitivity <- data.frame(
  method = methods[1:2], main_months = 61, check_months = 60,
  max_seasonal_difference_million = c(
    max(abs(common_add - as.numeric(add60$seasonal))),
    reference * max(abs(common_mul - as.numeric(mul60$seasonal)))),
  max_factor_difference = c(NA_real_, max(abs(common_mul - as.numeric(mul60$seasonal))))
)
write.csv(sensitivity, "whole-cycle-check.csv", row.names = FALSE, na = "")
example <- components[components$date == as.Date("2024-05-01"), ]
write.csv(example, "worked-example.csv", row.names = FALSE)
writeLines(c(
  "Created for the four-method restaurant-sales comparison.",
  paste("Input MD5", tools::md5sum(input)[[1]]),
  "Period = 12 months. No imputation, exclusions, deflation or calendar regressors.",
  "All methods fitted the same 61 observations, September 2021–September 2026.",
  "Classical centered moving average weights:",
  capture.output(print(c(.5, rep(1, 11), .5) / 12)),
  "STL actual windows:", capture.output(print(stl_fit$win)),
  "STL robust = FALSE, s.window = 7, default polynomial degrees and iterations.",
  "STR defaults for monthly ts, robust = FALSE, confidence = NULL.",
  paste("STR nFold =", str_fit$nFold, "gapCV =", str_fit$gapCV),
  "STR selected smoothing values:", capture.output(dput(str_fit$input$lambdas)),
  paste("STR internal cross-validation mean squared error", str_fit$optim.CV.MSE),
  "STR warnings:", if (length(str_warnings)) str_warnings else "None.",
  paste("stR version", packageVersion("stR")), capture.output(sessionInfo())
), "settings.txt")
source("plots.R")
print(summary, row.names = FALSE)
print(example, row.names = FALSE)
print(profiles[profiles$method == "Classical multiplicative", ], row.names = FALSE)
