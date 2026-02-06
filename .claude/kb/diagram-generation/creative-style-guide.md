> **DEPRECATED (2026-01-31):** This creative style guide is no longer in use.
> The production standard is **v3 Clean & Technical**.
> See: `docs/DIAGRAMS_STYLE_GUIDE.md` and `v3-logo-flow-style.md`

---

# Creative Style Guide - Visual Storytelling

## Overview

This guide defines the **creative, illustrative style** for diagrams inspired by presentation/infographic design rather than traditional technical diagrams.

**Philosophy:** Visual storytelling over technical precision. Make it engaging, colorful, and memorable.

---

## Design Principles

### 1. **Visual Narrative**
- Tell a story with the diagram
- Use visual metaphors and illustrations
- Make it engaging like an infographic
- Focus on concepts, not just components

### 2. **Bold Visual Elements**
- Large, colorful icons and illustrations
- Vibrant color accents (red, orange, yellow)
- Varied shapes (circles, rounded rectangles, badges)
- Visual hierarchy through size and color

### 3. **Simple, Direct Connections**
- **Straight arrows only** (no curves unless necessary)
- Arrows point directly to target centers
- Use arrow colors to indicate flow type
- Minimal points per arrow (2-3 max)

### 4. **Whitespace & Breathing Room**
- Even MORE spacing than standard diagrams
- Isolated "scenes" or sections
- Clear visual separation between concepts

---

## Creative Color Palette

### Vibrant Accent Colors

| Color | Hex | RGB | Usage |
|-------|-----|-----|-------|
| **Alert Red** | `#ef4444` | 239,68,68 | Important concepts, warnings |
| **Energetic Orange** | `#f97316` | 249,115,22 | Key processes, highlights |
| **Sunny Yellow** | `#fbbf24` | 251,191,36 | Success, completion |
| **Tech Blue** | `#3b82f6` | 59,130,246 | Technology, data |
| **Growth Green** | `#10b981` | 16,185,129 | Progress, validation |
| **Creative Purple** | `#8b5cf6` | 139,92,246 | AI, intelligence |

### Pastel Backgrounds (for contrast)

| Color | Hex | Usage |
|-------|-----|-------|
| Light Gray | `#f3f4f6` | Neutral backgrounds |
| Soft Blue | `#dbeafe` | Tech sections |
| Soft Purple | `#ede9fe` | AI sections |
| Soft Green | `#d1fae5` | Success states |
| Soft Orange | `#fed7aa` | Process flows |

---

## Element Styles

### Large Visual Icons (Circles)

Use **ellipses** instead of rectangles for key concepts:

```javascript
{
  type: "ellipse",
  width: 140,
  height: 140,
  strokeColor: "#ef4444",
  backgroundColor: "#fee2e2",
  strokeWidth: 3
}
```

**When to use:**
- Main concepts or stages
- Important services
- Hero elements
- Process nodes

### Badges / Labels

Small rounded rectangles for labels:

```javascript
{
  type: "rectangle",
  width: 120,
  height: 40,
  strokeColor: "#f97316",
  backgroundColor: "#ffffff",
  strokeWidth: 2,
  roundness: { type: 3 }
}
```

### Large Emoji Icons

Use emojis as LARGE visual elements (not small annotations):

**Size:** 48-64px font size
**Placement:** Center of circles or standalone

Examples:
- 📊 **Data/Analytics** - Size 56px
- ☁️ **Cloud/Storage** - Size 56px
- ⚡ **Processing** - Size 56px
- 🎯 **Business Goal** - Size 56px
- 🤖 **AI/Automation** - Size 56px

---

## Arrow Styles - SIMPLE & DIRECT

### Rule: Maximum 2 Points Per Arrow

**Good - Straight line:**
```javascript
{
  points: [[0, 0], [300, 0]]  // Horizontal
}
```

**Good - One corner:**
```javascript
{
  points: [[0, 0], [0, 100], [300, 100]]  // L-shape
}
```

**Bad - Too many curves:**
```javascript
{
  points: [[0, 0], [50, 20], [100, 80], [150, 100], [300, 120]]  // ❌ NO
}
```

### Arrow Targeting

**Always point to element centers:**

```javascript
// Calculate target center
const targetCenter = {
  x: target.x + target.width / 2,
  y: target.y + target.height / 2
};

// Arrow ends at center
arrow.endBinding = {
  elementId: target.id,
  focus: 0,  // 0 = center
  gap: 10
};
```

### Arrow Colors by Purpose

| Purpose | Color | Width | Style |
|---------|-------|-------|-------|
| **Main data flow** | `#3b82f6` (blue) | 4px | solid |
| **Important process** | `#ef4444` (red) | 4px | solid |
| **Success/completion** | `#10b981` (green) | 3px | solid |
| **Trigger/event** | `#f97316` (orange) | 3px | solid |
| **Secondary flow** | `#6b7280` (gray) | 2px | solid |
| **Metadata/config** | `#9ca3af` (light gray) | 2px | dashed |

---

## Layout Patterns - Creative

### Pattern 1: Hero Concept (Top)

```
        ┌─────────────┐
        │  🎯 GOAL    │  ← Large circle/ellipse
        └─────────────┘
               ↓ (straight arrow)
    ┌──────────────────────┐
    │                      │
    │   Main Content       │
    │                      │
    └──────────────────────┘
```

### Pattern 2: Process Flow (Horizontal)

```
  ⭕ Step 1  →  ⭕ Step 2  →  ⭕ Step 3  →  ⭕ Result
 (circle)      (circle)      (circle)      (circle)
  140×140       140×140       140×140       140×140
```

**Spacing:** 180-200px between circles

### Pattern 3: Comparison / Before-After

```
┌────────────────┐              ┌────────────────┐
│   BEFORE       │              │    AFTER       │
│                │      VS      │                │
│  [Old way]     │              │  [New way]     │
└────────────────┘              └────────────────┘
```

### Pattern 4: Layered Stack (Vertical)

```
┌──────────────────────────────────┐
│      TOP LAYER (colored)         │
├──────────────────────────────────┤
│      MIDDLE LAYER (different)    │
├──────────────────────────────────┤
│      BOTTOM LAYER (different)    │
└──────────────────────────────────┘
```

**Use different background colors for each layer**

---

## Visual Hierarchy

### Size Scale

| Element | Width | Height | Use |
|---------|-------|--------|-----|
| **Hero icon/circle** | 140-160px | 140-160px | Main concepts |
| **Process node** | 120-140px | 120-140px | Steps |
| **Service box** | 200-280px | 100-140px | Services |
| **Badge/label** | 100-150px | 35-50px | Small labels |
| **Section container** | 600-1000px | 300-500px | Groups |

### Font Sizes - Bold & Clear

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| **Hero title** | 32-36px | Bold | Accent color |
| **Section title** | 24-28px | Bold | Dark gray |
| **Component label** | 16-18px | Normal | Dark |
| **Description** | 14px | Normal | Medium gray |
| **Small annotation** | 12px | Normal | Light gray |

---

## Creative Elements

### 1. Circular Badges for Numbers

```javascript
{
  type: "ellipse",
  width: 50,
  height: 50,
  backgroundColor: "#ef4444",
  strokeColor: "#dc2626",
  strokeWidth: 2
}
// + Text "1" in white, 24px
```

### 2. Highlight Boxes

```javascript
{
  type: "rectangle",
  backgroundColor: "#fef3c7",  // Yellow highlight
  strokeColor: "#f59e0b",
  strokeWidth: 3,
  roundness: { type: 3 }
}
```

### 3. Dotted Containers

For grouping without heavy borders:

```javascript
{
  strokeStyle: "dotted",
  strokeWidth: 2,
  strokeColor: "#d1d5db",
  backgroundColor: "#f9fafb",
  opacity: 60
}
```

### 4. Shadow Effect (Visual Depth)

Use darker shade as background offset:

```javascript
// Background shadow
{
  x: box.x + 5,
  y: box.y + 5,
  backgroundColor: "#e5e7eb",
  opacity: 40
}
// Foreground box
{
  x: box.x,
  y: box.y,
  backgroundColor: "#ffffff"
}
```

---

## Example Compositions

### Data Pipeline - Creative Version

```
🗂️ Sources  →  ☁️ Cloud  →  ⚡ Process  →  📊 Insights  →  🎯 Action
(circle)       (circle)     (circle)      (circle)        (circle)
 orange         blue         purple        green           red
```

**Features:**
- Large emoji icons (56px)
- Colorful circles (140×140px)
- Straight arrows (4px, colored)
- Clean labels below each circle
- 200px spacing between elements

---

### Architecture - Creative Version

```
        ┌─────────────────────────┐
        │   🏢 Business Layer     │ ← Red accent
        └───────────┬─────────────┘
                    │ (straight down)
        ┌───────────▼─────────────┐
        │   🤖 AI Engine          │ ← Purple accent
        └───────────┬─────────────┘
                    │ (straight down)
        ┌───────────▼─────────────┐
        │   ☁️ Cloud Platform     │ ← Blue accent
        └───────────┬─────────────┘
                    │ (straight down)
        ┌───────────▼─────────────┐
        │   💾 Data Sources       │ ← Gray accent
        └─────────────────────────┘
```

**Features:**
- Vertical flow (top-down storytelling)
- Each layer has distinct color
- Large emoji icon in each box
- Straight arrows connecting centers
- 120px vertical spacing

---

## Quality Checklist - Creative Style

- [ ] Large, bold visual elements (circles, badges)
- [ ] Vibrant accent colors used strategically
- [ ] Large emoji icons (48-56px) for visual interest
- [ ] Arrows are straight or have MAX 1 corner
- [ ] Arrows point to element centers (focus: 0)
- [ ] Generous spacing (150-200px between major elements)
- [ ] Clear visual hierarchy (size, color, position)
- [ ] Tells a story (not just technical diagram)
- [ ] Engaging and memorable visual style
- [ ] Professional but creative presentation quality

---

**Last Updated:** 2026-01-30
**Version:** 1.0 - Creative/Illustrative Style
