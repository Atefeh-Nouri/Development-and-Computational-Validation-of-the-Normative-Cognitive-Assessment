# Remaining doc_audit reds -> exact Word edits (run the matching mirror sed ONLY after editing the .docx)

[d04] Sec 7.1 has TWO conflicting Corsi ranges. Data supports 4.18 -> 5.79.
      EDIT Word: delete/rewrite the stale "5.82 blocks ... 7.64 blocks" sentence.
      THEN: sed -i 's/SEC71_CORSI_RANGES_IN_DOC = \[(5.82, 7.64), (4.18, 5.79)\]/SEC71_CORSI_RANGES_IN_DOC = [(4.18, 5.79)]/' src/manuscript_claims.py

[d05] 5.3 equation + Abstract/6.4.2 test Age x Sex, but Table 3 Note omits it.
      RECOMMENDED (consistent end-state = interaction everywhere, since data shows
      NON-significant interaction = the sex-invariance finding the paper argues for):
        - Table 3 Note -> "Outcome ~ Age + Sex + Age:Sex + (1|school_type)"
        - replace printed slopes with the interaction values in results/tables/table3_truth.csv
          (CRT -19.246, SSRT -8.228, PS 2.738, d' 0.113, ...) and ADD AgeXSex / ICC / R2 / CI columns.
      THEN: sed -i 's/interaction_term_present=False/interaction_term_present=True/' src/manuscript_claims.py
            and update TABLE3_PRINTED[...] age_beta to the interaction values.
      (Alternative: drop beta3 from 5.3 + the interaction discussion to match the Note.)

[d06] 5.1/6.4.3 claim 40 clusters + ICC 0.049-0.063 + R2_c 0.328-0.448 + "school random
      intercepts"; shipped file = 2-level school_type, ICC~0, R2_c up to 0.65, printed
      table has no variance columns.
      EITHER regenerate the .xlsx with a real 40-level school_id column (then re-run 00/02),
      OR reword 5.1/6.4.3 to "school_type as a 2-level institutional proxy; full 40-cluster
      ICC deferred to the live cohort" and set the prose R2_c band to the data range.
      THEN: sed -i 's/CLAIMS_40_SCHOOL_CLUSTERS = True/CLAIMS_40_SCHOOL_CLUSTERS = False/' src/manuscript_claims.py
            sed -i 's/PROSE_CLAIMS_R2_C = (0.328, 0.448)/PROSE_CLAIMS_R2_C = (0.301, 0.654)/' src/manuscript_claims.py
            sed -i 's/TABLE3_PRINTS_VARIANCE_COMPONENTS = False/TABLE3_PRINTS_VARIANCE_COMPONENTS = True/' src/manuscript_claims.py   # only after the Word table gains those columns

[d07] Text names RVP decision criterion c; data has d' but no c column.
      EITHER add rvp_decision_criterion_c to the generator + re-run, OR drop "c" from 5.2/6.2.
      THEN: sed -i 's/"rvp_decision_criterion_c",//' src/manuscript_claims.py   # only after the Word battery drops c

[d09] 5.3/Abstract promise Satterthwaite df via R/lmerTest; engine = statsmodels/Wald.
      (bootstrap half already satisfied by the --boot 1000 run above.)
      EITHER produce Table 3 df/p from the R script on this same .xlsx (point estimates match),
      OR reword 5.3 to "Wald z-tests (statsmodels); Satterthwaite df in the R replication archive".
      THEN: sed -i 's/METHOD_SATTERTHWAITE_PROMISED   = True/METHOD_SATTERTHWAITE_PROMISED   = False/' src/manuscript_claims.py
