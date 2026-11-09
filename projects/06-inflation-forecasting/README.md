# Ghana Inflation Forecast

**Question:** Where will Ghana's headline inflation be in 12 months, and how much does the cedi drive it?

**Report:** `index.html`

## Data
- Monthly CPI (not seasonally adjusted) and GHS/USD, Jan 2000 to Jul 2026: World Bank Global Economic Monitor API (`CPTOTNSXN`, `DPANUSLCU`). Year-on-year rates match Ghana Statistical Service releases to one decimal place.
- Aug-Oct 2026 CPI extended with GSS year-on-year rates (`data/gss_recent_yoy.csv`, sources listed).

## Models and backtest (82 rolling forecast origins, Jan 2019 - Oct 2025)
| RMSE, pp | 1m | 3m | 6m | 12m |
|---|---|---|---|---|
| Random walk | 2.38 | 5.90 | 9.59 | 15.97 |
| SARIMA(1,0,1)(1,0,1)12 | 1.71 | 4.66 | 8.03 | 14.42 |
| ARDL with cedi depreciation | 1.93 | 4.61 | 7.85 | 13.73 |

## Results
- Base case (ARDL): inflation of 4.3-6.0% from Nov 2026 to Oct 2027, below the BoG target band of 8% ± 2%. Bands come from 1,500 bootstrapped simulations.
- Scenario: a 15% cedi depreciation over 12 months lifts inflation to about 8.0% by Oct 2027.
- Exchange-rate pass-through: about 17% within 12 months (p = 0.001); 0.68 in the long run.

## Reproduce
```bash
python scripts/fetch_data.py     # World Bank GEM API + GSS extension -> data/ghana_monthly.csv
python scripts/model.py          # backtest, forecast, pass-through -> data/results.json (~2 min)
python scripts/build_report.py
```

## Tools
Python (pandas, statsmodels: SARIMAX, OLS with HAC errors), bootstrap simulation, Chart.js.
