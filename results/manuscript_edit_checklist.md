# Manuscript Edit Checklist (auto-generated from the shipped dataset)

Replace LEFT (current `.docx`) with RIGHT (data-derived truth).

## 1. Table 1 per-cohort N
| Age | Paper | Data |
|---|---|---|
| `12` | `286` | `286` |
| `13` | `286` | `286` |
| `14` | `286` | `286` |
| `15` | `286` | `286` |
| `16` | `286` | `286` |
| `17` | `285` | `285` |
| `18` | `285` | `285` |

## 2. Table 2 core means
| Outcome | Paper @12->@18 | Data @12->@18 |
|---|---|---|
| `corsi_forward_span` | `[4.18, 4.36, 4.57, 4.87, 5.12, 5.52, 5.79]` | `[4.18, 4.36, 4.57, 4.87, 5.12, 5.52, 5.79]` |
| `srt_mean_latency` | `[388.36, 375.8, 366.03, 352.09, 337.98, 324.03, 311.49]` | `[388.36, 375.8, 366.03, 352.09, 337.98, 324.03, 311.49]` |
| `crt_mean_latency` | `[687.64, 670.48, 651.44, 629.94, 612.55, 591.26, 570.19]` | `[687.64, 670.48, 651.44, 629.94, 612.55, 591.26, 570.19]` |
| `stop_signal_rt` | `[298.81, 292.99, 283.65, 275.84, 268.33, 258.4, 251.51]` | `[298.81, 292.99, 283.65, 275.84, 268.33, 258.4, 251.51]` |
| `rvp_sensitivity_dprime` | `[1.67, 1.75, 1.85, 1.96, 2.11, 2.19, 2.34]` | `[1.67, 1.75, 1.85, 1.96, 2.11, 2.19, 2.34]` |
| `processing_speed_index` | `[77.78, 80.98, 83.12, 86.71, 89.03, 92.04, 94.4]` | `[77.78, 80.98, 83.12, 86.71, 89.03, 92.04, 94.4]` |

## 3. Table 3 core LMM fields
| Outcome | Field | Paper | Data |
|---|---|---|---|
| `corsi_forward_span` | `Intercept_Beta0` | `SKIP` | `4.906` |
| `corsi_forward_span` | `Age_Beta` | `0.275` | `0.276` |
| `corsi_forward_span` | `Sex_Beta` | `-0.033` | `-0.032` |
| `corsi_forward_span` | `Sex_P_Value` | `0.1762` | `0.39552034257025837` |
| `srt_mean_latency` | `Intercept_Beta0` | `SKIP` | `352.339` |
| `srt_mean_latency` | `Age_Beta` | `-12.936` | `-13.008` |
| `srt_mean_latency` | `Sex_Beta` | `0.246` | `0.218` |
| `srt_mean_latency` | `Sex_P_Value` | `0.7818` | `0.8967571300492457` |
| `crt_mean_latency` | `Intercept_Beta0` | `SKIP` | `631.292` |
| `crt_mean_latency` | `Age_Beta` | `-19.631` | `-19.687` |
| `crt_mean_latency` | `Sex_Beta` | `0.95` | `0.923` |
| `crt_mean_latency` | `Sex_P_Value` | `0.4577` | `0.6723173641161738` |
| `stop_signal_rt` | `Intercept_Beta0` | `SKIP` | `275.467` |
| `stop_signal_rt` | `Age_Beta` | `-8.088` | `-8.093` |
| `stop_signal_rt` | `Sex_Beta` | `0.693` | `0.69` |
| `stop_signal_rt` | `Sex_P_Value` | `0.2851` | `0.45952293281234946` |
| `rvp_sensitivity_dprime` | `Intercept_Beta0` | `SKIP` | `1.983` |
| `rvp_sensitivity_dprime` | `Age_Beta` | `0.113` | `0.112` |
| `rvp_sensitivity_dprime` | `Sex_Beta` | `0.003` | `0.003` |
| `rvp_sensitivity_dprime` | `Sex_P_Value` | `0.797` | `0.8431436560711665` |
| `processing_speed_index` | `Intercept_Beta0` | `SKIP` | `85.924` |
| `processing_speed_index` | `Age_Beta` | `2.782` | `2.796` |
| `processing_speed_index` | `Sex_Beta` | `0.113` | `0.118` |
| `processing_speed_index` | `Sex_P_Value` | `0.7399` | `0.7126574229280054` |

## 4. Remaining method/clause checks
- See `results/doc_punchlist.md` and the pytest `doc_audit` output.
- `d09` remains red until `src/analysis_pipeline.R` is run and registered.