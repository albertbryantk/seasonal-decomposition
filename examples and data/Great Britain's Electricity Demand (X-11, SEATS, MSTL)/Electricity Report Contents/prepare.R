read_demand <- function(path, year) {
  input <- read.csv(path, na.strings = c("", "NA", "N/A"))
  original_dates <- input$SETTLEMENT_DATE
  formats <- c("^\\d{4}-\\d{2}-\\d{2}$" = "%Y-%m-%d",
               "^\\d{2}/\\d{2}/\\d{4}$" = "%d/%m/%Y",
               "^\\d{2}-[A-Za-z]{3}-\\d{4}$" = "%d-%b-%Y",
               "^\\d{2}-[A-Za-z]{3}-\\d{2}$" = "%d-%b-%y")
  day <- rep(as.Date(NA), length(original_dates))
  for (pattern in names(formats)) {
    matches <- grepl(pattern, original_dates)
    day[matches] <- as.Date(original_dates[matches], formats[[pattern]])
  }
  stopifnot(!anyNA(day), all(format(day, "%Y") == year),
            is.numeric(input$ND), all(is.finite(input$ND) & input$ND > 0))
  if ("FORECAST_ACTUAL_INDICATOR" %in% names(input)) {
    stopifnot(all(input$FORECAST_ACTUAL_INDICATOR == "A"))
  }
  zone <- "Europe/London"
  first <- as.Date(sprintf("%d-01-01", year))
  last <- if (year == 2026L) as.Date("2026-11-04") else as.Date(sprintf("%d-12-31", year))
  end_time <- as.POSIXct(paste(last + 1, "00:00:00"), tz = zone)
  start_time <- as.POSIXct(paste(first, "00:00:00"), tz = zone)
  local_midnight <- as.POSIXct(paste(day, "00:00:00"), tz = zone)
  time <- local_midnight + 1800 * (input$SETTLEMENT_PERIOD - 1)
  result <- data.frame(day, time, period = input$SETTLEMENT_PERIOD, demand_mw = input$ND)
  result <- result[order(time), ]
  # Checking both the elapsed grid and local dates catches wrong settlement labels.
  stopifnot(identical(as.numeric(result$time),
                      as.numeric(seq(start_time, end_time - 1800, by = 1800))),
            identical(as.Date(result$time, tz = zone), result$day))
  result
}

prepare_demand <- function(archive, upload) {
  original_locale <- Sys.getlocale("LC_TIME")
  on.exit(Sys.setlocale("LC_TIME", original_locale))
  Sys.setlocale("LC_TIME", "C")
  paths <- c(file.path(archive, paste0(2015:2025, ".csv")), upload)
  yearly <- Map(read_demand, paths, 2015:2026)
  full <- do.call(rbind, yearly)
  stopifnot(all(diff(as.numeric(full$time)) == 1800))
  # November 2026 has four days, so exclude that month from monthly comparisons.
  complete <- full$day < as.Date("2026-11-01")
  monthly <- aggregate(full$demand_mw[complete],
                       list(month = paste0(format(full$day[complete], "%Y-%m"), "-01")), mean)
  names(monthly)[2] <- "observed_mw"
  monthly$month <- as.Date(monthly$month)
  stopifnot(identical(monthly$month, seq(as.Date("2015-01-01"),
                                       as.Date("2026-10-01"), by = "month")))
  list(monthly = monthly, recent = yearly[[12]], full = full,
       provenance = data.frame(year = 2015:2026, file = basename(paths),
                               md5 = unname(tools::md5sum(paths)),
                               rows = vapply(yearly, nrow, integer(1))))
}
