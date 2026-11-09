"""Credit default model on the UCI 'Default of Credit Card Clients' data (Yeh & Lien, 2009; 30,000 Taiwan
cardholders, 2005). Compares logistic regression with gradient boosting and turns scores into a
decline-rate strategy. Usage: python scripts/model.py -> data/results.json"""
import json, pathlib
import numpy as np, pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, roc_curve, brier_score_loss

root = pathlib.Path(__file__).resolve().parents[1]
d = pd.read_csv(root / "data/uci_credit_card_default.csv").rename(columns={"default payment next month": "default", "PAY_0": "PAY_1"})
y = d["default"]
pay = [f"PAY_{i}" for i in range(1, 7)]; bill = [f"BILL_AMT{i}" for i in range(1, 7)]; pamt = [f"PAY_AMT{i}" for i in range(1, 7)]
X = pd.DataFrame({
    "limit_bal": d.LIMIT_BAL,
    "age": d.AGE,
    "education": d.EDUCATION.where(d.EDUCATION.isin([1, 2, 3]), 4),   # 0,4,5,6 = other/unknown
    "status_latest": d.PAY_1,                                          # months past due last month (-2..8)
    "max_delay_6m": d[pay].max(axis=1),
    "months_late_6m": (d[pay] > 0).sum(axis=1),
    "utilisation": (d.BILL_AMT1 / d.LIMIT_BAL).clip(-1, 3),
    "avg_utilisation_6m": (d[bill].mean(axis=1) / d.LIMIT_BAL).clip(-1, 3),
    "pay_ratio_latest": (d.PAY_AMT1 / d.BILL_AMT1.where(d.BILL_AMT1 > 0)).fillna(1).clip(0, 2),
    "avg_payment_6m": d[pamt].mean(axis=1),
    "bill_trend": (d.BILL_AMT1 - d.BILL_AMT6) / d.LIMIT_BAL,
})
X = pd.get_dummies(X, columns=["education"], prefix="edu", drop_first=True, dtype=float)
X["log_limit"] = np.log(X.limit_bal); X["log_avg_payment"] = np.log1p(X.avg_payment_6m)
X = X.drop(columns=["limit_bal", "avg_payment_6m"])
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)

models = {
    "Logistic regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
    "Gradient boosting": HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=15, l2_regularization=1.0, random_state=42),
}
R = {"n": len(d), "default_rate": float(y.mean()), "features": list(X.columns), "train": len(Xtr), "test": len(Xte), "models": {}}
cv = StratifiedKFold(5, shuffle=True, random_state=42)
for name, m in models.items():
    cv_auc = cross_val_score(m, Xtr, ytr, cv=cv, scoring="roc_auc")
    m.fit(Xtr, ytr); p = m.predict_proba(Xte)[:, 1]
    fpr, tpr, _ = roc_curve(yte, p)
    auc = roc_auc_score(yte, p)
    ks = float(np.max(tpr - fpr))
    idx = np.linspace(0, len(fpr) - 1, 60).astype(int)
    # deciles (1 = riskiest)
    dec = pd.qcut(pd.Series(p).rank(method="first", ascending=False), 10, labels=range(1, 11))
    tab = pd.DataFrame({"y": yte.values, "p": p, "dec": dec.values}).groupby("dec", observed=True).agg(n=("y", "size"), bads=("y", "sum"), pred=("p", "mean"))
    tab["bad_rate"] = tab.bads / tab.n
    tab["cum_capture"] = tab.bads.cumsum() / tab.bads.sum()
    # strategy: decline riskiest k deciles, bad rate of the approved book
    strat = [{"decline_pct": k * 10, "approved_bad_rate": float(tab.bads.iloc[k:].sum() / tab.n.iloc[k:].sum()), "bads_caught": float(tab.cum_capture.iloc[k - 1]) if k else 0.0} for k in range(0, 6)]
    R["models"][name] = {"cv_auc_mean": float(cv_auc.mean()), "cv_auc_std": float(cv_auc.std()), "test_auc": float(auc), "gini": float(2 * auc - 1),
                         "ks": ks, "brier": float(brier_score_loss(yte, p)),
                         "roc": [[float(fpr[i]), float(tpr[i])] for i in idx],
                         "deciles": [{"decile": int(k), "n": int(r.n), "bad_rate": float(r.bad_rate), "pred": float(r.pred), "cum_capture": float(r.cum_capture)} for k, r in tab.iterrows()],
                         "strategy": strat}
lr = models["Logistic regression"][-1]
coefs = pd.Series(lr.coef_[0], index=X.columns).sort_values(key=abs, ascending=False)
R["lr_coefficients"] = {k: float(v) for k, v in coefs.items()}
# default rate by latest repayment status (raw data, full sample)
st = d.groupby(d.PAY_1.clip(-2, 4))["default"].agg(["mean", "size"])
R["by_status"] = [{"status": int(k), "default_rate": float(r["mean"]), "n": int(r["size"])} for k, r in st.iterrows()]
(root / "data/results.json").write_text(json.dumps(R, indent=1))
for k, v in R["models"].items():
    print(k, {x: round(v[x], 4) for x in ["cv_auc_mean", "cv_auc_std", "test_auc", "gini", "ks", "brier"]}); print(v["strategy"]); print([ (r["decile"], round(r["bad_rate"],3)) for r in v["deciles"]])
print(list(R["lr_coefficients"].items())[:6]); print(R["by_status"])
