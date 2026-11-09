"""Download all City of Chicago vendor payments with a 2025 check date (Socrata open data API).
Usage: python scripts/fetch_payments.py -> data/chicago_payments_2025.csv"""
import csv, json, time, urllib.request, urllib.parse, pathlib
BASE = "https://data.cityofchicago.org/resource/s4vu-giwb.json"
out = pathlib.Path(__file__).resolve().parents[1] / "data" / "chicago_payments_2025.csv"
fields = ["voucher_number", "amount", "check_date", "department_name", "contract_number", "vendor_name"]
rows, offset, page = [], 0, 50000
while True:
    q = urllib.parse.urlencode({"$where": "check_date like '%2025'", "$order": "voucher_number",
                                "$limit": page, "$offset": offset})
    for attempt in range(5):
        try:
            batch = json.load(urllib.request.urlopen(f"{BASE}?{q}", timeout=180)); break
        except Exception as e:
            print("retry", attempt, e); time.sleep(5)
    rows += batch; print(f"fetched {len(rows)}")
    if len(batch) < page: break
    offset += page
with out.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
    for r in rows: w.writerow({k: r.get(k, "") for k in fields})
print("wrote", out, len(rows))
