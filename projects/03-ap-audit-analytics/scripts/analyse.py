"""Audit analytics on City of Chicago 2025 vendor payments.
Tests: Benford first-digit and first-two-digit, round-amount payments, exact duplicate lines,
same-vendor same-amount payments under different vouchers within 30 days, reversals, vendor
and department concentration. Writes data/results.json and data/exceptions_*.csv.
Flags are audit risk indicators that call for follow-up, not findings of error or fraud."""
import json, pathlib
import numpy as np, pandas as pd

root = pathlib.Path(__file__).resolve().parents[1]
d = pd.read_csv(root / "data/chicago_payments_2025.csv", dtype={"voucher_number": str, "contract_number": str})
d["date"] = pd.to_datetime(d.check_date, format="%m/%d/%Y")
R0 = {"no_dept_rows": float(d.department_name.isna().mean()), "no_dept_value": float(d.loc[d.department_name.isna(), "amount"].sum() / d.amount.sum()),
      "no_dept_dv_share": float((d.loc[d.department_name.isna(), "contract_number"] == "DV").mean())}
d["department_name"] = d.department_name.fillna("(not recorded)")
R = {"rows": len(d), "total_usd": d.amount.sum(), "vendors": d.vendor_name.nunique(),
     "departments": int(d.department_name.nunique()), "date_min": str(d.date.min().date()), "date_max": str(d.date.max().date()), **R0}

# 1. Benford first digit (positive amounts >= $10)
pos = d[d.amount >= 10].copy()
digits = pos.amount.map(lambda x: f"{x:.2f}".lstrip("0")[:2])
pos["d1"] = digits.str[0].astype(int)
pos["d12"] = digits.str.replace(".", "", regex=False).str[:2].astype(int)
n = len(pos)
e1 = np.log10(1 + 1 / np.arange(1, 10)); o1 = pos.d1.value_counts(normalize=True).reindex(range(1, 10), fill_value=0).values
chi1 = float((((o1 - e1) ** 2) / e1).sum() * n)
mad1 = float(np.abs(o1 - e1).mean())
def nigrini1(m):  # Nigrini (2012) first-digit MAD thresholds
    return "Close conformity" if m < .006 else "Acceptable conformity" if m < .012 else "Marginal conformity" if m < .015 else "Nonconformity"
R["benford1"] = {"n": n, "observed": o1.round(4).tolist(), "expected": e1.round(4).tolist(), "mad": mad1,
                 "verdict": nigrini1(mad1), "chi2": chi1, "chi2_crit_8df_1pct": 20.09}

# 2. First-two digits
e2 = np.log10(1 + 1 / np.arange(10, 100)); o2 = pos.d12.value_counts(normalize=True).reindex(range(10, 100), fill_value=0).values
z = (np.abs(o2 - e2) - 1 / (2 * n)) / np.sqrt(e2 * (1 - e2) / n)
mad2 = float(np.abs(o2 - e2).mean())
spikes = pd.DataFrame({"digits": range(10, 100), "obs": o2, "exp": e2, "z": z, "excess_count": (o2 - e2) * n})
spikes = spikes[(spikes.z > 3.29) & (spikes.obs > spikes.exp)].sort_values("excess_count", ascending=False)
top_amounts = {}
for dg in spikes.digits.head(6):
    s = pos[pos.d12 == dg].amount.round(2).value_counts().head(3)
    top_amounts[int(dg)] = [[float(a), int(c)] for a, c in s.items()]
R["benford2"] = {"observed": o2.round(5).tolist(), "expected": e2.round(5).tolist(), "mad": mad2,
                 "verdict": "Close conformity" if mad2 < .0012 else "Acceptable conformity" if mad2 < .0018 else "Marginal conformity" if mad2 < .0022 else "Nonconformity",
                 "spikes": spikes.head(10).round(4).to_dict("records"), "spike_top_amounts": top_amounts}

# 3. Most frequent exact amounts
freq = pos.groupby(pos.amount.round(2)).agg(count=("amount", "size"), vendors=("vendor_name", "nunique")).sort_values("count", ascending=False).head(10)
R["frequent_amounts"] = [{"amount": float(a), "count": int(r["count"]), "vendors": int(r["vendors"])} for a, r in freq.iterrows()]

# 4. Round amounts (multiples of $1,000, >= $10,000)
rnd = pos[(pos.amount >= 10000) & ((pos.amount % 1000) == 0)]
R["round"] = {"count": len(rnd), "value": rnd.amount.sum(), "share_of_large": len(rnd) / max(1, (pos.amount >= 10000).sum())}
rnd.sort_values("amount", ascending=False).head(200).to_csv(root / "data/exceptions_round_amounts.csv", index=False)

# 5. Exact duplicate lines (all fields identical)
dup_lines = d[d.duplicated(keep=False)]
extra = d[d.duplicated(keep="first")]
R["dup_lines"] = {"rows_involved": len(dup_lines), "extra_rows": len(extra), "extra_value": extra.amount.sum()}
dup_lines.sort_values(["vendor_name", "amount"]).to_csv(root / "data/exceptions_duplicate_lines.csv", index=False)

# 6. Same vendor + same amount, different voucher, within 30 days (amounts >= $1,000)
big = d[d.amount >= 1000].sort_values(["vendor_name", "amount", "date"])
g = big.groupby(["vendor_name", "amount"])
big = big.assign(prev_date=g.date.shift(), prev_voucher=g.voucher_number.shift())
pairs = big[(big.prev_voucher.notna()) & (big.voucher_number != big.prev_voucher) & ((big.date - big.prev_date).dt.days <= 30)].copy()
pairs["days_apart"] = (pairs.date - pairs.prev_date).dt.days
recurring = pairs.groupby("vendor_name").size()
# vendors with many identical payments are usually fixed-fee contracts; isolate the rarer pairs
pairs["vendor_pairs"] = pairs.vendor_name.map(recurring)
susp = pairs[pairs.vendor_pairs <= 3].sort_values("amount", ascending=False)
R["near_dup"] = {"pairs_all": len(pairs), "value_all": pairs.amount.sum(), "pairs_isolated": len(susp),
                 "value_isolated": susp.amount.sum(), "top": susp.head(10)[["vendor_name", "department_name", "amount", "prev_date", "date", "prev_voucher", "voucher_number", "days_apart"]]
                 .assign(prev_date=lambda x: x.prev_date.dt.date.astype(str), date=lambda x: x.date.dt.date.astype(str)).to_dict("records")}
susp.drop(columns=["d1", "d12"], errors="ignore").to_csv(root / "data/exceptions_possible_duplicates.csv", index=False)

# 7. Reversals / credits
neg = d[d.amount < 0]
R["negatives"] = {"count": len(neg), "value": neg.amount.sum()}

# 8. Concentration
v = d.groupby("vendor_name").amount.sum().sort_values(ascending=False)
cum = v.cumsum() / v.sum()
R["vendor_conc"] = {"top10": v.head(10).round(0).to_dict(), "top10_share": float(v.head(10).sum() / v.sum()),
                    "vendors_for_80pct": int((cum < .8).sum() + 1), "vendor_count": len(v)}
dep = d.groupby("department_name").amount.agg(["sum", "size"]).sort_values("sum", ascending=False)
R["dept"] = [{"dept": k, "usd": float(r["sum"]), "n": int(r["size"])} for k, r in dep.head(10).iterrows()]
R["no_contract_share"] = float((d.contract_number == "DV").mean())
R["monthly"] = d.groupby(d.date.dt.to_period("M")).amount.sum().round(0).rename(lambda p: str(p)).to_dict()
R["weekday"] = d.date.dt.day_name().value_counts().to_dict()

(root / "data/results.json").write_text(json.dumps(R, indent=1, default=float))
print(json.dumps({k: R[k] for k in ["rows", "total_usd", "vendors", "benford1", "round", "dup_lines", "negatives", "no_contract_share"]}, indent=1, default=float))
print("near_dup", {k: R["near_dup"][k] for k in ["pairs_all", "value_all", "pairs_isolated", "value_isolated"]})
for t in R["near_dup"]["top"][:6]: print(t)
print("b2", R["benford2"]["mad"], R["benford2"]["verdict"]); print(R["benford2"]["spikes"][:6]); print(R["benford2"]["spike_top_amounts"])
print(R["frequent_amounts"][:6]); print(R["vendor_conc"]["top10_share"], R["vendor_conc"]["vendors_for_80pct"]); print(list(R["vendor_conc"]["top10"].items())[:5])
