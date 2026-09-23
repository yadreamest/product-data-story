# Chart selection and data rules

Ready-template guide: bar, funnel, line, stacked, KPI. For other questions, use [chart-atlas](chart-atlas.md) and [advanced-rendering](advanced-rendering.md). The five-template limit is a renderer constraint, not a limit on what the skill can build through a verified custom script.

| Question | Template | Essential rule |
|---|---|---|
| How do categories compare? | bar | Horizontal lengths from zero; direct values |
| Where do users leave a sequence? | funnel | Proportional stage bars for one cohort |
| How does one measure change with time? | line | Equally spaced observations only in the current renderer; gaps for missing values |
| What makes up the whole? | stacked | Exclusive parts of one known denominator |
| What is the latest level? | kpi | Explicit metric, unit, period and population |

## Bar

Semantic order wins; otherwise sort descending. Highlight focal series, retain neutral comparators. Use common domains for magnitude comparisons. Negative values are unsupported in the current renderer and must produce a validation error. Long labels wrap. More rows require height or another page, never smaller type. Benchmark scope includes geography, platform, cohort and time window when available; incompatible scopes require caveat and prohibit a categorical performance verdict.

## Funnel

Use ordered stages from the same cohort with comparable units. Left-aligned bars encode actual counts on one zero-based scale. Show stage name, count, share of initial cohort and previous-stage conversion with explicit labels if space allows. No trapezoids. Initial row has no previous-stage rate. Zero denominator yields unavailable. An increase between stages requires explanation or use of ordinary bars; never silently accept mixed events and unique-user counts.

Synthetic example: 10,000 → 3,200 → 1,600 implies 32% first-step conversion, 50% second-step conversion and 16% overall conversion. These are invented demonstration values, not company metrics.

## Line

Choose for ordered observations of one metric across time, not DAU versus WAU snapshots. V1 supports equally spaced periods only: daily, weekly, monthly or another explicitly declared regular cadence. Reject irregular observations rather than placing unequal intervals at equal distances. Preserve null gaps on the regular period grid. Default interpolation is linear. No invented smoothing, dual axes or assumed observations. End labels include series and value; use small multiples when too crowded. Forecast/estimated segments are not supported unless the renderer explicitly distinguishes them. Reduce tick frequency before reducing font size. A nonzero line domain requires visible ticks and a truthful interpretation.

## Stacked

Use only mutually exclusive, exhaustive parts. Validate reconciliation against counts or supplied shares and declared rounding precision; do not silently normalize inconsistent inputs. Category order remains stable. Small labels move outside or into a list. Exact counts and shares can accompany the stack in a compact table. Overlapping categories, averages and per-user rates must never be summed into a whole.

Synthetic overlap example: shares of 60%, 30% and 20% sum to 110%. Clarify overlap or inconsistency before stacking. When these are overlapping content preferences, retain separate bars with an explicit multiple-selection note. Do not invent a balancing segment or normalize them to 100%.

## KPI

Keep value, readable metric name, unit and exact observation period together. DAU and WAU are separate measures with separate windows. Delta requires a comparable reference period and defined formula. No decorative sparkline unless underlying time series is supplied. A single KPI should not dominate the page by size if the decision depends on its denominator or comparison.

## Deferred: cohort

Only add with entry-cohort rows, elapsed-age columns, cohort sizes and a precise retention definition. Use a sequential scale and distinguish observed zero, missing and not-yet-mature values. Future cells never become zero. Weighted aggregates need denominators. The ready renderer does not implement cohort charts. Use the custom route only with the required data and explicit maturity checks.

## References

[ONS zero-baseline guidance](https://service-manual.ons.gov.uk/data-visualisation/guidance/axes-and-gridlines), [Datawrapper stacked bars](https://www.datawrapper.de/academy/customizing-your-stacked-bar-chart), [Datawrapper line configuration](https://www.datawrapper.de/academy/customizing-your-line-chart), [Datawrapper missing-data guidance](https://www.datawrapper.de/academy/patchy-data). Read 2026-09-22. Template-specific input checks are our design recommendations, not claims that these sources prescribe this exact implementation.
