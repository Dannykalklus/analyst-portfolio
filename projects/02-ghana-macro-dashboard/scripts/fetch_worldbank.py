"""Download annual Ghana macro indicators from the World Bank API (no key needed).
Usage: python scripts/fetch_worldbank.py  -> writes data/ghana_annual_worldbank.csv"""
import csv, json, urllib.request, pathlib

INDICATORS = {
    "FP.CPI.TOTL.ZG": "inflation_cpi_pct",
    "PA.NUS.FCRF": "usd_ghs_avg",
    "NY.GDP.MKTP.KD.ZG": "gdp_growth_pct",
    "NY.GDP.MKTP.CD": "gdp_usd",
    "BN.CAB.XOKA.GD.ZS": "current_account_pct_gdp",
    "FI.RES.TOTL.MO": "reserves_months_imports",
    "BX.TRF.PWKR.CD.DT": "remittances_usd",
}
START, END = 2000, 2025
out = pathlib.Path(__file__).resolve().parents[1] / "data" / "ghana_annual_worldbank.csv"

rows = {y: {"year": y} for y in range(START, END + 1)}
for code, name in INDICATORS.items():
    url = f"https://api.worldbank.org/v2/country/GH/indicator/{code}?format=json&per_page=200&date={START}:{END}"
    payload = json.load(urllib.request.urlopen(url, timeout=60))
    for obs in payload[1] or []:
        y = int(obs["date"])
        if y in rows:
            rows[y][name] = obs["value"]

fields = ["year"] + list(INDICATORS.values())
with out.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for y in sorted(rows):
        w.writerow({k: rows[y].get(k, "") for k in fields})
print(f"wrote {out} ({len(rows)} years)")
