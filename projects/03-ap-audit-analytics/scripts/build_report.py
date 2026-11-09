"""Render index.html (audit report) from data/results.json. Usage: python scripts/build_report.py"""
import json, pathlib, html
root = pathlib.Path(__file__).resolve().parents[1]
R = json.loads((root / "data/results.json").read_text())
style = (root / "scripts/style.css").read_text()
m = lambda x: f"${x/1e6:,.1f}m"
bn = lambda x: f"${x/1e9:,.2f}bn"
pct = lambda x: f"{x*100:.1f}%"
esc = html.escape
b1, b2, nd, dl = R["benford1"], R["benford2"], R["near_dup"], R["dup_lines"]
spike_rows = "".join(
    f"<tr><td class='num'>{s['digits']}</td><td class='num'>{s['obs']*100:.2f}%</td><td class='num'>{s['exp']*100:.2f}%</td><td class='num'>{s['z']:.1f}</td>"
    f"<td>{', '.join(f'${a:,.2f} ({c:,}x)' for a, c in R['benford2']['spike_top_amounts'].get(str(s['digits']), []))}</td></tr>"
    for s in b2["spikes"][:6])
pair_rows = "".join(
    f"<tr><td>{esc(p['vendor_name'].title())}</td><td class='num'>{p['amount']:,.2f}</td><td class='num'>{p['prev_date']}</td><td class='num'>{p['date']}</td><td class='num'>{p['days_apart']}</td></tr>"
    for p in nd["top"][:8])
data = {"b1o": b1["observed"], "b1e": b1["expected"], "b2o": b2["observed"], "b2e": b2["expected"],
        "vend": [[k.title(), v] for k, v in R["vendor_conc"]["top10"].items()],
        "dept": [[d["dept"].title(), d["usd"]] for d in R["dept"]], "mon": R["monthly"]}
page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Accounts Payable Audit Analytics</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
{style}
<style>
table{{border-collapse:collapse;width:100%;font-size:.84rem}}th,td{{padding:6px 8px;border-bottom:1px solid var(--rule);text-align:left;vertical-align:top}}
thead th{{border-bottom:1px solid var(--ink);font-weight:600}}td.num,th.num{{text-align:right}}
.scroll{{overflow-x:auto}}.verdict{{font-family:var(--mono);font-size:.75rem;border:1px solid var(--gold);color:var(--gold);padding:2px 8px;display:inline-block;margin-top:6px}}
.findings h3{{font-family:var(--display);font-size:1.05rem;margin:18px 0 4px}}.findings p{{margin:0 0 6px;max-width:80ch}}
.proc{{font-size:.88rem;color:var(--muted)}}
</style></head>
<body>
<header><div class="wrap"><strong style="font-family:var(--display)">Daniel N. T. Tackie</strong><a class="back" href="../../index.html">Back to portfolio</a></div></header>
<main class="wrap">
<h1>Accounts payable audit analytics</h1>
<p class="lede">Data analytics tests that an internal or external auditor would run on a payables ledger, applied to every vendor payment the City of Chicago made in 2025 ({R['rows']:,} payment lines, {bn(R['total_usd'])}). Flags are risk indicators that call for follow-up, not conclusions of error or fraud.</p>
<div class="tiles">
 <div class="tile"><div class="l">Payment lines</div><div class="v num">{R['rows']/1000:,.1f}k</div><div class="s">{R['date_min']} to {R['date_max']}</div></div>
 <div class="tile"><div class="l">Total paid</div><div class="v num">{bn(R['total_usd'])}</div><div class="s">{R['vendors']:,} vendors</div></div>
 <div class="tile"><div class="l">No department</div><div class="v num">{pct(R['no_dept_rows'])}</div><div class="s">of lines; {pct(R['no_dept_value'])} of value</div></div>
 <div class="tile"><div class="l">Possible duplicates</div><div class="v num">{nd['pairs_isolated']:,}</div><div class="s">pairs, {m(nd['value_isolated'])}</div></div>
 <div class="tile"><div class="l">Identical lines</div><div class="v num">{dl['extra_rows']:,}</div><div class="s">repeat rows, {m(dl['extra_value'])}</div></div>
 <div class="tile"><div class="l">Benford, 1st digit</div><div class="v num">{b1['mad']:.4f}</div><div class="s">MAD: {b1['verdict'].lower()}</div></div>
</div>

<div class="grid">
 <div class="card"><h2>Benford's Law: first digit</h2><p class="sub">Share of payments by leading digit vs Benford expectation, {b1['n']:,} payments of $10 or more</p>
  <div class="chart"><canvas id="c1" aria-label="Benford first digit chart"></canvas></div>
  <span class="verdict">MAD {b1['mad']:.4f}: {b1['verdict']} (Nigrini)</span>
  <p class="note">The ledger as a whole fits Benford acceptably. The one clear excess is digit 5 ({b1['observed'][4]*100:.1f}% vs {b1['expected'][4]*100:.1f}% expected), which the two-digit test traces to fixed $50 and $500 payments.</p></div>
 <div class="card"><h2>Benford's Law: first two digits</h2><p class="sub">Observed vs expected share, digits 10 to 99</p>
  <div class="chart"><canvas id="c2" aria-label="Benford first two digits chart"></canvas></div>
  <span class="verdict">MAD {b2['mad']:.4f}: {b2['verdict']} (Nigrini)</span>
  <p class="note">At two-digit level the ledger does not conform, because many payments are standard fixed amounts. Each spike below can be traced to a small set of exact amounts.</p></div>
 <div class="card wide"><h2>Where the digit spikes come from</h2><p class="sub">Two-digit combinations significantly above expectation (z &gt; 3.29, p &lt; 0.001), with the exact amounts driving them</p>
  <div class="scroll"><table><thead><tr><th class="num">Digits</th><th class="num">Observed</th><th class="num">Expected</th><th class="num">z</th><th>Most common amounts</th></tr></thead><tbody>{spike_rows}</tbody></table></div>
  <p class="note">Almost all of these are direct vouchers with no contract and no department recorded. A $50 payment went to {R['frequent_amounts'][0]['vendors']:,} different payees, which points to a standard program payment, refund or stipend. An auditor would confirm each fixed amount against an approved rate schedule.</p></div>
 <div class="card wide"><h2>Possible duplicate payments</h2><p class="sub">Same vendor, same amount (≥ $1,000), different voucher number, paid within 30 days. Vendors with more than three such pairs are excluded as likely fixed recurring payments.</p>
  <div class="scroll"><table><thead><tr><th>Vendor</th><th class="num">Amount ($)</th><th class="num">First paid</th><th class="num">Paid again</th><th class="num">Days apart</th></tr></thead><tbody>{pair_rows}</tbody></table></div>
  <p class="note">{nd['pairs_isolated']:,} pairs worth {m(nd['value_isolated'])} meet the test ({nd['pairs_all']:,} pairs and {m(nd['value_all'])} before excluding recurring vendors). The largest are same-day pension fund transfers and legal settlements, which may well be separate obligations of equal size, so the next step is to inspect the supporting invoices. Full list: <span class="num">data/exceptions_possible_duplicates.csv</span>.</p></div>
 <div class="card"><h2>Vendor concentration</h2><p class="sub">Top 10 vendors by 2025 payments, $m</p>
  <div class="chart"><canvas id="c3" aria-label="Top vendors chart"></canvas></div>
  <p class="note">The top 10 vendors received {pct(R['vendor_conc']['top10_share'])} of spending. Just {R['vendor_conc']['vendors_for_80pct']} of {R['vendor_conc']['vendor_count']:,} vendors account for 80% of the money, mostly pension funds, tax and insurance.</p></div>
 <div class="card"><h2>Spending by department</h2><p class="sub">Top 10 by value, $m</p>
  <div class="chart"><canvas id="c4" aria-label="Department spend chart"></canvas></div>
  <p class="note">{pct(R['no_dept_value'])} of the value has no department recorded, so it cannot be traced to a budget owner from this extract. {pct(R['no_dept_dv_share'])} of those lines are direct vouchers.</p></div>
</div>

<section class="findings">
 <h2 style="font-size:1.3rem">Findings and recommended follow-up</h2>
 <h3>1. Missing department coding on {pct(R['no_dept_rows'])} of payment lines</h3>
 <p>{bn(R['total_usd']*R['no_dept_value'])} of payments cannot be linked to a department in the published data. <span class="proc">Procedure: confirm whether the field is missing at source or only in the public extract, and test whether direct vouchers carry budget-owner approval.</span></p>
 <h3>2. {nd['pairs_isolated']:,} possible duplicate payments ({m(nd['value_isolated'])})</h3>
 <p>{sum(1 for p in nd['top'] if p['days_apart']==0)} of the ten largest pairs were paid on the same day under different voucher numbers. <span class="proc">Procedure: vouch both payments to separate invoices or obligations; check vendor statements for credits.</span></p>
 <h3>3. {dl['extra_rows']:,} fully identical payment lines ({m(dl['extra_value'])})</h3>
 <p>Rows where voucher, amount, date, vendor and contract all match. These are usually split lines on one voucher, but they should reconcile to voucher totals. <span class="proc">Procedure: agree a sample of vouchers to the general ledger.</span></p>
 <h3>4. Fixed-amount payments distort the digit profile</h3>
 <p>The first-digit test conforms, but standard amounts ($50, $500, $775, $1,550) create large two-digit spikes. <span class="proc">Procedure: obtain the approved rate schedules and test that each fixed payment type matches one.</span></p>
 <h3>5. High concentration in a few counterparties</h3>
 <p>{R['vendor_conc']['vendors_for_80pct']} vendors take 80% of spending. <span class="proc">Procedure: focus substantive testing on these vendors; confirm balances directly with pension funds and banks.</span></p>
</section>

<footer>Data: City of Chicago Data Portal, "Payments" dataset (s4vu-giwb), all lines with a 2025 check date, downloaded through the Socrata API. Method: Nigrini (2012) Benford thresholds; duplicate rules as described above. Python (pandas, NumPy) and Chart.js. Analysis by Daniel N. T. Tackie. This is an independent portfolio exercise, not an audit opinion on the City of Chicago.</footer>
</main>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<script>
const D={json.dumps(data)};
const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const ink=css("--ink"),muted=css("--muted"),rule=css("--rule"),acc=css("--accent"),gold=css("--gold");
Chart.defaults.font.family=css("--body");Chart.defaults.color=muted;Chart.defaults.borderColor=rule;Chart.defaults.maintainAspectRatio=false;Chart.defaults.plugins.legend.labels.boxWidth=12;
const p=v=>(v*100).toFixed(1)+"%";
new Chart(c1,{{data:{{labels:[1,2,3,4,5,6,7,8,9],datasets:[{{type:"bar",label:"Observed",data:D.b1o,backgroundColor:acc}},{{type:"line",label:"Benford expected",data:D.b1e,borderColor:gold,backgroundColor:gold,pointRadius:3}}]}},
 options:{{plugins:{{tooltip:{{callbacks:{{label:c=>c.dataset.label+": "+p(c.parsed.y)}}}}}},scales:{{y:{{ticks:{{callback:v=>p(v)}}}},x:{{grid:{{display:false}},title:{{display:true,text:"First digit"}}}}}}}}}});
const l2=[...Array(90)].map((_,i)=>i+10);
new Chart(c2,{{data:{{labels:l2,datasets:[{{type:"bar",label:"Observed",data:D.b2o,backgroundColor:acc}},{{type:"line",label:"Benford expected",data:D.b2e,borderColor:gold,pointRadius:0,borderWidth:2}}]}},
 options:{{plugins:{{tooltip:{{callbacks:{{label:c=>c.dataset.label+": "+(c.parsed.y*100).toFixed(2)+"%"}}}}}},scales:{{y:{{ticks:{{callback:v=>p(v)}}}},x:{{grid:{{display:false}},ticks:{{maxTicksLimit:10,maxRotation:0}},title:{{display:true,text:"First two digits"}}}}}}}}}});
const hb=(el,rows,color)=>new Chart(el,{{type:"bar",data:{{labels:rows.map(r=>r[0].length>34?r[0].slice(0,33)+"…":r[0]),datasets:[{{data:rows.map(r=>r[1]/1e6),backgroundColor:color}}]}},
 options:{{indexAxis:"y",plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>"$"+c.parsed.x.toLocaleString(undefined,{{maximumFractionDigits:1}})+"m"}}}}}},scales:{{x:{{ticks:{{callback:v=>"$"+v.toLocaleString()+"m"}}}},y:{{grid:{{display:false}},ticks:{{font:{{size:11}}}}}}}}}}}});
hb(c3,D.vend,acc);hb(c4,D.dept,D.dept.map(r=>r[0].startsWith("(Not")?gold:acc));
</script></body></html>"""
(root / "index.html").write_text(page)
print("ok")
