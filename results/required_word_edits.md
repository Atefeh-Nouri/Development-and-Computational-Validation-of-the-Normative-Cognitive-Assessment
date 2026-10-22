# 3 mandatory Word edits (then the repo == the PDF)

1) Sec 7.1 - DELETE both stale Corsi sentences (search "5.82" and "4.18 ± 0.40"):
     "rising from 5.82 blocks at 12.0 years to 7.64 blocks at 18.9 years"
     "rising from 4.18 ± 0.40 blocks at age 12 to 5.79 ± 0.60 blocks at age 18 (β = 0.275, p < 0.001)"
   REPLACE WITH (matches Table 2 + Table 3):
     "rising from 5.21 blocks at age 12 to 6.84 blocks at age 18 (β1 = 0.271, p < .001)."

2) Table 3 Note - ADD the interaction term the paper's own Sec 5.3 equation already has:
     FIND:    Outcome ~ Age + Sex + (1|school_type)
     REPLACE: Outcome ~ Age + Sex + Age:Sex + (1|school_type)

3) Sec 6.4.3 prose - Conditional R2 band (arithmetic of Table 3's own β/σ2 gives 0.292 for Corsi):
     FIND:    0.328–0.448      REPLACE: 0.292–0.448
   (optional: Marginal R2 band 0.285–0.412 -> 0.246–0.412)
