# Excalidraw JSON Format Specification

## Overview

Excalidraw diagrams are stored as JSON files with a specific structure. This document provides the complete specification for generating valid Excalidraw files programmatically.

---

## Root Structure

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "generated-by-claude-code",
  "elements": [...],
  "appState": {
    "viewBackgroundColor": "#ffffff",
    "gridSize": null
  },
  "files": {}
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always "excalidraw" |
| `version` | number | Format version (use 2) |
| `source` | string | Origin identifier |
| `elements` | array | All diagram elements (shapes, text, arrows) |
| `appState` | object | Canvas settings |
| `files` | object | Embedded images as base64 data URLs (keyed by fileId) |

---

## Element Types

### Base Element Properties

All elements share these common properties:

```json
{
  "id": "unique_id_string",
  "type": "rectangle|ellipse|diamond|arrow|text|line|image",
  "x": 100,
  "y": 200,
  "width": 300,
  "height": 150,
  "angle": 0,
  "strokeColor": "#4a5568",
  "backgroundColor": "#e8f0fe",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "groupIds": [],
  "roundness": { "type": 3 },
  "seed": 12345,
  "version": 1,
  "versionNonce": 12345,
  "isDeleted": false,
  "boundElements": [],
  "updated": 1700000000000,
  "link": null,
  "locked": false
}
```

### Property Details

| Property | Type | Values | Description |
|----------|------|--------|-------------|
| `id` | string | Any unique string | Element identifier |
| `x`, `y` | number | Pixels | Top-left position |
| `width`, `height` | number | Pixels | Element dimensions |
| `angle` | number | Radians | Rotation angle (0 = no rotation) |
| `strokeColor` | string | Hex color | Border/outline color |
| `backgroundColor` | string | Hex color | Fill color |
| `fillStyle` | string | "solid", "hachure", "cross-hatch" | Fill pattern |
| `strokeWidth` | number | 1-4 | Border thickness (use 1 for arrows, 2 for containers) |
| `strokeStyle` | string | "solid", "dashed", "dotted" | Border style |
| `roughness` | number | 0-2 | Hand-drawn effect (0 = clean) |
| `opacity` | number | 0-100 | Transparency |
| `roundness` | object | `{"type": 0-3}` | Corner rounding (3 = rounded) |

---

## Shape Elements

### Rectangle

```json
{
  "id": "rect_1",
  "type": "rectangle",
  "x": 100,
  "y": 100,
  "width": 300,
  "height": 150,
  "angle": 0,
  "strokeColor": "#4285f4",
  "backgroundColor": "#e8f0fe",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "groupIds": [],
  "roundness": { "type": 3 },
  "seed": 100,
  "version": 1,
  "versionNonce": 100,
  "isDeleted": false,
  "boundElements": [
    { "id": "arrow_1", "type": "arrow" }
  ],
  "updated": 1700000000000,
  "link": null,
  "locked": false
}
```

**Use for:** Zones, containers, boxes, services

### Ellipse

```json
{
  "id": "ellipse_1",
  "type": "ellipse",
  "x": 500,
  "y": 100,
  "width": 200,
  "height": 100,
  "angle": 0,
  "strokeColor": "#7c3aed",
  "backgroundColor": "#f3e8ff",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "groupIds": [],
  "roundness": { "type": 2 },
  "seed": 200,
  "version": 1,
  "versionNonce": 200,
  "isDeleted": false,
  "boundElements": [],
  "updated": 1700000000000,
  "link": null,
  "locked": false
}
```

**Use for:** Orchestrators, agents, processes

### Diamond

```json
{
  "id": "diamond_1",
  "type": "diamond",
  "x": 400,
  "y": 400,
  "width": 150,
  "height": 100,
  "angle": 0,
  "strokeColor": "#0f9d58",
  "backgroundColor": "#c8e6c9",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "groupIds": [],
  "roundness": { "type": 2 },
  "seed": 300,
  "version": 1,
  "versionNonce": 300,
  "isDeleted": false,
  "boundElements": [],
  "updated": 1700000000000,
  "link": null,
  "locked": false
}
```

**Use for:** Decision points, schedulers, orchestration

---

## Text Elements

```json
{
  "id": "text_1",
  "type": "text",
  "x": 120,
  "y": 130,
  "width": 260,
  "height": 90,
  "angle": 0,
  "strokeColor": "#1a73e8",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "groupIds": [],
  "roundness": null,
  "seed": 400,
  "version": 1,
  "versionNonce": 400,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1700000000000,
  "link": null,
  "locked": false,
  "text": "Cloud Storage\\nBronze / Raw Zone",
  "fontSize": 16,
  "fontFamily": 1,
  "textAlign": "center",
  "verticalAlign": "top",
  "baseline": 16,
  "containerId": null,
  "originalText": "Cloud Storage\\nBronze / Raw Zone"
}
```

### Text Properties

| Property | Type | Values | Description |
|----------|------|--------|-------------|
| `text` | string | Any text | Content (use \\n for line breaks) |
| `fontSize` | number | 12-32 | Font size in pixels |
| `fontFamily` | number | 1, 2, 3 | 1=Normal, 2=Serif, 3=Mono |
| `textAlign` | string | "left", "center", "right" | Horizontal alignment |
| `verticalAlign` | string | "top", "middle", "bottom" | Vertical alignment |
| `baseline` | number | Same as fontSize | Text baseline |
| `containerId` | string | Element ID or null | Parent container |

---

## Arrow Elements

```json
{
  "id": "arrow_1",
  "type": "arrow",
  "x": 400,
  "y": 175,
  "width": 100,
  "height": 0,
  "angle": 0,
  "strokeColor": "#4285f4",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "groupIds": [],
  "roundness": { "type": 2 },
  "seed": 500,
  "version": 1,
  "versionNonce": 500,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1700000000000,
  "link": null,
  "locked": false,
  "points": [[0, 0], [100, 0]],
  "lastCommittedPoint": null,
  "startBinding": {
    "elementId": "rect_1",
    "focus": 0,
    "gap": 5
  },
  "endBinding": {
    "elementId": "rect_2",
    "focus": 0,
    "gap": 5
  },
  "startArrowhead": null,
  "endArrowhead": "arrow"
}
```

### Arrow Properties

| Property | Type | Description |
|----------|------|-------------|
| `points` | array | Array of [x, y] coordinates defining path |
| `startBinding` | object | Connection to start element |
| `endBinding` | object | Connection to end element |
| `startArrowhead` | string | "arrow", "dot", "triangle", null |
| `endArrowhead` | string | "arrow", "dot", "triangle", null |

### Binding Object

```json
{
  "elementId": "target_element_id",
  "focus": 0,
  "gap": 5
}
```

- `elementId`: ID of connected element
- `focus`: Position along edge (-1 to 1, 0 = center)
- `gap`: Distance from element edge in pixels (**minimum 5**, never use 1)

### Arrow Routing Rules

Arrows MUST NOT pass through any element they are not connected to.

**Routing Strategy: Manhattan (orthogonal segments)**

1. **Aligned elements** (same X or same Y): use straight arrow
   - `points: [[0, 0], [0, dy]]` (vertical) or `[[0, 0], [dx, 0]]` (horizontal)

2. **Non-aligned elements**: use L-shaped or Z-shaped routing
   - L-shape: `points: [[0, 0], [dx, 0], [dx, dy]]`
   - Z-shape: `points: [[0, 0], [dx/2, 0], [dx/2, dy], [dx, dy]]`

3. **Maximum segments**: 3 segments (4 points) per arrow

4. **Clearance**: Arrow path must maintain 20px distance from any non-connected element's bounding box

**Arrow strokeWidth Rule:**
- **ALL arrows MUST use `strokeWidth: 1`** — produces thin, elegant lines with proportionally small arrowheads
- Never use strokeWidth 2 or higher on arrows

**Anti-Overlap Checklist:**
- [ ] No arrow line passes through any rectangle interior
- [ ] No arrow line passes through any image element
- [ ] No arrow line passes through any text element
- [ ] Arrow labels do not overlap with any element

---

## Line Elements

```json
{
  "id": "line_1",
  "type": "line",
  "x": 300,
  "y": 200,
  "width": 150,
  "height": 100,
  "angle": 0,
  "strokeColor": "#4a5568",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "groupIds": [],
  "roundness": null,
  "seed": 600,
  "version": 1,
  "versionNonce": 600,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1700000000000,
  "link": null,
  "locked": false,
  "points": [[0, 0], [75, 50], [150, 100]],
  "lastCommittedPoint": null,
  "startBinding": null,
  "endBinding": null,
  "startArrowhead": null,
  "endArrowhead": null
}
```

**Use for:** Custom paths, decorative elements, dividers

---

## Image Elements

Images are embedded as base64 data URLs in the `files` object and referenced by `fileId` in image elements.

### Image Element Structure

```json
{
  "id": "logo_bigquery",
  "type": "image",
  "x": 100,
  "y": 100,
  "width": 48,
  "height": 48,
  "angle": 0,
  "strokeColor": "#000000",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "groupIds": [],
  "roundness": null,
  "seed": 12345,
  "version": 1,
  "versionNonce": 12345,
  "isDeleted": false,
  "boundElements": [
    { "id": "arrow_1", "type": "arrow" }
  ],
  "updated": 1706745600000,
  "link": null,
  "locked": false,
  "fileId": "bigquery_logo",
  "scale": [1, 1]
}
```

### Image-Specific Properties

| Property | Type | Description |
|----------|------|-------------|
| `fileId` | string | Reference to key in `files` object |
| `scale` | array | [scaleX, scaleY], typically [1, 1] |

### Files Object Structure

The root-level `files` object stores embedded image data:

```json
{
  "files": {
    "bigquery_logo": {
      "mimeType": "image/svg+xml",
      "id": "bigquery_logo",
      "dataURL": "data:image/svg+xml;base64,PHN2ZyB...",
      "created": 1706745600000,
      "lastRetrieved": 1706745600000
    }
  }
}
```

### Files Entry Properties

| Property | Type | Description |
|----------|------|-------------|
| `mimeType` | string | "image/svg+xml", "image/png", or "image/jpeg" |
| `id` | string | Same as the key in files object |
| `dataURL` | string | Complete base64 data URI |
| `created` | number | Unix timestamp (milliseconds) |
| `lastRetrieved` | number | Unix timestamp (milliseconds) |

### Constraints

- Maximum image size: 2MB after encoding
- Maximum dimension: 1440px on longest axis
- SVG preferred: 1-7KB typical, scalable, smallest file size
- Arrows CAN bind to image elements (same as rectangles)

### Logo Sizing

| Context | Width | Height | Use |
|---------|-------|--------|-----|
| **Logo-flow diagrams** | 48px | 48px | Standalone logos (uniform size, no exceptions) |
| **Inside containers** | 20-28px | 20-28px | Small icon within box |
| **Hero/featured** | 80-96px | 80-96px | Highlighted technology |

### Logo Library

Pre-encoded logos are available in:
- `.claude/kb/diagram-generation/logos/gcp.md` - GCP service logos
- `.claude/kb/diagram-generation/logos/general.md` - Database, tool, DevOps logos
- `.claude/kb/diagram-generation/logos/custom.md` - On-demand custom logos

Each logo entry includes ready-to-copy `fileId`, `dataURL`, element template, and files entry.

---

## Canvas Dimensions

All diagrams MUST use LinkedIn-optimized canvas sizes to ensure proper display on social media.

| Format | Width | Height | Ratio | Use Case |
|--------|-------|--------|-------|----------|
| **Portrait** | 1080 | 1350 | 4:5 | Vertical diagrams, carousels, pipelines (DEFAULT) |
| **Landscape** | 1200 | 627 | 1.91:1 | Horizontal diagrams, wide architecture overviews |

### Canvas Rules

- **Default format:** Portrait 1080x1350 (use unless diagram is explicitly horizontal)
- All elements MUST fit within canvas bounds with 40px margins
- `appState` should NOT set `scrollX`/`scrollY` — content starts at (40, 40)
- Ensure no element exceeds `canvas_width - 40` (x + width) or `canvas_height - 40` (y + height)

---

## Multi-Connection Arrow Routing (Star Schema / ER Diagrams)

When multiple elements in **Row A** connect to multiple elements in **Row B**, arrows WILL
visually collide unless routed through dedicated lanes. This section defines the algorithm.

### Step 1: Classify Connections by Distance

For each arrow, calculate the **horizontal distance** between source center and target center:

| Category | Horizontal Distance | Routing |
|----------|-------------------|---------|
| **Direct** | < source.width | Straight vertical (2 points only) |
| **Short** | < 2 × element spacing | L-shape, lowest lane |
| **Medium** | 2-3 × element spacing | L-shape, middle lane |
| **Long** | > 3 × element spacing | L-shape, highest lane |

### Step 2: Assign Routing Lanes

Allocate distinct Y-coordinates for each arrow's horizontal segment:

```
Channel top    = source_row_bottom + 15px
Lane 0 (top)   = channel_top + 0                  ← longest connections
Lane 1          = channel_top + 20px
Lane 2          = channel_top + 40px
Lane N (bottom) = channel_top + N × 20px           ← shortest connections
Channel bottom = Lane_N + 15px
Target row top = channel_bottom
```

**CRITICAL RULE:** No two arrows may share the same horizontal Y-coordinate.
Even if arrows don't physically overlap, stagger them for visual clarity.

### Step 3: Distribute Focus Values

When multiple arrows connect to the **same edge** of a rectangle, spread the `focus`
values evenly to prevent arrows from bunching at the center:

```
1 connection:  focus = [0]
2 connections: focus = [-0.4, +0.4]
3 connections: focus = [-0.5, 0, +0.5]
4 connections: focus = [-0.6, -0.2, +0.2, +0.6]
```

Order: leftmost arrow gets the most negative focus, rightmost gets the most positive.

### Step 4: Generate Arrow Points

**Direct connection** (source above target, horizontally aligned):
```javascript
points: [[0, 0], [0, totalVerticalDistance]]
```

**L-shaped connection** (source NOT above target):
```javascript
// Source exits bottom, goes to assigned lane, turns horizontal, then drops to target
const laneY = assignedLane * 20;  // relative to arrow start
const targetDeltaX = target.centerX - source.exitX;
const totalDeltaY = target.topY - source.bottomY;

points: [
  [0, 0],                           // exit source bottom
  [0, laneY],                       // drop to lane
  [targetDeltaX, laneY],            // horizontal to above target
  [targetDeltaX, totalDeltaY]       // drop to target
]
```

### Step 5: Position Labels

Place each arrow's label at the **midpoint of its horizontal segment**, 15px above:

```javascript
label.x = arrow.x + (points[1][0] + points[2][0]) / 2 - label.width / 2
label.y = arrow.y + laneY - 15
```

### Anti-Collision Verification

After generating all arrows, verify:
- [ ] No two horizontal segments share the same Y-coordinate
- [ ] No horizontal segment passes through a non-connected rectangle
- [ ] All labels are readable (not overlapping other labels or arrows)
- [ ] Focus values are distributed (no two arrows enter the same point on an edge)

---

## Arrow Label Rules

Arrow labels (text elements describing data flow on arrows) MUST follow these rules:

- **`textAlign`:** Always `"center"` (never `"left"` or `"right"`)
- **Position:** Calculate midpoint between source and target element centers:
  - `label.x = (source.centerX + target.centerX) / 2 - label.width / 2`
  - `label.y = arrow.y - 20` (20px above the arrow line)
- **Font:** fontFamily: 3 (monospace), fontSize: 10-11px
- **Color:** #868e96 (muted gray)

---

## Color Palette

### Standard Colors

| Component | Stroke | Background | Usage |
|-----------|--------|------------|-------|
| **On-Premise** | #4a5568 | #f8f9fa | Legacy systems, local infrastructure |
| **GCP Services** | #4285f4 | #e8f0fe | Cloud Storage, BigQuery, Cloud Functions |
| **Data Layers** | #0f9d58 | #e6f4ea | Medallion zones (Bronze/Silver/Gold) |
| **Bronze** | #e65100 | #f9ab00 | Raw data ingestion |
| **Silver** | #616161 | #c0c0c0 | Cleaned data |
| **Gold** | #f57f17 | #ffd700 | Analytics-ready |
| **Agentic AI** | #7c3aed | #f3e8ff | AI agents, orchestrators |
| **MCP/KB** | #d97706 | #f59e0b | Context protocol, knowledge base |
| **Business** | #ef4444 | #fee2e2 | Business value, outputs |

### Opacity Levels

| Use Case | Opacity |
|----------|---------|
| Primary elements | 100 |
| Secondary/annotations | 70-80 |
| Background zones | 50-60 |

---

## Layout Guidelines

### Positioning

- **Grid alignment:** Multiples of 10px
- **Zone padding:** 20-50px
- **Inter-element spacing:** 40-60px minimum
- **Arrow clearance:** 20px from text

### Sizing

| Element | Width | Height |
|---------|-------|--------|
| Small box | 150-200 | 70-90 |
| Medium box | 250-300 | 100-150 |
| Large box | 350-500 | 150-250 |
| Zone container | 300-700 | 300-700 |
| Text labels | Auto-fit | Auto-fit |

### Container Text Padding

Text inside rectangle containers MUST have minimum 12px padding on all sides:

| Padding | Formula |
|---------|---------|
| Left | `text.x = container.x + 12` |
| Top | `text.y = container.y + 12` |
| Right | `text.x + text.width <= container.x + container.width - 12` |
| Bottom | `text.y + text.height <= container.y + container.height - 12` |

### Z-Order

Elements render in array order:
1. Background zones (first)
2. Connecting arrows
3. Shape elements
4. Text labels (last, always on top)

---

## Best Practices

### ✅ Do

- Use `roughness: 0` for clean, professional look
- Set `roundness: {"type": 3}` for rounded rectangles
- Use `strokeWidth: 1` for ALL arrows (mandatory)
- Use `strokeWidth: 2` for container rectangles only
- Align elements to grid (x, y multiples of 10)
- Leave generous whitespace between zones

### ❌ Don't

- Overlap text elements
- Use more than 4-5 colors in one diagram
- Create arrows with more than 3 points (keep simple)
- Set opacity below 50 (hard to read)
- Use hand-drawn effect (roughness > 0) for technical diagrams

---

## Validation Checklist

Before generating final JSON:

- [ ] All elements have unique IDs
- [ ] All colors are valid hex codes
- [ ] All arrow bindings reference existing element IDs
- [ ] No text overlap (minimum 20px spacing)
- [ ] All coordinates are positive numbers
- [ ] Font sizes are between 12-32px
- [ ] Canvas bounds accommodate all elements
- [ ] JSON is valid and properly escaped

---

## Example: Complete Minimal Diagram

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "claude-code-diagram-generator",
  "elements": [
    {
      "id": "bg_zone",
      "type": "rectangle",
      "x": 20,
      "y": 20,
      "width": 500,
      "height": 300,
      "strokeColor": "#4285f4",
      "backgroundColor": "#e8f0fe",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "roundness": { "type": 3 },
      "angle": 0,
      "groupIds": [],
      "seed": 1,
      "version": 1,
      "versionNonce": 1,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1700000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "label_zone",
      "type": "text",
      "x": 40,
      "y": 35,
      "width": 150,
      "height": 25,
      "text": "GCP CLOUD",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "left",
      "verticalAlign": "top",
      "strokeColor": "#4285f4",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "roundness": null,
      "angle": 0,
      "groupIds": [],
      "baseline": 20,
      "containerId": null,
      "originalText": "GCP CLOUD",
      "seed": 2,
      "version": 1,
      "versionNonce": 2,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1700000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "service_box",
      "type": "rectangle",
      "x": 60,
      "y": 100,
      "width": 200,
      "height": 100,
      "strokeColor": "#4285f4",
      "backgroundColor": "#bbdefb",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "roundness": { "type": 3 },
      "angle": 0,
      "groupIds": [],
      "seed": 3,
      "version": 1,
      "versionNonce": 3,
      "isDeleted": false,
      "boundElements": [
        { "id": "arrow_1", "type": "arrow" }
      ],
      "updated": 1700000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "service_text",
      "type": "text",
      "x": 80,
      "y": 130,
      "width": 160,
      "height": 40,
      "text": "Cloud Storage\\nData Lake",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "strokeColor": "#1a73e8",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "roundness": null,
      "angle": 0,
      "groupIds": [],
      "baseline": 16,
      "containerId": null,
      "originalText": "Cloud Storage\\nData Lake",
      "seed": 4,
      "version": 1,
      "versionNonce": 4,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1700000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "service_box_2",
      "type": "rectangle",
      "x": 300,
      "y": 100,
      "width": 180,
      "height": 100,
      "strokeColor": "#4285f4",
      "backgroundColor": "#bbdefb",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "roundness": { "type": 3 },
      "angle": 0,
      "groupIds": [],
      "seed": 5,
      "version": 1,
      "versionNonce": 5,
      "isDeleted": false,
      "boundElements": [
        { "id": "arrow_1", "type": "arrow" }
      ],
      "updated": 1700000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "service_text_2",
      "type": "text",
      "x": 315,
      "y": 130,
      "width": 150,
      "height": 40,
      "text": "BigQuery\\nData Warehouse",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "strokeColor": "#1a73e8",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "roundness": null,
      "angle": 0,
      "groupIds": [],
      "baseline": 16,
      "containerId": null,
      "originalText": "BigQuery\\nData Warehouse",
      "seed": 6,
      "version": 1,
      "versionNonce": 6,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1700000000000,
      "link": null,
      "locked": false
    },
    {
      "id": "arrow_1",
      "type": "arrow",
      "x": 260,
      "y": 150,
      "width": 40,
      "height": 0,
      "strokeColor": "#4285f4",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "roundness": { "type": 2 },
      "angle": 0,
      "groupIds": [],
      "points": [[0, 0], [40, 0]],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "service_box",
        "focus": 0,
        "gap": 5
      },
      "endBinding": {
        "elementId": "service_box_2",
        "focus": 0,
        "gap": 5
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "seed": 7,
      "version": 1,
      "versionNonce": 7,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1700000000000,
      "link": null,
      "locked": false
    }
  ],
  "appState": {
    "viewBackgroundColor": "#ffffff",
    "gridSize": null
  },
  "files": {}
}
```

---

**Last Updated:** 2026-02-01
**Format Version:** Excalidraw v2
