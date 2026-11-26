colors <- c("#175B91", "#A34122", "#23725F", "#794D9D")
types <- 1:4
labels <- c("Classical additive", "Classical multiplicative", "STL", "STR")
tick_dates <- seq(as.Date("2022-01-01"), as.Date("2026-01-01"), by = "year")
open_plot <- function(file, height) {
  png(file, width = 1450, height = height, res = 140, bg = "white")
  par(mar = c(4.1, 5, 2.8, 1.2), mgp = c(2.6, .65, 0), las = 1, bty = "n",
      col.axis = "#1B2D40", col.lab = "#1B2D40", col.main = "#1B2D40", cex.axis = .9)
}
close_plot <- function() invisible(dev.off())
open_plot("sales-and-trend.png", 920)
par(mfrow = c(2, 1), mar = c(1.3, 5, 2.6, 1.2))
plot(dates, y / 1000, type = "n", xaxt = "n", xlab = "", ylab = "Sales (US$ billion)",
     main = "Observed monthly restaurant sales")
abline(h = axTicks(2), v = as.numeric(tick_dates), col = "#E2E8EE")
lines(dates, y / 1000, col = "#566779", lwd = 2)
par(mar = c(4.1, 5, 2.6, 1.2))
plot(dates, y / 1000, type = "n", xaxt = "n", xlab = "Month",
     ylab = "Trend (US$ billion)", main = "Estimated underlying level",
     ylim = range(components$trend_million, na.rm = TRUE) / 1000)
abline(h = axTicks(2), v = as.numeric(tick_dates), col = "#E2E8EE")
axis.Date(1, at = tick_dates, format = "%Y", tcl = -.25)
for (j in seq_along(methods)) {
  c <- components[components$method == methods[j], ]
  lines(dates, c$trend_million / 1000, col = colors[j], lty = types[j], lwd = 2.4)
}
legend("topleft", labels, col = colors, lty = types, lwd = 2.4, cex = .8, bty = "n", ncol = 2)
close_plot()

open_plot("seasonal-profiles.png", 670)
plot(1:12, rep(0, 12), type = "n", xaxt = "n",
     ylim = range(profiles$contribution_million) / 1000 + c(-.5, 2),
     xlab = "Month of year", ylab = "Seasonal contribution (US$ billion)",
     main = "Typical monthly seasonal contribution")
abline(h = axTicks(2), col = "#E2E8EE")
abline(h = 0, lty = 3, col = "#566779")
axis(1, at = 1:12, labels = month.abb, tcl = -.25)
for (j in seq_along(methods)) {
  p <- profiles[profiles$method == methods[j], ]
  lines(1:12 + (j - 2.5) * .035, p$contribution_million / 1000,
        col = colors[j], lwd = 2.2, lty = types[j], type = "o", pch = 14 + j, cex = .72)
}
legend("topleft", labels, col = colors, lty = types, pch = 15:18, lwd = 2.2,
       cex = .8, bty = "n", ncol = 2)
close_plot()

open_plot("remainders.png", 920)
par(mfrow = c(2, 2), mar = c(4, 4.7, 2.6, 1.2), mgp = c(2.7, .6, 0))
limits <- range(components$remainder_million, na.rm = TRUE) / 1000
for (j in seq_along(methods)) {
  c <- components[components$method == methods[j], ]
  plot(dates, y, type = "n", ylim = limits, xaxt = "n",
       main = labels[j], xlab = "Month", ylab = "Remainder (US$ billion)")
  abline(h = axTicks(2), v = as.numeric(tick_dates), col = "#E2E8EE")
  abline(h = 0, col = "#566779", lty = 3)
  axis.Date(1, at = tick_dates, format = "%Y", tcl = -.25)
  lines(dates, c$remainder_million / 1000, col = colors[j], lty = types[j], lwd = 2)
}
close_plot()
