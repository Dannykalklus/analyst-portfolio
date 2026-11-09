# Accounts Payable Audit Analytics

**Question:** If I were auditing this payables ledger, which payments would I select for follow-up, and why?

**Data:** every City of Chicago vendor payment with a 2025 check date: 115,797 lines, $10.66bn, 17,685 vendors. Source: City of Chicago Data Portal, *Payments* (dataset `s4vu-giwb`), downloaded through the Socrata API.

**Report:** `index.html`

## Tests
| Test | Result |
|---|---|
| Benford's Law, first digit (Nigrini MAD) | 0.0090, acceptable conformity; excess on digit 5 |
| Benford's Law, first two digits | 0.0022, nonconformity; spikes at 50, 15, 77, 75 traced to fixed $50, $500, $775, $1,550 payments |
| Same vendor, same amount, different voucher, within 30 days | 832 pairs, $146.6m (after excluding vendors with recurring fixed payments) |
| Fully identical lines | 1,056 repeat rows, $371.0m |
| Missing department coding | 54.1% of lines, 56.9% of value |
| Vendor concentration | Top 10 vendors 37.8%; 129 vendors make up 80% of spend |

Exception lists for follow-up are in `data/exceptions_*.csv`.

## Reproduce
```bash
python scripts/fetch_payments.py   # ~9 MB download from the Chicago open data API
python scripts/analyse.py          # runs the tests, writes data/results.json and the exception files
python scripts/build_report.py     # renders index.html
```

## Caveat
Flags are risk indicators that need follow-up with supporting documents. They are not findings of error or fraud. This is an independent portfolio exercise, not an audit of the City of Chicago.

## Tools
Python (pandas, NumPy), Benford analysis (Nigrini 2012 thresholds), Chart.js.
