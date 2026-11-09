"""Render index.html from data/results.json."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
R = json.loads((root / "data/results.json").read_text()); style = (root / "scripts/style.css").read_text()
F, PT = R["forecast"], R["passthrough"]
rw, sa, ar = R["rmse"]["Random walk"], R["rmse"]["SARIMA"], R["rmse"]["ARDL (with FX)"]
gain12 = 1 - ar["12"] / rw["12"]
rows = "".join(f"<tr><td>{n}</td>" + "".join(f"<td class='num'>{v[h]:.2f}</td>" for h in ["1", "3", "6", "12"]) + "</tr>" for n, v in R["rmse"].items())
mlab = lambda m: __import__("datetime").date(int(m[:4]), int(m[5:]), 1).strftime("%b %Y")
page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ghana Inflation Forecast</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
{style}<style>table{{border-collapse:collapse;width:100%;font-size:.86rem}}th,td{{padding:6px 8px;border-bottom:1px solid var(--rule);text-align:left}}thead th{{border-bottom:1px solid var(--ink);font-weight:600}}td.num,th.num{{text-align:right}}.scroll{{overflow-x:auto}}.findings p,.findings li{{max-width:80ch}}</style></head><body>
<header><div class="wrap"><strong style="font-family:var(--display)">Daniel N. T. Tackie</strong><a class="back" href="../../index.html">Back to portfolio</a></div></header>
<main class="wrap">
<h1>Where is Ghana's inflation heading?</h1>
<p class="lede">A 12-month forecast of headline inflation from 25 years of monthly CPI and exchange-rate data. Three models are tested on {R['n_origins']} historical forecast rounds, and the pass-through from the cedi to prices is measured.</p>
<div class="tiles">
 <div class="tile"><div class="l">Latest inflation</div><div class="v num">{R['last_yoy']:.1f}%</div><div class="s">{mlab(R['last_month'])}, GSS</div></div>
 <div class="tile"><div class="l">Forecast {mlab(F['months'][5])}</div><div class="v num">{F['ardl'][5]:.1f}%</div><div class="s">80% band {round(F['lo80'][5])+0:d} to {round(F['hi80'][5]):d}%</div></div>
 <div class="tile"><div class="l">Forecast {mlab(F['months'][-1])}</div><div class="v num">{F['ardl'][-1]:.1f}%</div><div class="s">80% band {round(F['lo80'][-1])+0:d} to {round(F['hi80'][-1]):d}%</div></div>
 <div class="tile"><div class="l">If the cedi falls 15%</div><div class="v num">{F['fx_shock'][-1]:.1f}%</div><div class="s">inflation by {mlab(F['months'][-1])}</div></div>
 <div class="tile"><div class="l">Long-run pass-through</div><div class="v num">{PT['long_run']:.2f}</div><div class="s">price rise per 1% depreciation</div></div>
 <div class="tile"><div class="l">Accuracy gain</div><div class="v num">{gain12*100:.0f}%</div><div class="s">12-month RMSE vs random walk</div></div>
</div>
<div class="grid">
 <div class="card wide"><h2>Inflation history and forecast</h2><p class="sub">Year-on-year CPI inflation, %. Forecast from the ARDL model, with 80% and 95% bands from 1,500 bootstrapped simulations</p>
  <div class="chart"><canvas id="c1" aria-label="Forecast fan chart"></canvas></div>
  <p class="note">The central path keeps inflation close to 5% through October 2027, below the Bank of Ghana's 8% ± 2% medium-term target band. The bands are wide because they carry the volatility of the past 25 years, including the 54% peak in December 2022. The SARIMA model (dotted) drifts up toward the 25-year average, which is why it does worse when the regime changes.</p></div>
 <div class="card"><h2>Forecast accuracy by horizon</h2><p class="sub">Root mean squared error, percentage points, {R['n_origins']} forecast origins (Jan 2019 to Oct 2025)</p>
  <div class="chart"><canvas id="c2" aria-label="RMSE by horizon"></canvas></div>
  <p class="note">Both models beat the random walk at every horizon. Adding the exchange rate (ARDL) gives the lowest error at 3, 6 and 12 months, cutting 12-month error by {gain12*100:.0f}%.</p></div>
 <div class="card"><h2>The cedi leads inflation</h2><p class="sub">Year-on-year inflation vs year-on-year depreciation of the cedi against the dollar, %</p>
  <div class="chart"><canvas id="c3" aria-label="Inflation and depreciation"></canvas></div>
  <p class="note">The 2022 currency collapse fed directly into the inflation spike. The 2025 appreciation drove the fall to 3%.</p></div>
 <div class="card"><h2>How fast the cedi reaches prices</h2><p class="sub">Cumulative effect of a 1% depreciation on monthly inflation, by months since the shock</p>
  <div class="chart"><canvas id="c4" aria-label="Pass-through by lag"></canvas></div>
  <p class="note">About {PT['short_run_sum']*100:.0f}% passes through directly within a year (jointly significant, p = {PT['p_sum']:.3f}). Including the persistence of inflation itself, the long-run pass-through is {PT['long_run']:.2f}.</p></div>
 <div class="card"><h2>Backtest results</h2><p class="sub">RMSE of year-on-year inflation forecasts, percentage points</p>
  <div class="scroll"><table><thead><tr><th>Model</th><th class="num">1 month</th><th class="num">3 months</th><th class="num">6 months</th><th class="num">12 months</th></tr></thead><tbody>{rows}</tbody></table></div>
  <p class="note">The errors are large in absolute terms because the test window includes the 2022 to 2023 crisis, when no model saw the spike coming.</p></div>
</div>
<section class="findings"><h2 style="font-size:1.3rem">What it means</h2>
<ul>
<li><strong>Base case:</strong> inflation stays around {min(F['ardl']):.1f} to {max(F['ardl']):.1f}% over the next year. That leaves room for the Bank of Ghana to hold or cut its 14% policy rate, and real interest rates stay high.</li>
<li><strong>Main risk is the cedi:</strong> a 15% depreciation would lift inflation to about {F['fx_shock'][-1]:.1f}% by {mlab(F['months'][-1])}, back to the middle of the target band.</li>
<li><strong>For valuation work:</strong> this path supports using a long-run inflation assumption of about 5 to 8% in cedi discount rates, as in my MTN Ghana model.</li>
</ul>
<h2 style="font-size:1.3rem;margin-top:24px">Method</h2>
<p>Monthly CPI (not seasonally adjusted) and GHS/USD from the World Bank Global Economic Monitor, January 2000 to July 2026, extended to October 2026 with Ghana Statistical Service year-on-year rates. The models work on monthly log changes. SARIMA(1,0,1)(1,0,1)<sub>12</sub> uses its own history only. The ARDL model uses inflation lags 1, 2 and 12 plus six lags of cedi depreciation, with the exchange rate held flat in forecasts. The rolling-origin backtest re-estimates every model at each origin. Pass-through is estimated by OLS with HAC standard errors over {R['sample']}.</p></section>
<footer>Data: World Bank Global Economic Monitor (CPTOTNSXN, DPANUSLCU); Ghana Statistical Service CPI releases (Aug to Oct 2026). Python (pandas, statsmodels) and Chart.js. Analysis by Daniel N. T. Tackie. Forecasts are illustrative, not investment advice.</footer>
</main>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<script>
const R={json.dumps({"F": F, "H": R["history"], "rmse": R["rmse"], "cum": PT["cum_by_lag"]})};
const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const muted=css("--muted"),rule=css("--rule"),acc=css("--accent"),gold=css("--gold"),ink=css("--ink"),bad=css("--bad");
Chart.defaults.font.family=css("--body");Chart.defaults.color=muted;Chart.defaults.borderColor=rule;Chart.defaults.maintainAspectRatio=false;Chart.defaults.plugins.legend.labels.boxWidth=12;
const ml=m=>new Date(+m.slice(0,4),+m.slice(5)-1,1).toLocaleString("en-GB",{{month:"short",year:"2-digit"}});
const hm=R.H.months.filter(m=>m>="2019-01"),hy=hm.map(m=>R.H.yoy[R.H.months.indexOf(m)]);
const labels=[...hm,...R.F.months].map(ml),n=hm.length,pad=a=>[...Array(n-1).fill(null),hy[n-1],...a],hid=Array(12).fill(null);
new Chart(c1,{{type:"line",data:{{labels,datasets:[
 {{label:"95% band",data:pad(R.F.hi95),borderWidth:0,pointRadius:0,backgroundColor:acc+"18",fill:"+1"}},
 {{label:"95% low",data:pad(R.F.lo95),borderWidth:0,pointRadius:0}},
 {{label:"80% band",data:pad(R.F.hi80),borderWidth:0,pointRadius:0,backgroundColor:acc+"33",fill:"+1"}},
 {{label:"80% low",data:pad(R.F.lo80),borderWidth:0,pointRadius:0}},
 {{label:"Actual",data:[...hy,...hid],borderColor:ink,borderWidth:2,pointRadius:0}},
 {{label:"ARDL forecast",data:pad(R.F.ardl),borderColor:acc,borderWidth:2.5,pointRadius:0}},
 {{label:"Cedi -15% scenario",data:pad(R.F.fx_shock),borderColor:bad,borderWidth:2,borderDash:[6,4],pointRadius:0}},
 {{label:"SARIMA",data:pad(R.F.sarima),borderColor:gold,borderWidth:2,borderDash:[2,3],pointRadius:0}}]}},
 options:{{interaction:{{mode:"index",intersect:false}},plugins:{{legend:{{labels:{{filter:i=>!i.text.includes("low")}}}},tooltip:{{filter:i=>!i.dataset.label.includes("low")&&i.parsed.y!=null}}}},
 scales:{{y:{{ticks:{{callback:v=>v+"%"}}}},x:{{grid:{{display:false}},ticks:{{maxTicksLimit:12,maxRotation:0}}}}}}}}}});
const hs=["1","3","6","12"],pal={{"Random walk":rule,"SARIMA":gold,"ARDL (with FX)":acc}};
new Chart(c2,{{type:"bar",data:{{labels:hs.map(h=>h+(h=="1"?" month":" months")),datasets:Object.entries(R.rmse).map(([k,v])=>({{label:k,data:hs.map(h=>+v[h].toFixed(2)),backgroundColor:pal[k]}}))}},
 options:{{scales:{{y:{{title:{{display:true,text:"RMSE (pp)"}}}},x:{{grid:{{display:false}}}}}}}}}});
new Chart(c3,{{type:"line",data:{{labels:R.H.months.map(ml),datasets:[{{label:"Inflation",data:R.H.yoy,borderColor:acc,pointRadius:0,borderWidth:2}},{{label:"Cedi depreciation",data:R.H.dep,borderColor:gold,pointRadius:0,borderWidth:2}}]}},
 options:{{interaction:{{mode:"index",intersect:false}},scales:{{y:{{ticks:{{callback:v=>v+"%"}}}},x:{{grid:{{display:false}},ticks:{{maxTicksLimit:8,maxRotation:0}}}}}}}}}});
new Chart(c4,{{type:"line",data:{{labels:R.cum.map((_,i)=>i),datasets:[{{label:"Cumulative pass-through",data:R.cum,borderColor:acc,backgroundColor:acc+"22",fill:true,pointRadius:3}}]}},
 options:{{plugins:{{legend:{{display:false}}}},scales:{{y:{{beginAtZero:true}},x:{{title:{{display:true,text:"Months after depreciation"}},grid:{{display:false}}}}}}}}}});
</script></body></html>"""
(root / "index.html").write_text(page); print("ok")
