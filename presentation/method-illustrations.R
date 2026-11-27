# Recreate the teaching figures from the presentation folder.
# Classical and STL plots fit deliberately constructed teaching data.
# X-11, SEATS, and MSTL plots reuse components from the supplied report.
# STR's diagram illustrates specified contributions without fitting a model.
out <- "figures"
dir.create(out, showWarnings = FALSE)
blue <- "#126b91"
orange <- "#c36324"
green <- "#19816c"
gray <- "#64717b"
start_plot <- function(name, rows = 1) {
  png(file.path(out, paste0(name, ".png")), width = 1400,
      height = if (rows == 1) 650 else 900, res = 150)
  par(mfrow = c(rows, 1), mar = c(3.5, 4.6, 2.2, 1),
      mgp = c(2.7, 0.8, 0), las = 1, cex = 0.95,
      col.axis = "#334a54", col.lab = "#243c46")
}
key <- function(labels, colors, types = rep(1, length(labels))) {
  legend("topleft", legend = labels, col = colors, lty = types,
         lwd = 2, bty = "n", cex = 0.82, horiz = TRUE)
}

t <- seq_len(120)
dates <- seq(as.Date("2015-01-01"), by = "month", length.out = length(t))
phase <- sin(2 * pi * (t - 1) / 12)
noise <- 0.8 * cos(2 * pi * t / 5)
add <- ts(100 + 0.6 * t + 12 * phase + noise, frequency = 12)
add_fit <- decompose(add)
start_plot("teaching-additive")
plot(dates, as.numeric(add), type = "l", col = gray, lwd = 1.5,
     xlab = "Illustrative year (monthly readings)", ylab = "Sales (illustrative units)",
     main = "A Similar Seasonal Amount as the Baseline Rises")
lines(dates, add_fit$trend, col = blue, lwd = 2.4)
key(c("Constructed sales", "Classical additive trend"), c(gray, blue))
dev.off()

mult <- ts((100 + 1.4 * t) * (1 + 0.15 * phase) * (1 + noise / 100), frequency = 12)
mult_fit <- decompose(mult, type = "multiplicative")
start_plot("teaching-multiplicative")
plot(dates, as.numeric(mult), type = "l", col = gray, lwd = 1.5,
     xlab = "Illustrative year (monthly readings)", ylab = "Sales (illustrative units)",
     main = "Similar Seasonal Percentages as the Baseline Rises")
lines(dates, mult_fit$trend, col = orange, lwd = 2.4)
key(c("Constructed sales", "Classical multiplicative trend"), c(gray, orange))
dev.off()

known_season <- (5 + 0.15 * t) * phase
changing <- ts(100 + 0.25 * t + known_season + noise, frequency = 12)
fixed <- decompose(changing)
flex <- stl(changing, s.window = 7, robust = FALSE)
start_plot("teaching-stl")
plot(dates, known_season, type = "l", col = gray, lwd = 2,
     ylim = range(known_season, fixed$seasonal, flex$time.series[, "seasonal"]),
     xlab = "Illustrative year (monthly readings)", ylab = "Seasonal effect (units)",
     main = "Fixed and Changing Seasonal Estimates on the Same Data")
abline(h = 0, lty = 3, col = "#c4cece")
lines(dates, fixed$seasonal, col = blue, lwd = 2, lty = 2)
lines(dates, flex$time.series[, "seasonal"], col = orange, lwd = 2.8, lty = 3)
key(c("Known constructed effect", "Classical additive", "STL, window 7"),
    c(gray, blue, orange), c(1, 2, 3))
dev.off()

root <- "C:/Users/alber/Downloads/examples"
monthly_path <- list.files(root, pattern = "^monthly-components.csv$",
                           recursive = TRUE, full.names = TRUE)
half_path <- list.files(root, pattern = "^half-hour-components.csv$",
                        recursive = TRUE, full.names = TRUE)
stopifnot(length(monthly_path) == 1, length(half_path) == 1)
monthly <- read.csv(monthly_path)
for (method in c("X-11", "SEATS")) {
  d <- monthly[monthly$method == method, ]
  x <- as.Date(d$month)
  start_plot(if (method == "X-11") "teaching-x11" else "teaching-seats")
  plot(x, d$observed_mw / 1000, type = "l", col = gray, lwd = 1.5,
       ylim = range(c(d$observed_mw, d$adjusted_mw)) / 1000,
       xlab = "Month", ylab = "Average demand (GW)",
       main = paste(method, "Seasonal and Calendar Adjustment in the Electricity Report"))
  lines(x, d$adjusted_mw / 1000, col = blue, lwd = 2)
  key(c("Observed", "Seasonally and calendar adjusted"), c(gray, blue))
  dev.off()
}

h <- read.csv(half_path)
time <- as.POSIXct(h$utc, format = "%Y-%m-%dT%H:%M:%SZ", tz = "UTC")
keep <- time >= as.POSIXct("2026-07-13", tz = "UTC") &
        time < as.POSIXct("2026-07-20", tz = "UTC")
start_plot("teaching-mstl", rows = 2)
plot(time[keep], h$daily_mw[keep] / 1000, type = "l", col = blue,
     lwd = 1.8, xlab = "July 13 to 19, 2026 (UTC)", ylab = "Daily effect (GW)",
     main = "MSTL Separates Daily and Weekly Contributions")
abline(h = 0, col = "#aebfc1", lty = 3)
plot(time[keep], h$weekly_mw[keep] / 1000, type = "l", col = orange,
     lwd = 1.8, xlab = "July 13 to 19, 2026 (UTC)", ylab = "Weekly effect (GW)",
     main = "Weekly Contribution Modifies the Daily Pattern")
abline(h = 0, col = "#aebfc1", lty = 3)
dev.off()

start_plot("teaching-str")
par(mar = c(3.5, 5.4, 2.2, 1))
bar_centers <- barplot(c(27, 5, 0.88741, 32.88741),
        names.arg = c("Trend", "Seasonal", "Remainder", "Observed"),
        col = c(blue, orange, gray, "#12373c"),
        border = NA, ylab = "Demand or contribution (GW)",
        main = "January 2026: Illustrative STR Components",
        ylim = c(0, 38))
text(bar_centers, c(27, 5, 0.88741, 32.88741) + 1,
     labels = c("27", "+5", "+0.88741", "32.88741"), cex = 0.9)
dev.off()

stopifnot(max(abs(changing - rowSums(flex$time.series))) < 1e-8)
cat("Created seven teaching figures. Classical/STL use constructed data,",
    "three figures reuse existing fits, and STR is a component illustration.\n")
