library(ggplot2)
args <- commandArgs(TRUE)
input <- read.csv(args[1])
output <- args[2]
# w <- as.numeric(args[3])
# h <- as.numeric(args[4])
# log <- as.logical(args[5])
# stop <- as.Date(args[6])

if (is.na(output)) output <- "output.pdf"
# if (is.na(w)) w <- 8
# if (is.na(h)) h <- 4.5
# if (is.na(log)) log <- FALSE

input$submission_date <- as.Date(input$submission_date)
input <- input[order(input$submission_date, input$pool_id), ]

filtered <- input[grep("ABC", input$pool_id, invert = TRUE), ]
filtered$cumsum <- cumsum(filtered$count)
filtered <- filtered[!duplicated(filtered$pool_id), ]

# if (is.na(stop)) stop <- max(filtered$submission_date)
# stop <- max(filtered$submission_date)
# start <- min(filtered$submission_date)

pdf(file = output, width = 8, height = 4.5)
g <- ggplot(filtered, aes(submission_date, cumsum)) + geom_line() + scale_x_date(date_breaks="1 month", "Date") + scale_y_log10("Total Cells Sequenced", limits = c(min(filtered$cumsum), 1e6), breaks = scales::trans_breaks("log10", function(x) 10^x)) + theme(axis.text.x = element_text(angle = 45, hjust = 1))
print(g)
g <- ggplot(filtered, aes(submission_date, cumsum)) + geom_line() + scale_x_date(date_breaks="1 month", "Date") + scale_y_continuous("Total Cells Sequenced") + theme(axis.text.x = element_text(angle = 45, hjust = 1))
print(g)
filtered$pool_id <- factor(filtered$pool_id, levels = filtered$pool_id)
g <- ggplot(filtered, aes(pool_id, count)) + geom_col() + scale_y_continuous("Cells Sequenced") + scale_x_discrete("Library (Chronological)") + theme(axis.text.x = element_text(angle = 90, hjust = 0, vjust = 0.5, size = 7))
print(g)

# ggsave(filename = output, width = w, height = h)
dev.off()

