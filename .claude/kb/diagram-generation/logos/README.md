# Logo Library for Diagram Generation

## Overview

This directory contains pre-encoded SVG logos as base64 data URLs
ready for embedding in Excalidraw JSON files.

## Files

| File | Contents | Count |
|------|----------|-------|
| `gcp.md` | Google Cloud Platform service logos | 8 |
| `general.md` | Databases, languages, tools, DevOps | 7+ |
| `custom.md` | On-demand logos fetched during generation | 0+ (grows over time) |

## How to Use (for the diagram-generator-agent)

1. Identify which technologies the diagram needs
2. Read the relevant logo file (gcp.md and/or general.md)
3. For each logo needed:
   a. Copy the `fileId` and use it in the image element's `fileId` property
   b. Copy the `dataURL` and add it to the Excalidraw `files` object
   c. Create a `type: "image"` element with the logo's fileId
4. Add `boundElements` to each image element for connected arrows
5. Add `startBinding`/`endBinding` to arrows referencing image element IDs
6. **If a logo is NOT found** in gcp.md or general.md, follow the
   "Custom Logo On-Demand Workflow" below

## Logo Entry Format

Each logo has:
- **fileId**: Unique identifier for Excalidraw reference
- **mimeType**: Always "image/svg+xml"
- **brand_color**: Official brand hex color
- **recommended_size**: Pixel dimensions for different contexts
- **dataURL**: Complete base64-encoded SVG data URI
- **Element template**: Copy-paste Excalidraw element JSON
- **Files entry**: Copy-paste Excalidraw files object entry

## Custom Logo On-Demand Workflow

When a diagram requires a technology not in the pre-built library:

### Step 1: Check custom.md
Read `logos/custom.md`. If the logo was previously fetched, use it directly.

### Step 2: Fetch from Simple Icons CDN
If not in custom.md, fetch the SVG:
- URL pattern: `https://cdn.simpleicons.org/{slug}/{hex_color}`
- The slug is the lowercase technology name (e.g., "apachedruid", "redis", "dbt")
- The hex_color is the brand color WITHOUT the # (e.g., "4169E1")
- Simple Icons has ~3000 brands: https://simpleicons.org/

### Step 3: Encode and Save
1. Take the SVG content returned
2. Base64-encode it
3. Format as data URL: `data:image/svg+xml;base64,{encoded}`
4. Append a new entry to `logos/custom.md` following the standard format:
   - fileId: `{technology_slug}_logo`
   - All standard fields (mimeType, brand_color, dataURL, templates)

### Step 4: Use in Diagram
The logo is now permanently available in custom.md for this and future diagrams.

### Fallback: Text Placeholder
If the SVG cannot be fetched (technology not in Simple Icons):
1. Create a rounded rectangle (12px border-radius) with:
   - Width: 48px, Height: 48px
   - Stroke: brand color (or #495057 if unknown)
   - Fill: transparent
   - roughness: 0
2. Add text element centered inside:
   - Technology abbreviation (max 4 chars, e.g., "DRUID")
   - fontFamily: 3, fontSize: 10px
   - Color: same as stroke
3. This placeholder is functional but should be replaced with a real
   logo when available

## Adding Logos Manually

1. Download SVG from Simple Icons (https://cdn.simpleicons.org/{slug})
   or official brand assets
2. Base64-encode: In a browser console, use `btoa(svgString)` or
   use an online converter
3. Format as data URL: `data:image/svg+xml;base64,{encoded}`
4. Add entry to the appropriate .md file following existing format
5. Test by creating a minimal .excalidraw with the logo and opening
   in excalidraw.com

## Sources

- Simple Icons CDN: `https://cdn.simpleicons.org/{slug}/{hex_color}`
- Simple Icons Browser: `https://simpleicons.org/`
- GCP Official: `https://cloud.google.com/icons`
- GCP Icons: `https://gcpicons.com/`

## Licensing

- Simple Icons: CC0 / Open Source
- GCP Official: Permitted for documentation and diagrams

---

**Last Updated:** 2026-01-31
