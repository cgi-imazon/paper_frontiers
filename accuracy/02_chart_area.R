library('ggplot2') # nolint: single_quotes_linter.
library('reshape2') # nolint: single_quotes_linter.
library('ggthemes')  # nolint: single_quotes_linter.
library('scales')  # nolint: single_quotes_linter.




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





# input data
data <- read.csv(path_table_area)
data <- data[, c("variable", "area", "area_adjusted", "year")]

data_melted <- melt(
    data, na.rm = FALSE,
    value.name = "value",
    variable.name = "metric",
    id = c("variable", "year")
)




# rename values
data_melted$metric <- as.character(data_melted$metric)
data_melted$metric[data_melted$metric == "area"] <- "Pixel-counting area"
data_melted$metric[data_melted$metric == "area_adjusted"] <- "Adjusted area"
data_melted$variable[data_melted$variable == "Rock Outcrop"] <- "Outcrop"




# order class charts
data_melted$variable <- factor(
    data_melted$variable,
    levels = order_classes
)





# display chart
base <- ggplot(
    data_melted,
    aes(year)) +
    geom_line(aes(y = value, linetype = metric, color = variable), size = 1.5) +
    xlab("") + ylab("Area (Mha)") +
    scale_x_continuous(breaks = seq(1985, 2022, by = 6)) +
    scale_y_continuous(
        labels = unit_format(unit = "", scale = 1e-6),
        limits = c(0, NA)) +
    scale_color_manual(values = color_classes, guide = "none") +
    facet_wrap(~variable, scales = "free", nrow = 5, ncol = 2) +
    theme_pander() +
    theme(legend.position = "bottom", legend.title = element_blank())


#ggsave(
#    filename = 'paper_c8/accuracy/area_chart_ii.png', plot = base, units = 'in',
#    width = 9, height = 8, dpi = 3000) # nolint

print(base, width = 1500, height = 700)