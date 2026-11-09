"""Render index.html from data/results.json. Usage: python scripts/build_report.py"""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
R = json.loads((root / "data/results.json").read_text()); style = (root / "scripts/style.css").read_text()
lr, gb = R["models"]["Logistic regression"], R["models"]["Gradient boosting"]
p = lambda x: f"{x*100:.1f}%"
names = {"months_late_6m": "Months paid late (last 6)", "status_latest": "Latest repayment status", "log_avg_payment": "Average payment (log)",
         "utilisation": "Current utilisation", "pay_ratio_latest": "Latest payment / bill", "log_limit": "Credit limit (log)", "max_delay_6m": "Worst delay (last 6)",
         "avg_utilisation_6m": "Average utilisation", "bill_trend": "Bill trend", "age": "Age", "edu_2": "Education: university", "edu_3": "Education: high school", "edu_4": "Education: other"}
coef = [[names.get(k, k), v] for k, v in list(R["lr_coefficients"].items())[:8]]
srow = "".join(f"<tr><td class='num'>{s['decline_pct']}%</td><td class='num'>{p(s['approved_bad_rate'])}</td><td class='num'>{p(s['bads_caught'])}</td><td class='num'>{p(l['approved_bad_rate'])}</td></tr>"
               for s, l in zip(gb["strategy"], lr["strategy"]))
mrow = "".join(f"<tr><td>{n}</td><td class='num'>{m['cv_auc_mean']:.3f} ± {m['cv_auc_std']:.3f}</td><td class='num'>{m['test_auc']:.3f}</td><td class='num'>{m['gini']:.3f}</td><td class='num'>{m['ks']:.3f}</td><td class='num'>{m['brier']:.3f}</td></tr>" for n, m in R["models"].items())
s20 = gb["strategy"][2]
D = {"roc_gb": gb["roc"], "roc_lr": lr["roc"], "dec": [[r["decile"], r["bad_rate"], r["pred"]] for r in gb["deciles"]],
     "st": [[r["status"], r["default_rate"], r["n"]] for r in R["by_status"]], "coef": coef}
page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Credit Default Risk Model</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
{style}<style>table{{border-collapse:collapse;width:100%;font-size:.86rem}}th,td{{padding:6px 8px;border-bottom:1px solid var(--rule);text-align:left}}thead th{{border-bottom:1px solid var(--ink);font-weight:600}}td.num,th.num{{text-align:right}}.scroll{{overflow-x:auto}}.findings p{{max-width:80ch}}</style></head><body>
<header><div class="wrap"><strong style="font-family:var(--display)">Daniel N. T. Tackie</strong><a class="back" href="../../index.html">Back to portfolio</a></div></header>
<main class="wrap">
<h1>Credit default risk model</h1>
<p class="lede">Which cardholders will miss next month's payment? Two models trained on {R['n']:,} real credit card accounts (UCI, Yeh &amp; Lien 2009). The scores are then turned into a decline strategy a lender could use.</p>
<div class="tiles">
 <div class="tile"><div class="l">Accounts</div><div class="v num">{R['n']/1000:.0f}k</div><div class="s">{R['train']:,} train / {R['test']:,} test</div></div>
 <div class="tile"><div class="l">Default rate</div><div class="v num">{p(R['default_rate'])}</div><div class="s">next-month default</div></div>
 <div class="tile"><div class="l">Best AUC</div><div class="v num">{gb['test_auc']:.3f}</div><div class="s">gradient boosting, test set</div></div>
 <div class="tile"><div class="l">Gini</div><div class="v num">{gb['gini']:.2f}</div><div class="s">vs {lr['gini']:.2f} logistic</div></div>
 <div class="tile"><div class="l">KS statistic</div><div class="v num">{gb['ks']:.2f}</div><div class="s">max separation</div></div>
 <div class="tile"><div class="l">Decline 20%</div><div class="v num">{p(s20['approved_bad_rate'])}</div><div class="s">bad rate, from {p(R['default_rate'])}</div></div>
</div>
<div class="grid">
 <div class="card"><h2>ROC curves</h2><p class="sub">True positive rate vs false positive rate on the held-out test set</p><div class="chart"><canvas id="c1" aria-label="ROC curves"></canvas></div>
  <p class="note">Gradient boosting beats logistic regression by {gb['test_auc']-lr['test_auc']:.3f} AUC. Five-fold cross-validation gives the same ranking ({gb['cv_auc_mean']:.3f} vs {lr['cv_auc_mean']:.3f}), so the gap is not luck of the split.</p></div>
 <div class="card"><h2>Bad rate by risk decile</h2><p class="sub">Gradient boosting; decile 1 = riskiest 10% of accounts</p><div class="chart"><canvas id="c2" aria-label="Decile chart"></canvas></div>
  <p class="note">Default rates fall from {p(gb['deciles'][0]['bad_rate'])} in the riskiest decile to {p(gb['deciles'][-1]['bad_rate'])} in the safest. Predicted and actual rates track closely, so the scores can be read as probabilities.</p></div>
 <div class="card"><h2>Repayment status drives default</h2><p class="sub">Default rate by last month's repayment status (raw data, all {R['n']:,} accounts)</p><div class="chart"><canvas id="c3" aria-label="Default by status"></canvas></div>
  <p class="note">Status −2 to 0 means no balance, paid in full or paid on time; 1 to 4 means months overdue. One month late almost triples the default rate, and two months late pushes it to {p([r for r in R['by_status'] if r['status']==2][0]['default_rate'])}.</p></div>
 <div class="card"><h2>What the logistic model weights</h2><p class="sub">Standardised coefficients; positive raises default risk</p><div class="chart"><canvas id="c4" aria-label="Coefficients"></canvas></div>
  <p class="note">Repayment behaviour dominates. Higher payments and higher credit limits lower risk. Sex and marital status were left out of the model on fair-lending grounds.</p></div>
 <div class="card wide"><h2>From scores to a credit decision</h2><p class="sub">Decline the riskiest share of applicants and measure the bad rate of the accounts that remain</p>
  <div class="scroll"><table><thead><tr><th class="num">Declined</th><th class="num">Bad rate of approved (GB)</th><th class="num">Defaulters caught (GB)</th><th class="num">Bad rate of approved (logistic)</th></tr></thead><tbody>{srow}</tbody></table></div>
  <p class="note">Declining the riskiest 20% would catch {p(s20['bads_caught'])} of defaulters and cut the approved book's bad rate from {p(R['default_rate'])} to {p(s20['approved_bad_rate'])}. The right cut-off depends on the margin earned on good accounts against the loss on bad ones.</p></div>
 <div class="card wide"><h2>Model comparison</h2><div class="scroll"><table><thead><tr><th>Model</th><th class="num">CV AUC (5-fold)</th><th class="num">Test AUC</th><th class="num">Gini</th><th class="num">KS</th><th class="num">Brier</th></tr></thead><tbody>{mrow}</tbody></table></div>
  <p class="note">Logistic regression is easier to explain to a credit committee and regulator. Gradient boosting ranks risk better. A common approach is to keep the logistic model as the official scorecard and use the boosted model as a challenger.</p></div>
</div>
<section class="findings"><h2 style="font-size:1.3rem">Method</h2>
<p>Features engineered from six months of history: months paid late, worst delay, latest repayment status, utilisation (current and average), latest payment-to-bill ratio, average payment, bill trend, credit limit, age and education. 70/30 stratified split (seed 42), five-fold cross-validation on the training set, and evaluation on the untouched test set using AUC, Gini, KS and Brier score.</p>
<p>Limitation: the data are Taiwanese cardholders from 2005, so the model shows the method. It is not ready to deploy on a Ghanaian lender's book without retraining on local data.</p></section>
<footer>Data: Yeh, I.-C. &amp; Lien, C. (2009), "The comparisons of data mining techniques for the predictive accuracy of probability of default of credit card clients", Expert Systems with Applications 36(2), 2473-2480; UCI Machine Learning Repository dataset 350. Python (pandas, scikit-learn) and Chart.js. Analysis by Daniel N. T. Tackie.</footer>
</main>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<script>
const D={json.dumps(D)};
const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const muted=css("--muted"),rule=css("--rule"),acc=css("--accent"),gold=css("--gold"),ink=css("--ink"),bad=css("--bad");
Chart.defaults.font.family=css("--body");Chart.defaults.color=muted;Chart.defaults.borderColor=rule;Chart.defaults.maintainAspectRatio=false;Chart.defaults.plugins.legend.labels.boxWidth=12;
const pc=v=>(v*100).toFixed(0)+"%";
new Chart(c1,{{type:"scatter",data:{{datasets:[
 {{label:"Gradient boosting",data:D.roc_gb.map(r=>({{x:r[0],y:r[1]}})),showLine:true,borderColor:acc,pointRadius:0,borderWidth:2.5}},
 {{label:"Logistic regression",data:D.roc_lr.map(r=>({{x:r[0],y:r[1]}})),showLine:true,borderColor:gold,pointRadius:0,borderWidth:2}},
 {{label:"Random",data:[{{x:0,y:0}},{{x:1,y:1}}],showLine:true,borderColor:rule,borderDash:[4,4],pointRadius:0}}]}},
 options:{{scales:{{x:{{min:0,max:1,title:{{display:true,text:"False positive rate"}},ticks:{{callback:pc}}}},y:{{min:0,max:1,title:{{display:true,text:"True positive rate"}},ticks:{{callback:pc}}}}}}}}}});
new Chart(c2,{{data:{{labels:D.dec.map(r=>r[0]),datasets:[{{type:"bar",label:"Actual bad rate",data:D.dec.map(r=>r[1]),backgroundColor:acc}},{{type:"line",label:"Predicted",data:D.dec.map(r=>r[2]),borderColor:gold,backgroundColor:gold,pointRadius:3}}]}},
 options:{{plugins:{{tooltip:{{callbacks:{{label:c=>c.dataset.label+": "+(c.parsed.y*100).toFixed(1)+"%"}}}}}},scales:{{y:{{beginAtZero:true,ticks:{{callback:pc}}}},x:{{grid:{{display:false}},title:{{display:true,text:"Risk decile (1 = riskiest)"}}}}}}}}}});
new Chart(c3,{{type:"bar",data:{{labels:D.st.map(r=>r[0]==-2?"No balance":r[0]==-1?"Paid in full":r[0]==0?"On time":r[0]+(r[0]>=4?"+":"")+" mo late"),datasets:[{{label:"Default rate",data:D.st.map(r=>r[1]),backgroundColor:D.st.map(r=>r[0]>0?bad:acc)}}]}},
 options:{{plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>(c.parsed.y*100).toFixed(1)+"% of "+D.st[c.dataIndex][2].toLocaleString()+" accounts"}}}}}},scales:{{y:{{beginAtZero:true,ticks:{{callback:pc}}}},x:{{grid:{{display:false}}}}}}}}}});
new Chart(c4,{{type:"bar",data:{{labels:D.coef.map(r=>r[0]),datasets:[{{data:D.coef.map(r=>r[1]),backgroundColor:D.coef.map(r=>r[1]>0?bad:acc)}}]}},
 options:{{indexAxis:"y",plugins:{{legend:{{display:false}}}},scales:{{y:{{grid:{{display:false}}}}}}}}}});
</script></body></html>"""
(root / "index.html").write_text(page); print("ok")
