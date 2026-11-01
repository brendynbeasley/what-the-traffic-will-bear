"""Extension: is rail pricing still discrimination by commodity class, or something finer?

Pigou's third degree sorts buyers into groups by a visible mark (for freight, the kind of goods)
and charges each group one price. If that is how railroads price, most of the spread in markups
should lie between commodities. If prices are set shipper by shipper, as confidential contracts
allow, most of the spread should lie inside each commodity. The STB's stratification reports split
every commodity's revenue and variable cost into three bands of revenue-to-variable-cost ratio
(below 1.0, 1.0 to 1.8, 1.8 and above), which makes the within-commodity spread visible.

Steps:
    1. CRSR2 (2-digit STCC): share of each commodity's revenue in each R/VC band.
    2. CRSR5 (5-digit STCC x car-type group x band): revenue-weighted variance of log R/VC,
       split into the part explained by commodity group, by 5-digit commodity, by commodity x car
       type, and the remainder between bands inside the same commodity and car type.
       Because each band is itself an average over many shipments, the true within-commodity
       spread is larger than this; the between-commodity shares are upper bounds.

Outputs (results/):
    band_shares.csv          revenue and R/VC by commodity and band (CRSR2)
    variance_split.csv       the decomposition
    band_shares.png          figure 2

Usage (from the repository root):
    python src/where_markups_live.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parent))  # so the sibling script imports under python -I
import value_of_service as v  # noqa: E402

CRSR2 = v.RAW / "CRSR2-2024.xlsx"
CRSR5 = v.RAW / "CRSR5-2024.xlsx"
BANDS = ["below 1.0", "1.0 to 1.8", "1.8 and above"]
TOP_N = 16      # commodities shown in the figure, by revenue


def load_crsr2():
    raw = pd.read_excel(CRSR2, header=None, dtype=str, engine="openpyxl")
    d = raw[raw[0].str.fullmatch(r"\d{2}", na=False)].copy()
    rows = []
    for _, r in d.iterrows():
        for i, band in enumerate(BANDS):
            rev, vc = pd.to_numeric(r[4 + 4 * i], errors="coerce"), pd.to_numeric(r[5 + 4 * i], errors="coerce")
            rows.append({"stcc2": r[0], "label": r[1].strip(), "band": band, "rev": rev, "vc": vc})
    b = pd.DataFrame(rows)
    redacted = b.groupby("stcc2").rev.apply(lambda s: s.isna().any())
    print(f"CRSR2 2024: {b.stcc2.nunique()} STCC groups; {redacted.sum()} have at least one redacted band (dropped)")
    b = b[~b.stcc2.map(redacted)]
    b["rvc"] = b.rev / b.vc
    tot = b.groupby("stcc2").rev.transform("sum")
    b["share_of_commodity_revenue"] = b.rev / tot
    b["commodity_revenue"] = tot
    b["commodity_rvc"] = tot / b.groupby("stcc2").vc.transform("sum")
    return b


def load_crsr5():
    raw = pd.read_excel(CRSR5, header=None, dtype=str, engine="openpyxl")
    d = raw.iloc[6:].copy()
    d = d[d[0].str.fullmatch(r"\d{5}", na=False)]
    rows = []
    for _, r in d.iterrows():
        for i, band in enumerate(BANDS):
            rows.append({"stcc5": r[0], "name": str(r[1]).strip(), "car_group": r[2], "band": band,
                         "rev": pd.to_numeric(r[6 + 4 * i], errors="coerce"),
                         "vc": pd.to_numeric(r[7 + 4 * i], errors="coerce")})
    b = pd.DataFrame(rows)
    n0, rev_all = len(b), b.rev.sum()
    b = b[b.rev.notna() & b.vc.notna() & (b.rev > 0) & (b.vc > 0)].copy()
    print(f"CRSR5 2024: {d.shape[0]} STCC5 x car-group rows, {n0} row-bands; kept {len(b)} released, positive "
          f"row-bands ({n0 - len(b)} redacted or empty)")
    b["stcc2"] = b.stcc5.str[:2]
    drop = b.stcc2.isin(v.NON_COMMODITY)
    print(f"  dropped {drop.sum()} non-commodity row-bands, revenue ${b.rev[drop].sum() / 1e6:,.1f} bn")
    b = b[~drop].copy()
    b["sctg2"] = v.map_sctg(b.stcc5)
    b["cell"] = b.stcc5 + "_" + b.car_group
    b["y"] = np.log(b.rev / b.vc)
    print(f"  {len(b)} row-bands, {b.stcc5.nunique()} commodities, revenue ${b.rev.sum() / 1e6:,.1f} bn")
    return b


def weighted_r2(formula, data):
    res = smf.wls(formula, data, weights=data.rev).fit()
    return res.rsquared, int(res.df_model)


def variance_split(b):
    w = b.rev / b.rev.sum()
    mean = (w * b.y).sum()
    total = (w * (b.y - mean) ** 2).sum()
    cfs = v.load_cfs()
    b = b.join(cfs[["value_per_ton"]], on="sctg2")
    rows = [{"layer": "total variance of log R/VC (revenue weighted)", "value": total, "params": 0}]
    bv = b[b.value_per_ton.notna()].assign(lv=lambda x: np.log(x.value_per_ton))
    for label, formula, data in [
        ("share explained by value per ton of the goods", "y ~ lv", bv),
        ("share explained by commodity group (SCTG, 2-digit)", "y ~ C(sctg2)", b),
        ("share explained by commodity (STCC, 5-digit)", "y ~ C(stcc5)", b),
        ("share explained by commodity x car type", "y ~ C(cell)", b),
    ]:
        r2, k = weighted_r2(formula, data)
        levels = data[formula.split("C(")[1].rstrip(")")].nunique() if "C(" in formula else 0
        rows.append({"layer": label, "value": r2, "params": k, "levels": levels})
    rows.append({"layer": "share left between R/VC bands within commodity x car type",
                 "value": 1 - rows[-1]["value"], "params": 0})
    rows.append({"layer": "row-bands used", "value": len(b), "params": 0})
    rows.append({"layer": "revenue covered, $ billion", "value": b.rev.sum() / 1e6, "params": 0})
    return pd.DataFrame(rows)


def figure(bands):
    top = (bands.drop_duplicates("stcc2").sort_values("commodity_revenue", ascending=False).head(TOP_N))
    order = top.sort_values("commodity_revenue").stcc2.tolist()
    p = bands.pivot(index="stcc2", columns="band", values="share_of_commodity_revenue").loc[order, BANDS]
    labels = top.set_index("stcc2").label.loc[order]
    fig, ax = plt.subplots(figsize=(8.5, 6.2))
    left = np.zeros(len(p))
    colors = ["#8fb3d9", "#c9c9c9", "#c0504d"]
    for band, col in zip(BANDS, colors):
        ax.barh(range(len(p)), p[band] * 100, left=left, color=col, label=f"R/VC {band}")
        left += p[band].values * 100
    ax.set_yticks(range(len(p)))
    ax.set_yticklabels([f"{l} ({bands.set_index('stcc2').commodity_rvc[c].iloc[0]:.2f})" for c, l in labels.items()],
                       fontsize=8)
    ax.set_xlabel("Share of the commodity's 2024 rail revenue, %")
    ax.set_title("Inside each commodity, rail traffic runs from below variable cost to above the 180% line\n"
                 "(commodity's overall R/VC in parentheses)", fontsize=10)
    ax.legend(frameon=False, fontsize=8, loc="lower center", bbox_to_anchor=(0.5, -0.2), ncol=3)
    ax.set_xlim(0, 100)
    fig.tight_layout()
    fig.savefig(v.OUT / "band_shares.png", dpi=160)
    plt.close(fig)


def main():
    v.OUT.mkdir(exist_ok=True)
    bands = load_crsr2()
    bands.to_csv(v.OUT / "band_shares.csv", index=False, float_format="%.5g")
    goods = bands[~bands.stcc2.isin(v.NON_COMMODITY)]
    big = goods[goods.commodity_revenue > 1e6]           # commodities with more than $1 billion of revenue
    lo = big[big.band == BANDS[0]].share_of_commodity_revenue
    hi = big[big.band == BANDS[2]].share_of_commodity_revenue
    print(f"  {big.stcc2.nunique()} commodities with > $1 bn revenue: share below cost ranges "
          f"{lo.min():.1%} to {lo.max():.1%}; share at 1.8+ ranges {hi.min():.1%} to {hi.max():.1%}")
    allg = goods.groupby("band").agg(rev=("rev", "sum"), vc=("vc", "sum"))
    allg["share"] = allg.rev / allg.rev.sum()
    allg["rvc"] = allg.rev / allg.vc
    print(allg.round(3).to_string())
    allg.to_csv(v.OUT / "band_totals.csv", float_format="%.5g")

    split = variance_split(load_crsr5())
    split.to_csv(v.OUT / "variance_split.csv", index=False, float_format="%.5g")
    print(split.to_string(index=False))
    figure(goods)
    print("wrote results/band_shares.csv, band_totals.csv, variance_split.csv, band_shares.png")


if __name__ == "__main__":
    main()
