# Excalidraw Layout Patterns

## Overview

This document defines spatial organization patterns for clean, professional, and didactic diagrams. Follow these patterns to ensure consistent, readable visualizations without visual clutter or overlap.

---

## Core Principles

### 1. **Generous Whitespace**
- Minimum 100px padding between major zones
- Minimum 40px spacing between related elements
- Minimum 20px clearance around text

### 2. **Hierarchical Zones**
- Group related components visually
- Use background rectangles to define zones
- Maximum 3-4 major zones per diagram

### 3. **Grid Alignment**
- All coordinates in multiples of 10px
- Consistent element sizes within categories
- Vertical and horizontal alignment of related items

### 4. **Visual Flow**
- Left-to-right for sequential processes
- Top-to-bottom for hierarchical structures
- Curved arrows for feedback loops

---

## Layout Templates

### Template 1: Horizontal 3-Zone Architecture

**Use for:** Infrastructure diagrams, multi-tier systems

```
┌──────────────────────────────────────────────────────────────────────┐
│  DIAGRAM TITLE (centered, large font)                               │
├─────────────────┬─────────────────────┬───────────────────────────┤
│                 │                     │                           │
│    ZONE 1       │     ZONE 2          │       ZONE 3             │
│  (On-Premise)   │   (Cloud/Core)      │   (AI/Business)          │
│                 │                     │                           │
│   ┌────────┐    │    ┌─────────┐     │    ┌──────────┐          │
│   │Source 1│───→│───→│Service A│────→│───→│ Output 1 │          │
│   └────────┘    │    └─────────┘     │    └──────────┘          │
│                 │                     │                           │
│   ┌────────┐    │    ┌─────────┐     │    ┌──────────┐          │
│   │Source 2│───→│───→│Service B│────→│───→│ Output 2 │          │
│   └────────┘    │    └─────────┘     │    └──────────┘          │
│                 │                     │                           │
└─────────────────┴─────────────────────┴───────────────────────────┘

Dimensions:
- Canvas width: ~2000px
- Zone width: ~600-650px each
- Zone padding: 40-50px
- Zone spacing: 20px between zones
```

**Coordinates:**
```javascript
const zones = {
  zone1: { x: 20, y: 80, width: 600, height: 700 },
  zone2: { x: 660, y: 80, width: 660, height: 700 },
  zone3: { x: 1360, y: 80, width: 600, height: 700 }
};
```

---

### Template 2: Vertical Medallion Pipeline

**Use for:** Data flow diagrams, ETL pipelines

```
┌──────────────────────────────────────────┐
│  INGESTION & LANDING                     │
│  ┌────────────┐      ┌────────────┐     │
│  │  Source    │─────→│Cloud Storage│     │
│  └────────────┘      └────────────┘     │
└──────────────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────┐
│  MEDALLION ARCHITECTURE                  │
│  ┌────────┐  ┌────────┐  ┌────────┐    │
│  │ BRONZE │→ │ SILVER │→ │  GOLD  │    │
│  │  Raw   │  │Cleaned │  │  Star  │    │
│  └────────┘  └────────┘  └────────┘    │
└──────────────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────┐
│  ORCHESTRATION                           │
│       ┌─────────────────┐                │
│       │   Scheduler     │                │
│       └─────────────────┘                │
└──────────────────────────────────────────┘

Dimensions:
- Canvas width: ~1200px
- Zone height: 200-250px each
- Vertical spacing: 60px between zones
- Internal padding: 40px
```

**Coordinates:**
```javascript
const layers = {
  ingestion: { x: 60, y: 80, width: 1100, height: 200 },
  medallion: { x: 60, y: 340, width: 1100, height: 220 },
  orchestration: { x: 60, y: 620, width: 1100, height: 160 }
};
```

---

### Template 3: Hub-and-Spoke (Multi-Agent)

**Use for:** AI agent orchestration, microservices

```
                  ┌─────────────────┐
                  │                 │
           ┌─────→│  ORCHESTRATOR   │←─────┐
           │      │   (Central Hub) │      │
           │      └─────────────────┘      │
           │               ↓               │
           │               ↓               │
    ┌──────┴──────┐  ┌──────────┐  ┌─────┴──────┐
    │   Agent 1   │  │ Agent 2  │  │  Agent 3   │
    │  Inventory  │  │  Sales   │  │   Supply   │
    └─────────────┘  └──────────┘  └────────────┘
           │               │               │
           └───────────────┼───────────────┘
                           ↓
                  ┌─────────────────┐
                  │   MCP / Data    │
                  │   Bridge Layer  │
                  └─────────────────┘

Dimensions:
- Canvas: 1400px × 900px
- Orchestrator: 260×100 (center at x:570, y:85)
- Agents: 150×70 each
- Radial spacing: 200px from center
- Bottom layer: Full width
```

**Coordinates:**
```javascript
const hubSpoke = {
  orchestrator: { x: 570, y: 85, width: 260, height: 100 },
  agent1: { x: 350, y: 230, width: 150, height: 70 },
  agent2: { x: 625, y: 230, width: 150, height: 70 },
  agent3: { x: 900, y: 230, width: 150, height: 70 },
  mcp: { x: 400, y: 365, width: 600, height: 90 }
};
```

---

### Template 4: Grid Layout (Multiple Services)

**Use for:** Technology stack, service catalog

```
┌────────────────────────────────────────────┐
│  GCP SERVICES                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │ Service 1│  │ Service 2│  │ Service 3││
│  └──────────┘  └──────────┘  └──────────┘│
│                                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │ Service 4│  │ Service 5│  │ Service 6││
│  └──────────┘  └──────────┘  └──────────┘│
└────────────────────────────────────────────┘

Dimensions:
- Grid: 3 columns × N rows
- Cell size: 200×100
- Horizontal spacing: 50px
- Vertical spacing: 40px
- Zone padding: 40px
```

**Coordinates:**
```javascript
function gridPosition(row, col, cellWidth=200, cellHeight=100,
                      spacingX=50, spacingY=40, offsetX=60, offsetY=120) {
  return {
    x: offsetX + col * (cellWidth + spacingX),
    y: offsetY + row * (cellHeight + spacingY),
    width: cellWidth,
    height: cellHeight
  };
}
```

---

### Template 5: Star Schema / Entity-Relationship (Multi-Target)

**Use for:** Dimensional models, star schemas, ER diagrams with many-to-many connections

**Problem this solves:** When N source elements each connect to M target elements,
arrows WILL overlap and become unreadable unless routed through dedicated channels.

```
┌─────────────────────────────────────────────────────────────────────┐
│  ROW 1: DIMENSIONS                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ dim_date │  │dim_product│  │ dim_unit │  │dim_region│          │
│  └────┬─┬───┘  └────┬─┬───┘  └────┬─┬───┘  └────┬─┬───┘          │
│       │ │           │ │           │ │           │ │               │
│  ═════╪═╪═══════════╪═╪═══════════╪═╪═══════════╪═╪═══ LANE 1 ═══ │
│       │ └───────────│─│───────────│─│───────────│─│──→ fact_stock │
│  ═════╪═════════════╪═╪═══════════╪═╪═══════════╪═════ LANE 2 ═══ │
│       │             │ └───────────│─│──→        │                  │
│  ═════╪═════════════╪═════════════╪═╪═══════════╪═════ LANE 3 ═══ │
│       │             │             │ └──→        │                  │
│  ═════╪═════════════╪═════════════╪═════════════╪═════ LANE 4 ═══ │
│       └──→          └──→          └──→          └──→              │
│                                                                     │
│  ROW 2: FACTS                                                       │
│  ┌──────────────────────┐          ┌──────────────────────┐        │
│  │     fact_sales       │          │     fact_stock       │        │
│  └──────────────────────┘          └──────────────────────┘        │
└─────────────────────────────────────────────────────────────────────┘
```

**Key Concept: Routing Channels**

Between source row and target row, allocate a **routing channel** with dedicated
horizontal lanes. Each arrow gets its own lane to prevent overlap.

```
Routing Channel Height = num_lanes × lane_spacing + 2 × channel_padding
  - lane_spacing: 20px between lanes
  - channel_padding: 15px top and bottom
  - num_lanes: number of unique arrow paths that need distinct horizontal segments
```

**Coordinates (4 dimensions → 2 facts example):**

```javascript
const starSchema = {
  // Canvas: 1200×700 (landscape for star schema)
  canvas: { width: 1200, height: 700 },
  margin: 40,

  // Row 1: Dimensions (all same Y, evenly spaced)
  dimensions: {
    y: 85,
    height: 110,
    items: [
      { id: "dim_date",    x: 40,  width: 240 },
      { id: "dim_product", x: 310, width: 240 },
      { id: "dim_unit",    x: 580, width: 240 },
      { id: "dim_region",  x: 850, width: 240 }
    ]
  },

  // Routing Channel: between rows
  routingChannel: {
    top: 195 + 15,       // dim bottom + padding
    laneSpacing: 20,     // 20px between each lane
    // Assign each cross-connection to a separate lane
    // Rule: nearby connections get LOWER lanes (closer to target)
    //        distant connections get HIGHER lanes (closer to source)
    lanes: {
      // Lane 0 (lowest, closest to facts): direct/nearby connections
      // Lane 1: medium distance
      // Lane 2: far connections
      // Lane 3 (highest, closest to dims): very far cross-connections
    }
  },

  // Row 2: Facts (positioned BELOW routing channel)
  facts: {
    y: 310,              // routingChannel.top + (num_lanes × 20) + 15
    height: 150,
    items: [
      { id: "fact_sales", x: 80,  width: 340 },
      { id: "fact_stock", x: 580, width: 340 }
    ]
  }
};
```

**Arrow Lane Assignment Strategy:**

When dimensions connect to multiple facts, assign lanes based on **connection distance**:

| Arrow | From → To | Distance | Lane | Y-offset |
|-------|-----------|----------|------|----------|
| dim_date → fact_sales | nearby | short | 3 (bottom) | +60px |
| dim_product → fact_sales | nearby | short | 3 (bottom) | +60px |
| dim_unit → fact_stock | nearby | short | 3 (bottom) | +60px |
| dim_region → fact_stock | nearby | short | 3 (bottom) | +60px |
| dim_product → fact_stock | medium | medium | 2 | +40px |
| dim_unit → fact_sales | medium | medium | 2 | +40px |
| dim_date → fact_stock | far | long | 1 (top) | +20px |
| dim_region → fact_sales | far | long | 1 (top) | +20px |

**Rules:**
1. **Short connections** (source directly above or near target): use straight vertical arrows, NO L-shape needed
2. **Medium connections** (1-2 elements away): use L-shape with dedicated lane
3. **Long connections** (crossing 3+ elements): use L-shape with HIGHEST lane (furthest from other arrows)
4. **Each horizontal segment must be on a UNIQUE Y-coordinate** — never share horizontal lanes
5. **Labels** placed at the midpoint of the horizontal segment, 15px ABOVE the lane
6. **Focus values** on bindings: distribute evenly along the edge to spread connection points
   - For a box with 2 outgoing arrows: focus = -0.4 and +0.4
   - For a box with 1 arrow: focus = 0

**Focus Distribution Formula:**
```javascript
// When N arrows connect to the same edge of a rectangle:
function distributeFocus(numConnections) {
  if (numConnections === 1) return [0];
  const step = 1.2 / (numConnections - 1);  // spread across -0.6 to +0.6
  return Array.from({length: numConnections}, (_, i) => -0.6 + i * step);
}
```

---

## Element Sizing Standards

### Shape Sizes

| Type | Small | Medium | Large | Extra Large |
|------|-------|--------|-------|-------------|
| **Width** | 200 | 320 | 450 | 650 |
| **Height** | 90 | 130 | 200 | 320 |

**Usage:**
- **Small:** Individual components, agents, services
- **Medium:** Main services, databases, major components
- **Large:** Zone containers, major systems
- **Extra Large:** Background zones, major sections

### Text Sizes

| Purpose | Font Size | Line Height |
|---------|-----------|-------------|
| **Zone titles** | 28px | 35px |
| **Section headers** | 20-22px | 28px |
| **Component labels** | 16-18px | 22px |
| **Annotations** | 12-14px | 18px |

### Icon Sizes

| Context | Dimensions |
|---------|------------|
| **Inline icons** | 30×30 |
| **Component icons** | 50×50 |
| **Hero icons** | 80×80 |

---

## Spacing Guidelines

### Padding

```
Element Padding:
- Zone padding (internal): 40-50px
- Component padding (text inside box): 10-20px
- Section header margin-top: 15px
```

### Spacing

```
Element Spacing:
- Between major zones: 100-120px
- Between components in same zone: 40-60px
- Between related components: 20-30px
- Arrow clearance from text: 20px minimum
```

### Margins

```
Canvas Margins:
- Top: 20px
- Left/Right: 20px
- Bottom: 40px
- Between layers: 60px
```

---

## Arrow Patterns

### Straight Horizontal Arrow

```javascript
{
  type: "arrow",
  x: startX,
  y: centerY,
  width: distance,
  height: 0,
  points: [[0, 0], [distance, 0]],
  startBinding: { elementId: "source", focus: 0, gap: 1 },
  endBinding: { elementId: "target", focus: 0, gap: 1 }
}
```

### Straight Vertical Arrow

```javascript
{
  type: "arrow",
  x: centerX,
  y: startY,
  width: 0,
  height: distance,
  points: [[0, 0], [0, distance]],
  startBinding: { elementId: "source", focus: 0, gap: 1 },
  endBinding: { elementId: "target", focus: 0, gap: 1 }
}
```

### L-Shaped Arrow (Down then Right)

```javascript
{
  type: "arrow",
  x: startX,
  y: startY,
  width: horizontalDistance,
  height: verticalDistance,
  points: [
    [0, 0],                           // Start
    [0, verticalDistance / 2],        // Down
    [horizontalDistance, verticalDistance / 2], // Right
    [horizontalDistance, verticalDistance]      // End
  ],
  startBinding: { elementId: "source", focus: 0, gap: 1 },
  endBinding: { elementId: "target", focus: 0, gap: 1 }
}
```

### Return Arrow (Feedback Loop)

```javascript
{
  type: "arrow",
  x: startX,
  y: startY,
  strokeStyle: "dashed",  // Distinguish from forward flow
  points: [
    [0, 0],
    [0, -50],              // Up
    [-200, -50],           // Left
    [-200, 0]              // Down to target
  ],
  endArrowhead: "arrow",
  startArrowhead: null
}
```

---

## Zone Organization

### Background Zone Pattern

Always create zones in this order:

1. **Background zone** (rectangle with light fill)
2. **Zone title** (text at top)
3. **Internal components** (shapes and arrows)
4. **Component labels** (text on top)

```javascript
const zone = [
  // 1. Background
  {
    id: "bg_zone_name",
    type: "rectangle",
    x: 20,
    y: 20,
    width: 600,
    height: 700,
    strokeColor: "#4285f4",
    backgroundColor: "#e8f0fe",
    opacity: 100,
    // ... other properties
  },
  // 2. Title
  {
    id: "label_zone_name",
    type: "text",
    x: 40,
    y: 35,
    text: "ZONE TITLE",
    fontSize: 28,
    // ... other properties
  },
  // 3. Components
  // ... component rectangles, ellipses, etc.
  // 4. Labels
  // ... text labels for components
];
```

---

## Anti-Patterns (Avoid)

### ❌ Common Mistakes

**Overlapping Text:**
```
BAD:
  Component
    Label
  [overlaps with]
  Arrow Label

GOOD:
  Component
    Label

  Arrow Label (20px below)
```

**Unaligned Elements:**
```
BAD:
  Box1 at y: 103
  Box2 at y: 108
  Box3 at y: 97

GOOD:
  Box1 at y: 100
  Box2 at y: 100
  Box3 at y: 100
```

**Inconsistent Spacing:**
```
BAD:
  A ← 30px → B ← 80px → C ← 15px → D

GOOD:
  A ← 50px → B ← 50px → C ← 50px → D
```

**Too Many Connections:**
```
BAD:
  [Agent A] ←→←→←→ [Agent B]
           ↓↑↓↑
  [Agent C] ←→←→←→ [Agent D]

GOOD:
  [Agent A] → [Orchestrator] → [Agent B]
                    ↓
  [Agent C] ← [Orchestrator] ← [Agent D]
```

---

## Responsive Considerations

### Canvas Size Recommendations

| Diagram Type | Width | Height | Aspect Ratio |
|--------------|-------|--------|--------------|
| **Simple (1-2 zones)** | 1000-1400px | 600-800px | 16:9 |
| **Complex (3-4 zones)** | 1800-2200px | 700-900px | 2:1 |
| **Vertical flow** | 1000-1400px | 1200-2000px | 3:4 |
| **Complete mega** | 2500-3500px | 1500-2500px | 3:2 |

### Scaling Rules

When diagram needs to fit smaller space:

1. **Reduce spacing first** (from 60px to 40px between elements)
2. **Shrink zones proportionally** (maintain aspect ratios)
3. **Reduce font sizes last** (minimum 12px for readability)

---

## Layout Checklist

Before finalizing diagram layout:

- [ ] All elements aligned to 10px grid
- [ ] No overlapping text or elements
- [ ] Minimum 40px spacing between components
- [ ] Zone padding is 40-50px on all sides
- [ ] Arrows have 20px clearance from text
- [ ] Related elements have consistent sizes
- [ ] Consistent spacing throughout diagram
- [ ] Visual hierarchy is clear (background → shapes → text)
- [ ] Color coding is consistent
- [ ] Canvas size accommodates all elements with margin

---

## Layout Helper Functions

### Calculate Center Position

```javascript
function centerElement(container, element) {
  return {
    x: container.x + (container.width - element.width) / 2,
    y: container.y + (container.height - element.height) / 2
  };
}
```

### Distribute Horizontally

```javascript
function distributeHorizontal(elements, startX, startY, spacing) {
  let x = startX;
  return elements.map(el => {
    const pos = { ...el, x, y: startY };
    x += el.width + spacing;
    return pos;
  });
}
```

### Calculate Arrow Points

```javascript
function connectElements(source, target, style = "direct") {
  const sourceCenter = {
    x: source.x + source.width / 2,
    y: source.y + source.height / 2
  };
  const targetCenter = {
    x: target.x + target.width / 2,
    y: target.y + target.height / 2
  };

  if (style === "direct") {
    return {
      x: source.x + source.width,
      y: sourceCenter.y,
      points: [
        [0, 0],
        [target.x - (source.x + source.width), 0]
      ]
    };
  }
  // Add more styles as needed
}
```

---

## Example: Complete 3-Zone Layout

See `examples/alt2_handcrafted.md` for full annotated example.

**Quick Reference:**
```javascript
const diagram = {
  canvas: { width: 2100, height: 750 },
  zones: {
    onprem: { x: 20, y: 20, w: 380, h: 700 },
    gcp: { x: 440, y: 20, w: 700, h: 700 },
    agentic: { x: 1180, y: 20, w: 520, h: 700 },
    business: { x: 1740, y: 20, w: 310, h: 700 }
  },
  spacing: {
    betweenZones: 40,
    betweenComponents: 50,
    padding: 40
  }
};
```

---

**Last Updated:** 2026-01-30
**Version:** 1.0
