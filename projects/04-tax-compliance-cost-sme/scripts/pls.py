"""Minimal PLS-SEM (Lohmoller algorithm, mode A, path weighting scheme) with
measurement-model diagnostics. Used by analyse.py."""
import numpy as np, pandas as pd

def zs(a): return (a - a.mean(0)) / a.std(0, ddof=0)

def pls(X, blocks, paths, tol=1e-7, max_iter=300):
    """X: DataFrame of indicators. blocks: {lv: [cols]}. paths: list of (from, to)."""
    lvs = list(blocks)
    Xs = {lv: zs(X[blocks[lv]].values.astype(float)) for lv in lvs}
    w = {lv: np.ones(len(blocks[lv])) for lv in lvs}
    Y = {lv: zs(Xs[lv] @ w[lv]) for lv in lvs}
    for _ in range(max_iter):
        Z = {}
        for j in lvs:
            preds = [i for i, k in paths if k == j]; succ = [k for i, k in paths if i == j]
            z = np.zeros(len(X))
            if preds:
                P = np.column_stack([Y[i] for i in preds]); b = np.linalg.lstsq(P, Y[j], rcond=None)[0]
                z += P @ b
            for k in succ: z += np.corrcoef(Y[j], Y[k])[0, 1] * Y[k]
            Z[j] = z
        nw = {j: Xs[j].T @ zs(Z[j]) / len(X) for j in lvs}
        nY = {j: zs(Xs[j] @ nw[j]) for j in lvs}
        # scale weights so LV has unit variance
        nw = {j: nw[j] / np.std(Xs[j] @ nw[j]) for j in lvs}
        diff = max(np.abs(nw[j] - w[j]).max() for j in lvs)
        w, Y = nw, nY
        if diff < tol: break
    scores = pd.DataFrame(Y, index=X.index)
    load = {j: np.array([np.corrcoef(Xs[j][:, c], Y[j])[0, 1] for c in range(Xs[j].shape[1])]) for j in lvs}
    return scores, w, load, Xs

def structural(scores, endo_map):
    """endo_map: {endogenous: [predictors]} -> coefs, R2"""
    out, r2 = {}, {}
    for y, xs in endo_map.items():
        P = scores[xs].values; b = np.linalg.lstsq(P, scores[y].values, rcond=None)[0]
        out.update({(x, y): bb for x, bb in zip(xs, b)})
        r2[y] = 1 - ((scores[y].values - P @ b) ** 2).mean() / scores[y].values.var()
    return out, r2

def reliability(Xs, w, load):
    res = {}
    for j in Xs:
        l, k = load[j], len(load[j]); S = np.corrcoef(Xs[j].T)
        alpha = k / (k - 1) * (1 - k / S.sum())
        cr = l.sum() ** 2 / (l.sum() ** 2 + (1 - l ** 2).sum())
        ave = (l ** 2).mean()
        ww = w[j]; W = np.outer(ww, ww)
        rho_a = (ww @ ww) ** 2 * (ww @ (S - np.diag(np.diag(S))) @ ww) / (ww @ (W - np.diag(np.diag(W))) @ ww)
        res[j] = {"alpha": alpha, "rho_a": rho_a, "cr": cr, "ave": ave}
    return res

def htmt(X, blocks):
    lvs = list(blocks); R = X.corr().abs(); out = {}
    def mono(cols):
        r = R.loc[cols, cols].values; return r[np.triu_indices(len(cols), 1)].mean()
    for a in range(len(lvs)):
        for b in range(a + 1, len(lvs)):
            A, B = blocks[lvs[a]], blocks[lvs[b]]
            out[(lvs[a], lvs[b])] = R.loc[A, B].values.mean() / np.sqrt(mono(A) * mono(B))
    return out
