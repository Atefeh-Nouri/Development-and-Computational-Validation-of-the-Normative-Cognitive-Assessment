#!/usr/bin/env Rscript

# NCAD R publication engine.
# Model:
#   Outcome ~ age_c + sex_male + (1 | group_col)
#
# age_c:
#   age centered at 15
#
# sex_male:
#   0 = Female
#   1 = Male
#
# group_col:
#   default = school_type
#   override with environment variable NCAD_GROUP_COL
#
# Output:
#   results/tables/table3_R_satterthwaite.csv

# --- NCAD custom R library bootstrap ---
ncad_libs <- c(
  Sys.getenv("NCAD_R_LIB"),
  Sys.getenv("R_LIBS_USER"),
  "D:/prerequisite/R-library"
)
ncad_libs <- unique(ncad_libs[nzchar(ncad_libs)])
ncad_libs <- ncad_libs[dir.exists(ncad_libs)]

if (length(ncad_libs) > 0) {
  .libPaths(c(ncad_libs, .libPaths()))
}

cat("[R] library paths:\n")
print(.libPaths())

cat("[R] package availability:\n")
need_probe <- c("readxl", "lme4", "lmerTest", "dplyr", "tibble")
print(sapply(need_probe, requireNamespace, quietly = TRUE))
# ---------------------------------------

suppressPackageStartupMessages({
  need <- c("readxl", "lme4", "lmerTest", "dplyr", "tibble")
  miss <- need[!vapply(need, requireNamespace, TRUE, quietly = TRUE)]
  if (length(miss)) {
    stop(
      paste0(
        "Missing R packages: ",
        paste(miss, collapse = ", "),
        "\nInstall with:\n",
        "install.packages(c('readxl','lme4','lmerTest','dplyr','tibble'))"
      )
    )
  }

  library(readxl)
  library(lme4)
  library(lmerTest)
  library(dplyr)
  library(tibble)
})

args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) >= 1) args[1] else "."
nsim <- if (length(args) >= 2) as.integer(args[2]) else 1000L

set.seed(20261015)

xlsx_path <- file.path(root, "dataset", "NCAD_Iranian_Dataset.xlsx")
if (!file.exists(xlsx_path)) {
  stop(paste("Dataset not found:", xlsx_path))
}

df <- as.data.frame(
  read_excel(
    xlsx_path,
    sheet = "Simulated Data",
    skip = 1
  )
)

# Required columns.
required_cols <- c("age", "sex")
missing_cols <- setdiff(required_cols, names(df))
if (length(missing_cols)) {
  stop(paste("Missing required dataset columns:", paste(missing_cols, collapse = ", ")))
}

# Center age exactly as in the manuscript.
df$age_c <- as.numeric(df$age) - 15

# Dummy-code sex exactly as in the manuscript:
# 0 = Female, 1 = Male.
df$sex_male <- as.integer(tolower(as.character(df$sex)) == "male")

# Choose grouping column.
# Default follows the Table 3 note used in this repository: school_type.
# If your manuscript version uses school_id, run with:
#   NCAD_GROUP_COL=school_id Rscript src/analysis_pipeline.R . 1000
group_col <- Sys.getenv("NCAD_GROUP_COL", "school_type")

if (!group_col %in% names(df)) {
  if ("school_id" %in% names(df)) {
    group_col <- "school_id"
  } else if ("school_type" %in% names(df)) {
    group_col <- "school_type"
  } else {
    stop("No valid grouping column found. Expected school_type or school_id.")
  }
}

df[[group_col]] <- factor(df[[group_col]])

cat(sprintf("[R] dataset = %s\n", xlsx_path))
cat(sprintf("[R] N = %d\n", nrow(df)))
cat(sprintf("[R] grouping column = %s\n", group_col))
cat(sprintf("[R] grouping levels = %d\n", length(unique(df[[group_col]]))))
cat(sprintf("[R] bootstrap nsim = %d\n", nsim))

outcome_cols <- c(
  "corsi_forward_span",
  "corsi_backward_span",
  "corsi_cumulative_errors",
  "srt_mean_latency",
  "srt_response_time_cv",
  "crt_mean_latency",
  "crt_response_time_cv",
  "stop_signal_rt",
  "rvp_sensitivity_dprime",
  "rvp_decision_criterion_c",
  "processing_speed_index"
)

outcome_cols <- intersect(outcome_cols, names(df))

if (length(outcome_cols) == 0) {
  stop("No outcome columns found in dataset.")
}

rows <- list()

for (cc in outcome_cols) {
  f <- as.formula(
    paste(cc, "~ age_c + sex_male + (1 |", group_col, ")")
  )

  m <- lmer(f, data = df, REML = TRUE)
  s <- summary(m)

  fe <- as.data.frame(coef(s))
  pcol <- if ("Pr(>|t|)" %in% names(fe)) "Pr(>|t|)" else "Pr(>F)"

  g <- function(nm, what) {
    if (!(nm %in% rownames(fe))) return(NA_real_)
    col <- switch(what, est = "Estimate", df = "df", p = pcol)
    as.numeric(fe[nm, col])
  }

  vc <- as.data.frame(VarCorr(m))

  s2u <- NA_real_
  s2e <- NA_real_

  if ("vcov" %in% names(vc) && "grp" %in% names(vc)) {
    u_row <- vc[vc$grp == group_col, ]
    e_row <- vc[vc$grp == "Residual", ]

    if (nrow(u_row) >= 1) s2u <- as.numeric(u_row$vcov[1])
    if (nrow(e_row) >= 1) s2e <- as.numeric(e_row$vcov[1])
  }

  if (is.na(s2e)) {
    s2e <- as.numeric(summary(m)$sigma^2)
  }

  if (is.na(s2u)) {
    s2u <- 0
  }

  # Nakagawa-style R2 without requiring MuMIn.
  X <- model.matrix(~ age_c + sex_male, data = df)
  beta <- fixef(m)[colnames(X)]

  if (any(is.na(beta))) {
    vf <- NA_real_
  } else {
    vf <- var(as.vector(X %*% beta))
  }

  denom <- vf + s2u + s2e

  if (is.na(vf) || is.na(denom) || denom <= 0) {
    r2_marginal <- NA_real_
    r2_conditional <- NA_real_
  } else {
    r2_marginal <- vf / denom
    r2_conditional <- (vf + s2u) / denom
  }

  icc <- if (!is.na(s2u) && !is.na(s2e) && (s2u + s2e) > 0) {
    s2u / (s2u + s2e)
  } else {
    NA_real_
  }

  if (nsim > 0) {
    bt <- bootMer(
      m,
      function(mm) fixef(mm)["age_c"],
      nsim = nsim,
      seed = 20261015,
      use.u = FALSE
    )

    ci <- quantile(bt$t, probs = c(0.025, 0.975), na.rm = TRUE)
    ci_low <- unname(ci[1])
    ci_high <- unname(ci[2])
  } else {
    ci_low <- NA_real_
    ci_high <- NA_real_
  }

  rows[[cc]] <- tibble(
    outcome = cc,
    column = cc,
    group_column = group_col,
    intercept = g("(Intercept)", "est"),
    age_beta = g("age_c", "est"),
    age_df = g("age_c", "df"),
    age_p = g("age_c", "p"),
    sex_beta = g("sex_male", "est"),
    sex_df = g("sex_male", "df"),
    sex_p = g("sex_male", "p"),
    s2_school = s2u,
    s2_resid = s2e,
    icc = icc,
    r2_marginal = r2_marginal,
    r2_conditional = r2_conditional,
    ci_low = ci_low,
    ci_high = ci_high
  )

  cat(
    sprintf(
      "[R] %-26s age_beta=%9.3f  df=%8.2f  p=%.3g  ICC=%.4f  R2c=%.4f\n",
      cc,
      g("age_c", "est"),
      g("age_c", "df"),
      g("age_c", "p"),
      icc,
      r2_conditional
    )
  )
}

out <- bind_rows(rows)

tables_dir <- file.path(root, "results", "tables")
dir.create(tables_dir, recursive = TRUE, showWarnings = FALSE)

out_path <- file.path(tables_dir, "table3_R_satterthwaite.csv")
write.csv(out, out_path, row.names = FALSE)

cat(sprintf("[R] wrote %s\n", out_path))
