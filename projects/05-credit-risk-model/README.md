# Credit Default Risk Model

**Question:** Which credit card customers will default next month, and how should a lender use the scores?

**Data:** UCI *Default of Credit Card Clients* (Yeh & Lien, 2009). 30,000 real accounts, six months of repayment, bill and payment history, 22.1% default rate. **Report:** `index.html`

## Results (held-out test set, 9,000 accounts)
| Model | CV AUC | Test AUC | Gini | KS |
|---|---|---|---|---|
| Logistic regression | 0.762 | 0.748 | 0.50 | 0.40 |
| Gradient boosting | 0.787 | 0.780 | 0.56 | 0.42 |

- Declining the riskiest 20% of accounts catches 51% of defaulters and cuts the approved book's bad rate from 22.1% to 13.6%.
- Repayment behaviour is the strongest driver. Customers one month late default at 34%, against 13% for those paying on time.
- Sex and marital status are excluded on fair-lending grounds.

## Reproduce
```bash
python scripts/model.py          # feature engineering, cross-validation, test metrics -> data/results.json
python scripts/build_report.py   # renders index.html
```

## Tools
Python (pandas, scikit-learn: logistic regression, HistGradientBoosting), ROC/AUC, KS, Gini, Brier score, Chart.js.
