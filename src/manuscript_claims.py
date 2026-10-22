"""
Manuscript mirror.

This file transcribes what the current PDF/docx asserts.
The audit compares this mirror to the data-derived truth manifest.

Canonical model from Table 3 Note:
  Outcome ~ Age + Sex + (1|school_type)
  Age centered at 15.0
  Sex dummy-coded: 0=Female, 1=Male
  No Age x Sex interaction in the reported Table 3 model.
"""

TABLE1_PER_AGE = {12: 286, 13: 286, 14: 286, 15: 286, 16: 286, 17: 285, 18: 285}

TABLE1_TOTALS = dict(
    N=2000,
    female=1022,
    male=978,
    public=1227,
    private=773,
    razavi=1000,
    south_khorasan=500,
    north_khorasan=500,
)

TABLE2_GRID_AVAILABLE = True

TABLE2 = {
    "corsi_forward_span":     [4.18, 4.36, 4.57, 4.87, 5.12, 5.52, 5.79],
    "srt_mean_latency":       [388.36, 375.80, 366.03, 352.09, 337.98, 324.03, 311.49],
    "crt_mean_latency":       [687.64, 670.48, 651.44, 629.94, 612.55, 591.26, 570.19],
    "stop_signal_rt":         [298.81, 292.99, 283.65, 275.84, 268.33, 258.40, 251.51],
    "rvp_sensitivity_dprime": [1.67, 1.75, 1.85, 1.96, 2.11, 2.19, 2.34],
    "processing_speed_index": [77.78, 80.98, 83.12, 86.71, 89.03, 92.04, 94.40],
}

TABLE3_NOTE = dict(
    formula="Outcome ~ Age + Sex + (1|school_type)",
    age_centered_at=15.0,
    sex_coding="0=Female,1=Male",
    interaction_term_present=False,
)

TABLE3_PRINTED = {
    "corsi_forward_span": dict(
        age_beta=0.275,
        age_p="<0.001",
        sex_beta=-0.033,
        sex_p=0.1762,
    ),
    "srt_mean_latency": dict(
        age_beta=-12.936,
        age_p="<0.001",
        sex_beta=0.246,
        sex_p=0.7818,
    ),
    "crt_mean_latency": dict(
        age_beta=-19.631,
        age_p="<0.001",
        sex_beta=0.950,
        sex_p=0.4577,
    ),
    "stop_signal_rt": dict(
        age_beta=-8.088,
        age_p="<0.001",
        sex_beta=0.693,
        sex_p=0.2851,
    ),
    "rvp_sensitivity_dprime": dict(
        age_beta=0.113,
        age_p="<0.001",
        sex_beta=0.003,
        sex_p=0.7970,
    ),
    "processing_speed_index": dict(
        age_beta=2.782,
        age_p="<0.001",
        sex_beta=0.113,
        sex_p=0.7399,
    ),
}

# The manuscript prose promises variance-partitioning diagnostics.
# If your printed Table 3 truly omits ICC/sigma2/R2 columns, set this False
# and edit the prose accordingly.
TABLE3_PRINTS_VARIANCE_COMPONENTS = True
TABLE3_PRINTS_BOOTSTRAP_CI = True
TABLE3_PRINTS_INTERACTION = False

SEC71_CORSI_RANGES_IN_DOC = [(4.18, 5.79)]

PROSE_DISCUSSES_AGE_BY_SEX_INTERACTION = False

PROSE_CLAIMS_R2_M = (0.285, 0.412)
PROSE_CLAIMS_R2_C = (0.328, 0.448)
PROSE_CLAIMS_SCHOOL_RANDOM_INTERCEPTS = True

# The explicit Table 3 Note uses school_type, not a 40-level school_id.
CLAIMS_40_SCHOOL_CLUSTERS = False

NAMED_BATTERY_OUTCOMES = {
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
    "processing_speed_index",
}

METHOD_ENGINE_PROMISED = "R / lme4 / lmerTest / tidyverse"
METHOD_SATTERTHWAITE_PROMISED = True
METHOD_BOOTSTRAP_1000_PROMISED = True

INFOGRAPHIC_SSRT_VALUES_IN_CIRCULATION = (-8.093, -8.093)  # regenerated from table3_truth.csv
