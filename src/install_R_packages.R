#!/usr/bin/env Rscript

# Install/check NCAD R dependencies.
# Uses environment variables:
#   NCAD_R_LIB      optional R library path, e.g. D:/prerequisite/R-library
#   NCAD_R_PKG_DIR  optional folder containing offline .zip Windows R packages

lib <- Sys.getenv("NCAD_R_LIB", "")
lib <- gsub("\\\\", "/", lib)

if (nzchar(lib)) {
  ok <- tryCatch({
    dir.create(lib, recursive = TRUE, showWarnings = FALSE)
    TRUE
  }, error = function(e) FALSE)

  if (ok) {
    .libPaths(c(lib, .libPaths()))
  } else {
    warning("Could not create/use NCAD_R_LIB; falling back to default R library.")
    lib <- ""
  }
}

pkg_dir <- Sys.getenv("NCAD_R_PKG_DIR", "")
pkg_dir <- gsub("\\\\", "/", pkg_dir)

need <- c("readxl", "lme4", "lmerTest", "dplyr", "tibble")

local_install <- function(p) {
  if (!nzchar(pkg_dir) || !dir.exists(pkg_dir)) return(FALSE)

  zips <- list.files(pkg_dir, pattern = "[.]zip$", full.names = TRUE)
  if (length(zips) == 0) return(FALSE)

  hit <- zips[grepl(paste0("^", p, "_"), basename(zips))]
  if (length(hit) == 0) return(FALSE)

  cat("[R] installing offline package:", basename(hit[1]), "\n")
  install.packages(hit[1], repos = NULL, type = "win.binary")

  requireNamespace(p, quietly = TRUE)
}

# First try offline packages from D:/prerequisite/R-packages if present.
for (p in need) {
  if (!requireNamespace(p, quietly = TRUE)) {
    local_install(p)
  }
}

# Then install anything still missing from CRAN.
missing <- need[!vapply(need, requireNamespace, logical(1), quietly = TRUE)]

if (length(missing) > 0) {
  target_lib <- if (nzchar(lib)) lib else .libPaths()[1]

  cat("[R] installing from CRAN:", paste(missing, collapse = ", "), "\n")
  cat("[R] target library:", target_lib, "\n")

  install.packages(
    missing,
    lib = target_lib,
    repos = "https://cloud.r-project.org",
    dependencies = TRUE
  )
}

ok <- vapply(need, requireNamespace, logical(1), quietly = TRUE)
print(ok)

if (!all(ok)) {
  stop("One or more required R packages are still missing.")
}

cat("[R] All required R packages are available.\n")
print(.libPaths())
