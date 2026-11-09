"""Monthly Ghana CPI (not seasonally adjusted) and GHS/USD exchange rate from the World Bank
Global Economic Monitor (source 15), 2000M01 onward. Extends CPI past the GEM's last month using
Ghana Statistical Service year-on-year rates listed in data/gss_recent_yoy.csv.
Usage: python scripts/fetch_data.py -> data/ghana_monthly.csv"""
import json, urllib.request, pathlib
import pandas as pd
root = pathlib.Path(__file__).resolve().parents[1]
def gem(code):
    u = f"https://api.worldbank.org/v2/country/GH/indicator/{code}?source=15&format=json&per_page=2000&date=2000M01:2030M12"
    obs = json.load(urllib.request.urlopen(u, timeout=60))[1]
    s = pd.Series({pd.Period(o["date"].replace("M", "-"), "M"): o["value"] for o in obs if o["value"] is not None}).sort_index()
    return s
cpi, fx = gem("CPTOTNSXN"), gem("DPANUSLCU")
df = pd.DataFrame({"cpi": cpi, "usd_ghs": fx})
df["cpi_source"] = df.cpi.notna().map({True: "World Bank GEM", False: ""})
gss = pd.read_csv(root / "data/gss_recent_yoy.csv")
for _, r in gss.iterrows():
    p = pd.Period(r.month, "M")
    if p not in df.index or pd.isna(df.loc[p, "cpi"]):
        base = df.loc[p - 12, "cpi"]
        df.loc[p, "cpi"] = base * (1 + r.yoy_pct / 100); df.loc[p, "cpi_source"] = f"Extended with GSS YoY ({r.source})"
df = df.sort_index()
df["inflation_yoy"] = (df.cpi / df.cpi.shift(12) - 1) * 100
df["depreciation_yoy"] = (df.usd_ghs / df.usd_ghs.shift(12) - 1) * 100
df.index.name = "month"; df.to_csv(root / "data/ghana_monthly.csv")
print(df.tail(16).round(2).to_string())
