# NCAD Codebook / Data Dictionary (Sheet 2 of dataset/NCAD_Iranian_Dataset.xlsx)

**Synthetic, empirically calibrated benchmark (N=2,000); disclosed as synthetic in Sec 6.1.**

| Variable                 | Label                    | Unit               | Valid_Range        | Description                                                                                                   |
|:-------------------------|:-------------------------|:-------------------|:-------------------|:--------------------------------------------------------------------------------------------------------------|
| participant_id           | Participant Id           | identifier         |                    | pseudonymous / decorative                                                                                     |
| age                      | Age                      | years              |                    | 12-18                                                                                                         |
| province                 | Province                 | category           |                    | Khorasan Razavi / South / North                                                                               |
| school_type              | School Type              | score              |                    | institutional clustering variable; random intercept (1|school_type); 2 levels (Public/Private)                |
| sex                      | Sex                      | score              |                    | dummy-coded in models: 0=Female, 1=Male                                                                       |
| grade                    | School grade             | grade              |                    | age-5 capped at 12                                                                                            |
| first_name               | First Name               | identifier         |                    | pseudonymous / decorative                                                                                     |
| last_name                | Last Name                | identifier         |                    | pseudonymous / decorative                                                                                     |
| corsi_forward_span       | Corsi Forward Span       | score              | 1.83 to 7.969      | outcome                                                                                                       |
| srt_mean_latency         | Srt Mean Latency         | ms                 | 169.129 to 518.815 | outcome                                                                                                       |
| crt_mean_latency         | Crt Mean Latency         | ms                 | 392.609 to 852.775 | outcome                                                                                                       |
| stop_signal_rt           | Stop Signal Rt           | ms                 | 195.053 to 361.506 | outcome                                                                                                       |
| rvp_sensitivity_dprime   | Rvp Sensitivity Dprime   | d-prime (unitless) | 0.341 to 3.306     | log-linear SDT correction applied upstream (Hautus 1995; Stanislaw & Todorov 1999): +0.5 hits/FA, +1.0 trials |
| processing_speed_index   | Processing Speed Index   | index points       | 58.61 to 114.427   | outcome                                                                                                       |
| corsi_backward_span      | Corsi Backward Span      | score              | 2.01 to 6.245      | outcome                                                                                                       |
| corsi_cumulative_errors  | Corsi Cumulative Errors  | score              | -1.879 to 13.999   | outcome                                                                                                       |
| srt_response_time_cv     | Srt Response Time Cv     | ratio (SD/mean)    | 0.043 to 0.415     | outcome                                                                                                       |
| crt_response_time_cv     | Crt Response Time Cv     | ratio (SD/mean)    | 0.042 to 0.441     | outcome                                                                                                       |
| rvp_decision_criterion_c | Rvp Decision Criterion C | c (unitless)       | -0.357 to 0.785    | log-linear SDT correction applied upstream                                                                    |
