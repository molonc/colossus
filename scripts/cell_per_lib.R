
library(ggplot2)
args <- commandArgs(TRUE)
input <- read.csv(args[1])
output <- args[2]
w <- as.numeric(args[3])
h <- as.numeric(args[4])

if (is.na(output)) output <- "output.pdf"
if (is.na(w)) w <- 8
if (is.na(h)) h <- 4.5

input$submission_date <- as.Date(input$submission_date)
input <- input[order(input$submission_date), ]

filtered <- input[grep("ABC", input$pool_id, invert = TRUE), ]
filtered$cumsum <- cumsum(filtered$count)

g <- ggplot(filtered, aes(pool_id, count)) + geom_col() + scale_y_continuous("Cells Sequenced") + scale_x_discrete("Library (Chronological)") + theme(axis.text.x = element_text(angle = 90, hjust = 0, vjust = 0.5))

ggsave(filename = output, width = w, height = h)
