args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2L) stop("Usage: Rscript analyze.R <archive directory> <2026 CSV>")
source("prepare.R")
input <- prepare_demand(args[1], args[2])
m <- input$monthly
h <- input$recent
suppressPackageStartupMessages(library(seasonal))
seasonal::checkX13(fail = TRUE, fullcheck = FALSE)

sales <- ts(m$observed_mw, start = c(2015, 1), frequency = 12)
# Monthly readings are means. Use the share of weekdays rather than a count.
calendar_days <- seq(as.Date("2012-01-01"), as.Date("2029-12-31"), by = "day")
is_weekday <- !(as.POSIXlt(calendar_days)$wday %in% c(0, 6))
weekday_share <- tapply(is_weekday, format(calendar_days, "%Y-%m"), mean)
calendar <- ts(cbind(weekday_share = (as.numeric(weekday_share) - 5 / 7) * 100),
               start = c(2012, 1), frequency = 12)
x11 <- seas(
  sales, transform.function = "log", xreg = calendar, regression.usertype = "td",
  regression.aictest = NULL, x11 = "", x11.mode = "mult", out = TRUE,
  x11.save = c("d10", "d11", "d12", "d13", "d16"), na.action = na.fail
)
seats <- seas(
  sales, transform.function = "log", xreg = calendar, regression.usertype = "td",
  regression.aictest = NULL, seats.noadmiss = "no", out = TRUE,
  seats.save = c("s10", "s11", "s12", "s13", "s16"), na.action = na.fail
)
stopifnot(isTRUE(all.equal(coef(x11), coef(seats), tolerance = 1e-10)),
          identical(x11$model$arima$model, seats$model$arima$model),
          identical(x11$model$arima$model, "(1 0 0)(0 1 1)"))
tolerance <- 1e-6

compare_lag <- function(x, lag) {
  rows <- seq_len(length(x) - lag)
  cor(x[rows], x[rows + lag])
}
read_monthly <- function(fit, tables, method) {
  parts <- series(fit, tables, reeval = FALSE)
  stopifnot(identical(tsp(parts), tsp(sales)), nrow(parts) == nrow(m),
            all(is.finite(parts) & parts > 0), length(fit$err$error) == 0L)
  values <- unclass(as.matrix(parts))
  out <- data.frame(
    month = m$month, method, observed_mw = m$observed_mw, observed_status = "observed_mean",
    component_status = "estimated", seasonal_factor = as.numeric(values[, 1]),
    adjusted_mw = as.numeric(values[, 2]), trend_mw = as.numeric(values[, 3]),
    irregular_factor = as.numeric(values[, 4]), combined_factor = as.numeric(values[, 5]),
    calendar_factor = as.numeric(values[, 5] / values[, 1])
  )
  stopifnot(max(abs(out$observed_mw - out$adjusted_mw * out$combined_factor)) <= tolerance,
            max(abs(out$adjusted_mw - out$trend_mw * out$irregular_factor)) <= tolerance)
  out
}
x <- read_monthly(x11, c("d10", "d11", "d12", "d13", "d16"), "X-11")
s <- read_monthly(seats, c("s10", "s11", "s12", "s13", "s16"), "SEATS")
stopifnot(max(abs(x$calendar_factor - s$calendar_factor)) < 1e-6)
monthly_checks <- function(series, fit) {
  tests <- qs(fit)
  data.frame(
    method = series$method[1], positions = nrow(series),
    raw_error = max(abs(series$observed_mw - series$adjusted_mw * series$combined_factor)),
    adjusted_error = max(abs(series$adjusted_mw - series$trend_mw * series$irregular_factor)),
    tolerance_mw = tolerance, raw_qs = tests["qsori", "qs"],
    adjusted_qs = tests["qssadj", "qs"], adjusted_qs_p = tests["qssadj", "p-val"],
    irregular_lag12 = compare_lag(series$irregular_factor, 12L), lag12_pairs = nrow(series) - 12L,
    warnings = paste(unlist(fit$err$warning), collapse = " | "),
    notes = paste(unlist(fit$err$note), collapse = " | ")
  )
}
checks <- rbind(monthly_checks(x, x11), monthly_checks(s, seats))

full <- input$full
rows_per_month <- table(format(full$day, "%Y-%m"))
weights <- as.numeric(rows_per_month[format(m$month, "%Y-%m")])
stopifnot(!anyNA(weights))
seasons <- lapply(2016:2026, function(year) {
  winter <- m$month >= as.Date(sprintf("%d-12-01", year - 1L)) &
    m$month < as.Date(sprintf("%d-03-01", year))
  summer <- m$month >= as.Date(sprintf("%d-06-01", year)) &
    m$month < as.Date(sprintf("%d-09-01", year))
  average <- function(values, select) weighted.mean(values[select], weights[select])
  seasonal <- function(series) {
    winter_factor <- average(series$seasonal_factor, winter)
    summer_factor <- average(series$seasonal_factor, summer)
    reference <- average(series$trend_mw, winter | summer)
    c(pct = 100 * (winter_factor / summer_factor - 1),
      mw = reference * (winter_factor - summer_factor),
      winter_factor = winter_factor, summer_factor = summer_factor, reference_mw = reference)
  }
  winter_mean <- average(m$observed_mw, winter)
  summer_mean <- average(m$observed_mw, summer)
  data.frame(
    year, winter_mean, summer_mean, raw_mw = winter_mean - summer_mean,
    raw_pct = (winter_mean / summer_mean - 1) * 100,
    x11 = as.list(seasonal(x)), seats = as.list(seasonal(s))
  )
})
seasons <- do.call(rbind, seasons)
overall <- do.call(rbind, lapply(list(2016:2018, 2024:2026, 2026), function(years) {
  chosen <- seasons[seasons$year %in% years, ]
  data.frame(first = min(years), last = max(years),
             as.list(colMeans(chosen[, c("raw_mw", "raw_pct", "x11.pct", "x11.mw", "seats.pct", "seats.mw")])))
}))

mat <- forecast::mstl(forecast::msts(h$demand_mw, c(48, 336)),
                      s.window = c(11, 15), robust = TRUE)
stopifnot(identical(colnames(mat), c("Data", "Trend", "Seasonal48", "Seasonal336", "Remainder")),
          all(mat[, "Data"] == h$demand_mw), all(is.finite(mat)))
zone <- "Europe/London"
weekend <- as.POSIXlt(h$time, tz = zone)$wday %in% c(0, 6)
clock <- format(h$time, "%H:%M", tz = zone)
a <- data.frame(
  utc = format(h$time, "%Y-%m-%dT%H:%M:%SZ", tz = "UTC"),
  local_time = format(h$time, "%Y-%m-%d %H:%M %Z", tz = zone),
  observed_mw = h$demand_mw, observed_status = "observed", component_status = "estimated",
  trend_mw = as.numeric(mat[, "Trend"]), daily_mw = as.numeric(mat[, "Seasonal48"]),
  weekly_mw = as.numeric(mat[, "Seasonal336"]), remainder_mw = as.numeric(mat[, "Remainder"])
)
a$fit_mw <- a$trend_mw + a$daily_mw + a$weekly_mw
a$seasonal_mw <- a$daily_mw + a$weekly_mw
half_error <- max(abs(a$observed_mw - a$fit_mw - a$remainder_mw))
stopifnot(half_error < tolerance)
half_checks <- data.frame(
  positions = nrow(a), error = half_error, tolerance_mw = tolerance,
  lag48 = compare_lag(a$remainder_mw, 48L), pairs48 = nrow(a) - 48L,
  lag336 = compare_lag(a$remainder_mw, 336L), pairs336 = nrow(a) - 336L,
  max_remainder_mw = a$remainder_mw[which.max(abs(a$remainder_mw))],
  max_remainder_time = a$local_time[which.max(abs(a$remainder_mw))]
)
get_profile <- function(label, select) {
  result <- aggregate(a[select, c("observed_mw", "fit_mw", "seasonal_mw")],
                      list(clock = clock[select], weekend = weekend[select]), mean)
  result$span <- label
  result
}
profiles <- rbind(
  get_profile("All", rep(TRUE, nrow(h))),
  get_profile("January", format(h$day, "%m") == "01"),
  get_profile("July", format(h$day, "%m") == "07")
)
peaks <- do.call(rbind, lapply(split(profiles, list(profiles$span, profiles$weekend)), function(p) {
  j <- which.max(p$fit_mw)
  k <- which.max(p$observed_mw)
  data.frame(p[j, c("span", "weekend", "clock", "fit_mw")],
             observed_peak_clock = p$clock[k], observed_peak_mw = p$observed_mw[k])
}))
all_p <- profiles[profiles$span == "All", ]
gap <- all_p[!all_p$weekend, "seasonal_mw"] - all_p[all_p$weekend, "seasonal_mw"]
weekday_gap <- data.frame(clock = all_p[!all_p$weekend, "clock"][which.max(gap)],
                          max_mw = max(gap), average_mw = mean(gap))
monthly_example <- rbind(x[x$month == as.Date("2026-01-01"), ],
                         s[s$month == as.Date("2026-01-01"), ])
half_example <- a[a$local_time == "2026-07-15 19:30 BST", ]
stopifnot(nrow(half_example) == 1)

outputs <- list(
  "monthly-components" = rbind(x, s), "half-hour-components" = a,
  "winter-summer-by-year" = seasons, "winter-summary" = overall,
  "monthly-checks" = checks, "half-hour-checks" = half_checks,
  "clock-profiles" = profiles, "peak-times" = peaks, "weekday-gap" = weekday_gap,
  "monthly-example" = monthly_example, "half-hour-example" = half_example,
  "downloaded-inputs" = input$provenance
)
for (file in names(outputs)) write.csv(outputs[[file]], paste0(file, ".csv"), row.names = FALSE)
archive_manifest <- file.path(args[1], "sources.csv")
if (file.exists(archive_manifest)) file.copy(archive_manifest, "source-urls.csv", overwrite = TRUE)
audit <- c(
  "Monthly calendar covariate: percentage points of weekday share from 5/7.",
  "No moving-holiday variable was supplied. X-13 outlier detection was enabled.",
  "MSTL: 48 and 336 half-hours, robust STL, windows 11 and 15, no transform.",
  "All 2026 readings used for MSTL. November 2026 excluded from monthly input only.",
  "X-11 coefficient estimates:", capture.output(print(coef(x11))),
  "SEATS coefficient estimates:", capture.output(print(coef(seats))),
  "X-11 specification:", capture.output(print(x11$spc)),
  "X-11 selected model:", capture.output(print(x11$model)),
  "X-11 fitting messages:", capture.output(print(x11$err)),
  "SEATS specification:", capture.output(print(seats$spc)),
  "SEATS selected model:", capture.output(print(seats$model)),
  "SEATS fitting messages:", capture.output(print(seats$err)),
  paste("X-13 build", udg(x11, "build")),
  paste("forecast package", packageVersion("forecast")),
  paste("seasonal package", packageVersion("seasonal")),
  paste("x13binary package", packageVersion("x13binary")),
  capture.output(sessionInfo())
)
writeLines(audit, "settings.txt")

source("plots.R")
print(overall)
print(peaks, row.names = FALSE)
print(weekday_gap)
print(checks[, setdiff(names(checks), c("warnings", "notes"))], row.names = FALSE)
print(half_checks)
print(monthly_example, row.names = FALSE)
print(half_example, row.names = FALSE)
