# v3 Logo-Flow Style Specification

**Purpose:** Diagrams using only technology logos + arrows + labels. No containers.
**Use case:** Executive presentations, portfolio overview, visual storytelling.

---

## Definition

A logo-flow diagram shows technology relationships using official brand logos
connected by arrows with brief labels. It contains ZERO containers (no rectangles,
ellipses, or diamonds as backgrounds/groups).

---

## Element Types Allowed

| Element | Excalidraw Type | Usage |
|---------|-----------------|-------|
| Logo | `type: "image"` | Technology representation |
| Label | `type: "text"` | Name below logo |
| Arrow | `type: "arrow"` | Data/control flow |
| Arrow Label | `type: "text"` | Brief flow description |
| Zone Label | `type: "text"` | Optional group heading |

## Element Types FORBIDDEN

- `type: "rectangle"` - No containers or boxes
- `type: "ellipse"` - No circles or ovals
- `type: "diamond"` - No decision shapes
- `type: "line"` - No decorative lines

---

## Visual Specs

### Logos
- **Size:** 48x48 (uniform for ALL logos, no exceptions)
- **Scale:** [1, 1]
- **Opacity:** 100
- **Roughness:** 0
- **boundElements:** Must list all connected arrows

> **IMPORTANT:** Do NOT use 64x64 or any other size. All logos are 48x48 for visual consistency.

### Labels (below logo)
- **Font:** fontFamily: 3 (monospace)
- **Size:** 11px
- **Color:** #495057
- **Alignment:** center, positioned 8px below logo bottom edge
- **Content:** Technology name only (e.g., "BigQuery", "PostgreSQL")

### Arrows
- **Stroke width:** 1px (mandatory — thinner arrows with proportional arrowheads)
- **Stroke color:** #495057
- **Stroke style:** solid
- **Roughness:** 0
- **End arrowhead:** "arrow"
- **Start arrowhead:** null
- **Points:** Maximum 2 segments (straight or 1 bend)
- **Binding:** startBinding + endBinding to image elements, focus: 0, **gap: 5** (mandatory, never use gap: 1)

> **MANDATORY:** All arrow bindings MUST use `gap: 5`. Values below 5 cause ugly overlapping with element edges.

### Arrow Labels
- **Font:** fontFamily: 3 (monospace)
- **Size:** 10px
- **Color:** #868e96
- **`textAlign`:** `"center"` (mandatory, never `"left"` or `"right"`)
- **Position:** Calculate midpoint between source and target logos, then offset 16px above:
  - `label.x = (source.x + source.width/2 + target.x + target.width/2) / 2 - label.width / 2`
  - `label.y = arrow.y - 16`
- **Content:** Brief description (e.g., "CSV", "Event Trigger", "Query")

> **MANDATORY:** Arrow labels MUST use `textAlign: "center"`. The `"left"` alignment causes labels to drift away from arrows.

### Zone Labels (optional)
- **Font:** fontFamily: 3 (monospace)
- **Size:** 14px
- **Color:** #ced4da
- **Alignment:** center
- **Position:** 15px above topmost logo in group
- **Content:** Zone name in caps (e.g., "DATA SOURCES", "WAREHOUSE")

---

## Canvas Dimensions

All logo-flow diagrams MUST use LinkedIn-optimized canvas sizes.

| Format | Width | Height | Ratio | Use Case |
|--------|-------|--------|-------|----------|
| **Portrait** | 1080 | 1350 | 4:5 | Vertical pipelines, carousels (DEFAULT) |
| **Landscape** | 1200 | 627 | 1.91:1 | Horizontal architecture overviews |

### Canvas Rules

- **Default:** Portrait 1080x1350 (use unless explicitly horizontal)
- All elements MUST fit within 40px margins on all sides
- Content area: x=[40..1040], y=[40..1310] for portrait
- Content area: x=[40..1160], y=[40..587] for landscape

---

## Anti-Overlap Rules

1. No arrow path may intersect any image element bounding box (except its bound start/end elements)
2. Arrow labels must not overlap any logo or other text element
3. Use Manhattan routing (L-shaped/Z-shaped) when source and target are not aligned
4. Maximum 3 segments per arrow path (4 points)
5. All arrows MUST use `strokeWidth: 1` — never 2 or higher

---

## Layout Rules

### Flow Direction
- **Primary:** Left to Right (horizontal)
- **Secondary:** Top to Bottom (for vertical relationships)

### Spacing
- **Between logos (horizontal):** 150-200px center-to-center
- **Between logos (vertical):** 120px center-to-center
- **Between zone groups:** 150px (measured from bottom of one zone's name labels to top of next zone's logos)
- **Canvas margins:** 40px all sides

### Alignment
- **Grid:** 10px alignment
- **Vertical alignment:** Logos in same horizontal flow share same Y coordinate
- **Horizontal alignment:** Logos in same vertical flow share same X coordinate

### Background
- **Color:** #ffffff (white)
- **Grid:** null (no grid)

---

## Example: MR. HEALTH Architecture (logo-flow)

```
  DATA SOURCES          INGESTION             WAREHOUSE              BI

  [PG Logo]            [GCS Logo]             [BQ Logo]          [Looker Logo]
  PostgreSQL  --CSV-->  Cloud Storage --Event-> BigQuery --Query-> Looker Studio
                                |
                           [CF Logo]
                        Cloud Functions
                         csv-processor
```

### Coordinates for this example:

| Element | x | y | width | height |
|---------|---|---|-------|--------|
| Zone: DATA SOURCES | 50 | 50 | 120 | 18 |
| Logo: PostgreSQL | 62 | 90 | 48 | 48 |
| Label: PostgreSQL | 48 | 146 | 76 | 14 |
| Zone: INGESTION | 250 | 50 | 100 | 18 |
| Logo: Cloud Storage | 262 | 90 | 48 | 48 |
| Label: Cloud Storage | 240 | 146 | 92 | 14 |
| Logo: Cloud Functions | 262 | 210 | 48 | 48 |
| Label: Cloud Functions | 236 | 266 | 100 | 14 |
| Zone: WAREHOUSE | 470 | 50 | 100 | 18 |
| Logo: BigQuery | 482 | 90 | 48 | 48 |
| Label: BigQuery | 474 | 146 | 64 | 14 |
| Zone: BI | 670 | 50 | 30 | 18 |
| Logo: Looker Studio | 662 | 90 | 48 | 48 |
| Label: Looker Studio | 644 | 146 | 84 | 14 |
| Arrow: PG->GCS | 110 | 114 | 152 | 0 |
| Arrow label: CSV | 160 | 98 | 30 | 12 |
| Arrow: GCS->BQ | 310 | 114 | 172 | 0 |
| Arrow label: Event | 370 | 98 | 50 | 12 |
| Arrow: BQ->Looker | 530 | 114 | 132 | 0 |
| Arrow label: Query | 574 | 98 | 44 | 12 |
| Arrow: GCS->CF | 286 | 138 | 0 | 72 |
| Arrow label: Trigger | 294 | 170 | 56 | 12 |

---

## Dual Generation Logic

### When to generate logo-flow alongside v3_technical:

| Diagram Type | Generate Logo-Flow? | Condition |
|-------------|---------------------|-----------|
| infrastructure | ALWAYS | - |
| data-flow | ALWAYS | - |
| before-after | CONTEXTUAL | Only if comparing technologies |
| multi-agent | CONTEXTUAL | If num_agents >= 5 |
| pipeline | CONTEXTUAL | If num_technologies >= 6 |
| data-model | NEVER | Structural, not technology-flow |
| roadmap | NEVER | Timeline, no logos |

### Output naming:
- `{name}_v3_technical.excalidraw`
- `{name}_v3_logo_flow.excalidraw`

---

## Quality Checklist

- [ ] Zero rectangles, ellipses, or diamonds in elements array
- [ ] All logos have corresponding entries in files object
- [ ] All arrows have valid startBinding and endBinding to image elements
- [ ] All image elements have boundElements listing their arrows
- [ ] Labels positioned 8px below logos, centered
- [ ] Arrow labels positioned 16px above arrows
- [ ] Consistent spacing (150-200px horizontal, 120px vertical)
- [ ] All text uses fontFamily: 3 (monospace)
- [ ] Background is white (#ffffff)

---

**Last Updated:** 2026-02-01
**Version:** 1.1 - v3 Logo-Flow Style (anti-overlap, strokeWidth:1, zone spacing 150px)
