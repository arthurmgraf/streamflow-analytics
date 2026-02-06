# Excalidraw Style Guide

## Overview

This guide defines the visual identity for all generated diagrams: colors, typography, visual hierarchy, and design patterns. Follow these guidelines to create clean, professional, and didactic visualizations.

---

## IMPORTANT: v3 Clean & Technical is the Production Standard

As of 2026-01-31, the **v3 Clean & Technical** style is the default for all diagrams.

**Key v3 differences from the generic style below:**
- **Typography:** fontFamily: 3 (Monospace) for ALL text, not fontFamily: 1 (Virgil)
- **Title:** 32px monospace
- **Body text:** 10-11px monospace (not 16px)
- **Section headers:** 14-20px monospace
- **Information density:** >= 80% per component box
- **Spacing:** 15-20px between components (tighter than generic 40-60px)
- **Colors:** Data Sources #fa5252, Ingestion #FBBC04, Warehouse #4285F4, BI #2f9e44

**Full v3 specification:** See `docs/DIAGRAMS_STYLE_GUIDE.md`
**Logo-flow variant:** See `v3-logo-flow-style.md`

The generic style guide below is retained as reference but should NOT be used directly.
Use v3 specs from the documents above.

---

## Design Philosophy

### Core Values

1. **Clarity over Decoration** - Every visual element serves a purpose
2. **Consistency** - Predictable patterns aid comprehension
3. **Professionalism** - Suitable for portfolio and client presentations
4. **Didactic Focus** - Optimized for teaching and explanation

### Visual Characteristics

- ✅ **Clean and minimalist** - No unnecessary embellishments
- ✅ **High contrast** - Readable on any display
- ✅ **Color-coded** - Semantic meaning through color
- ✅ **Generous whitespace** - Room to breathe
- ✅ **Consistent shapes** - Rectangles for services, ellipses for agents, diamonds for decision points

---

## Color Palette

### Primary Zone Colors

Used for major architectural zones and categories.

| Zone/Category | Stroke | Background | RGB (Stroke) | RGB (BG) | Use Case |
|---------------|--------|------------|--------------|----------|----------|
| **On-Premise** | `#4a5568` | `#f8f9fa` | 74,85,104 | 248,249,250 | Legacy systems, local infrastructure |
| **GCP Cloud** | `#4285f4` | `#e8f0fe` | 66,133,244 | 232,240,254 | Google Cloud Platform services |
| **Agentic AI** | `#7c3aed` | `#f3e8ff` | 124,58,237 | 243,232,255 | AI agents, orchestration, ML |
| **Business** | `#ef4444` | `#fee2e2` | 239,68,68 | 254,226,226 | Business outcomes, KPIs, value |

### Data Layer Colors (Medallion)

| Layer | Stroke | Background | RGB (Stroke) | RGB (BG) | Description |
|-------|--------|------------|--------------|----------|-------------|
| **Bronze** | `#e65100` | `#f9ab00` | 230,81,0 | 249,171,0 | Raw ingestion, unvalidated |
| **Silver** | `#616161` | `#c0c0c0` | 97,97,97 | 192,192,192 | Cleaned, validated, conformed |
| **Gold** | `#f57f17` | `#ffd700` | 245,127,23 | 255,215,0 | Analytics-ready, star schema |
| **Transformation** | `#0f9d58` | `#e6f4ea` | 15,157,88 | 230,244,234 | Transformation processes |

### Service/Component Colors

| Component Type | Stroke | Background | Usage |
|----------------|--------|------------|-------|
| **Storage** | `#4285f4` | `#bbdefb` | GCS, S3, data lakes |
| **Compute** | `#4285f4` | `#bbdefb` | Cloud Functions, VMs, containers |
| **Database** | `#0f9d58` | `#c8e6c9` | BigQuery, PostgreSQL, NoSQL |
| **AI/ML** | `#7c3aed` | `#a855f7` | Individual agents, models |
| **Context/KB** | `#d97706` | `#f59e0b` | MCP, knowledge bases, RAG |
| **Message Queue** | `#f59e0b` | `#fef3c7` | Pub/Sub, Kafka, queues |
| **Orchestration** | `#0f9d58` | `#c8e6c9` | Schedulers, workflow engines |

### Text Colors

| Purpose | Color | RGB | Usage |
|---------|-------|-----|-------|
| **Primary text** | `#1a73e8` | 26,115,232 | Main labels, service names |
| **Secondary text** | `#4a5568` | 74,85,104 | Annotations, descriptions |
| **Zone headers** | Zone stroke color | - | Match parent zone |
| **Light text on dark** | `#ffffff` | 255,255,255 | Text on dark backgrounds |
| **Muted text** | `#718096` | 113,128,150 | Notes, less important info |

### Accent Colors

| Purpose | Color | RGB | Usage |
|---------|-------|-----|-------|
| **Success** | `#10b981` | 16,185,129 | Successful operations |
| **Warning** | `#f59e0b` | 245,158,11 | Attention needed |
| **Error** | `#ef4444` | 239,68,68 | Failures, problems |
| **Info** | `#3b82f6` | 59,130,246 | Information, tips |

---

## Typography

### Font Families

Excalidraw supports three font families:

| Family | Code | Usage |
|--------|------|-------|
| **Normal (Virgil)** | `1` | Default for all text - clean, readable |
| **Serif (Helvetica)** | `2` | Not used - avoid |
| **Monospace (Cascadia)** | `3` | Code snippets, technical identifiers (rare) |

**Standard:** Use `fontFamily: 1` (Normal/Virgil) for all text.

### Font Sizes

| Purpose | Size | Line Height | Usage |
|---------|------|-------------|-------|
| **Diagram title** | `32px` | `42px` | Main diagram title (if present) |
| **Zone headers** | `24px` | `32px` | Major section titles (REDUCED for cleaner look) |
| **Section headers** | `18-20px` | `26px` | Sub-section titles |
| **Component labels** | `14-16px` | `20px` | Service names, component names (REDUCED) |
| **Descriptions** | `12-14px` | `18px` | Multi-line descriptions |
| **Annotations** | `11px` | `16px` | Small notes, metadata |

### Text Alignment

| Element Type | Alignment | Vertical Align |
|--------------|-----------|----------------|
| **Zone headers** | `center` or `left` | `top` |
| **Component labels** | `center` | `top` |
| **Descriptions** | `center` | `top` |
| **Annotations** | `left` or `center` | `top` |
| **Arrow labels** | `center` | `top` |

### Text Width Guidelines

| Text Type | Max Width | Word Wrap |
|-----------|-----------|-----------|
| **Single-line labels** | 200px | No |
| **Multi-line labels** | 250px | Yes (use `\n`) |
| **Descriptions** | 280px | Yes (use `\n`) |
| **Annotations** | 240px | Yes (use `\n`) |

---

## Shape Styles

### Rectangles

**Primary usage:** Services, databases, components, zone backgrounds

```javascript
{
  type: "rectangle",
  strokeWidth: 2,           // Primary elements
  strokeStyle: "solid",     // Always solid
  fillStyle: "solid",       // Always solid
  roughness: 0,             // Clean, no hand-drawn effect
  opacity: 100,             // Fully opaque
  roundness: { type: 3 }    // Rounded corners
}
```

**Variations:**
- **Zone backgrounds:** `strokeWidth: 2`, `opacity: 100`
- **Primary components:** `strokeWidth: 2`, `opacity: 100`
- **Secondary components:** `strokeWidth: 1`, `opacity: 100`

### Ellipses

**Primary usage:** Orchestrators, central hubs, processes

```javascript
{
  type: "ellipse",
  strokeWidth: 2,
  strokeStyle: "solid",
  fillStyle: "solid",
  roughness: 0,
  opacity: 100,
  roundness: { type: 2 }    // Natural ellipse
}
```

**When to use:**
- Central orchestrators (hub-and-spoke)
- Agent coordinators
- Circular processes

### Diamonds

**Primary usage:** Decision points, schedulers, conditional logic

```javascript
{
  type: "diamond",
  strokeWidth: 2,
  strokeStyle: "solid",
  fillStyle: "solid",
  roughness: 0,
  opacity: 100,
  roundness: { type: 2 }
}
```

**When to use:**
- Schedulers and cron jobs
- Decision points in flows
- Conditional branches

### Lines and Arrows

**Primary usage:** Data flow, relationships, connections

```javascript
{
  type: "arrow",
  strokeWidth: 2,           // Primary flows
  strokeStyle: "solid",     // Main flows
  roughness: 0,
  opacity: 100,
  roundness: { type: 2 },
  endArrowhead: "arrow",
  startArrowhead: null
}
```

**Variations:**
| Flow Type | Stroke Width | Stroke Style | Usage |
|-----------|--------------|--------------|-------|
| **Primary data flow** | `3` | `solid` | Main pipeline flows |
| **Secondary flow** | `2` | `solid` | Component connections |
| **Metadata/config** | `2` | `dashed` | Configuration, metadata sync |
| **Feedback loop** | `1` | `dashed` | Return paths, feedback |
| **Trigger/event** | `2` | `solid` | Event-driven triggers |

---

## Visual Hierarchy

### Layer Order (Z-Index)

Elements render in array order. Follow this sequence:

1. **Zone backgrounds** (largest rectangles, lowest z-index)
2. **Zone titles** (text on zone backgrounds)
3. **Sub-zones** (nested containers)
4. **Connecting arrows** (data flows)
5. **Component shapes** (rectangles, ellipses, diamonds)
6. **Component labels** (text on top of shapes)
7. **Annotations** (floating text, notes)

### Size Hierarchy

| Level | Width | Height | Usage |
|-------|-------|--------|-------|
| **Canvas** | 1000-3500px | 600-2500px | Total diagram size |
| **Major zones** | 300-700px | 300-700px | Architectural zones |
| **Sub-zones** | 200-600px | 150-220px | Grouped components |
| **Large components** | 250-380px | 100-150px | Major services |
| **Medium components** | 150-250px | 70-100px | Standard services |
| **Small components** | 100-150px | 50-70px | Utilities, helpers |

### Opacity Hierarchy

| Element | Opacity | Purpose |
|---------|---------|---------|
| **Primary elements** | `100` | Main components, active elements |
| **Annotations** | `70-80` | Supporting text, descriptions |
| **Background patterns** | `50-60` | Subtle visual guides |
| **Disabled/inactive** | `40-50` | Out of scope, future state |

---

## Spacing Standards

### Padding (Internal)

| Element | Padding | Description |
|---------|---------|-------------|
| **Zone containers** | `60-80px` | Space between zone border and contents (INCREASED) |
| **Component boxes** | `15-25px` | Space between box border and text (INCREASED) |
| **Text blocks** | `10-15px` | Margin around multi-line text |

### Spacing (External)

| Relationship | Spacing | Description |
|--------------|---------|-------------|
| **Between major zones** | `150-200px` | Large architectural separations (INCREASED) |
| **Between sub-zones** | `80-100px` | Related sections (INCREASED) |
| **Between components** | `60-80px` | Independent components (INCREASED) |
| **Between related items** | `40-50px` | Grouped components (INCREASED) |
| **Arrow clearance** | `30px` | Space between arrows and text (INCREASED) |

### Margins (Canvas)

| Edge | Margin | Description |
|------|--------|-------------|
| **Top** | `20px` | Canvas top margin |
| **Left/Right** | `20px` | Canvas side margins |
| **Bottom** | `40px` | Canvas bottom margin |
| **Inter-layer** | `60px` | Between horizontal layers |

---

## Icon Guidelines

### Icon Sizing

| Context | Size | Usage |
|---------|------|-------|
| **Inline icons** | `30×30px` | Small decorative icons |
| **Component icons** | `50×50px` | Service/tech logos |
| **Hero icons** | `80×80px` | Major feature highlights |

### Icon Placement

- **Within components:** Center horizontally, top 1/3 vertically
- **Next to labels:** Left-aligned, vertically centered with text
- **Standalone:** Centered in designated area

### Icon Style

- **Format:** SVG or base64-encoded PNG
- **Colors:** Match component color scheme or grayscale
- **Opacity:** 60-100% depending on emphasis
- **Background:** Transparent

---

## Arrow Styling

### Arrow Types

| Type | Stroke Width | Stroke Style | End Arrowhead | Usage |
|------|--------------|--------------|---------------|-------|
| **Data flow** | `3px` | `solid` | `arrow` | Primary data movement |
| **API calls** | `2px` | `solid` | `arrow` | Service-to-service |
| **Config/metadata** | `2px` | `dashed` | `arrow` | Configuration sync |
| **Feedback** | `1px` | `dashed` | `arrow` | Return paths |
| **Trigger** | `2px` | `solid` | `arrow` | Event triggers |

### Arrow Labels

Position arrow labels:
- **Above arrow:** Short descriptions ("Daily Upload", "Trigger")
- **Below arrow:** Technical details (rarely used)
- **On arrow path:** Never (overlaps make it unreadable)

**Label styling:**
```javascript
{
  type: "text",
  fontSize: 12,
  fontFamily: 1,
  textAlign: "center",
  strokeColor: "#4a5568",  // Muted
  opacity: 80              // Slightly transparent
}
```

---

## Anti-Patterns (Avoid)

### ❌ Don't Do This

**Over-styling:**
```javascript
// BAD: Too many effects
{
  roughness: 2,           // Hand-drawn effect (avoid)
  strokeStyle: "dotted",  // Hard to see
  opacity: 30,            // Too transparent
  strokeWidth: 0.5        // Too thin
}
```

**Inconsistent colors:**
```javascript
// BAD: Random colors
Zone1: { backgroundColor: "#ff0000" }  // Random red
Zone2: { backgroundColor: "#00ff00" }  // Random green
Zone3: { backgroundColor: "#0000ff" }  // Random blue

// GOOD: Semantic colors
Zone1: { backgroundColor: "#f8f9fa" }  // On-premise (gray)
Zone2: { backgroundColor: "#e8f0fe" }  // GCP (blue)
Zone3: { backgroundColor: "#f3e8ff" }  // AI (purple)
```

**Overlapping text:**
```javascript
// BAD: Text overlaps
Component: { x: 100, y: 100 }
Label: { x: 105, y: 110 }      // Overlaps component border
Arrow: { y: 115 }              // Overlaps label

// GOOD: Clear separation
Component: { x: 100, y: 100 }
Label: { x: 120, y: 120 }      // Inside component, centered
Arrow: { y: 220 }              // 20px below component
```

---

## Accessibility

### Color Blindness Considerations

- ✅ Don't rely solely on color to convey meaning
- ✅ Use shapes + colors together
- ✅ Ensure high contrast (4.5:1 minimum)
- ✅ Test with grayscale view

### Contrast Ratios

| Combination | Ratio | Pass |
|-------------|-------|------|
| `#1a73e8` on `#ffffff` | 4.8:1 | ✅ WCAG AA |
| `#4a5568` on `#f8f9fa` | 5.2:1 | ✅ WCAG AA |
| `#ffffff` on `#7c3aed` | 6.1:1 | ✅ WCAG AA |
| `#3e2723` on `#ffd700` | 8.3:1 | ✅ WCAG AAA |

### Font Size Minimums

- **Minimum readable size:** 12px
- **Preferred minimum:** 14px
- **Body text:** 16px

---

## Style Checklist

Before finalizing diagram style:

- [ ] All colors from approved palette
- [ ] Consistent stroke widths within diagram
- [ ] `roughness: 0` for all elements (clean look)
- [ ] `roundness: {type: 3}` for rectangles
- [ ] Font sizes between 12-32px
- [ ] Text color has sufficient contrast
- [ ] No hand-drawn effects (roughness > 0)
- [ ] Consistent opacity levels
- [ ] Zone backgrounds lighter than components
- [ ] Semantic color usage (not random)

---

## Quick Reference

### Default Component Style

```javascript
const defaultComponent = {
  strokeWidth: 2,
  strokeStyle: "solid",
  fillStyle: "solid",
  roughness: 0,
  opacity: 100,
  roundness: { type: 3 }
};
```

### Default Text Style

```javascript
const defaultText = {
  fontSize: 16,
  fontFamily: 1,
  textAlign: "center",
  verticalAlign: "top",
  strokeColor: "#1a73e8",
  backgroundColor: "transparent"
};
```

### Default Arrow Style

```javascript
const defaultArrow = {
  strokeWidth: 2,
  strokeStyle: "solid",
  roughness: 0,
  opacity: 100,
  roundness: { type: 2 },
  startArrowhead: null,
  endArrowhead: "arrow"
};
```

---

**Last Updated:** 2026-01-30
**Version:** 1.0
