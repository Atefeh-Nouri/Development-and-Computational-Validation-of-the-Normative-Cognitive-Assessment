"""Manuscript targets (Draw B = the PDF's Tables 1-3). VERIFY each value against
the PDF before OSF deposit - this file is the single source of calibration."""
from types import SimpleNamespace

T = SimpleNamespace(
 N_PER_AGE = {12:286, 13:285, 14:286, 15:286, 16:285, 17:286, 18:286},
 SEX_TOTALS = {"female":1022, "male":978},
 TYPE_TOTALS = {"public":1227, "private":773},
 PROVINCE_TOTALS = {"Khorasan Razavi":1000, "South Khorasan":500, "North Khorasan":500},
 # (n_public_schools, n_private_schools) per province -> 40 schools total
 PROVINCE_SCHOOL_PLAN = {"Khorasan Razavi":(12,8), "South Khorasan":(6,4), "North Khorasan":(6,4)},
 PUBLIC_QUOTA  = {"Khorasan Razavi":614, "South Khorasan":306, "North Khorasan":307},   # sums 1227
 PRIVATE_QUOTA = {"Khorasan Razavi":386, "South Khorasan":194, "North Khorasan":193},   # sums  773
 OUTCOMES = {
  # core 6: Table 3 tuples  b=(b0@age15, b_age, b_sex, b_agexsex), s2u, s2e
  # (ICC = s2u/(s2u+s2e) reproduces the printed 0.061/0.063/0.061/0.056/0.049/0.062)
  "corsi_forward_span":      dict(col="corsi_span",             b=(6.12,  0.271, 0.042, 0.008), s2u=0.048, s2e=0.742),
  "srt_mean_latency":        dict(col="srt_mean_ms",            b=(306.8,-12.42,-1.85 ,-0.32 ), s2u=82.4 , s2e=1215.0),
  "crt_mean_latency":        dict(col="crt_mean_ms",            b=(570.4,-21.65,-2.10 ,-0.45 ), s2u=185.2, s2e=2840.5),
  "stop_signal_rt":          dict(col="ssrt_ms",                b=(244.8,-11.28,-1.42 ,-0.21 ), s2u=52.1 , s2e=882.4),
  "rvp_sensitivity_dprime":  dict(col="sdt_dprime",             b=(2.02 , 0.112, 0.015, 0.003), s2u=0.003, s2e=0.058),
  "processing_speed_index":  dict(col="processing_speed",       b=(86.42, 2.780, 0.312, 0.045), s2u=3.85 , s2e=58.40),
  # supplementary 5 (completes the 11-outcome battery named in the paper).
  # errors/CV rows carry over the previous benchmark draw; backward/c are defaults.
  # VERIFY against PDF Table 2/3 if they are printed there, then re-run the generator.
  "corsi_backward_span":     dict(col="corsi_backward_span",    b=(5.35 , 0.212, 0.038, 0.005 ), s2u=0.0004*100, s2e=0.615),
  "corsi_cumulative_errors": dict(col="corsi_cumulative_errors",b=(4.78 ,-0.409, 0.050, 0.027 ), s2u=0.030 , s2e=1.050),
  "srt_response_time_cv":    dict(col="srt_response_time_cv",   b=(0.260,-0.014, 0.002, 0.0007), s2u=0.0004, s2e=0.0062),
  "crt_response_time_cv":    dict(col="crt_response_time_cv",   b=(0.301,-0.017,-0.003,-0.0005), s2u=0.0006, s2e=0.0098),
  "rvp_decision_criterion_c":dict(col="rvp_decision_criterion_c",b=(0.42, 0.021,-0.008, 0.001 ), s2u=0.002 , s2e=0.041),
 })
