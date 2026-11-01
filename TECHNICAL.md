# Technical notes

This is the technical companion to the [README](README.md). It covers the original work, the data, the rules, the
full set of test statistics and how to reproduce everything. Every table is in
[results/FINDINGS.md](results/FINDINGS.md).

## The original study

A. C. Pigou, *The Economics of Welfare*, London: Macmillan, 1920. Part II, chapter XIV, "Discriminating Monopoly"
(pp. 240–255), and chapter XV, "The Special Problem of Railway Rates" (pp. 256–282). In the fourth edition (1932)
these are chapters XVII and XVIII. I read the first edition's full text on the Internet Archive
(`economicsofwelfa00pigouoft`) and checked chapter numbers against the 1932 edition there.

The work is theoretical and has no data table. Its claims that this repository tests are the following, with the
page in the 1920 edition.

| Claim | Where |
|---|---|
| Three degrees of discrimination; in practice "the third degree only is found" | ch. XIV §§5–6, pp. 244–246 |
| First-degree example, 100 units sold as one bundle for 300 shillings against 1 shilling at the margin | ch. XIV §6, pp. 244–245 |
| Cost of service corresponds to simple competition, value of service to the third degree | ch. XV §§7–8 |
| Goods classes are drawn mainly by value; absolute, not percentage, charges rise with value | ch. XV §6, pp. 269–270 |
| Straight-line demand, constant cost: monopoly markup is half the gap between cost and the top demand price | ch. XV §6, footnote, p. 268 |
| Straight-line demands: third-degree output equals simple-monopoly output when both markets are served | Appendix III §24, pp. 951–952 |

## Headline results

| Test | Estimate | SE | 95% CI | N |
|---|---|---|---|---|
| ln R/VC on ln value, commodity groups | −0.019 | 0.021 | [−0.060, 0.022] | 33 |
| Same, revenue weights | −0.028 | 0.028 | [−0.083, 0.027] | 33 |
| Pigou's straight-line prediction at R/VC = 1.61 | 0.689 | | | |
| ln R/VC on ln value, cells, car-group FE, revenue weights | 0.047 | 0.024 | [0.000, 0.094] | 1,434 (33 clusters) |
| ln revenue per ton on ln value | 0.355 | 0.072 | [0.213, 0.496] | 33 |
| ln revenue per ton-mile on ln value, holding ln cost per ton-mile | −0.054 | 0.019 | [−0.090, −0.017] | 33 |
| ln R/VC on rail tonnage share (per 10 points) and ln value | −0.010 | 0.025 | [−0.059, 0.039] | 28 |
| Share of variance of ln R/VC explained by detailed commodity and car type | 35.2% | | | 1,280 cells |

## Data

| File | Source | What it holds |
|---|---|---|
| `data/raw/CRSR7-2024.xlsx` | STB, Commodity Revenue Stratification Report, 7-digit STCC, 2024 | Revenue, URCS variable cost, tons, cars, average miles by STCC7 and car type |
| `data/raw/CRSR5-2024.xlsx` | Same, 5-digit STCC | The same split into R/VC zones below 1.0, 1.0–1.8, 1.8+ by STCC5 and car-type group |
| `data/raw/CRSR2-2024.xlsx` | Same, 2-digit STCC | The same zones by STCC2 |
| `data/raw/CF2200A09.zip` | Census, 2022 Commodity Flow Survey, table A09 | Value and tons by SCTG, mode and distance |
| `data/raw/PublicUseWaybillSample2024.zip` | STB, Public Use Waybill Sample 2024 (68 MB, downloaded by the script, not committed) | 2,166,913 waybill records, for the revenue check |
| `data/stcc_to_sctg2.csv` | My crosswalk | STCC prefix to SCTG 2-digit group, longest prefix wins |

STB files are from stb.gov (Reports and Data, Economic Data, and Waybill) and the Census file from
www2.census.gov/programs-surveys/cfs/data/2022/, all downloaded on 1 November 2026.

## Method

Rules fixed before looking at results:

- Unit of the main test is the SCTG 2-digit group, the finest level at which the survey publishes rail value per ton.
  Revenue, cost, tons and ton-miles are summed over released STCC7 by car-type cells; R/VC is the ratio of sums.
- STCC groups 41–47 and 50 (miscellaneous and mixed shipments, returned empties, forwarder, mail, shipper
  association, small packages) are dropped because they carry no commodity identity.
- Value per ton is the survey's rail value divided by rail tons. Where either is suppressed I use all modes and flag
  the group; test A3 drops flagged groups. Crude petroleum (SCTG 16) has no survey value and is left out of tests.
- Ton-miles per cell are tons times the report's average miles per carload.
- Dependence on rail is rail tons over all-mode tons for the group, all distances. The 250-mile-plus version was
  planned but only 10 groups have no suppressed distance band, so it is not reported.
- Standard errors are HC1 at the group level and clustered by SCTG group at the cell level.

The tests:

```math
\begin{aligned}
\text{(A)}\quad & \ln \text{R/VC}_g = \alpha + \beta \ln v_g + \varepsilon_g \\
\text{(B)}\quad & \ln (R/\text{tm})_g = \alpha + \beta \ln v_g + \theta \ln (VC/\text{tm})_g + \varepsilon_g \\
\text{(C)}\quad & \ln (R/\text{ton})_g = \alpha + \beta \ln v_g + \varepsilon_g \\
\text{(D)}\quad & \ln \text{R/VC}_c = \beta \ln v_{g(c)} + \gamma \ln \text{miles}_c + \delta \ln (\text{tons/car})_c + \mu_{k(c)} + \varepsilon_c \\
\text{(E)}\quad & \ln \text{R/VC}_g = \alpha + \phi\, s_g + \beta \ln v_g + \varepsilon_g
\end{aligned}
```

Here *g* is a commodity group, *c* a commodity by car-type cell, *k* one of 16 equipment groups, *tm* ton-miles and
$`s_g`$ rail's tonnage share in tens of percentage points. The value-of-service hypothesis is $`\beta > 0`$ in (A), (B) and
(D); the cost-of-service hypothesis is $`\beta = 0`$ with $`\theta`$ near 1 in (B).

Pigou's straight-line case gives the benchmark. With $`p_i = (a_i + c)/2`$ and $`a_i = \kappa v_i`$,

```math
\frac{d \ln \text{R/VC}_i}{d \ln v_i} = 1 - \frac{1}{2\,\text{R/VC}_i} = 1 - \frac{1}{2 \times 1.609} = 0.689
```

The extension decomposes the revenue-weighted variance of ln R/VC across released STCC5 by car-group by zone cells
(1,280 cells, $63.6 billion) with weighted least squares on nested fixed effects, reporting $`R^2`$ at each layer.
The value-per-ton layer uses the 1,277 of these cells that have a survey value (crude petroleum has none).

## Full test statistics

| Test | Coefficient | SE | p | N |
|---|---|---|---|---|
| A1 group, equal weights | −0.019 | 0.021 | 0.372 | 33 |
| A2 group, revenue weights | −0.028 | 0.028 | 0.322 | 33 |
| A3 rail-published values only | −0.004 | 0.030 | 0.902 | 28 |
| A4 without coal and motor vehicles | −0.017 | 0.022 | 0.449 | 31 |
| B1 value, holding cost per ton-mile | −0.054 | 0.019 | 0.004 | 33 |
| B1 cost per ton-mile | 1.184 | 0.121 | < 0.001 | 33 |
| C1 freight share of value | −0.645 | 0.072 | < 0.001 | 33 |
| C2 revenue per ton | 0.355 | 0.072 | < 0.001 | 33 |
| C3 tons per car | −0.384 | 0.075 | < 0.001 | 33 |
| D1 cells, revenue weights | 0.047 | 0.024 | 0.049 | 1,434 |
| D2 cells, equal weights | 0.087 | 0.019 | < 0.001 | 1,434 |
| D3 covered hoppers | 0.046 | 0.024 | 0.055 | 225 |
| D3 tank cars | −0.135 | 0.079 | 0.085 | 421 |
| E1 rail share alone | −0.005 | 0.033 | 0.884 | 28 |
| E2 rail share, with value | −0.010 | 0.025 | 0.692 | 28 |
| E3 rail share, revenue weights | −0.037 | 0.017 | 0.032 | 28 |
| E4 rail share, without coal | 0.034 | 0.063 | 0.587 | 27 |
| E5 rail share, cells | 0.022 | 0.020 | 0.268 | 1,363 |

Variance split of ln R/VC (total weighted variance 0.167): value per ton 1.6%, SCTG group (39 levels) 16.4%, STCC5
(367) 32.3%, STCC5 by car group (617) 35.2%, remainder between zones 64.8%.

Revenue check: the public-use file's expanded revenue is $101.2 billion against $79.4 billion in the Board's two-digit
report, a ratio of 1.275. The public-use file's STCC is read from columns 36–40 and expanded revenue from columns
231–241, as laid out in the 2024 Waybill Reference Guide.

## Reproducing the results

```bash
pip install -r requirements.txt
python src/value_of_service.py
python src/where_markups_live.py
```

The first script downloads the 68 MB public-use waybill file once; add `--skip-puf` to skip the revenue check. Python
3.12 or later.

## References

- Pigou, A. C. (1912). *Wealth and Welfare*. Macmillan.
- Pigou, A. C. (1920). *The Economics of Welfare*. Macmillan. Fourth edition 1932.
- Pigou, A. C. & Taussig, F. W. (1913). Railway rates and joint costs. *Quarterly Journal of Economics* 27(4).
- Taussig, F. W. (1891). A contribution to the theory of railway rates. *Quarterly Journal of Economics*, July 1891, pp. 438–465.
- Surface Transportation Board. 2024 STB Waybill Reference Guide. stb.gov.
- 49 U.S.C. § 10707(d).
