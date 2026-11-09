# Tax Compliance Cost and SME Performance in Ghana (MSc research)

**Question:** Does the cost of complying with GRA tax obligations reduce SME performance, and does responsibility accounting weaken that effect?

**Report:** `index.html`

## Design
- Survey of 384 GRA-registered SMEs in Greater Accra (Google Forms, Sep-Oct 2026), 24 five-point Likert items.
- Constructs: tax compliance cost (8 items: monetary, time and psychological costs), responsibility accounting (8), firm outcomes (8: profitability and sales performance).
- PLS-SEM implemented from scratch in Python (`scripts/pls.py`: Lohmöller algorithm, mode A, path weighting). Moderation tested with the two-stage approach; inference from 5,000 percentile bootstrap resamples.

## Results
| Hypothesis | β | t | p | 95% CI | Decision |
|---|---|---|---|---|---|
| H1 Tax compliance cost → Firm outcomes | -0.294 | 6.66 | < .001 | [-0.383, -0.212] | Supported |
| H2 Responsibility accounting → Firm outcomes | +0.343 | 7.77 | < .001 | [0.262, 0.432] | Supported |
| H3 TCC × RA → Firm outcomes | +0.205 | 4.72 | < .001 | [0.117, 0.286] | Supported |

R² = 0.255. All loadings > 0.70, α and CR > 0.89, AVE > 0.58, HTMT < 0.40. The effect of compliance cost falls from -0.50 (weak responsibility accounting) to -0.09 (strong).

## Reproduce
```bash
python scripts/analyse.py path/to/responses.csv   # writes data/results.json, data/sample_profile.json
python scripts/build_report.py
```
Raw survey responses are not published, to protect respondents; they are available on request.

## Tools
Python (NumPy, pandas), PLS-SEM, bootstrapping, Chart.js.
