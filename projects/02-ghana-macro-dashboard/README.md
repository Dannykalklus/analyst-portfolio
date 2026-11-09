# Ghana Macro Dashboard

**Question:** How far has Ghana's economy recovered since the 2022-2023 crisis, and how tight is monetary policy now?

**Live dashboard:** `index.html` (open in a browser).

## Data (all real, all sourced)
| File | Coverage | Source |
|---|---|---|
| `data/ghana_annual_worldbank.csv` | 2000-2025, annual | World Bank WDI API: inflation, USD/GHS, GDP growth, GDP, current account, reserves, remittances |
| `data/ghana_monthly_2025_2026.csv` | Jan 2025 - Oct 2026, monthly | Ghana Statistical Service CPI releases and Bank of Ghana MPC decisions. The source is listed on every row |

## Reproduce
```bash
python scripts/fetch_worldbank.py     # refresh annual data from the World Bank API
python scripts/build_dashboard.py     # rebuild index.html from the CSVs
```
To add a new month, append a row to the monthly CSV with its source, then rebuild.

## Findings
1. Inflation fell from 23.5% (Jan 2025) to 3.2% (Mar 2026), then rose back to 5.5% by Oct 2026.
2. The Bank of Ghana cut the policy rate by 1,400 bp (28% to 14%), but the real policy rate rose from 3.5 pp to a peak of 14.3 pp, because inflation fell faster than the rate.
3. 2025 was the only year since 2000 in which the cedi's average rate against the dollar strengthened (-11.5%).
4. The current account showed a surplus of 8.2% of GDP in 2025, after deficits of 7-12% in 2008-2013.

## Tools
Python (standard library), World Bank API, Chart.js, HTML/CSS.
