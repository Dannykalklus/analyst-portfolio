# MTN Ghana (Scancom PLC): Equity Valuation

**Question:** What is MTN Ghana worth per share, and how does that compare with its Ghana Stock Exchange price?

**Answer (base case, Oct 2026):** Blended fair value of about **GHS 8.42** against a market price of **GHS 6.67**, which implies roughly **26% upside**. On FY2025 earnings the stock trades at **11.3x P/E** and **5.9x EV/EBITDA** (including leases), with a **7.2% dividend yield**.

> Educational portfolio project, not investment advice.

## What's in the model
| Tab | Contents |
|---|---|
| Cover | Question, method, live key outputs |
| Inputs | Share price, CAPM inputs, and yearly drivers (all editable) |
| Historical | Audited FY2024 (restated) and FY2025 group statements, with balance-sheet and cash tie-out checks |
| Ratios | Growth mix, margins, ROE, liquidity and leverage with Mobile Money float stripped out, cash conversion, market multiples |
| Forecast | Revenue built by line (data, voice, MoMo, digital), margins, tax and levy, EPS, DPS, FCFE for 2026-2030 |
| Valuation | FCFE DCF, dividend discount model, blended value, Ke x g sensitivity grid |
| Sources | Every external figure, with links |

## Method
- **Revenue** is forecast by service line. Data and MoMo growth are calibrated to management's 2026 guidance (service revenue growth in the mid-to-upper 30s%), then fade toward nominal GDP growth.
- **Cost of equity** comes from CAPM in cedi terms: 364-day T-bill 9.67% + beta 1.0 × Ghana ERP 8.0% = **17.7%**. Terminal growth is 7%.
- **FCFE** = PAT + D&A − capex − lease principal − ΔNWC. Leases are treated as operating cash outflows, so they are not counted again as debt.
- **Mobile Money float** (GHS 38.4bn) is customer money held in trust, matched by e-money obligations. It is excluded from ratio and valuation work because it would otherwise distort liquidity and returns.

## Key findings
1. **Data is the growth engine.** It made up 55% of service revenue in FY2025 (50% in FY2024) and grew 48.8%. Voice fell to 16% of service revenue.
2. **Exceptional profitability.** EBITDA margin was 60.1%, ROE 63% and ROA excluding float 33%.
3. **Effectively debt-free.** Net debt including leases was negative (net cash) at end-2025.
4. **The valuation depends on discount rate assumptions.** Terminal value is about 64% of DCF equity value. Across Ke 15.7%-19.7% and g 5%-9%, the DCF value ranges from about GHS 6.10 to GHS 12.09.

## Limitations and next steps
- Only two years of history; extending to FY2021-FY2023 would show trends better.
- Beta is assumed at 1.0, because MTN makes up most of GSE turnover and a regression against the GSE-CI is circular.
- FY2024 financing cash-flow lines are not legible in the published PDF; only the total is used.
- Next: add a peer multiples comparison (other African MTN opcos, Airtel Africa) and a 2-page research note.

## Tools
Excel (driver-based modelling, DCF/DDM, sensitivity analysis). Data from audited financial statements.
