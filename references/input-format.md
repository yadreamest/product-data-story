# Input contract v1

Root: `{"pages": [...]}`. Example: `../examples/demo.json`.

Each page requires `title` (up to 110 characters), `period`, `source`, `charts` (1–3). Optional `eyebrow`.
Each chart requires:

| Field | Meaning |
|---|---|
| `type` | `bar`, `funnel`, `line`, `stacked`, `kpi` |
| `title` | Up to 90 characters |
| `base` | Population / denominator definition, up to 170 characters |
| `unit` | `%`, `count`, `мин`, `тыс.` or another unit label |
| `labels` | Array of labels, 1–80 characters each |
| `values` | Same-length array of nonnegative finite numbers or null |
| `note` | Optional qualification, up to 220 characters |
| `decimals` | 0 (default), 1 or 2 |
| `highlight` | Indices to accent; defaults to `[0]`; `[]` means no highlight |

Funnel: no missing values; non-increasing, positive initial count. Notes should state that cohort/window is shared and whether inputs are rounded. Conversion from a zero intermediate stage is undefined (shown as dash).

Line: single series only, 2–12 observations; explicitly set `equally_spaced: true`. Null creates a gap. Give the temporal interval in base or note. Uneven time points are unsupported; do not set equally_spaced merely to pass validation.

Stacked: `exclusive: true`, unit `%`, sum exactly 100 within 0.001 numerical tolerance. Rounded data summing to 99/101 should use bars plus an explanation, not invented adjustment. Max 5 segments, short labels. No legend hidden behind a tooltip.

Capacity: bar 7 rows, funnel 6 rows, line 12 points, stacked 5 segments, KPI 3 values. Split overly long or dense content across pages. Missing values remain null; explicit zero stays zero. Source links are plain provenance text, not fetched by the renderer.

Outputs: one PNG (160dpi) and editable-text SVG per page, multi-page `report.pdf`, local `index.html`, `input.json`, `validation.json`. SVG text needs the included Inter fonts installed on the receiving editor for exact fidelity; PDF embeds Inter. PNG needs no installed fonts. HTML is a gallery, not an interactive dashboard. Renderer validation cannot prove analytical comparability or detect all text collisions; inspect exports.

`--out` must be new or empty. Rendering takes place in a temporary sibling directory and publishes the complete bundle only after checks pass; a failed attempt must not alter an earlier successful report. Use a new version directory for revisions.
