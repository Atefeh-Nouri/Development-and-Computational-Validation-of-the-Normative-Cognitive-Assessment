"""
Generate the NCAD synthetic benchmark so that:
- Table 1 totals match the manuscript:
  N=2000; 1022 female, 978 male;
  public=1227, private=773;
  Khorasan Razavi=1000, South Khorasan=500, North Khorasan=500.
- Table 2 age means match the manuscript's developmental means.
- Table 3 sex effects match the manuscript's printed Sex_Beta values.
- Random school_type intercepts and residual variances are calibrated to
  produce ICC and Conditional R2 inside the manuscript's reported bands.
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20261015
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset" / "NCAD_Iranian_Dataset.xlsx"

AGES = [12, 13, 14, 15, 16, 17, 18]

N_PER_AGE = {12: 286, 13: 286, 14: 286, 15: 286, 16: 286, 17: 285, 18: 285}
SEX_TOTALS = {"female": 1022, "male": 978}

PROVINCE_QUOTA = {
    "Khorasan Razavi": 1000,
    "South Khorasan": 500,
    "North Khorasan": 500,
}

TYPE_QUOTA = {
    "Public": 1227,
    "Private": 773,
}

PROVINCE_TYPE_QUOTA = {
    "Khorasan Razavi": {"Public": 614, "Private": 386},
    "South Khorasan": {"Public": 306, "Private": 194},
    "North Khorasan": {"Public": 307, "Private": 193},
}

# Core outcomes: values transcribed from the manuscript tables/prose.
CORE_TARGETS = {
    "corsi_forward_span": dict(
        means=[4.18, 4.36, 4.57, 4.87, 5.12, 5.52, 5.79],
        beta_age=0.275,
        beta_sex=-0.033,
        icc=0.061,
        r2c=0.330,
    ),
    "srt_mean_latency": dict(
        means=[388.36, 375.80, 366.03, 352.09, 337.98, 324.03, 311.49],
        beta_age=-12.936,
        beta_sex=0.246,
        icc=0.063,
        r2c=0.360,
    ),
    "crt_mean_latency": dict(
        means=[687.64, 670.48, 651.44, 629.94, 612.55, 591.26, 570.19],
        beta_age=-19.631,
        beta_sex=0.950,
        icc=0.061,
        r2c=0.420,
    ),
    "stop_signal_rt": dict(
        means=[298.81, 292.99, 283.65, 275.84, 268.33, 258.40, 251.51],
        beta_age=-8.088,
        beta_sex=0.693,
        icc=0.056,
        r2c=0.390,
    ),
    "rvp_sensitivity_dprime": dict(
        means=[1.67, 1.75, 1.85, 1.96, 2.11, 2.19, 2.34],
        beta_age=0.113,
        beta_sex=0.003,
        icc=0.049,
        r2c=0.340,
    ),
    "processing_speed_index": dict(
        means=[77.78, 80.98, 83.12, 86.71, 89.03, 92.04, 94.40],
        beta_age=2.782,
        beta_sex=0.113,
        icc=0.062,
        r2c=0.400,
    ),
}

# Supplementary outcomes named in the battery / present in the dataset.
SUPPLEMENTAL_TARGETS = {
    "corsi_backward_span": dict(
        means=[3.50, 3.70, 3.90, 4.10, 4.30, 4.50, 4.70],
        beta_sex=0.0,
        icc=0.055,
        r2c=0.380,
    ),
    "corsi_cumulative_errors": dict(
        means=[9.50, 8.80, 8.10, 7.40, 6.70, 6.00, 5.30],
        beta_sex=0.0,
        icc=0.055,
        r2c=0.380,
    ),
    "srt_response_time_cv": dict(
        means=[0.285, 0.262, 0.241, 0.222, 0.206, 0.192, 0.182],
        beta_sex=0.0,
        icc=0.055,
        r2c=0.380,
    ),
    "crt_response_time_cv": dict(
        means=[0.298, 0.276, 0.254, 0.235, 0.218, 0.204, 0.194],
        beta_sex=0.0,
        icc=0.055,
        r2c=0.380,
    ),
    "rvp_decision_criterion_c": dict(
        means=[0.412, 0.358, 0.305, 0.252, 0.204, 0.161, 0.125],
        beta_sex=0.0,
        icc=0.055,
        r2c=0.380,
    ),
}


def solve_random_variances(fixed_var: float, icc: float, r2_cond: float) -> tuple[float, float]:
    """
    Given:
      ICC = u / (u + e)
      R2c = (F + u) / (F + u + e)

    Solve for u and e.
    """
    r = float(icc)
    R = float(r2_cond)
    F = max(float(fixed_var), 1e-12)

    if R <= r + 1e-8:
        # Fallback: keep ICC target but make random variance tiny.
        u = 1e-6
        e = max(F * (1.0 - R) / max(R, 1e-6), 1e-6)
        return u, e

    u = r * F * (1.0 - R) / (R - r)
    e = u * (1.0 - r) / r

    return max(u, 1e-8), max(e, 1e-8)


def make_demographics(rng: np.random.Generator) -> pd.DataFrame:
    n = sum(N_PER_AGE.values())

    ages = np.concatenate([[a] * cnt for a, cnt in N_PER_AGE.items()])

    slots = []
    for prov, types in PROVINCE_TYPE_QUOTA.items():
        for typ, cnt in types.items():
            slots.extend([(prov, typ)] * cnt)

    assert len(slots) == n
    rng.shuffle(slots)

    df = pd.DataFrame(
        {
            "participant_id": [f"NCAD-{i + 1:04d}" for i in range(n)],
            "age": ages,
            "province": [s[0] for s in slots],
            "school_type": [s[1] for s in slots],
        }
    )

    # Assign sex stratified by age x school_type to avoid sex confounding
    # with the random school_type intercept.
    male_total = SEX_TOTALS["male"]
    female_total = SEX_TOTALS["female"]
    assert male_total + female_total == n

    sex = np.array(["female"] * n, dtype=object)

    cell_groups = list(df.groupby(["age", "school_type"]).indices.values())
    counts = np.array([len(g) for g in cell_groups], dtype=float)

    raw_male = counts * (male_total / n)
    male_counts = np.floor(raw_male).astype(int)

    rem = male_total - int(male_counts.sum())
    if rem > 0:
        frac = raw_male - male_counts
        order = np.argsort(-frac)
        male_counts[order[:rem]] += 1
    elif rem < 0:
        # Rare rounding correction.
        order = np.argsort(male_counts)
        male_counts[order[:(-rem)]] -= 1

    for g, m in zip(cell_groups, male_counts):
        if m > 0:
            choose = rng.choice(np.asarray(g), size=int(m), replace=False)
            sex[choose] = "male"

    assert (sex == "male").sum() == male_total
    assert (sex == "female").sum() == female_total

    df["sex"] = sex
    df["grade"] = np.minimum(df["age"].astype(int) - 5, 12)

    # Decorative identity fields, deterministic from seed.
    FN_F = [
        "Fatemeh", "Zahra", "Maryam", "Reyhaneh", "Narges",
        "Sara", "Yasaman", "Parisa", "Mahsa", "Elaheh",
    ]
    FN_M = [
        "Amirhossein", "Mohammad", "Ali", "Reza", "Sina",
        "Arman", "Parsa", "Hossein", "Mehdi", "Kian",
    ]
    LN = [
        "Nouri", "Karimi", "Rezaei", "Mousavi", "Hosseini",
        "Ahmadi", "Moradi", "Ghasemi", "Sadeghi", "Jafari",
    ]

    first = []
    for s in df["sex"]:
        pool = FN_F if s == "female" else FN_M
        first.append(pool[int(rng.integers(0, len(pool)))])

    df["first_name"] = first
    df["last_name"] = [LN[int(rng.integers(0, len(LN)))] for _ in range(n)]

    return df


def generate_outcome(
    df: pd.DataFrame,
    rng: np.random.Generator,
    col: str,
    means: list[float],
    beta_age: float,
    beta_sex: float,
    icc: float,
    r2c: float,
) -> np.ndarray:
    n = len(df)

    age_arr = df["age"].to_numpy(dtype=float)
    age_c = age_arr - 15.0

    male_arr = (df["sex"].to_numpy() == "male")
    male_float = male_arr.astype(float)

    fixed = beta_age * age_c + beta_sex * male_float
    F = float(np.var(fixed))

    u_var, e_var = solve_random_variances(F, icc=icc, r2_cond=r2c)

    type_codes = pd.Categorical(df["school_type"]).codes
    type_counts = np.bincount(type_codes)

    type_effects = rng.normal(0.0, np.sqrt(u_var), size=len(type_counts))
    type_effects -= np.average(type_effects, weights=type_counts)
    u_i = type_effects[type_codes]

    e = rng.normal(0.0, np.sqrt(e_var), size=n)

    y = fixed + u_i + e

    # Force exact age marginal means and exact within-age male-female difference.
    for i, a in enumerate(AGES):
        age_mask = age_arr == float(a)
        m_mask = age_mask & male_arr
        f_mask = age_mask & (~male_arr)

        target = float(means[i])
        n_age = int(age_mask.sum())
        n_male = int(m_mask.sum())
        pm = n_male / n_age if n_age else 0.0

        mean_female = target - pm * beta_sex
        mean_male = target + (1.0 - pm) * beta_sex

        if n_male > 0:
            y[m_mask] += mean_male - y[m_mask].mean()
        if (n_age - n_male) > 0:
            y[f_mask] += mean_female - y[f_mask].mean()

    return np.round(y, 3)


def main() -> None:
    rng = np.random.default_rng(SEED)

    df = make_demographics(rng)

    all_targets = {}

    for label, spec in CORE_TARGETS.items():
        all_targets[label] = spec

    for label, spec in SUPPLEMENTAL_TARGETS.items():
        means = spec["means"]
        # Estimate beta_age from the target means themselves.
        x = np.array([a - 15.0 for a in AGES], dtype=float)
        beta_age = float(np.polyfit(x, np.array(means, dtype=float), 1)[0])
        all_targets[label] = dict(
            means=means,
            beta_age=beta_age,
            beta_sex=spec.get("beta_sex", 0.0),
            icc=spec.get("icc", 0.055),
            r2c=spec.get("r2c", 0.38),
        )

    for col, spec in all_targets.items():
        df[col] = generate_outcome(
            df,
            rng,
            col=col,
            means=spec["means"],
            beta_age=spec["beta_age"],
            beta_sex=spec["beta_sex"],
            icc=spec["icc"],
            r2c=spec["r2c"],
        )
        print(f"[gen] generated {col}")

    with pd.ExcelWriter(DATA, engine="openpyxl") as xw:
        df.to_excel(xw, sheet_name="Simulated Data", index=False, startrow=1)
        xw.sheets["Simulated Data"]["A1"] = (
            "NCAD Iranian Synthetic Benchmark Dataset - calibrated to manuscript "
            "Tables 1-3 (src/generate_synthetic_data.py, SEED=20261015)"
        )

    print(f"[gen] wrote {DATA}")
    print(f"[gen] N={len(df)}")
    print(f"[gen] schools/types={df['school_type'].nunique()}")
    print(f"[gen] columns={list(df.columns)}")


if __name__ == "__main__":
    main()
