"""Build index.html from the two CSV files. Usage: python scripts/build_dashboard.py"""
import csv, json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
ann = list(csv.DictReader(open(root/"data/ghana_annual_worldbank.csv")))
mon = list(csv.DictReader(open(root/"data/ghana_monthly_2025_2026.csv")))
f = lambda v: None if v in ("", None) else float(v)
A = {k: [f(r[k]) for r in ann] for k in ann[0] if k != "year"}
A["year"] = [int(r["year"]) for r in ann]
M = {"month": [r["month"] for r in mon],
     "infl": [f(r["inflation_yoy_pct"]) for r in mon],
     "mpr": [f(r["policy_rate_pct"]) for r in mon]}
M["real"] = [round(p - i, 1) for p, i in zip(M["mpr"], M["infl"])]
fx = A["usd_ghs_avg"]
A["fx_change"] = [None] + [round((fx[i]/fx[i-1]-1)*100, 1) for i in range(1, len(fx))]
last = -1
kpi = {
 "infl": M["infl"][last], "infl_prev": M["infl"][last-1], "mpr": M["mpr"][last],
 "real": M["real"][last], "real_start": M["real"][0], "month": M["month"][last],
 "gdp": A["gdp_growth_pct"][last], "ca": A["current_account_pct_gdp"][last],
 "res": A["reserves_months_imports"][last], "fx25": fx[last], "fx24": fx[-2],
 "fxchg": A["fx_change"][last], "gdpusd": A["gdp_usd"][last]/1e9,
}
html = (root/"scripts/template.html").read_text()
html = html.replace("/*DATA*/", "const A=%s;const M=%s;const K=%s;" % (json.dumps(A), json.dumps(M), json.dumps(kpi)))
(root/"index.html").write_text(html)
print(json.dumps(kpi, indent=1))
