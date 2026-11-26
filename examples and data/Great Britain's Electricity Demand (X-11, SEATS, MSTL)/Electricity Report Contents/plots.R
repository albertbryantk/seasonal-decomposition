navy <- "#182B43"
blue <- "#185D93"
orange <- "#A54424"
gray <- "#596879"
green <- "#317761"
grid_color <- "#DFE7EF"

open_plot <- function(name, height) {
  png(name, width = 1450, height = height, res = 140, bg = "white")
  par(mar = c(4.2, 5.4, 2.6, 1.3), mgp = c(3.1, .58, 0), las = 1, bty = "n",
      col.axis = navy, col.lab = navy, col.main = navy, cex.axis = .88)
}
close_plot <- function() invisible(dev.off())

open_plot("monthly-demand.png", 670)
years <- seq(as.Date("2015-01-01"), as.Date("2026-01-01"), by = "year")
plot(m$month, m$observed_mw / 1000, type = "n", xaxt = "n",
     main = "Monthly demand and underlying trend", xlab = "Month",
     ylab = "Average demand (GW)")
abline(h = axTicks(2), v = as.numeric(years), col = grid_color)
axis.Date(1, at = years, format = "%Y", tcl = -.25)
lines(m$month, m$observed_mw / 1000, col = gray, lwd = 1.8)
lines(x$month, x$trend_mw / 1000, col = blue, lwd = 2.6)
lines(s$month, s$trend_mw / 1000, col = orange, lwd = 2.6, lty = 2)
legend("topright", c("Observed mean", "X-11 trend", "SEATS trend"),
       col = c(gray, blue, orange), lwd = 2, lty = c(1, 1, 2), bty = "n")
close_plot()

open_plot("winter-gap.png", 660)
par(mfrow = c(1, 2), mar = c(4.2, 5.2, 2.7, 1.6), cex.main = 1)
season_panel <- function(values, unit, title, legend_here = FALSE) {
  plot(seasons$year, values[, 1], type = "n", xaxt = "n", ylim = range(values),
       main = title, xlab = "Year winter ends", ylab = unit)
  ax <- seq(2016, 2026, by = 2)
  abline(h = axTicks(2), v = ax, col = grid_color)
  axis(1, at = ax, tcl = -.25)
  for (j in seq_len(ncol(values))) {
    lines(seasons$year, values[, j], col = c(gray, blue, orange)[j], lwd = 2.2,
          type = "o", pch = c(1, 16, 17)[j], lty = c(3, 1, 2)[j], cex = .64)
  }
  if (legend_here) {
    legend("topleft", c("Observed", "X-11", "SEATS"), col = c(gray, blue, orange),
           pch = c(1, 16, 17), lty = c(3, 1, 2), lwd = 2, bty = "n", cex = .77)
  }
}
season_panel(as.matrix(seasons[, c("raw_pct", "x11.pct", "seats.pct")]),
             "Winter above summer (%)", "Relative winter increase", legend_here = TRUE)
season_panel(as.matrix(seasons[, c("raw_mw", "x11.mw", "seats.mw")]) / 1000,
             "Winter minus summer (GW)", "Winter increase in power")
close_plot()

open_plot("half-hour-components.png", 1080)
par(mfrow = c(4, 1), mar = c(.9, 5.4, 1.9, 1.2))
week <- h$day >= as.Date("2026-07-13") & h$day < as.Date("2026-07-20")
sample_pos <- which(week)
u <- seq_along(sample_pos)
ticks <- seq(1L, length(u), by = 48L)
half_panel <- function(values, title, bottom = FALSE, zero = FALSE, colors, types) {
  if (bottom) par(mar = c(4.25, 5.4, 1.9, 1.2))
  values <- values / 1000
  plot(u, values[, 1], type = "n", xaxt = "n", ylim = range(values), main = title,
       xlab = if (bottom) "UK local date" else "", ylab = "GW")
  abline(h = axTicks(2), v = ticks, col = grid_color)
  if (zero) abline(h = 0, col = gray, lty = 3)
  if (bottom) axis(1, at = ticks, labels = format(h$day[sample_pos[ticks]], "%d %b"), tcl = -.25)
  for (j in seq_len(ncol(values))) {
    lines(u, values[, j], col = colors[j], lwd = 2, lty = types[j])
  }
}
half_panel(as.matrix(a[week, c("observed_mw", "fit_mw", "trend_mw")]),
           "Observed demand, fitted demand and trend", colors = c(gray, blue, green), types = c(1, 2, 3))
legend("topright", c("Observed", "MSTL fitted", "Trend"), col = c(gray, blue, green),
       lty = c(1, 2, 3), lwd = 2, bty = "n", cex = .75, horiz = TRUE)
half_panel(as.matrix(a[week, "daily_mw", drop = FALSE]), "Daily component",
           zero = TRUE, colors = blue, types = 1)
half_panel(as.matrix(a[week, "weekly_mw", drop = FALSE]), "Weekly component",
           zero = TRUE, colors = orange, types = 1)
half_panel(as.matrix(a[week, "remainder_mw", drop = FALSE]), "Remainder",
           bottom = TRUE, zero = TRUE, colors = gray, types = 1)
close_plot()

open_plot("clock-demand.png", 675)
par(mfrow = c(1, 3), mar = c(4.2, 4.2, 2.7, 1.1), mgp = c(2.8, .55, 0))
ylimits <- range(profiles$fit_mw) / 1000
hours <- (0:47) / 2
for (label in c("All", "January", "July")) {
  p <- profiles[profiles$span == label, ]
  stopifnot(nrow(p) == 96, identical(p$clock[!p$weekend], p$clock[p$weekend]))
  plot(hours, p$fit_mw[!p$weekend] / 1000, type = "n", xaxt = "n", ylim = ylimits,
       main = if (label == "All") "All 2026 readings" else label,
       xlab = "UK local hour", ylab = "Fitted demand (GW)")
  ticks <- seq(0, 24, by = 6)
  abline(h = axTicks(2), v = ticks, col = grid_color)
  axis(1, at = ticks, tcl = -.25)
  for (j in c(FALSE, TRUE)) {
    values <- p$fit_mw[p$weekend == j] / 1000
    peak <- which.max(values)
    col <- if (j) orange else blue
    lines(hours, values, col = col, lwd = 2.3, lty = 1L + as.integer(j))
    points(hours[peak], values[peak], col = col, pch = if (j) 17 else 16, cex = .82)
  }
  if (label == "All") {
    legend("topleft", c("Weekdays", "Weekends"), col = c(blue, orange), pch = c(16, 17),
           lwd = 2, lty = 1:2, bty = "n", cex = .72)
  }
}
close_plot()
