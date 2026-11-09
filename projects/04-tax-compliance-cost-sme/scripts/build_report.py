"""Render index.html from data/results.json and data/sample_profile.json."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
R = json.loads((root / "data/results.json").read_text()); P = json.loads((root / "data/sample_profile.json").read_text())
style = (root / "scripts/style.css").read_text()
h1, h2, h3 = R["paths"]
fmtp = lambda p: "&lt; 0.001" if p < 0.001 else f"{p:.3f}"
names = {"TCC": "Tax compliance cost", "RA": "Responsibility accounting", "FO": "Firm outcomes"}
mrows = "".join(f"<tr><td>{names[k]}</td><td class='num'>{len(R['loadings'][k])}</td><td class='num'>{min(R['loadings'][k].values()):.3f} to {max(R['loadings'][k].values()):.3f}</td><td class='num'>{v['alpha']:.3f}</td><td class='num'>{v['rho_a']:.3f}</td><td class='num'>{v['cr']:.3f}</td><td class='num'>{v['ave']:.3f}</td></tr>" for k, v in R["reliability"].items())
hrows = "".join(f"<tr><td>{x['hypothesis']}</td><td class='num'>{x['beta']:+.3f}</td><td class='num'>{x['t']:.2f}</td><td class='num'>{fmtp(x['p'])}</td><td class='num'>[{x['ci_low']:.3f}, {x['ci_high']:.3f}]</td><td class='num'>{R['f2'][['TCC','RA','INT'][i]]:.3f}</td><td>{'Supported' if x['supported'] else 'Not supported'}</td></tr>" for i, x in enumerate(R["paths"]))
D = {"b": [h1["beta"], h2["beta"], h3["beta"]], "prof": {k: P[k] for k in ["Number of employees", "Main business activity", "Who handles tax matters?"]}}
page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tax Compliance Cost and SME Performance</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
{style}<style>table{{border-collapse:collapse;width:100%;font-size:.86rem}}th,td{{padding:6px 8px;border-bottom:1px solid var(--rule);text-align:left}}thead th{{border-bottom:1px solid var(--ink);font-weight:600}}td.num,th.num{{text-align:right}}.scroll{{overflow-x:auto}}
.model svg{{width:100%;height:auto;max-height:300px}}.model text{{font-family:var(--body);fill:var(--ink)}}.model .box{{fill:var(--paper);stroke:var(--ink)}}.model .lbl{{font-family:var(--mono);font-size:13px}}.findings p{{max-width:80ch}}</style></head><body>
<header><div class="wrap"><strong style="font-family:var(--display)">Daniel N. T. Tackie</strong><a class="back" href="../../index.html">Back to portfolio</a></div></header>
<main class="wrap">
<h1>Tax compliance cost and SME performance in Ghana</h1>
<p class="lede">My approved MSc long essay (University of Ghana Business School, supervised by Dr. Nicholas Asare). Does the cost of complying with GRA tax obligations hurt small business performance, and does responsibility accounting soften the damage? Survey of {R['n']} SMEs in Greater Accra, analysed with PLS-SEM and {R['n_boot']:,} bootstrap resamples.</p>
<div class="tiles">
 <div class="tile"><div class="l">SMEs surveyed</div><div class="v num">{R['n']}</div><div class="s">Greater Accra, GRA-registered</div></div>
 <div class="tile"><div class="l">Compliance cost effect</div><div class="v num">{h1['beta']:+.2f}</div><div class="s">β on firm outcomes, p {fmtp(h1['p'])}</div></div>
 <div class="tile"><div class="l">Resp. accounting effect</div><div class="v num">{h2['beta']:+.2f}</div><div class="s">β on firm outcomes</div></div>
 <div class="tile"><div class="l">Moderation</div><div class="v num">{h3['beta']:+.2f}</div><div class="s">interaction β, f² {R['f2']['INT']:.3f}</div></div>
 <div class="tile"><div class="l">R²</div><div class="v num">{R['r2_full']:.3f}</div><div class="s">firm outcomes ({R['r2_main']:.3f} without interaction)</div></div>
 <div class="tile"><div class="l">Hypotheses</div><div class="v num">3 / 3</div><div class="s">supported, 95% CI excludes 0</div></div>
</div>
<div class="grid">
 <div class="card model"><h2>Structural model</h2><p class="sub">Standardised path coefficients</p>
 <svg viewBox="0 0 520 260" role="img" aria-label="Path diagram">
  <defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="currentColor"/></marker></defs>
  <g style="color:var(--ink)">
  <rect class="box" x="10" y="160" width="150" height="56" rx="4"/><text x="85" y="185" text-anchor="middle" font-size="13">Tax compliance</text><text x="85" y="202" text-anchor="middle" font-size="13">cost</text>
  <rect class="box" x="360" y="160" width="150" height="56" rx="4"/><text x="435" y="193" text-anchor="middle" font-size="13">Firm outcomes</text>
  <rect class="box" x="185" y="20" width="150" height="56" rx="4"/><text x="260" y="45" text-anchor="middle" font-size="13">Responsibility</text><text x="260" y="62" text-anchor="middle" font-size="13">accounting</text>
  <line x1="160" y1="188" x2="356" y2="188" stroke="currentColor" stroke-width="2" marker-end="url(#ar)"/>
  <line x1="300" y1="76" x2="400" y2="156" stroke="currentColor" stroke-width="2" marker-end="url(#ar)"/>
  <line x1="245" y1="76" x2="245" y2="184" stroke="var(--gold)" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#ar)" style="color:var(--gold)"/>
  <text class="lbl" x="300" y="210" text-anchor="middle">H1 {h1['beta']:+.3f}***</text>
  <text class="lbl" x="372" y="110">H2 {h2['beta']:+.3f}***</text>
  <text class="lbl" x="152" y="135" style="fill:var(--gold)">H3 {h3['beta']:+.3f}***</text>
  <text x="435" y="236" text-anchor="middle" font-size="12" style="fill:var(--muted)">R² = {R['r2_full']:.3f}</text></g></svg>
 <p class="note">*** p &lt; 0.001. Responsibility accounting raises performance directly and weakens the harm from compliance cost (dashed line = moderation).</p></div>
 <div class="card"><h2>How responsibility accounting changes the cost effect</h2><p class="sub">Predicted firm outcomes (standardised) across compliance cost, at low, average and high responsibility accounting</p>
 <div class="chart"><canvas id="c1" aria-label="Simple slopes"></canvas></div>
 <p class="note">Slope of compliance cost: {R['simple_slopes']['-1']:+.2f} where responsibility accounting is weak (−1 SD), {R['simple_slopes']['0']:+.2f} at the average, and {R['simple_slopes']['1']:+.2f} where it is strong (+1 SD).</p></div>
 <div class="card wide"><h2>Hypothesis tests</h2><p class="sub">Two-stage moderation, percentile bootstrap with {R['n_boot']:,} resamples</p>
 <div class="scroll"><table><thead><tr><th>Hypothesis</th><th class="num">β</th><th class="num">t</th><th class="num">p</th><th class="num">95% CI</th><th class="num">f²</th><th>Decision</th></tr></thead><tbody>{hrows}</tbody></table></div></div>
 <div class="card wide"><h2>Measurement model</h2><p class="sub">Reflective constructs, five-point Likert items (8 per construct)</p>
 <div class="scroll"><table><thead><tr><th>Construct</th><th class="num">Items</th><th class="num">Loadings</th><th class="num">Cronbach's α</th><th class="num">ρA</th><th class="num">CR</th><th class="num">AVE</th></tr></thead><tbody>{mrows}</tbody></table></div>
 <p class="note">All loadings exceed 0.70 and AVE exceeds 0.50. HTMT ratios are all below 0.85 (highest {max(R['htmt'].values()):.3f}), and inner VIF is {R['vif_inner']:.2f}. Profitability and sales performance were first tested as separate constructs, but their HTMT of {R['htmt_fo_split']:.2f} showed they are not empirically distinct, so they were combined into one firm-outcomes construct.</p></div>
 <div class="card wide"><h2>Who responded</h2><p class="sub">Number of firms by size (green), sector (gold) and who handles tax matters (black)</p><div class="chart" style="height:260px"><canvas id="c2" aria-label="Sample profile"></canvas></div></div>
</div>
<section class="findings"><h2 style="font-size:1.3rem">What it means</h2>
<p><strong>For SME owners:</strong> compliance cost is a real drag on profitability and sales (a 1 SD rise lowers outcomes by {abs(h1['beta']):.2f} SD). Firms that assign clear cost responsibility, budget by unit and hold managers to account lose much less: at high responsibility accounting the effect almost disappears.</p>
<p><strong>For GRA and policymakers:</strong> simpler filing and clearer guidance would ease the burden directly. Training SMEs in basic management accounting would also help them absorb the burden that remains.</p>
<p><strong>Limitations:</strong> cross-sectional, self-reported data from one region; purposive sampling limits generalisation; outcomes are perceived rather than audited figures.</p></section>
<footer>Survey data collected by the author through Google Forms (29 Sep to 16 Oct 2026), {R['n']} valid responses, no straight-lining detected. PLS-SEM implemented in Python (Lohmöller algorithm, path weighting, two-stage interaction; Hair et al., 2022 criteria). Raw responses are kept private to protect respondents. Daniel N. T. Tackie, MSc Accounting and Finance, University of Ghana Business School.</footer>
</main>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<script>
const D={json.dumps(D)};
const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const muted=css("--muted"),rule=css("--rule"),acc=css("--accent"),gold=css("--gold"),bad=css("--bad"),ink=css("--ink");
Chart.defaults.font.family=css("--body");Chart.defaults.color=muted;Chart.defaults.borderColor=rule;Chart.defaults.maintainAspectRatio=false;Chart.defaults.plugins.legend.labels.boxWidth=12;
const xs=[-2,-1,0,1,2],[b1,b2,b3]=D.b,line=m=>xs.map(x=>({{x,y:+(b1*x+b2*m+b3*x*m).toFixed(3)}}));
new Chart(c1,{{type:"scatter",data:{{datasets:[
 {{label:"High RA (+1 SD)",data:line(1),showLine:true,borderColor:acc,backgroundColor:acc,pointRadius:0,borderWidth:2.5}},
 {{label:"Average RA",data:line(0),showLine:true,borderColor:ink,backgroundColor:ink,pointRadius:0,borderWidth:2,borderDash:[5,4]}},
 {{label:"Low RA (−1 SD)",data:line(-1),showLine:true,borderColor:bad,backgroundColor:bad,pointRadius:0,borderWidth:2.5}}]}},
 options:{{scales:{{x:{{min:-2,max:2,title:{{display:true,text:"Tax compliance cost (SD)"}}}},y:{{title:{{display:true,text:"Firm outcomes (SD)"}}}}}}}}}});
const groups=Object.entries(D.prof),labels=[],vals=[],cols=[],pal=[acc,gold,ink];
groups.forEach(([g,o],gi)=>Object.entries(o).forEach(([k,v])=>{{labels.push(k);vals.push(v);cols.push(pal[gi])}}));
new Chart(c2,{{type:"bar",data:{{labels,datasets:[{{data:vals,backgroundColor:cols}}]}},options:{{plugins:{{legend:{{display:false}},
 tooltip:{{callbacks:{{title:c=>labels[c[0].dataIndex],label:c=>c.parsed.y+" firms"}}}}}},scales:{{x:{{grid:{{display:false}},ticks:{{font:{{size:10}},maxRotation:40,minRotation:40}}}}}}}}}});
</script></body></html>"""
(root / "index.html").write_text(page); print("ok")
