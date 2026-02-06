# Analysis: alt2_handcrafted.excalidraw

## Overview

This document analyzes the `diagrams/alt2_handcrafted.excalidraw` file to extract patterns, best practices, and design decisions for use as a reference when generating new diagrams.

**Source:** `diagrams/alt2_handcrafted.excalidraw`
**Type:** Architecture diagram (4-zone horizontal layout)
**Canvas Size:** ~2100px × 750px
**Zones:** 4 major zones (On-Premise, GCP Data Mesh, Agentic AI Engine, Business Value)

---

## Structure Analysis

### Zone Organization

The diagram uses a **4-zone horizontal layout** with clear separation:

```
┌──────────┬─────────────────────┬──────────────────┬──────────────┐
│ ON-      │ GCP DATA MESH       │ AGENTIC AI       │ BUSINESS     │
│ PREMISE  │ (Ingestion + Layers)│ ENGINE           │ VALUE        │
│          │                     │                  │              │
│ CSV      │ GCS → CF → BQ       │ Orchestrator     │ Looker       │
│ Sources  │ Bronze/Silver/Gold  │ + Agents + MCP   │ Alerts       │
│ PG DB    │ Scheduler           │ + KB             │ Decisions    │
└──────────┴─────────────────────┴──────────────────┴──────────────┘
```

**Coordinates:**
| Zone | X | Y | Width | Height |
|------|---|---|-------|--------|
| On-Premise | 20 | 20 | 380 | 700 |
| GCP Data Mesh | 440 | 20 | 700 | 700 |
| Agentic AI Engine | 1180 | 20 | 520 | 700 |
| Business Value | 1740 | 20 | 310 | 700 |

**Total Canvas:** 2070px × 740px

**Spacing between zones:** 20-40px

---

## Color Scheme

### Zone Colors

| Zone | Stroke | Background | Usage |
|------|--------|------------|-------|
| On-Premise | `#4a5568` | `#f8f9fa` | Gray - Legacy/existing systems |
| GCP Data Mesh | `#4285f4` | `#e8f0fe` | Blue - Cloud infrastructure |
| Agentic AI | `#7c3aed` | `#f3e8ff` | Purple - AI/ML systems |
| Business Value | `#ef4444` | `#fee2e2` | Red - Business outcomes |

### Component Colors

| Component | Stroke | Background |
|-----------|--------|------------|
| CSV Sources | `#4a5568` | `#e2e8f0` |
| PostgreSQL | `#4a5568` | `#e2e8f0` |
| Cloud Storage | `#4285f4` | `#bbdefb` |
| Cloud Functions | `#4285f4` | `#bbdefb` |
| Bronze Layer | `#e65100` | `#f9ab00` |
| Silver Layer | `#616161` | `#c0c0c0` |
| Gold Layer | `#f57f17` | `#ffd700` |
| Scheduler | `#4285f4` | `#c8e6c9` |
| Orchestrator | `#5b21b6` | `#7c3aed` |
| Agents | `#7e22ce` | `#a855f7` |
| MCP | `#d97706` | `#f59e0b` |
| Knowledge Base | `#a16207` | `#fbbf24` |
| Business Outputs | `#dc2626` | `#ef4444` |

---

## Typography

### Font Sizes Used

| Purpose | Size | Examples |
|---------|------|----------|
| Zone titles | 28px | "ON-PREMISE", "GCP DATA MESH" |
| Section headers | 16-20px | "Ingestion & Landing", "BigQuery - Medallion" |
| Component labels | 15-18px | "Cloud Storage", "Multi-Agent Orchestrator" |
| Descriptions | 14-15px | "Pharmacy Retail Network", "Real-time Insights" |
| Small annotations | 12px | "CSV FILES", "Trigger", "Load" |

### Text Alignment

- **Zone titles:** Center-aligned
- **Component labels:** Center-aligned
- **Section headers:** Left-aligned
- **Annotations:** Center or left-aligned

---

## Element Patterns

### Pattern 1: Zone Container + Title

```javascript
[
  // Background rectangle
  {
    id: "bg_onprem",
    type: "rectangle",
    x: 20,
    y: 20,
    width: 380,
    height: 700,
    strokeColor: "#4a5568",
    backgroundColor: "#f8f9fa",
    strokeWidth: 2,
    roundness: { type: 3 }
  },
  // Zone title
  {
    id: "label_onprem",
    type: "text",
    x: 80,
    y: 35,
    width: 260,
    height: 35,
    text: "ON-PREMISE",
    fontSize: 28,
    fontFamily: 1,
    textAlign: "center"
  }
]
```

**Pattern:** Background rectangle first (lower z-index), then title text on top.

### Pattern 2: Service Box + Label

```javascript
[
  // Service rectangle
  {
    id: "node_cs",
    type: "rectangle",
    x: 490,
    y: 125,
    width: 260,
    height: 80,
    strokeColor: "#4285f4",
    backgroundColor: "#bbdefb",
    strokeWidth: 2,
    roundness: { type: 3 }
  },
  // Service label
  {
    id: "text_cs",
    type: "text",
    x: 510,
    y: 138,
    width: 220,
    height: 55,
    text: "Cloud Storage\\nBronze / Raw Zone",
    fontSize: 16,
    textAlign: "center"
  }
]
```

**Pattern:** Box first, label centered inside with padding.

### Pattern 3: Medallion Layers (Bronze → Silver → Gold)

```javascript
const medallionLayers = [
  // Bronze
  { x: 490, y: 360, width: 170, height: 90, bg: "#f9ab00" },
  // Silver
  { x: 700, y: 360, width: 170, height: 90, bg: "#c0c0c0" },
  // Gold
  { x: 910, y: 360, width: 170, height: 90, bg: "#ffd700" }
];

// Connected by arrows
const arrows = [
  { from: "bronze", to: "silver", strokeWidth: 3 },
  { from: "silver", to: "gold", strokeWidth: 3 }
];
```

**Pattern:** Same-sized boxes, horizontally aligned, connected by thick arrows.

### Pattern 4: Hub-and-Spoke (Orchestrator + Agents)

```javascript
// Center: Orchestrator (ellipse)
{
  id: "node_orchestrator",
  type: "ellipse",
  x: 1310,
  y: 85,
  width: 260,
  height: 100
}

// Spoke: Agents (rectangles)
const agents = [
  { id: "inv", x: 1200, y: 230, width: 150, height: 70 },
  { id: "sales", x: 1370, y: 230, width: 150, height: 70 },
  { id: "supply", x: 1540, y: 230, width: 150, height: 70 }
];

// Connected by arrows from orchestrator to each agent
```

**Pattern:** Central ellipse with rectangular "satellites" below.

---

## Arrow Styles

### Data Flow Arrows

```javascript
{
  strokeWidth: 2,
  strokeStyle: "solid",
  strokeColor: "#4285f4",
  endArrowhead: "arrow"
}
```

**Usage:** Primary data movement (CSV → GCS, GCS → CF, etc.)

### Transformation Arrows (Medallion)

```javascript
{
  strokeWidth: 3,          // Thicker for emphasis
  strokeStyle: "solid",
  strokeColor: "#0f9d58",  // Green for transformation
  endArrowhead: "arrow"
}
```

**Usage:** Bronze → Silver → Gold flow

### Metadata/Config Arrows

```javascript
{
  strokeWidth: 2,
  strokeStyle: "dashed",   // Dashed for non-primary flow
  strokeColor: "#4a5568",
  endArrowhead: "arrow"
}
```

**Usage:** PostgreSQL → Cloud Storage (metadata sync)

### Orchestration Arrows

```javascript
{
  strokeWidth: 1,
  strokeStyle: "dashed",
  strokeColor: "#4285f4",
  opacity: 80,
  endArrowhead: "arrow"
}
```

**Usage:** Scheduler → Bronze/Silver/Gold

---

## Spacing Analysis

### Zone Spacing

- **Between zones:** 20-40px
- **Internal zone padding:** 40-60px
- **Zone title margin-top:** 15px

### Component Spacing

- **Between unrelated components:** 60px
- **Between related components:** 20-40px
- **Component-to-arrow clearance:** 20px minimum

### Text Spacing

- **Inside box padding:** 10-20px from border
- **Multi-line text line spacing:** ~1.4x font size
- **Label below component:** 10-15px gap

---

## Layout Techniques

### Technique 1: Sub-zones within Zones

The GCP zone contains two sub-zones:

```
GCP Data Mesh (main zone)
  ├─ Ingestion & Landing (sub-zone, dashed border)
  │    ├─ Cloud Storage
  │    └─ Cloud Functions
  └─ BigQuery - Medallion Architecture (sub-zone, dashed border)
       ├─ Bronze
       ├─ Silver
       └─ Gold
```

**Implementation:**
- Main zone: solid border, `strokeWidth: 2`
- Sub-zone: dashed border, `strokeWidth: 1`, lighter background

### Technique 2: Visual Depth with Colors

**Hierarchy:**
1. **Zone background** - Lightest shade (e.g., `#e8f0fe`)
2. **Sub-zone background** - Medium shade (e.g., `#d2e3fc`)
3. **Component background** - Darker shade (e.g., `#bbdefb`)

Creates visual hierarchy without additional elements.

### Technique 3: Diamond for Decision Points

```javascript
{
  type: "diamond",
  width: 280,
  height: 120,
  // Used for scheduler/orchestration
}
```

**When to use:** Schedulers, decision points, conditional logic.

---

## Best Practices Observed

### ✅ Good Practices

1. **Consistent zone widths:** Zones have similar proportions
2. **Color coding:** Each zone has distinct color family
3. **Clear labels:** Every component has a readable label
4. **Visual hierarchy:** Zones → sub-zones → components
5. **Arrow differentiation:** Solid for data, dashed for control
6. **Generous whitespace:** No cramped elements
7. **Aligned elements:** Components align horizontally/vertically
8. **Semantic shapes:** Ellipse for orchestrator, diamond for scheduler

### ⚠️ Issues to Improve

1. **Some text overlap:** Arrows cross text in a few places
2. **Inconsistent spacing:** Some areas have 20px gaps, others 60px
3. **Arrow complexity:** Some L-shaped arrows have too many points
4. **Zone padding variation:** Not uniform across all zones

---

## Element Count

| Type | Count | Notes |
|------|-------|-------|
| Rectangles | 20+ | Zones, services, components |
| Ellipses | 2 | Orchestrator, decorative |
| Diamonds | 1 | Scheduler |
| Arrows | 15+ | Data flows, connections |
| Text | 35+ | Labels, titles, descriptions |
| Lines | 1 | Decorative (KB fold) |

**Total elements:** ~75

---

## Reusable Patterns

### Pattern: Zone Template

```javascript
function createZone(id, title, x, y, width, height, strokeColor, bgColor) {
  return [
    {
      id: `bg_${id}`,
      type: "rectangle",
      x, y, width, height,
      strokeColor,
      backgroundColor: bgColor,
      strokeWidth: 2,
      strokeStyle: "solid",
      fillStyle: "solid",
      roughness: 0,
      opacity: 100,
      roundness: { type: 3 },
      // ... other required properties
    },
    {
      id: `label_${id}`,
      type: "text",
      x: x + 60,
      y: y + 15,
      width: width - 120,
      height: 35,
      text: title,
      fontSize: 28,
      fontFamily: 1,
      textAlign: "center",
      strokeColor: strokeColor,
      // ... other required properties
    }
  ];
}
```

### Pattern: Service Box Template

```javascript
function createServiceBox(id, label, x, y, width, height, strokeColor, bgColor) {
  return [
    {
      id: `node_${id}`,
      type: "rectangle",
      x, y, width, height,
      strokeColor,
      backgroundColor: bgColor,
      strokeWidth: 2,
      roundness: { type: 3 },
      // ... other properties
    },
    {
      id: `text_${id}`,
      type: "text",
      x: x + 20,
      y: y + 15,
      width: width - 40,
      height: height - 30,
      text: label,
      fontSize: 16,
      textAlign: "center",
      strokeColor: darker(strokeColor),
      // ... other properties
    }
  ];
}
```

---

## Key Learnings

### Layout

1. **4-zone layout works well** for complex architectures
2. **Zone widths should be proportional** to content density
3. **Horizontal flow** (left → right) for sequential processes
4. **Vertical grouping** within zones for related components

### Colors

1. **Semantic color families** per zone (gray, blue, purple, red)
2. **Lighter backgrounds for zones,** darker for components
3. **Consistent color within zone** creates cohesion
4. **Medallion colors** (bronze/silver/gold) are recognizable

### Typography

1. **Large titles** (28px) for zones establish hierarchy
2. **Medium labels** (16-18px) for components are readable
3. **Small annotations** (12px) for supplementary info
4. **Center-aligned text** works best for most components

### Arrows

1. **Thicker arrows** (3px) for main data flows draw attention
2. **Dashed arrows** for non-primary connections reduce visual noise
3. **Minimize arrow points** (2-3 max) for clarity
4. **Color-code arrows** to match zones/flows

---

## Recommended Improvements

### For Future Diagrams

1. **Increase spacing between some elements** to 50px minimum
2. **Standardize zone padding** to 50px on all sides
3. **Reduce arrow complexity** (max 3 points per arrow)
4. **Add more whitespace** in dense areas (GCP zone)
5. **Align all components to 10px grid** consistently

---

## Application to New Diagrams

### When generating architecture diagrams:

1. **Use 3-4 zone layout** for complex systems
2. **Apply semantic color families** per zone
3. **Use sub-zones with dashed borders** for grouping
4. **Center components within zones** when possible
5. **Connect with appropriately styled arrows**
6. **Ensure minimum 40px spacing** between elements
7. **Add zone titles** with 28px font, centered
8. **Use consistent shapes** (rectangles for services, ellipses for orchestrators)

---

## Code Example: Minimal Zone

```javascript
const onPremZone = [
  // Background
  {
    id: "bg_onprem",
    type: "rectangle",
    x: 20,
    y: 20,
    width: 380,
    height: 700,
    angle: 0,
    strokeColor: "#4a5568",
    backgroundColor: "#f8f9fa",
    fillStyle: "solid",
    strokeWidth: 2,
    strokeStyle: "solid",
    roughness: 0,
    opacity: 100,
    groupIds: [],
    roundness: { type: 3 },
    seed: 100,
    version: 1,
    versionNonce: 100,
    isDeleted: false,
    boundElements: null,
    updated: Date.now(),
    link: null,
    locked: false
  },
  // Title
  {
    id: "label_onprem",
    type: "text",
    x: 80,
    y: 35,
    width: 260,
    height: 35,
    angle: 0,
    strokeColor: "#4a5568",
    backgroundColor: "transparent",
    fillStyle: "solid",
    strokeWidth: 1,
    strokeStyle: "solid",
    roughness: 0,
    opacity: 100,
    groupIds: [],
    roundness: null,
    seed: 101,
    version: 1,
    versionNonce: 101,
    isDeleted: false,
    boundElements: null,
    updated: Date.now(),
    link: null,
    locked: false,
    text: "ON-PREMISE",
    fontSize: 28,
    fontFamily: 1,
    textAlign: "center",
    verticalAlign: "top",
    baseline: 28,
    containerId: null,
    originalText: "ON-PREMISE"
  }
];
```

---

**Summary:** The alt2 diagram demonstrates effective use of zones, colors, and hierarchy. Minor improvements in spacing and alignment would enhance clarity. Use as primary reference for multi-zone architecture diagrams.

---

**Analysis Date:** 2026-01-30
**Diagram Version:** alt2_handcrafted.excalidraw
**Analyst:** Claude Code Diagram Generator Agent
