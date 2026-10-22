#!/usr/bin/env Rscript
# R/lme4/lmerTest pipeline promised by the manuscript.
# Model: Outcome ~ Age_c + Sex_male + (1 | school_type)
# Sex_male: 0=Female, 1=Male
# Writes results/tables/table3_R_satterthwaite.csv

suppressPackageStartupMessages({
  need <- c("readxl", "lme4", "lmerTest", "dplyr", "tibble", "MuMIn")
  miss <- need[!vapply(need, requireNamespace, TRUE, quietly = TRUE)]
  if (length(miss)) {
    stop(
      paste(
        "Missing R packages:",
        paste(miss, collapse = ", "),
        "\nInstall with:\n",
        "install.packages(c('readxl','lme4','lmerTest','tidyverse','MuMIn'))"
      )
    )
  }

  library(readxl)
  library(lme4)
  library(lmerTest)
  library(dplyr)
  library(tibble)
  library(MuMIn)
})

args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) >= 1) args[1] else "."
nsim <- if (length(args) >= 2) as.integer(args[2]) else 1000L

set.seed(20261015)

df <- as.data.frame(
  read_excel(
    file.path(root, "dataset", "NCAD_Iranian_Dataset.xlsx"),
    sheet = "Simulated Data",
    skip = 1
  )
)

df$age_c <- as.numeric(df$age) - 15
df$sex_male <- as.integer(tolower(as.character(df$sex)) == "male")
df$school_type <- factor(df$school_type)

lab <- c(
  corsi_forward_span = "corsi_forward_span",
  corsi_backward_span = "corsi_backward_span",
  corsi_cumulative_errors = "corsi_cumulative_errors",
  srt_mean_latency = "srt_mean_latency",
  srt_response_time_cv = "srt_response_time_cv",
  crt_mean_latency = "crt_mean_latency",
  crt_response_time_cv = "crt_response_time_cv",
  stop_signal_rt = "stop_signal_rt",
  rvp_sensitivity_dprime = "rvp_sensitivity_dprime",
  rvp_decision_criterion_c = "rvp_decision_criterion_c",
  processing_speed_index = "processing_speed_index"
)

rows <- list()

for (cc in names(lab)) {
  f <- as.formula(paste(cc, "~ age_c + sex_male + (1 | school_type)"))

  m <- lmer(f, data = df, REML = TRUE)
  s <- summary(m)

  fe <- as.data.frame(coef(s))
  pcol <- if ("Pr(>|t|)" %in% names(fe)) "Pr(>|t|)" else "Pr(>F)"

  g <- function(nm, what) {
    if (!(nm %in% rownames(fe))) return(NA_real_)
    col <- switch(what, est = "Estimate", df = "df", p = pcol)
    fe[nm, col]
  }

  vc <- as.data.frame(VarCorr(m))
  s2u <- vc$vcov[vc$grp == "school_type"]
  s2e <- vc$vcov[vc$grp == "Residual"]

  r2 <- r.squaredGLMM(m)

  bt <- bootMer(
    m,
    function(mm) fixef(mm)["age_c"],
    nsim = nsim,
    seed = 20261015,
    use.u = FALSE
  )

  ci <- quantile(bt$t, probs = c(0.025, 0.975), na.rm = TRUE)

  rows[[cc]] <- tibble(
    outcome = lab[[cc]],
    column = cc,
    intercept = g("(Intercept)", "est"),
    age_beta = g("age_c", "est"),
    age_df = g("age_c", "df"),
    age_p = g("age_c", "p"),
    sex_beta = g("sex_male", "est"),
    sex_df = g("sex_male", "df"),
    sex_p = g("sex_male", "p"),
    s2_school = s2u,
    s2_resid = s2e,
    icc = s2u / (s2u + s2e),
    r2_marginal = r2[1],
    r2_conditional = r2[2],
    ci_low = ci[1],
    ci_high = ci[2]
  )

  cat(
    sprintf(
      "[R] %-26s age_beta=%9.3f df=%7.2f p=%.3g ICC=%.4f\n",
      lab[[cc]],
      g("age_c", "est"),
      g("age_c", "df"),
      g("age_c", "p"),
      s2u / (s2u + s2e)
    )
  )
}

out <- bind_rows(rows)

dir.create(file.path(root, "results", "tables"), recursive = TRUE, showWarnings = FALSE)

write.csv(
  out,
  file.path(root, "results", "tables", "table3_R_satterthwaite.csv"),
  row.names = FALSE
)

cat(sprintf("[R] wrote table3_R_satterthwaite.csv (bootMer nsim=%d)\n", nsim))
