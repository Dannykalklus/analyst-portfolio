"""PLS-SEM: Tax compliance cost (TCC) -> Firm outcomes (FO), moderated by responsibility accounting (RA).
Two-stage approach for the interaction (Hair et al., 2022). 5,000 bootstrap resamples.
Input: the survey export (CSV path as first argument). Writes data/results.json and data/sample_profile.json.
Usage: python scripts/analyse.py <responses.csv>"""
import sys, json, pathlib
import numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from pls import pls, structural, reliability, htmt, zs

root = pathlib.Path(__file__).resolve().parents[1]
raw = pd.read_csv(sys.argv[1])
L = raw[raw.columns[9:]].apply(lambda s: s.str[0].astype(int)); L.columns = [c.split(".")[0] for c in L.columns]
B = {"TCC": [f"TCC{i}" for i in range(1, 9)], "RA": [f"RA{i}" for i in range(1, 9)], "FO": [f"FO{i}" for i in range(1, 9)]}
PATHS = [("TCC", "FO"), ("RA", "FO")]

def estimate(df):
    s, w, l, Xs = pls(df, B, PATHS)
    main, r2_main = structural(s, {"FO": ["TCC", "RA"]})
    s2 = s.copy(); s2["INT"] = zs((s.TCC * s.RA).values)
    full, r2_full = structural(s2, {"FO": ["TCC", "RA", "INT"]})
    return s, w, l, Xs, main, r2_main, full, r2_full

s, w, l, Xs, main, r2m, full, r2f = estimate(L)
R = {"n": len(L)}
R["loadings"] = {lv: dict(zip(B[lv], np.round(l[lv], 3).tolist())) for lv in B}
R["reliability"] = {lv: {k: round(float(v), 3) for k, v in d.items()} for lv, d in reliability(Xs, w, l).items()}
# discriminant validity
H = {"PROF": B["FO"][:4], "SALES": B["FO"][4:], "TCC": B["TCC"], "RA": B["RA"]}
R["htmt_fo_split"] = round(float(htmt(L, H)[("PROF", "SALES")]), 3)
R["htmt"] = {f"{a}-{b}": round(float(v), 3) for (a, b), v in htmt(L, B).items()}
corr = s.corr(); R["fornell_larcker"] = {lv: {"sqrt_ave": round(float(np.sqrt(R["reliability"][lv]["ave"])), 3),
                                                "max_corr": round(float(corr[lv].drop(lv).abs().max()), 3)} for lv in B}
# inner VIF
r = np.corrcoef(s.TCC, s.RA)[0, 1]; R["vif_inner"] = round(float(1 / (1 - r ** 2)), 3)
R["r2_main"] = round(float(r2m["FO"]), 3); R["r2_full"] = round(float(r2f["FO"]), 3)
# f2 for each predictor in the full model
def r2_without(drop):
    s2 = s.copy(); s2["INT"] = zs((s.TCC * s.RA).values)
    return structural(s2, {"FO": [x for x in ["TCC", "RA", "INT"] if x != drop]})[1]["FO"]
R["f2"] = {x: round(float((r2f["FO"] - r2_without(x)) / (1 - r2f["FO"])), 3) for x in ["TCC", "RA", "INT"]}

# bootstrap
rng = np.random.default_rng(42); NB = 5000; boot = []
for b in range(NB):
    idx = rng.integers(0, len(L), len(L)); df = L.iloc[idx].reset_index(drop=True)
    *_, f2_, _ = estimate(df)
    boot.append([f2_[("TCC", "FO")], f2_[("RA", "FO")], f2_[("INT", "FO")]])
boot = np.array(boot)
est = np.array([full[("TCC", "FO")], full[("RA", "FO")], full[("INT", "FO")]])
labels = ["H1: TCC -> FO", "H2: RA -> FO", "H3: TCC x RA -> FO"]
R["paths"] = []
for i, lab in enumerate(labels):
    se = boot[:, i].std(ddof=1); t = est[i] / se
    p = 2 * min((boot[:, i] <= 0).mean(), (boot[:, i] >= 0).mean())
    lo, hi = np.percentile(boot[:, i], [2.5, 97.5])
    R["paths"].append({"hypothesis": lab, "beta": round(float(est[i]), 3), "se": round(float(se), 3), "t": round(float(t), 2),
                       "p": float(p), "ci_low": round(float(lo), 3), "ci_high": round(float(hi), 3), "supported": bool(lo > 0 or hi < 0)})
# simple slopes (standardised): effect of TCC on FO at RA = -1, 0, +1 SD
R["simple_slopes"] = {str(k): round(float(est[0] + est[2] * k), 3) for k in (-1, 0, 1)}
R["n_boot"] = NB
(root / "data/results.json").write_text(json.dumps(R, indent=1))

prof = {c.split(". ", 1)[1]: raw[c].value_counts().to_dict() for c in raw.columns[2:9] if raw[c].nunique() > 1}
(root / "data/sample_profile.json").write_text(json.dumps(prof, indent=1))
print(json.dumps({k: R[k] for k in ["reliability", "htmt", "htmt_fo_split", "fornell_larcker", "vif_inner", "r2_main", "r2_full", "f2", "paths", "simple_slopes"]}, indent=1))
