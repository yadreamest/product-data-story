# Product Data Story: design system

Status: RECOMMENDED — v2 Inter, 2026-09-23. Design-lead visual owner verification covered only `outputs/example-v2/page-01.png`, `outputs/demo-v2/page-01.png` and `outputs/demo-v2/page-02.png`: all three were opened and inspected for composition, hierarchy and spacing. Verified corrections: grids behind bars, aligned stacked-chart percentages, plain explicit stage-conversion notes, and dated weekly observations within the displayed demo period. Previously identified visual blockers are resolved in these PNGs. Other formats, phone-size readability and all possible inputs were not verified in this pass. Final direction approval remains with the report owner. The theme is original and proposed, not an existing brand system.

## Composition

One question per card; at most three evidence blocks per vertical page. Fixed reading order: section and period → title → population and unit → chart → source/method note. Neutral titles are the default. Finding-led wording requires supplied evidence. Benchmark verdicts require a benchmark source, comparable scope and explicit range/definition.

Treat all required metadata as content: source, base/population and period must survive PNG, SVG, PDF and HTML. Keep notes near the chart they qualify, not in a detached global footer. Carry chart title and metadata into alt text / an equivalent data table where available.

## V2 tokens

All dimensions below are logical pixels on a 1000 px wide artboard. Higher-resolution raster exports scale the complete artboard uniformly, without changing its composition. Define values in one renderer theme; no per-chart overrides.

| Semantic token | Value | Use |
|---|---|---|
| `canvasWidth` | 1000 | Fixed editorial export width |
| `pagePadding` | 56 | Left and right; content width 888 |
| `fontFamily` | Inter | All text; load actual font, do not silently substitute |
| `title` | 34 / 38 px, weight 600 | Page title |
| `section` | 22 / 26 px | Evidence-block heading |
| `base`, `note` | 14 / 20 px | Population, scope, source and caveats |
| `label` | 16 / 22 px | Category labels, left aligned |
| `value` | 17 / 22 px | Chart value labels |
| `kpi` | 44 / 48 px | Standalone primary number |
| `rowMinHeight` | 44 | Single-line bar/funnel row |
| `barHeight` | 18 | Uniform bar/funnel mark thickness |
| `labelColumnWidth` | 240 | Left-aligned category-label column |
| `labelToPlotGap` | 20 | Label column to plot; plot begins at x=316 |
| `stackHeight` | 28 | Composition mark |
| `linePlotHeight` | 200 | Plot region, excluding title/axis labels/notes |
| `sectionGap` | 32 | Clear spacing between completed blocks |

Slash notation means font size / line height. Sizes are specified in pixels; a Matplotlib implementation must convert to points through its chosen DPI rather than treating pixel values as points. Only the page-title weight is locked by this brief; use consistent regular text for labels/notes and a restrained shared emphasis weight for headings/values. Do not silently vary weights by chart.

Keep semantic color roles `surface`, `ink`, `muted`, `rule`, `accent`, `comparator`, `missing`, and stroke roles `axisStroke`, `seriesStroke`, `referenceStroke` centralized in the existing theme. This typography/layout iteration does not introduce a new palette.

Use a near-white surface, dark text, quiet rules, one main accent and neutral comparison bars. Accent means focal series, not success. Preserve recurring series identities. Use one font family. Tabular figures are a desired capability, not a verified renderer feature: Matplotlib does not automatically enable Inter's OpenType `tnum`; claim equal-width digits only after measuring the rendered glyph advances in the actual font/rendering setup. Reserve width for labels and values; wrap text or grow the page instead of shrinking it. No decorative gradients, shadows, pictorial funnels or ornamental outlines.

## Content-driven geometry

Page height is derived from actual content, not a fixed tall canvas. Compute each block from wrapped heading, base text, chart rows or plot, and notes; then insert the 32 px gap. A 44 px row is a minimum: multiline labels increase row height, with marks vertically centred in that row. Measure text using Inter before placing it. Reserve value-label width inside the 888 px content area before calculating the plot domain; the 628 px remaining after label column and gap includes this value allowance. Nothing may escape the right margin.

Left-align all category labels at the same x position. Do not right-align short labels against bars. Keep title and metadata aligned to the page margin. Do not stretch three short rows to fill a large arbitrary plot. A 200 px line plot is a distinct fixed plotting region with additional room for its axes and notes.

## Labels and marks

- Direct values beside bars and endpoints reduce legend lookups. Category labels already present do not need a second legend.
- Absolute bars begin at zero; comparable panels share a domain. Percentage shares use 0–100. Label units consistently in axes, values and notes.
- Small segments move labels outside; never overflow them into neighbouring segments.
- Explain percentages versus percentage-point changes. Preserve raw numeric precision in data, formatting only at display.
- Missing values are not zero. Never imply a smooth observed path through absent observations.
- Notes must remain readable at the intended delivery size; a large raster scaled to phone width is not sufficient verification.

## Input/output states

Empty data: explicit validation error and no export. Invalid schema or contradictory totals: specific error, no success claim. Required metadata missing: do not fabricate it. Zero denominator: unavailable rate. Rendering failure: clear failure and retain editable input. V1 does not support negative values or irregularly spaced time observations; reject them instead of distorting their geometry. Loading/offline/destructive interaction states are N/A for static file export.

## V2 visual acceptance criteria

The following are checks to perform, not claims already verified:

- Actual Inter glyphs render in Cyrillic and Latin; no fallback, missing glyphs or unexpected weight changes.
- At 1000 px, title/heading/body/value sizes follow the token hierarchy. Category labels have a visibly shared left edge, with stable chart starts and direct values.
- Three-row comparisons feel compact; block spacing is 32 px without oversized blank vertical areas. Page height ends after its content and final padding.
- Long labels wrap without touching the next row, marks or values. Large values and small stacked segments remain within margins; every label belongs unambiguously to its mark.
- Page title, source, period and population are intact in every export. Numeric formatting, rounded shares and units agree with input and locale.
- Verify grayscale meaning, text contrast and a scaled delivery preview. Do not claim mobile readability from the 1000 px preview alone; 14 px notes become too small when the entire page is substantially reduced.
- Inspect a normal page and stress fixtures with long Cyrillic labels, multiline notes, tiny segments, large numbers and missing line values. Fix visible clipping or overlap before marking PNG review complete.

## Verification record

Open every requested format and inspect rendered marks and text. Check source numbers, arithmetic, zero baseline, metadata persistence, long Russian labels, small segments and no clipping. Verify distinguishability in grayscale and text contrast. Keep a digital data table or exact JSON alongside exports. Count successful renders and timing only after actual execution. Tool success is not human design approval.

V2 PNG: three demo/source-example pages reviewed by design lead on 2026-09-23, scope recorded above. V2 PDF: the same three pages rasterized and inspected; embedded Inter family verified. SVG and HTML: generated, no separate visual acceptance. Narrow-delivery readability: unverified. Independent data/layout review: long-label stress case and 14 regression tests passed; no guarantee for all inputs.

## Primary references

- [ONS: axes and gridlines](https://service-manual.ons.gov.uk/data-visualisation/guidance/axes-and-gridlines): zero baseline for bars and sparse labelled gridlines.
- [Datawrapper: stacked bars](https://www.datawrapper.de/academy/customizing-your-stacked-bar-chart): direct values, category labels and screen-size checks.
- [Datawrapper: line charts](https://www.datawrapper.de/academy/customizing-your-line-chart): date axes, number formats, endpoint labels and line styles.
- [Datawrapper: missing observations](https://www.datawrapper.de/academy/patchy-data): visible gaps or clearly identified assumed paths.

References read 2026-09-22. These references guide design decisions; no external template code/assets were copied.

## Heading rhythm — v4.0.1

Use explicit line advance, not a renderer-specific line-spacing multiplier: font metrics can make the actual step much larger. Main headings use 34 px type / 38 px advance; section headings 22 / 26 with 10 px reserved after the final line box before the description. Measure the visible bounds after rendering; descriptions must not appear attached to the final title line.

For square 1080 px post cards, use Inter SemiBold 50 px / 54 px line advance. Keep subtitle spacing separate from line-height. The verified two-line layout starts at y=138; description starts at y=273. For other line counts derive the description position from measured title bounds and preserve the same visual separation. Do not reuse a fixed subtitle coordinate if the title grows. Verify both full-size and phone-size PNGs.
