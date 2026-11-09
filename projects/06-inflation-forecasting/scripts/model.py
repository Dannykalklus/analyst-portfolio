"""Forecast Ghana headline inflation 12 months ahead and estimate exchange-rate pass-through.
Models (fitted on 100 x monthly log change in CPI):
  RW    : year-on-year inflation stays at its latest value (benchmark)
  SARIMA: SARIMA(1,0,1)(1,0,1,12) with constant on monthly inflation
  ARDL  : monthly inflation on its own lags (1,2,12) and cedi depreciation lags (1-6); future FX held flat
Rolling-origin backtest, Jan 2019 to Oct 2025 origins, horizons 1-12. Writes data/results.json."""
import json, pathlib, warnings
import numpy as np, pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.statespace.sarimax import SARIMAX
warnings.filterwarnings("ignore")
root = pathlib.Path(__file__).resolve().parents[1]
df = pd.read_csv(root / "data/ghana_monthly.csv", index_col=0); df.index = pd.PeriodIndex(df.index, freq="M")
lc = np.log(df.cpi); pi = 100 * lc.diff()                         # monthly inflation, %
dep = 100 * np.log(df.usd_ghs).diff()                              # monthly depreciation, %
start = pd.Period("2002-01", "M")

def yoy_path(hist_lc, fc_pi):
    """turn forecast monthly log changes into YoY % for each horizon"""
    path = hist_lc.iloc[-1] + np.cumsum(fc_pi) / 100
    full = pd.concat([hist_lc, pd.Series(path, index=pd.period_range(hist_lc.index[-1] + 1, periods=len(fc_pi), freq="M"))])
    return (np.exp(full - full.shift(12)) - 1).iloc[-len(fc_pi):] * 100

def f_sarima(t, h=12, ci=False):
    y = pi[start:t]
    m = SARIMAX(y.values, order=(1, 0, 1), seasonal_order=(1, 0, 1, 12), trend="c").fit(disp=False)
    if not ci: return m.forecast(h)
    fc = m.get_forecast(h); return fc.predicted_mean, fc.se_mean, m

def ardl_X(p, d):
    X = pd.DataFrame({"pi1": p.shift(1), "pi2": p.shift(2), "pi12": p.shift(12)})
    for k in range(1, 7): X[f"dep{k}"] = d.shift(k)
    return sm.add_constant(X)

def f_ardl(t, h=12):
    p, d = pi[start:t].copy(), dep[start:t].copy()
    d = d.ffill()
    X = ardl_X(p, d); ok = X.notna().all(1)
    m = sm.OLS(p[ok], X[ok]).fit()
    out = []
    for i in range(h):
        nxt = p.index[-1] + 1
        p.loc[nxt] = np.nan; d.loc[nxt] = 0.0           # future FX flat
        x = ardl_X(p, d).iloc[-1]; v = float(m.params @ x); p.loc[nxt] = v; out.append(v)
    return np.array(out)

# ---------- backtest ----------
origins = pd.period_range("2019-01", "2025-10", freq="M")
H = [1, 3, 6, 12]; err = {k: {h: [] for h in H} for k in ["Random walk", "SARIMA", "ARDL (with FX)"]}
actual_yoy = df.inflation_yoy
for t in origins:
    hist = lc[:t]; last = actual_yoy[t]
    fcs = {"SARIMA": yoy_path(hist, f_sarima(t)), "ARDL (with FX)": yoy_path(hist, f_ardl(t))}
    for h in H:
        tgt = t + h; a = actual_yoy[tgt]
        err["Random walk"][h].append(last - a)
        for k, f in fcs.items(): err[k][h].append(f.iloc[h - 1] - a)
rmse = {k: {h: float(np.sqrt(np.mean(np.square(v[h])))) for h in H} for k, v in err.items()}
mae = {k: {h: float(np.mean(np.abs(v[h]))) for h in H} for k, v in err.items()}

# ---------- final forecast from latest data ----------
T = pi.index[-1]; hist = lc[:T]
mean, se, msar = f_sarima(T, 12, ci=True)

def ardl_sim(t, h=12, n=3000, fx_path=None, seed=7):
    """ARDL forecast paths with bootstrapped residuals; fx_path = monthly depreciation % for future months"""
    p0, d0 = pi[start:t].copy(), dep[start:t].ffill()
    X = ardl_X(p0, d0); ok = X.notna().all(1); m = sm.OLS(p0[ok], X[ok]).fit(); res = m.resid.values
    rng = np.random.default_rng(seed); fx = np.zeros(h) if fx_path is None else np.asarray(fx_path)
    def one(shocks):
        p, d = p0.copy(), d0.copy(); out = []
        for i in range(h):
            nxt = p.index[-1] + 1; p.loc[nxt] = np.nan; d.loc[nxt] = fx[i]
            v = float(m.params @ ardl_X(p, d).iloc[-1]) + shocks[i]; p.loc[nxt] = v; out.append(v)
        return np.array(out)
    central = yoy_path(hist, one(np.zeros(h)))
    sims = np.array([yoy_path(hist, one(rng.choice(res, h))).values for _ in range(n)])
    return central, sims

central, sims = ardl_sim(T, n=1500)
scen, _ = ardl_sim(T, n=1, fx_path=[100 * np.log(1.15) / 12] * 12)   # cedi loses 15% over 12 months
fut = pd.period_range(T + 1, periods=12, freq="M")
forecast = {"months": [str(x) for x in fut], "ardl": central.round(2).tolist(),
            "lo80": np.percentile(sims, 10, 0).round(2).tolist(), "hi80": np.percentile(sims, 90, 0).round(2).tolist(),
            "lo95": np.percentile(sims, 2.5, 0).round(2).tolist(), "hi95": np.percentile(sims, 97.5, 0).round(2).tolist(),
            "fx_shock": scen.round(2).tolist(), "sarima": yoy_path(hist, mean).round(2).tolist()}

# ---------- exchange-rate pass-through ----------
p, d = pi[start:].copy(), dep[start:].ffill()
X = pd.DataFrame({f"pi{k}": p.shift(k) for k in (1, 2, 12)})
for k in range(0, 13): X[f"dep{k}"] = d.shift(k)
X = sm.add_constant(X); ok = X.notna().all(1) & p.notna()
pt = sm.OLS(p[ok], X[ok]).fit(cov_type="HAC", cov_kwds={"maxlags": 12})
b = pt.params[[f"dep{k}" for k in range(13)]]; rho = pt.params[["pi1", "pi2", "pi12"]].sum()
lr = b.sum() / (1 - rho)
cum = (b.cumsum()).round(4).tolist()
R = {"obs": int(ok.sum()), "sample": f"{p[ok].index[0]} to {p[ok].index[-1]}", "last_month": str(T),
     "last_yoy": float(actual_yoy[T]), "rmse": rmse, "mae": mae, "n_origins": len(origins), "forecast": forecast,
     "passthrough": {"short_run_sum": float(b.sum()), "long_run": float(lr), "cum_by_lag": cum,
                     "p_sum": float(pt.f_test(" + ".join(b.index) + " = 0").pvalue), "r2": float(pt.rsquared)},
     "history": {"months": [str(x) for x in actual_yoy["2015-01":].index], "yoy": actual_yoy["2015-01":].round(2).tolist(),
                 "dep": df.depreciation_yoy["2015-01":].round(2).where(lambda s: s.notna(), None).tolist()},
     "sarima_aic": float(msar.aic)}
(root / "data/results.json").write_text(json.dumps(R, indent=1, default=lambda o: None if o != o else o))
print(json.dumps({"rmse": rmse, "pt": R["passthrough"], "fc": {k: forecast[k] for k in ["months", "sarima", "lo80", "hi80", "ardl"]}}, indent=1))
