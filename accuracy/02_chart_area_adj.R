library('ggplot2') # nolint: single_quotes_linter.
library('reshape2') # nolint: single_quotes_linter.
library('ggthemes')  # nolint: single_quotes_linter.
library('scales')  # nolint: single_quotes_linter.
library('dplyr') # nolint: single_quotes_linter.



# config data
path_table_area <- 'paper_c8/accuracy/data/metrics_accuracy/table_area_adjusted.csv' # nolint

order_classes <- c(
    "Forest",
    "Flooded Forest",
    "Natural Grassland",
    "Wetland",
    "Shrubland",
    "Water",
    "Pastureland",
    "Cropland",
    "Bareland and Impervious",
    "Outcrop"
)

color_classes <- c(
    "#006400",
    "#76a5af",
    "#b8af4f",
    "#45c2a5",
    "#00ff00",
    "#0000ff",
    "#ffd966",
    "#e974ed",
    "#ea9999",
    "#ff8C00"
)

classes_colors <- as.list(setNames(color_classes, order_classes)) # nolint



# input data
data <- read.csv(path_table_area)

data_f <- data[, c(
    "variable",
    "area",
    "area_adjusted",
    "inferior_limit",
    "superior_limit",
    "year"
)]



# rename classes
data_f$variable[data_f$variable == "Rock Outcrop"] <- "Outcrop"
data_f$variable <- as.character(data_f$variable)




# order dataframe
data_f$variable <- factor(
    data_f$variable,
    levels = order_classes
)



data_f$diff <- (data_f$superior_limit - data_f$inferior_limit)


# display chart
base <- ggplot(
    data_f,
    aes(
        x = year,
        ymin = inferior_limit,
        ymax = superior_limit,
        color = variable,
        linetype = variable
    )) +
    geom_line(
        aes(y = area, linetype = "Pixel-counting area"), size = 1.5) +
    geom_line(
        aes(y = area_adjusted, linetype = "Area adjusted"), size = 1.5) +
    geom_ribbon(alpha = .2, show.legend = FALSE, aes(fill = variable)) +
    xlab("") + ylab("Area (Mha)") +
    scale_x_continuous(breaks = seq(1985, 2022, by = 6)) +
    scale_y_continuous(
        labels = unit_format(unit = "", scale = 1e-6),
        limits = c(0, NA)) +
    scale_color_manual(values = color_classes, guide = "none") +
    scale_fill_manual(values = classes_colors) +
    scale_linetype_manual(
        values = c("Pixel-counting area" = "solid", "Area adjusted" = "dotted"),
        labels =  c("Area Adjusted", "Pixel-counting area")) +

    facet_wrap(~variable, scales = "free", nrow = 5, ncol = 2) +
    theme_pander() +
    theme(legend.position = "bottom", legend.title = element_blank())

print(base)