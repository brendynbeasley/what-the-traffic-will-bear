# Pigou (1920) on 2024 rail rates: findings

## In plain English

Arthur Pigou wrote in 1920 that railways practise discrimination of the third degree, sorting freight into classes
and charging valuable goods more over cost than cheap ones. This study checks that against the Surface
Transportation Board's 2024 revenue and cost figures for every released commodity.

- **Valuable goods do not carry higher markups.** Metallurgical coal (R/VC 2.89), PVC resin (2.20) and crushed
  limestone (1.99) carry some of the highest markups; new passenger cars (1.23), beer (1.36) and thermal coal (1.37)
  some of the lowest. Across 33 commodity groups the elasticity of R/VC with respect to value is −0.019 (SE 0.021),
  against about 0.69 in Pigou's own straight-line case. Within car types the cell-level estimate is small and
  positive (0.047 with revenue weights, 0.087 with equal weights), still far below 0.69.
- **They do pay more per ton, and cost explains it.** A rack car of new cars holds 21 tons against 107 in a hopper of
  corn, so its cost per ton-mile is 12.6 cents against 2.1. Revenue per ton rises with value (elasticity 0.35), and
  once cost per ton-mile is held fixed, value has no positive effect.
- **Rail dependence does not explain markups either.** Coal, 57% of whose tonnage goes by rail, carries a
  below-average markup (1.52) because most of its revenue is coal billed for fuel or steam purposes (thermal coal).
- **Most of the spread is inside each commodity.** Chemicals, coal, farm products and every other STCC group with more than
  $1 billion of revenue have traffic both below variable cost and above the 180% legal threshold. Detailed commodity
  and car type explain at most 35% of the variance of markups.

A friendlier account is in the [README](../README.md).

**Key to the labels.** *R/VC* = revenue divided by the STB's Uniform Railroad Costing System variable cost. *SCTG* =
Standard Classification of Transported Goods (Commodity Flow Survey groups). *STCC* = Standard Transportation
Commodity Code (rail freight codes). *Value* = 2022 CFS value per ton of rail shipments, or all modes when the rail
figure is suppressed. *Rail tonnage share* = rail tons over all-mode tons in the 2022 CFS. *Freight/value* = revenue
per ton over value per ton. Tests A to E are defined in [TECHNICAL.md](../TECHNICAL.md); "group" tests have one row per
SCTG group with HC1 errors, "cell" tests one row per STCC7 by car-type cell with errors clustered by SCTG group.

## Sample

| Item | Value |
|---|---|
| Revenue in the 2024 report, all data | $79,356 million |
| Variable cost in the report, all data | $50,772 million (R/VC 1.563) |
| Revenue in released STCC7 by car-type cells | $68,216 million in 1,559 cells |
| Dropped as non-commodity traffic (STCC 41–47, 50) | $12,903 million |
| Used | 1,438 cells, $55,313 million, R/VC 1.609, 34 SCTG groups, 16 car groups |
| Pigou straight-line benchmark elasticity at R/VC 1.609 | 0.689 |

From `sample_summary.csv`.

## Every test (`value_tests.csv`)

| test | term | coef | se | 95% CI | p | n | clusters |
|---|---|---|---|---|---|---|---|
| A1 group: log R/VC on log value, equal weights | lv | −0.019 | 0.021 | [−0.060, 0.022] | 0.372 | 33 |  |
| A2 group: log R/VC on log value, revenue weights | lv | −0.028 | 0.028 | [−0.083, 0.027] | 0.322 | 33 |  |
| A3 group: as A1, rail-published values only | lv | −0.004 | 0.030 | [−0.063, 0.055] | 0.902 | 28 |  |
| A4 group: as A1, without coal and motor vehicles | lv | −0.017 | 0.022 | [−0.060, 0.027] | 0.449 | 31 |  |
| B1 group: log revenue per ton-mile on log value and log cost per ton-mile | lv | −0.054 | 0.019 | [−0.090, −0.017] | 0.004 | 33 |  |
| B1 group: log revenue per ton-mile on log value and log cost per ton-mile | lvc_tm | 1.184 | 0.121 | [0.948, 1.420] | < 0.001 | 33 |  |
| C1 group: log freight share of value on log value | lv | −0.645 | 0.072 | [−0.787, −0.504] | < 0.001 | 33 |  |
| C2 group: log revenue per ton on log value | lv | 0.355 | 0.072 | [0.213, 0.496] | < 0.001 | 33 |  |
| C3 group: log tons per car on log value | lv | −0.384 | 0.075 | [−0.532, −0.236] | < 0.001 | 33 |  |
| E1 group: log R/VC on rail share of tonnage | share10 | −0.005 | 0.033 | [−0.069, 0.059] | 0.884 | 28 |  |
| E2 group: log R/VC on rail share and log value | share10 | −0.010 | 0.025 | [−0.059, 0.039] | 0.692 | 28 |  |
| E2 group: log R/VC on rail share and log value | lv | −0.007 | 0.028 | [−0.062, 0.047] | 0.790 | 28 |  |
| E3 group: as E2, revenue weights | share10 | −0.037 | 0.017 | [−0.072, −0.003] | 0.032 | 28 |  |
| E4 group: as E2, without coal | share10 | 0.034 | 0.063 | [−0.089, 0.157] | 0.587 | 27 |  |
| D1 cell: log R/VC on log value, car-group FE, revenue weights | lv | 0.047 | 0.024 | [0.000, 0.094] | 0.049 | 1434 | 33 |
| D2 cell: as D1, equal weights | lv | 0.087 | 0.019 | [0.049, 0.125] | < 0.001 | 1434 | 33 |
| E5 cell: rail share, log value, car-group FE, revenue weights | share10 | 0.022 | 0.020 | [−0.017, 0.062] | 0.268 | 1363 | 28 |
| D3 cell: covered hoppers only, revenue weights | lv | 0.046 | 0.024 | [−0.001, 0.093] | 0.055 | 225 | 18 |
| D3 cell: tank cars only, revenue weights | lv | −0.135 | 0.079 | [−0.290, 0.019] | 0.085 | 421 | 14 |

*lv* = ln value per ton; *lvc_tm* = ln variable cost per ton-mile; *share10* = rail tonnage share in tens of
percentage points.

## Commodity groups (`commodity_groups.csv`)

| SCTG | Group | Revenue $M | R/VC | Rev ¢/ton-mi | VC ¢/ton-mi | Haul mi | Tons/car | Value $/ton | Value source | Rail tonnage share | Freight/value |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15 | Coal | 7910 | 1.52 | 2.69 | 1.77 | 736 | 117.4 | 57 | rail | 57.0 | 0.35 |
| 36 | Motorized and other vehicles (includes parts) | 6637 | 1.32 | 15.37 | 11.68 | 1078 | 20.3 | 8298 | rail | 2.9 | 0.02 |
| 02 | Cereal grains (includes seed) | 5170 | 1.57 | 3.52 | 2.24 | 1170 | 97.2 | 250 | rail | 25.7 | 0.165 |
| 24 | Plastics and rubber | 3346 | 1.93 | 5.92 | 3.07 | 654 | 77.8 | 1275 | rail | 16.2 | 0.03 |
| 20 | Basic chemicals | 3264 | 2.47 | 6.77 | 2.74 | 764 | 99.1 | 560 | rail | 14.5 | 0.092 |
| 19 | Other coal and petroleum products n.e.c. | 2753 | 1.83 | 6.05 | 3.3 | 767 | 78.3 | 472 | rail | 17.5 | 0.098 |
| 07 | Other prepared foodstuffs and fats and oils | 2608 | 1.46 | 4.88 | 3.36 | 1080 | 63.0 | 784 | rail | 6.2 | 0.067 |
| 17 | Gasoline and aviation turbine fuel | 2416 | 1.69 | 4.59 | 2.72 | 967 | 93.8 | 800 | rail | 5.3 | 0.055 |
| 04 | Animal feed and products of animal origin | 2199 | 1.59 | 3.73 | 2.34 | 1110 | 96.7 | 283 | rail | 17.3 | 0.146 |
| 32 | Base metal in primary or semi-finished forms | 2104 | 1.51 | 6.56 | 4.34 | 786 | 92.5 | 1177 | rail | 10.8 | 0.044 |
| 26 | Wood products | 2018 | 1.61 | 4.85 | 3.0 | 1340 | 86.8 | 598 | rail | 7.7 | 0.109 |
| 27 | Pulp, newsprint, paper, and paperboard | 2014 | 1.51 | 6.6 | 4.38 | 1014 | 69.9 | 790 | rail | 15.8 | 0.085 |
| 22 | Fertilizers | 1836 | 1.82 | 4.06 | 2.23 | 998 | 101.8 | 345 | rail | 16.7 | 0.117 |
| 31 | Non-metallic mineral products | 1834 | 2.0 | 6.32 | 3.16 | 637 | 103.7 | 216 | all modes |  | 0.186 |
| 03 | Other agricultural products | 1319 | 1.65 | 3.49 | 2.12 | 1242 | 102.8 | 567 | rail | 10.7 | 0.076 |
| 41 | Waste and scrap | 1210 | 1.43 | 5.53 | 3.87 | 606 | 94.0 | 389 | rail | 8.6 | 0.086 |
| 11 | Natural sands | 1011 | 1.75 | 4.33 | 2.47 | 600 | 113.8 | 20 | rail | 12.3 | 1.272 |
| 12 | Gravel and crushed stone | 852 | 1.96 | 5.6 | 2.87 | 226 | 106.2 | 11 | rail | 8.3 | 1.15 |
| 18 | Fuel oils | 791 | 1.52 | 4.45 | 2.93 | 1135 | 87.8 | 861 | rail | 6.1 | 0.059 |
| 08 | Alcoholic beverages | 723 | 1.3 | 4.78 | 3.69 | 1592 | 63.5 | 1037 | rail | 4.4 | 0.073 |
| 16 | Crude petroleum (no CFS value) | 660 | 1.26 | 2.77 | 2.19 | 1523 | 92.7 |  |  |  |  |
| 23 | Other chemical products n.e.c. | 616 | 1.94 | 6.35 | 3.27 | 987 | 61.2 | 1291 | rail | 7.1 | 0.049 |
| 06 | Milled grain and bakery products | 496 | 1.84 | 5.42 | 2.95 | 890 | 93.0 | 694 | rail | 6.8 | 0.069 |
| 30 | Textiles and leather | 380 | 1.41 | 6.87 | 4.87 | 1372 | 12.0 | 3592 | rail | 0.3 | 0.026 |
| 37 | Transportation equipment n.e.c. | 265 | 1.72 | 15.18 | 8.83 | 607 | 26.0 | 1763 | rail | 17.8 | 0.052 |
| 35 | Electronic and electrical equipment | 228 | 1.89 | 12.07 | 6.38 | 1361 | 10.7 | 1961 | rail | 1.3 | 0.084 |
| 13 | Other non-metallic minerals n.e.c. | 198 | 1.78 | 5.37 | 3.01 | 721 | 104.7 | 64 | rail | 19.8 | 0.609 |
| 39 | Furniture, mattresses and lighting | 111 | 1.72 | 8.02 | 4.67 | 1442 | 12.3 | 7132 | all modes |  | 0.016 |
| 28 | Paper or paperboard articles | 98 | 1.08 | 4.48 | 4.14 | 1254 | 15.8 | 1800 | all modes |  | 0.031 |
| 05 | Meat, poultry, fish and seafood | 85 | 1.69 | 5.54 | 3.28 | 963 | 91.8 | 1920 | rail | 4.1 | 0.028 |
| 25 | Logs and other wood in the rough | 69 | 2.31 | 7.47 | 3.24 | 194 | 101.2 | 275 | all modes |  | 0.053 |
| 38 | Precision instruments and apparatus | 37 | 1.53 | 6.2 | 4.04 | 1662 | 14.4 | 34231 | all modes |  | 0.003 |
| 14 | Metallic ores and concentrates | 32 | 2.43 | 7.07 | 2.9 | 489 | 99.9 | 287 | rail | 21.2 | 0.12 |
| 34 | Machinery | 23 | 3.36 | 105.08 | 31.31 | 1065 | 6.1 | 4830 | rail | 1.6 | 0.232 |

## Named commodities (`named_commodities.csv`)

Value per ton is the commodity's SCTG group average, not the commodity's own.

| Commodity | STCC7 | SCTG | Revenue $M | VC $M | Tons M | R/VC | Rev ¢/ton-mi | VC ¢/ton-mi | Haul mi | Tons/car | Rev $/ton | Group value $/ton | Freight/value |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Metallurgical coal | 1121210 | 15 | 1508.4 | 522.2 | 47.7 | 2.89 | 7.14 | 2.47 | 443 | 111.5 | 31.6 | 57 | 0.558 |
| PVC resin | 2821141 | 24 | 478.7 | 217.1 | 10.7 | 2.2 | 6.63 | 3.01 | 675 | 90.6 | 44.74 | 1275 | 0.035 |
| Crushed limestone | 1421965 | 12 | 519.3 | 260.9 | 39.2 | 1.99 | 5.62 | 2.82 | 236 | 103.7 | 13.26 | 11 | 1.205 |
| Portland cement | 3241115 | 31 | 757.4 | 381.9 | 25.1 | 1.98 | 6.01 | 3.03 | 502 | 106.3 | 30.18 | 216 | 0.14 |
| Sugar | 2062110 | 07 | 305.9 | 158.3 | 5.8 | 1.93 | 6.34 | 3.28 | 833 | 104.5 | 52.85 | 784 | 0.067 |
| Polyethylene pellets | 2821142 | 24 | 1469.2 | 805.8 | 45.1 | 1.82 | 5.31 | 2.91 | 613 | 96.7 | 32.54 | 1275 | 0.026 |
| Propane | 2912111 | 19 | 448.9 | 248.6 | 8.6 | 1.81 | 5.83 | 3.23 | 898 | 63.8 | 52.32 | 472 | 0.111 |
| Frac sand | 1441316+1441317 | 11 | 723.2 | 425.6 | 30.7 | 1.7 | 4.01 | 2.36 | 587 | 114.4 | 23.53 | 20 | 1.152 |
| Ethanol | 2818445+2818446 | 17 | 2304.6 | 1358.4 | 50.3 | 1.7 | 4.54 | 2.68 | 1009 | 94.6 | 45.83 | 800 | 0.057 |
| Wheat | 0113710 | 02 | 1282.1 | 780.7 | 30.7 | 1.64 | 4.01 | 2.44 | 1043 | 102.8 | 41.8 | 250 | 0.167 |
| Corn | 0113215 | 02 | 3255.8 | 2041.5 | 80.5 | 1.59 | 3.39 | 2.12 | 1195 | 107.0 | 40.47 | 250 | 0.162 |
| Soybean meal | 2092314 | 04 | 1059.2 | 673.1 | 25.0 | 1.57 | 3.7 | 2.35 | 1145 | 105.4 | 42.41 | 283 | 0.15 |
| Lumber | 2421184 | 26 | 1212.4 | 786.7 | 18.7 | 1.54 | 4.56 | 2.96 | 1423 | 93.1 | 64.81 | 598 | 0.108 |
| Steel sheet in coils | 3312332 | 32 | 994.0 | 699.6 | 19.5 | 1.42 | 6.78 | 4.77 | 754 | 92.6 | 51.1 | 1177 | 0.043 |
| Thermal coal | 1121290 | 15 | 6401.6 | 4675.8 | 351.2 | 1.37 | 2.35 | 1.72 | 776 | 118.2 | 18.23 | 57 | 0.322 |
| Beer | 2082110 | 08 | 468.1 | 343.8 | 6.6 | 1.36 | 4.81 | 3.53 | 1463 | 88.5 | 70.42 | 1037 | 0.068 |
| New pickups and vans | 3711215 | 36 | 1668.3 | 1225.4 | 9.5 | 1.36 | 19.19 | 14.1 | 916 | 19.8 | 175.73 | 8298 | 0.021 |
| New passenger cars | 3711120 | 36 | 4148.1 | 3380.8 | 23.7 | 1.23 | 15.43 | 12.58 | 1132 | 21.2 | 174.72 | 8298 | 0.021 |

## Extension: where the spread lives

### Revenue by R/VC zone, commodity traffic

| R/VC zone | Share of commodity revenue | Average R/VC in zone |
|---|---|---|
| Below 1.0 | 8.7% | 0.78 |
| 1.0 to 1.8 | 44.3% | 1.38 |
| 1.8 and above | 47.0% | 2.56 |

Commodity traffic only, STCC groups whose three zones are all released (`band_totals.csv`).

### Revenue by R/VC zone within each commodity (`band_shares.csv`)

Shares in percent of each commodity's revenue. STCC groups with a redacted zone are omitted.

| STCC | Commodity | Revenue $M | R/VC | Below 1.0 | 1.0 to 1.8 | 1.8+ | R/VC of below-1.0 traffic | R/VC of 1.8+ traffic |
|---|---|---|---|---|---|---|---|---|
| 28 | Chemical Products | 13424 | 2.02 | 4.3 | 27.8 | 68.0 | 0.79 | 2.81 |
| 11 | Coal Products | 8126 | 1.53 | 15.3 | 40.1 | 44.5 | 0.8 | 2.72 |
| 20 | Food Products | 7954 | 1.49 | 8.4 | 54.5 | 37.1 | 0.77 | 2.29 |
| 37 | Transportation Equipment | 7346 | 1.34 | 16.1 | 55.8 | 28.1 | 0.78 | 2.45 |
| 01 | Farm Products | 7021 | 1.57 | 7.6 | 51.6 | 40.8 | 0.77 | 2.2 |
| 29 | Petroleum or Coal Products | 4111 | 1.71 | 7.9 | 39.5 | 52.6 | 0.85 | 2.53 |
| 14 | Nonmetallic Minerals | 3035 | 1.9 | 4.8 | 35.1 | 60.1 | 0.81 | 2.84 |
| 33 | Metal Products | 2690 | 1.55 | 6.5 | 53.6 | 39.9 | 0.75 | 2.33 |
| 26 | Pulp & Paper Products | 2496 | 1.45 | 10.3 | 55.6 | 34.1 | 0.73 | 2.28 |
| 24 | Wood Products | 2386 | 1.6 | 4.1 | 54.0 | 41.9 | 0.81 | 2.34 |
| 32 | Stone & Glass Products | 2255 | 1.97 | 2.0 | 33.6 | 64.4 | 0.84 | 2.55 |
| 40 | Scrap Materials | 1762 | 1.43 | 10.3 | 57.9 | 31.9 | 0.77 | 2.24 |
| 13 | Petroleum Products | 824 | 1.27 | 13.4 | 82.7 | 3.9 | 0.91 | 2.09 |
| 10 | Metallic Ores | 662 | 2.15 | 7.7 | 16.4 | 76.0 | 0.83 | 2.89 |
| 23 | Finished Textiles | 447 | 1.39 | 11.7 | 56.9 | 31.4 | 0.72 | 2.23 |
| 36 | Electrical Machinery | 382 | 1.99 | 6.4 | 34.4 | 59.2 | 0.77 | 3.49 |
| 30 | Plastic Products | 370 | 1.52 | 8.9 | 52.7 | 38.4 | 0.74 | 2.39 |
| 35 | Machinery | 243 | 2.28 | 4.7 | 22.0 | 73.2 | 0.8 | 3.37 |
| 25 | Furniture | 193 | 1.62 | 5.6 | 48.0 | 46.4 | 0.72 | 2.3 |
| 48 | Hazardous Waste | 106 | 2.5 | 0.9 | 16.4 | 82.7 | 0.84 | 3.03 |
| 38 | Scientific Instruments | 88 | 1.38 | 11.6 | 61.0 | 27.4 | 0.78 | 2.09 |
| 39 | Miscellaneous Products | 67 | 1.71 | 5.9 | 41.0 | 53.2 | 0.73 | 2.53 |
| 34 | Fabricated Metal Products | 48 | 1.52 | 13.2 | 45.0 | 41.7 | 0.75 | 2.81 |
| 27 | Printed Matter | 20 | 1.11 | 27.0 | 59.8 | 13.2 | 0.74 | 2.09 |
| 22 | Textile Mill Products | 14 | 1.38 | 14.0 | 50.1 | 35.9 | 0.73 | 2.25 |

### Variance split of ln R/VC

| Layer | Share of variance | Levels |
|---|---|---|
| Total weighted variance of ln R/VC | 0.167 | |
| Value per ton of the goods | 1.6% | |
| Commodity group (SCTG 2-digit) | 16.4% | 39 |
| Commodity (STCC 5-digit) | 32.3% | 367 |
| Commodity by car-type group | 35.2% | 617 |
| Left between R/VC zones within commodity by car type | 64.8% | |

1,280 released commodity, car-group and zone cells, $63.6 billion of revenue (`variance_split.csv`).

## Revenue check against the public-use waybill file (`masking_check.csv`)

STB two-digit report revenue (groups with all three zones released; the ALL row is the report's total) against
expanded revenue in the 2024 Public Use Waybill Sample, in $ million. The Board's waybill reference guide says
railroads may report contract revenue scaled by a confidential factor.

| STCC | Group | STB report $M | Public file $M | Ratio |
|---|---|---|---|---|
| ALL | All STCC groups | 79353 | 101150 | 1.275 |
| 28 | Chemical Products | 13424 | 17281 | 1.287 |
| 46 | Misc Mixed Shipments Exc, Forwarded | 10563 | 14143 | 1.339 |
| 11 | Coal Products | 8126 | 9866 | 1.214 |
| 20 | Food Products | 7954 | 9516 | 1.196 |
| 37 | Transportation Equipment | 7346 | 10047 | 1.368 |
| 01 | Farm Products | 7021 | 7916 | 1.128 |
| 29 | Petroleum or Coal Products | 4111 | 5356 | 1.303 |
| 14 | Nonmetallic Minerals | 3035 | 3674 | 1.21 |
| 33 | Metal Products | 2690 | 3611 | 1.342 |
| 26 | Pulp & Paper Products | 2496 | 3343 | 1.34 |
| 24 | Wood Products | 2386 | 3212 | 1.346 |
| 32 | Stone & Glass Products | 2255 | 2859 | 1.268 |
| 40 | Scrap Materials | 1762 | 2281 | 1.295 |
| 42 | Empty Containers | 1245 | 1684 | 1.353 |
| 13 | Petroleum Products | 824 | 1088 | 1.32 |
| 10 | Metallic Ores | 662 | 776 | 1.172 |
| 44 | Freight Forwarder Traffic | 471 | 553 | 1.174 |
| 23 | Finished Textiles | 447 | 619 | 1.385 |
| 41 | Miscellaneous Freight | 398 | 496 | 1.246 |
| 36 | Electrical Machinery | 382 | 500 | 1.31 |
| 30 | Plastic Products | 370 | 517 | 1.398 |
| 35 | Machinery | 243 | 318 | 1.312 |
| 25 | Furniture | 193 | 257 | 1.333 |
| 48 | Hazardous Waste | 106 | 129 | 1.223 |
| 38 | Scientific Instruments | 88 | 115 | 1.302 |
| 39 | Miscellaneous Products | 67 | 88 | 1.314 |
| 34 | Fabricated Metal Products | 48 | 68 | 1.409 |
| 27 | Printed Matter | 20 | 25 | 1.236 |
| 22 | Textile Mill Products | 14 | 21 | 1.481 |

## Figures

- `value_vs_markup.png`: R/VC against value per ton by SCTG group, bubble size by revenue.
- `band_shares.png`: revenue by R/VC zone within the 16 largest commodity groups.
