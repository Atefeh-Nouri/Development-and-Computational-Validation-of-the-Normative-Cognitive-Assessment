#!/usr/bin/env Rscript
lib <- "D:/prerequisite/R-library"
if (dir.exists(lib)) .libPaths(c(lib, .libPaths()))
dir.create("docs", showWarnings = FALSE, recursive = TRUE)
writeLines(capture.output(sessionInfo()), "docs/R_sessionInfo.txt")
ip <- installed.packages(priority = NULL)
keep <- intersect(c("readxl","lme4","lmerTest","dplyr","tibble"), rownames(ip))
v <- ip[keep, "Version"]
writeLines(c(paste0("R ", R.version.string), paste0(keep, " == ", v[keep])), "docs/R_packages.txt")
cat("[R] docs/R_sessionInfo.txt + docs/R_packages.txt written\n"); print(v)
