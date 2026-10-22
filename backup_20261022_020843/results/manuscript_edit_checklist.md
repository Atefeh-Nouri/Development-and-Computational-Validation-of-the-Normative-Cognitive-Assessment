# Manuscript Edit Checklist (auto-generated from the shipped dataset)

Replace the LEFT value (current `.docx`) with the RIGHT value (data-derived truth).
`SKIP` = the value is not printed in the excerpt we were given, so the audit
declines to fabricate a comparison. Point estimates are engine-independent;
p-values here are Wald/normal-approx (statsmodels) - see item 9 for Satterthwaite.

## 1. Table 1 - per-cohort N (replace the grid with `results/tables/table1_truth.csv`)
| Age | Paper | Data |
|---|---|---|
| `12` | `286` | `286` |
| `13` | `286` | `286` |
| `14` | `SKIP (not in excerpt)` | `286` |
| `15` | `SKIP (not in excerpt)` | `286` |
| `16` | `SKIP (not in excerpt)` | `286` |
| `17` | `SKIP (not in excerpt)` | `285` |
| `18` | `SKIP (not in excerpt)` | `285` |

## 2. Table 2 - descriptive means (replace with `table2_truth.csv`, 2-decimal APA)
_Numeric M±SD grid is absent from the excerpt; the only Corsi evidence in the text is the §7.1 narrative (see item 4). Per-age means are therefore SKIP._

## 3. Table 3 - LMM estimates (replace with `table3_truth.csv`)
| Outcome | Field | Paper | Data |
|---|---|---|---|
| `corsi_forward_span` | `Intercept_Beta0` | `SKIP (row/field not in excerpt)` | `4.897` |
| `corsi_forward_span` | `Age_Beta` | `SKIP (row/field not in excerpt)` | `0.267` |
| `corsi_forward_span` | `Sex_Beta` | `SKIP (row/field not in excerpt)` | `0.033` |
| `corsi_forward_span` | `AgeXSex_Beta` | `SKIP (row/field not in excerpt)` | `0.017` |
| `corsi_forward_span` | `Sigma2_School` | `SKIP (row/field not in excerpt)` | `0.0003` |
| `corsi_forward_span` | `Sigma2_Resid` | `SKIP (row/field not in excerpt)` | `0.2955` |
| `corsi_forward_span` | `ICC` | `SKIP (row/field not in excerpt)` | `0.0011` |
| `corsi_forward_span` | `R2_Marginal` | `SKIP (row/field not in excerpt)` | `0.5066` |
| `corsi_forward_span` | `R2_Conditional` | `SKIP (row/field not in excerpt)` | `0.5071` |
| `srt_mean_latency` | `Intercept_Beta0` | `SKIP (row/field not in excerpt)` | `350.951` |
| `srt_mean_latency` | `Age_Beta` | `SKIP (row/field not in excerpt)` | `-13.125` |
| `srt_mean_latency` | `Sex_Beta` | `SKIP (row/field not in excerpt)` | `-0.245` |
| `srt_mean_latency` | `AgeXSex_Beta` | `SKIP (row/field not in excerpt)` | `0.3675` |
| `srt_mean_latency` | `Sigma2_School` | `SKIP (row/field not in excerpt)` | `0.0` |
| `srt_mean_latency` | `Sigma2_Resid` | `SKIP (row/field not in excerpt)` | `393.2975` |
| `srt_mean_latency` | `ICC` | `SKIP (row/field not in excerpt)` | `0.0` |
| `srt_mean_latency` | `R2_Marginal` | `SKIP (row/field not in excerpt)` | `0.6298` |
| `srt_mean_latency` | `R2_Conditional` | `SKIP (row/field not in excerpt)` | `0.6298` |
| `crt_mean_latency` | `Intercept_Beta0` | `SKIP (row/field not in excerpt)` | `630.989` |
| `crt_mean_latency` | `Age_Beta` | `-19.631` | `-19.246` |
| `crt_mean_latency` | `Sex_Beta` | `0.95` | `-0.952` |
| `crt_mean_latency` | `AgeXSex_Beta` | `SKIP (row/field not in excerpt)` | `-0.7454` |
| `crt_mean_latency` | `Sigma2_School` | `SKIP (row/field not in excerpt)` | `0.0` |
| `crt_mean_latency` | `Sigma2_Resid` | `SKIP (row/field not in excerpt)` | `816.8896` |
| `crt_mean_latency` | `ICC` | `SKIP (row/field not in excerpt)` | `0.0` |
| `crt_mean_latency` | `R2_Marginal` | `SKIP (row/field not in excerpt)` | `0.6536` |
| `crt_mean_latency` | `R2_Conditional` | `SKIP (row/field not in excerpt)` | `0.6536` |
| `stop_signal_rt` | `Intercept_Beta0` | `SKIP (row/field not in excerpt)` | `276.169` |
| `stop_signal_rt` | `Age_Beta` | `-8.088` | `-8.228` |
| `stop_signal_rt` | `Sex_Beta` | `0.693` | `-0.693` |
| `stop_signal_rt` | `AgeXSex_Beta` | `SKIP (row/field not in excerpt)` | `0.2707` |
| `stop_signal_rt` | `Sigma2_School` | `SKIP (row/field not in excerpt)` | `1.3278` |
| `stop_signal_rt` | `Sigma2_Resid` | `SKIP (row/field not in excerpt)` | `210.3532` |
| `stop_signal_rt` | `ICC` | `SKIP (row/field not in excerpt)` | `0.0063` |
| `stop_signal_rt` | `R2_Marginal` | `SKIP (row/field not in excerpt)` | `0.5528` |
| `stop_signal_rt` | `R2_Conditional` | `SKIP (row/field not in excerpt)` | `0.5556` |
| `rvp_sensitivity_dprime` | `Intercept_Beta0` | `SKIP (row/field not in excerpt)` | `1.982` |
| `rvp_sensitivity_dprime` | `Age_Beta` | `0.113` | `0.113` |
| `rvp_sensitivity_dprime` | `Sex_Beta` | `0.003` | `-0.003` |
| `rvp_sensitivity_dprime` | `AgeXSex_Beta` | `SKIP (row/field not in excerpt)` | `0.0002` |
| `rvp_sensitivity_dprime` | `Sigma2_School` | `SKIP (row/field not in excerpt)` | `0.0003` |
| `rvp_sensitivity_dprime` | `Sigma2_Resid` | `SKIP (row/field not in excerpt)` | `0.0537` |
| `rvp_sensitivity_dprime` | `ICC` | `SKIP (row/field not in excerpt)` | `0.0062` |
| `rvp_sensitivity_dprime` | `R2_Marginal` | `SKIP (row/field not in excerpt)` | `0.4842` |
| `rvp_sensitivity_dprime` | `R2_Conditional` | `SKIP (row/field not in excerpt)` | `0.4874` |
| `processing_speed_index` | `Intercept_Beta0` | `SKIP (row/field not in excerpt)` | `86.352` |
| `processing_speed_index` | `Age_Beta` | `2.782` | `2.738` |
| `processing_speed_index` | `Sex_Beta` | `0.113` | `-0.113` |
| `processing_speed_index` | `AgeXSex_Beta` | `SKIP (row/field not in excerpt)` | `0.0865` |
| `processing_speed_index` | `Sigma2_School` | `SKIP (row/field not in excerpt)` | `0.0` |
| `processing_speed_index` | `Sigma2_Resid` | `SKIP (row/field not in excerpt)` | `58.2441` |
| `processing_speed_index` | `ICC` | `SKIP (row/field not in excerpt)` | `0.0` |
| `processing_speed_index` | `R2_Marginal` | `SKIP (row/field not in excerpt)` | `0.347` |
| `processing_speed_index` | `R2_Conditional` | `SKIP (row/field not in excerpt)` | `0.347` |

> Table 3 Note declares a **no-interaction** model, so `AgeXSex_Beta` and the variance columns (Sigma2/ICC/R2) are intentionally absent from the printed table - that omission is flagged by d05/d06, not a number to paste.

## 4. §7.1 narrative (Corsi)
| Corsi@12 | Corsi@18 |
|---|---|
| `5.82 <- STALE, delete/rewrite` | `7.64 <- STALE, delete/rewrite` |
| `4.18 <- DATA-SUPPORTED` | `5.79 <- DATA-SUPPORTED` |
| `data 4.18` | `data 5.79` |

## 5. Abstract - Age x Sex interaction
- Paper asserts **significant**; data gives **NON-significant (parallel)**.
- Reword the Abstract to match §6.4.2 and Table 3 (see d05).

## 6. 40-school-cluster / ICC / conditional-R2 claims
- Data grouping = `school_type` (2 levels); `cluster_supported=False`.
- EITHER regenerate the `.xlsx` with a real 40-level `school_id`, OR qualify §5.1/§6.4.3 to a 2-level institutional proxy and reset the prose R2_c band to the data range (see d06). Prose R2_c = (0.328, 0.448); data R2_c range = [0.301, 0.654].

## 7. Battery scope
- Named outcomes not in data: ['rvp_decision_criterion_c'].
- Add the missing column to the generator, or drop it from §5.2/§6.2 (see d07).

## 8. Infographic SSRT slope (single value)
| `text -8.228 / bar -8.228` | `data -8.228  <- use everywhere; re-render GitHub_Hero.png from table3_truth.csv` |

## 9. Inference method (Satterthwaite / REML / lme4 / bootstrap)
- Engine p-method = `wald_normal_approx`; satterthwaite_available=False; bootstrap_iterations=1000.
- Honour §5.3 verbatim by generating Table 3's df/p from the R/`lme4`+`lmerTest` script on this same `.xlsx` (point estimates match; only df/p differ), OR reword §5.3 to Wald z-tests + R replication archive (see d09).