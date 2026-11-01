"""Pigou's railway test on 2024 US freight rates: do railroads price by the value of the goods?

Pigou (1920, Part II, ch. XV) said a railroad pricing on the "cost of service principle" charges
every commodity the same rate per unit of cost, while one pricing on the "value of service
principle" practises discrimination of the third degree and charges valuable goods more. This
script puts the two principles side by side with the Surface Transportation Board's 2024
Commodity Revenue Stratification Report, which gives freight revenue and the Board's own
estimate of variable cost (URCS) for every released commodity and car type, and the 2022
Commodity Flow Survey, which gives the value per ton of goods moved by rail.

Outputs (results/):
    commodity_groups.csv      one row per SCTG commodity group: revenue, cost, value, ratios
    value_tests.csv           every regression in the README and TECHNICAL notes
    named_commodities.csv     the table of recognizable commodities
    sample_summary.csv        sample size and aggregate revenue and cost
    masking_check.csv         STB report revenue vs public-use waybill revenue, by STCC group
    value_vs_markup.png       figure 1

Usage (from the repository root):
    python src/value_of_service.py              # downloads the 68 MB public-use waybill once
    python src/value_of_service.py --skip-puf   # skip the masking check
"""

import argparse
import urllib.request
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "results"

CRSR7 = RAW / "CRSR7-2024.xlsx"        # stb.gov, Commodity Revenue Stratification Report, 7-digit STCC
CFS = RAW / "CF2200A09.zip"            # census.gov, 2022 CFS table A09, commodity x mode
CROSSWALK = ROOT / "data" / "stcc_to_sctg2.csv"   # my STCC -> SCTG mapping, longest prefix wins
PUF_URL = "https://www.stb.gov/wp-content/uploads/PublicUseWaybillSample2024.zip"
PUF = RAW / "PublicUseWaybillSample2024.zip"

SUMMARY = {}   # sample counts collected along the way, written to results/sample_summary.csv

# STCC groups with no commodity identity (returned empties, forwarder and mixed intermodal
# traffic, mail, small packages, shipper associations). Their rates say nothing about the
# value of a good, so they are set aside before any test.
NON_COMMODITY = {"41", "42", "43", "44", "45", "46", "47", "50"}

# The statutory floor below which the STB cannot find market dominance (49 U.S.C. 10707(d)).
RVC_THRESHOLD = 1.80

# Commodities for the names table: 7-digit STCC codes, summed across car types.
NAMED = {
    "Thermal coal": ["1121290"],
    "Metallurgical coal": ["1121210"],
    "Crushed limestone": ["1421965"],
    "Frac sand": ["1441316", "1441317"],
    "Corn": ["0113215"],
    "Wheat": ["0113710"],
    "Soybean meal": ["2092314"],
    "Ethanol": ["2818445", "2818446"],
    "Lumber": ["2421184"],
    "Portland cement": ["3241115"],
    "Polyethylene pellets": ["2821142"],
    "PVC resin": ["2821141"],
    "Propane": ["2912111"],
    "Sugar": ["2062110"],
    "Steel sheet in coils": ["3312332"],
    "Beer": ["2082110"],
    "New passenger cars": ["3711120"],
    "New pickups and vans": ["3711215"],
}


def load_crsr7():
    raw = pd.read_excel(CRSR7, header=None, dtype=str, engine="openpyxl")
    d = raw.iloc[5:].copy()
    d.columns = ["stcc7", "name", "car", "car_name", "records", "cars", "tons", "rev", "vc", "miles"]
    d = d[d.stcc7.str.fullmatch(r"\d{7}", na=False)].copy()
    for c in ["records", "cars", "tons", "rev", "vc", "miles"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    totals = raw[raw[0].astype(str).str.startswith("TOTALS")]
    print(f"CRSR7 2024: {len(d)} released STCC7 x car-type cells, revenue ${d.rev.sum() / 1e6:,.1f} bn")
    print("  report totals (revenue $000):", dict(zip(totals[0], pd.to_numeric(totals[7]))))
    SUMMARY["report_revenue_all_musd"] = pd.to_numeric(totals[7]).iloc[1] / 1000
    SUMMARY["report_revenue_released_musd"] = pd.to_numeric(totals[7]).iloc[0] / 1000
    SUMMARY["report_vc_all_musd"] = pd.to_numeric(totals[8]).iloc[1] / 1000
    SUMMARY["released_cells"] = len(d)
    d["stcc2"] = d.stcc7.str[:2]
    drop = d.stcc2.isin(NON_COMMODITY)
    SUMMARY["non_commodity_revenue_musd"] = d.rev[drop].sum() / 1000
    print(f"  dropped {drop.sum()} non-commodity cells (STCC {sorted(NON_COMMODITY)}), "
          f"revenue ${d.rev[drop].sum() / 1e6:,.1f} bn")
    d = d[~drop].copy()
    bad = d[["tons", "rev", "vc", "miles"]].isna().any(axis=1) | (d.vc <= 0) | (d.tons <= 0)
    print(f"  dropped {bad.sum()} cells with missing or zero cost, tons or miles")
    d = d[~bad].copy()
    d["ton_miles"] = d.tons * d.miles          # thousand tons x average miles per carload
    d["car_group"] = d.car.str[0]              # AAR equipment group letter (C covered hopper, T tank, ...)
    return d


def map_sctg(stcc7):
    cw = pd.read_csv(CROSSWALK, dtype=str)
    rules = sorted(zip(cw.stcc_prefix, cw.sctg2), key=lambda r: -len(r[0]))
    def one(code):
        for prefix, sctg in rules:
            if code.startswith(prefix):
                return sctg
        return None
    return stcc7.map(one)


def load_cfs():
    """Value per ton of 2022 shipments by SCTG group: rail where published, all modes otherwise."""
    with zipfile.ZipFile(CFS) as z:
        d = pd.read_csv(z.open("CF2200A09.dat"), sep="|", dtype=str)
    d = d[(d.SHIPDIST == "001") & (d.COMM.str.len() == 2)]
    num = lambda s: pd.to_numeric(s, errors="coerce")
    out = {}
    for mode, tag in [("12", "rail"), ("00", "all")]:
        m = d[d.DMODE == mode].set_index("COMM")
        ok = m.VAL_F.isna() & m.TON_F.isna() & (num(m.VAL) > 0) & (num(m.TON) > 0)
        out[f"value_{tag}"] = num(m.VAL).where(ok)        # $ million
        out[f"tons_{tag}"] = num(m.TON).where(ok)         # thousand tons
        out[f"cv_value_{tag}"] = num(m.VAL_S).where(ok)   # coefficient of variation, %
    cfs = pd.DataFrame(out)
    cfs["label"] = d[d.DMODE == "00"].set_index("COMM").COMM_LABEL
    # Pigou's non-transferability: how much of the commodity's tonnage goes by rail rather than
    # truck, barge or pipeline (all distances; the 250+ mile bands are too often suppressed).
    cfs["rail_share"] = cfs.tons_rail / cfs.tons_all
    cfs["vpt_rail"] = cfs.value_rail * 1e6 / (cfs.tons_rail * 1e3)
    cfs["vpt_all"] = cfs.value_all * 1e6 / (cfs.tons_all * 1e3)
    cfs["value_per_ton"] = cfs.vpt_rail.fillna(cfs.vpt_all)
    cfs["value_source"] = np.where(cfs.vpt_rail.notna(), "rail", np.where(cfs.vpt_all.notna(), "all modes", ""))
    print(f"CFS 2022: {len(cfs)} SCTG groups; rail value per ton published for {cfs.vpt_rail.notna().sum()}, "
          f"all-modes fallback for {(cfs.value_source == 'all modes').sum()}, none for {(cfs.value_source == '').sum()}")
    return cfs


def group_table(cells, cfs):
    g = cells.groupby("sctg2").agg(rev=("rev", "sum"), vc=("vc", "sum"), tons=("tons", "sum"),
                                  cars=("cars", "sum"), ton_miles=("ton_miles", "sum"),
                                  cells=("rev", "size"))
    g = g.join(cfs[["label", "value_per_ton", "value_source", "cv_value_rail", "rail_share"]])
    g["rvc"] = g.rev / g.vc
    g["rev_per_tm_cents"] = g.rev / g.ton_miles * 100      # $000 / (000 ton-miles) -> cents
    g["vc_per_tm_cents"] = g.vc / g.ton_miles * 100
    g["rev_per_ton"] = g.rev / g.tons                      # dollars per ton
    g["avg_haul"] = g.ton_miles / g.tons
    g["tons_per_car"] = g.tons * 1000 / g.cars
    g["freight_share_of_value"] = g.rev_per_ton / g.value_per_ton
    g["rev_share"] = g.rev / g.rev.sum()
    return g.sort_values("rev", ascending=False)


def fit(formula, data, weights=None, cluster=None):
    model = smf.wls(formula, data, weights=weights) if weights is not None else smf.ols(formula, data)
    if cluster is not None:
        return model.fit(cov_type="cluster", cov_kwds={"groups": cluster})
    return model.fit(cov_type="HC1")


def record(rows, label, res, term, n_groups=None):
    ci = res.conf_int().loc[term]
    rows.append({"test": label, "term": term, "coef": res.params[term], "se": res.bse[term],
                 "ci_low": ci[0], "ci_high": ci[1], "p": res.pvalues[term], "n": int(res.nobs),
                 "clusters": n_groups, "r2": res.rsquared})


def run_tests(g, cells):
    rows = []
    k = g[g.value_per_ton.notna()].copy()
    k["lv"] = np.log(k.value_per_ton)
    k["lrvc"] = np.log(k.rvc)
    k["lrev_tm"] = np.log(k.rev_per_tm_cents)
    k["lvc_tm"] = np.log(k.vc_per_tm_cents)
    k["lshare"] = np.log(k.freight_share_of_value)
    k["lrev_ton"] = np.log(k.rev_per_ton)
    record(rows, "A1 group: log R/VC on log value, equal weights", fit("lrvc ~ lv", k), "lv")
    record(rows, "A2 group: log R/VC on log value, revenue weights", fit("lrvc ~ lv", k, k.rev), "lv")
    rail = k[k.value_source == "rail"]
    record(rows, "A3 group: as A1, rail-published values only", fit("lrvc ~ lv", rail), "lv")
    no_big = k[~k.index.isin(["15", "36"])]
    record(rows, "A4 group: as A1, without coal and motor vehicles", fit("lrvc ~ lv", no_big), "lv")
    res = fit("lrev_tm ~ lv + lvc_tm", k)
    record(rows, "B1 group: log revenue per ton-mile on log value and log cost per ton-mile", res, "lv")
    record(rows, "B1 group: log revenue per ton-mile on log value and log cost per ton-mile", res, "lvc_tm")
    record(rows, "C1 group: log freight share of value on log value", fit("lshare ~ lv", k), "lv")
    record(rows, "C2 group: log revenue per ton on log value", fit("lrev_ton ~ lv", k), "lv")
    record(rows, "C3 group: log tons per car on log value", fit("np.log(tons_per_car) ~ lv", k), "lv")
    r = k[k.rail_share.notna()].copy()
    r["share10"] = r.rail_share * 10          # coefficient per 10 points of rail's tonnage share
    record(rows, "E1 group: log R/VC on rail share of tonnage", fit("lrvc ~ share10", r), "share10")
    res = fit("lrvc ~ share10 + lv", r)
    record(rows, "E2 group: log R/VC on rail share and log value", res, "share10")
    record(rows, "E2 group: log R/VC on rail share and log value", res, "lv")
    record(rows, "E3 group: as E2, revenue weights", fit("lrvc ~ share10 + lv", r, r.rev), "share10")
    record(rows, "E4 group: as E2, without coal", fit("lrvc ~ share10 + lv", r[r.index != "15"]), "share10")

    c = cells.join(g[["value_per_ton"]], on="sctg2")
    c = c[c.value_per_ton.notna()].copy()
    c["lv"] = np.log(c.value_per_ton)
    c["lrvc"] = np.log(c.rev / c.vc)
    c["lmiles"] = np.log(c.miles)
    c["ltpc"] = np.log(c.tons * 1000 / c.cars)
    n_cl = c.sctg2.nunique()
    f = "lrvc ~ lv + lmiles + ltpc + C(car_group)"
    record(rows, "D1 cell: log R/VC on log value, car-group FE, revenue weights", fit(f, c, c.rev, c.sctg2), "lv", n_cl)
    record(rows, "D2 cell: as D1, equal weights", fit(f, c, None, c.sctg2), "lv", n_cl)
    cs = c.join(r[["share10"]], on="sctg2", how="inner")
    record(rows, "E5 cell: rail share, log value, car-group FE, revenue weights",
           fit(f.replace("lv", "lv + share10"), cs, cs.rev, cs.sctg2), "share10", cs.sctg2.nunique())
    for grp, name in [("C", "covered hoppers"), ("T", "tank cars")]:
        s = c[c.car_group == grp]
        record(rows, f"D3 cell: {name} only, revenue weights", fit("lrvc ~ lv + lmiles + ltpc", s, s.rev, s.sctg2),
               "lv", s.sctg2.nunique())
    print(f"  group-level tests use {len(k)} SCTG groups ({len(r)} with a published rail share); "
          f"cell-level tests use {len(c)} cells in {n_cl} groups")
    return pd.DataFrame(rows)


def named_table(cells, g):
    rows = []
    for label, codes in NAMED.items():
        s = cells[cells.stcc7.isin(codes)]
        if s.empty:
            print(f"  named commodity not in released data: {label}")
            continue
        sctg = s.sctg2.iloc[0]
        rows.append({"commodity": label, "stcc7": "+".join(codes), "sctg2": sctg,
                     "sctg_label": g.loc[sctg, "label"], "revenue_musd": s.rev.sum() / 1000, "vc_musd": s.vc.sum() / 1000,
                     "tons_m": s.tons.sum() / 1000, "rvc": s.rev.sum() / s.vc.sum(),
                     "rev_per_tm_cents": s.rev.sum() / s.ton_miles.sum() * 100,
                     "vc_per_tm_cents": s.vc.sum() / s.ton_miles.sum() * 100,
                     "avg_haul_miles": s.ton_miles.sum() / s.tons.sum(),
                     "tons_per_car": s.tons.sum() * 1000 / s.cars.sum(),
                     "rev_per_ton": s.rev.sum() / s.tons.sum(),
                     "group_value_per_ton": g.loc[sctg, "value_per_ton"]})
    t = pd.DataFrame(rows)
    t["freight_share_of_value"] = t.rev_per_ton / t.group_value_per_ton
    return t.sort_values("rvc", ascending=False)


def masking_check(skip):
    """Compare the STB report's revenue with the public-use file's expanded revenue by STCC group."""
    if skip:
        print("masking check skipped (--skip-puf)")
        return None
    if not PUF.exists():
        print(f"downloading {PUF_URL} (68 MB) ...")
        tmp = PUF.with_suffix(".part")
        req = urllib.request.Request(PUF_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as r, open(tmp, "wb") as f:
            f.write(r.read())
        tmp.rename(PUF)
    with zipfile.ZipFile(PUF) as z:
        puf = pd.read_fwf(z.open("PublicUseWaybillSample2024.txt"), colspecs=[(35, 40), (230, 241)],
                          header=None, names=["stcc", "xrev"], dtype={"stcc": str})
    print(f"public-use waybill 2024: {len(puf):,} records, expanded revenue ${puf.xrev.sum() / 1e9:,.1f} bn")
    puf["stcc2"] = puf.stcc.str[:2]
    p = puf.groupby("stcc2").xrev.sum() / 1000                    # -> $000
    raw = pd.read_excel(RAW / "CRSR2-2024.xlsx", header=None, dtype=str, engine="openpyxl")
    d = raw[raw[0].str.fullmatch(r"\d{2}", na=False)].set_index(0)
    rev = d[[4, 8, 12]].apply(pd.to_numeric, errors="coerce")
    released = rev.notna().all(axis=1)
    m = pd.DataFrame({"label": d[1], "stb_revenue": rev.sum(axis=1).where(released), "puf_revenue": p})
    m.index.name = "stcc2"
    m["puf_over_stb"] = m.puf_revenue / m.stb_revenue
    tot = raw[raw[0].astype(str).str.startswith("TOTAL")]
    released_total = pd.to_numeric(tot.iloc[0, [4, 8, 12]]).sum()
    print(f"  public-use expanded revenue / STB two-digit report total: {p.sum() / released_total:.3f}")
    m.loc["ALL"] = ["All STCC groups", released_total, p.sum(), p.sum() / released_total]
    return m


def figure(g, tests):
    k = g[g.value_per_ton.notna()]
    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    ax.scatter(k.value_per_ton, k.rvc, s=np.sqrt(k.rev) / 2.2, alpha=0.55, color="#3b6ea5", edgecolor="white")
    for code, r in k.iterrows():
        if r.rev_share > 0.03 or r.rvc > 2.2 or r.rvc < 1.35 or r.value_per_ton < 25:
            ax.annotate(short_label(r.label), (r.value_per_ton, r.rvc), fontsize=7.5,
                        xytext=(4, 3), textcoords="offset points", color="#333333")
    a1 = tests[tests.test.str.startswith("A1")].iloc[0]
    x = np.linspace(np.log(k.value_per_ton.min()), np.log(k.value_per_ton.max()), 50)
    res = smf.ols("np.log(rvc) ~ np.log(value_per_ton)", k).fit()
    ax.plot(np.exp(x), np.exp(res.params.iloc[0] + res.params.iloc[1] * x), color="#b5443b", lw=1.5,
            label=f"fitted, elasticity {a1.coef:.2f} (SE {a1.se:.2f})")
    ax.axhline(RVC_THRESHOLD, color="gray", ls="--", lw=1, label="180% statutory threshold")
    ax.axhline(1.0, color="gray", ls=":", lw=1, label="revenue = variable cost")
    ax.set_xscale("log")
    ax.set_xlabel("Value of goods moved by rail, dollars per ton (2022 CFS, log scale)")
    ax.set_ylabel("Revenue / variable cost, 2024")
    ax.set_title("Rail markups over cost against the value of the goods, by commodity group")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "value_vs_markup.png", dpi=160)
    plt.close(fig)


def short_label(s):
    s = s.split("(")[0].split(",")[0].strip()
    return s if len(s) <= 28 else s[:26] + "."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-puf", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)

    cells = load_crsr7()
    cells["sctg2"] = map_sctg(cells.stcc7)
    unmapped = cells.sctg2.isna()
    print(f"  mapped to SCTG: {(~unmapped).sum()} cells; unmapped (dropped): {unmapped.sum()}")
    cells = cells[~unmapped]
    cfs = load_cfs()
    g = group_table(cells, cfs)
    missing = g.value_per_ton.isna()
    print(f"  {len(g)} SCTG groups carry rail revenue; {missing.sum()} have no CFS value "
          f"({', '.join(g.index[missing])}), revenue share {g.rev_share[missing].sum():.1%}")
    g.to_csv(OUT / "commodity_groups.csv", float_format="%.5g")

    tests = run_tests(g, cells)
    tests.to_csv(OUT / "value_tests.csv", index=False, float_format="%.5g")
    print(tests[["test", "term", "coef", "se", "p", "n"]].to_string(index=False))

    named = named_table(cells, g)
    named.to_csv(OUT / "named_commodities.csv", index=False, float_format="%.5g")
    print(named[["commodity", "rvc", "rev_per_tm_cents", "avg_haul_miles", "group_value_per_ton"]].round(2).to_string(index=False))

    SUMMARY.update({"cells_used": len(cells), "car_groups": cells.car_group.nunique(), "revenue_used_musd": cells.rev.sum() / 1000,
                    "vc_used_musd": cells.vc.sum() / 1000, "rvc_used": cells.rev.sum() / cells.vc.sum(),
                    "sctg_groups": len(g), "report_rvc_all": SUMMARY["report_revenue_all_musd"] / SUMMARY["report_vc_all_musd"]})
    # Pigou's linear-demand case with the demand price for carriage proportional to value:
    # d ln(R/VC) / d ln(value) = 1 - 1 / (2 R/VC), evaluated at the sample's overall R/VC.
    SUMMARY["pigou_linear_implied_elasticity"] = 1 - 1 / (2 * SUMMARY["rvc_used"])
    pd.Series(SUMMARY, name="value").rename_axis("measure").to_csv(OUT / "sample_summary.csv", float_format="%.6g")
    m = masking_check(args.skip_puf)
    if m is not None:
        m.to_csv(OUT / "masking_check.csv", float_format="%.5g")
        big = m[m.stb_revenue > 1e6].sort_values("stb_revenue", ascending=False)
        print(big[["label", "stb_revenue", "puf_revenue", "puf_over_stb"]].round(3).to_string())
    figure(g, tests)
    print("wrote results/commodity_groups.csv, value_tests.csv, named_commodities.csv, "
          "sample_summary.csv, masking_check.csv, value_vs_markup.png")


if __name__ == "__main__":
    main()
