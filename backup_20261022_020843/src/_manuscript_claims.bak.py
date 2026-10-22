"""Faithful transcription of the PROVIDED manuscript excerpt (final edition.docx).
None  ->  the number is NOT printed in the excerpt we were given; the audit must
SKIP it (do not fabricate a comparison).  Present values are copied verbatim.
This file mirrors the PAPER, not the data; doc_audit compares it to the truth
manifest produced by 00_regenerate_truth.py from the shipped .xlsx."""

# ---- Table 1 : totals are fully printed and match the data exactly ----
TABLE1_TOTALS = dict(N=2000, female=1022, male=978, public=1227, private=773,
                     razavi=1000, south_khorasan=500, north_khorasan=500)
# per-cohort N : only ages 12 & 13 are shown as explicit rows in the excerpt
# (12 = 151F+135M = 286 ; 13 = 140F+146M = 286). 14-18 are NOT in the excerpt.
TABLE1_PER_AGE = {12: 286, 13: 286, 14: None, 15: None, 16: None, 17: None, 18: None}

# ---- Table 2 : the numeric M±SD grid is NOT in the excerpt (caption + 2 narrative
#      sentences only).  Per-age means are therefore UNVERIFIABLE -> SKIP. ----
TABLE2_GRID_AVAILABLE = False

# ---- Table 3 : what the excerpt ACTUALLY prints (the Note + four rows). ----
#      The Note's formula has NO interaction term and codes sex 0=Female,1=Male
#      (i.e. reference = female, coefficient = male effect).  No intercept / ICC /
#      sigma2 / R2 / bootstrap-CI / interaction columns exist in the printed table.
TABLE3_NOTE = dict(formula="Outcome ~ Age + Sex + (1|school_type)",
                   age_centered_at=15.0, sex_coding="0=Female,1=Male",
                   interaction_term_present=False)
TABLE3_PRINTED = {                       # age_beta, age_p, sex_beta(female-ref), sex_p
  "corsi_forward_span":       None,      # row not shown in excerpt
  "srt_mean_latency":         None,      # row not shown in excerpt
  "crt_mean_latency":         dict(age_beta=-19.631, age_p="<0.001", sex_beta=0.950, sex_p=0.4577),
  "stop_signal_rt":           dict(age_beta=-8.088,  age_p="<0.001", sex_beta=0.693, sex_p=0.2851),
  "rvp_sensitivity_dprime":   dict(age_beta=0.113,   age_p="<0.001", sex_beta=0.003, sex_p=0.7970),
  "processing_speed_index":   dict(age_beta=2.782,   age_p="<0.001", sex_beta=0.113, sex_p=0.7399),
}
TABLE3_PRINTS_VARIANCE_COMPONENTS = False   # prose promises them; table omits them
TABLE3_PRINTS_BOOTSTRAP_CI        = False
TABLE3_PRINTS_INTERACTION         = False

# ---- Internal contradictions that EXIST in the excerpt (genuine author fixes) ----
SEC71_CORSI_RANGES_IN_DOC = [(5.82, 7.64), (4.18, 5.79)]   # two incompatible sentences
PROSE_DISCUSSES_AGE_BY_SEX_INTERACTION = True               # Abstract + 6.4.2
PROSE_CLAIMS_R2_M = (0.285, 0.412)                          # Phase-2 prose
PROSE_CLAIMS_R2_C = (0.328, 0.448)
PROSE_CLAIMS_SCHOOL_RANDOM_INTERCEPTS = True
CLAIMS_40_SCHOOL_CLUSTERS = True                            # 5.1 / 6.4.3
NAMED_BATTERY_OUTCOMES = {"corsi_forward_span", "srt_mean_latency", "crt_mean_latency",
   "stop_signal_rt", "rvp_sensitivity_dprime", "rvp_decision_criterion_c",
   "processing_speed_index"}                                # note: includes 'c'
METHOD_ENGINE_PROMISED          = "R / lme4 / lmerTest / tidyverse"
METHOD_SATTERTHWAITE_PROMISED   = True
METHOD_BOOTSTRAP_1000_PROMISED  = True
INFOGRAPHIC_SSRT_VALUES_IN_CIRCULATION = (-8.088, -8.082)    # the static GitHub graphic
