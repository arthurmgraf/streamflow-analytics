# Icon Library for Diagram Generation

## Overview

This library provides icon references and text-based representations for common technologies and services used in diagrams. Icons enhance recognition and make diagrams more professional and intuitive.

---

## Icon Strategy

### Implementation Approaches

1. **Text-Based Icons (Current MVP)**
   - Use styled text labels with technology names
   - Smaller font size, monospace, reduced opacity
   - Example: `[GCS]`, `[BigQuery]`, `[Python]`

2. **Future: Embedded SVG/Base64**
   - Embed actual logos as base64 data URLs
   - Requires license compliance
   - Higher visual quality

### Current MVP: Text Icons

For MVP, we use **text-based icon placeholders**:

```javascript
{
  id: "icon_gcs",
  type: "text",
  text: "☁ GCS",  // Cloud emoji + abbreviation
  fontSize: 12,
  fontFamily: 3,   // Monospace
  opacity: 70,
  textAlign: "center",
  strokeColor: "#718096"
}
```

---

## GCP Services Icons

### Storage Services

| Service | Icon Text | Emoji | Color |
|---------|-----------|-------|-------|
| **Cloud Storage** | `☁ GCS` | ☁ | `#4285f4` |
| **BigQuery** | `📊 BQ` | 📊 | `#4285f4` |
| **Cloud SQL** | `🗄️ SQL` | 🗄️ | `#4285f4` |
| **Firestore** | `🔥 FIRE` | 🔥 | `#f59e0b` |
| **Datastore** | `💾 DS` | 💾 | `#4285f4` |

### Compute Services

| Service | Icon Text | Emoji | Color |
|---------|-----------|-------|-------|
| **Cloud Functions** | `⚡ CF` | ⚡ | `#4285f4` |
| **Cloud Run** | `🏃 RUN` | 🏃 | `#4285f4` |
| **Compute Engine** | `🖥️ GCE` | 🖥️ | `#4285f4` |
| **App Engine** | `🚀 GAE` | 🚀 | `#4285f4` |
| **Kubernetes (GKE)** | `☸ GKE` | ☸ | `#4285f4` |

### Data Services

| Service | Icon Text | Emoji | Color |
|---------|-----------|-------|-------|
| **Dataflow** | `🌊 FLOW` | 🌊 | `#4285f4` |
| **Dataproc** | `⚙️ PROC` | ⚙️ | `#4285f4` |
| **Pub/Sub** | `📬 PS` | 📬 | `#f59e0b` |
| **Dataform** | `📋 DF` | 📋 | `#4285f4` |
| **Composer (Airflow)** | `🎼 COMP` | 🎼 | `#4285f4` |

### AI/ML Services

| Service | Icon Text | Emoji | Color |
|---------|-----------|-------|-------|
| **Vertex AI** | `🧠 VERTEX` | 🧠 | `#7c3aed` |
| **AI Platform** | `🤖 AI` | 🤖 | `#7c3aed` |
| **AutoML** | `✨ AUTO` | ✨ | `#7c3aed` |
| **Vision API** | `👁️ VISION` | 👁️ | `#7c3aed` |
| **Natural Language** | `💬 NLP` | 💬 | `#7c3aed` |

---

## Other Cloud Providers

### AWS Services

| Service | Icon Text | Emoji | Color |
|---------|-----------|-------|-------|
| **S3** | `📦 S3` | 📦 | `#ff9900` |
| **Lambda** | `λ LAMB` | λ | `#ff9900` |
| **RDS** | `🗄️ RDS` | 🗄️ | `#ff9900` |
| **DynamoDB** | `⚡ DDB` | ⚡ | `#ff9900` |
| **Redshift** | `📊 RS` | 📊 | `#ff9900` |

### Azure Services

| Service | Icon Text | Emoji | Color |
|---------|-----------|-------|-------|
| **Blob Storage** | `📦 BLOB` | 📦 | `#0078d4` |
| **Functions** | `⚡ AF` | ⚡ | `#0078d4` |
| **SQL Database** | `🗄️ SQL` | 🗄️ | `#0078d4` |
| **Synapse** | `📊 SYN` | 📊 | `#0078d4` |
| **Event Hub** | `📬 EH` | 📬 | `#0078d4` |

---

## Programming Languages

| Language | Icon Text | Emoji | Color |
|----------|-----------|-------|-------|
| **Python** | `🐍 PY` | 🐍 | `#3776ab` |
| **JavaScript** | `JS` | - | `#f7df1e` |
| **TypeScript** | `TS` | - | `#3178c6` |
| **Java** | `☕ JAVA` | ☕ | `#007396` |
| **Go** | `🐹 GO` | 🐹 | `#00add8` |
| **Rust** | `🦀 RUST` | 🦀 | `#ce422b` |
| **SQL** | `📊 SQL` | 📊 | `#cc2927` |

---

## Databases

| Database | Icon Text | Emoji | Color |
|----------|-----------|-------|-------|
| **PostgreSQL** | `🐘 PG` | 🐘 | `#4169e1` |
| **MySQL** | `🐬 MY` | 🐬 | `#4479a1` |
| **MongoDB** | `🍃 MONGO` | 🍃 | `#47a248` |
| **Redis** | `⚡ REDIS` | ⚡ | `#dc382d` |
| **Elasticsearch** | `🔍 ES` | 🔍 | `#005571` |

---

## Data Tools

| Tool | Icon Text | Emoji | Color |
|------|-----------|-------|-------|
| **Apache Spark** | `⚡ SPARK` | ⚡ | `#e25a1c` |
| **Kafka** | `📬 KAFKA` | 📬 | `#231f20` |
| **Airflow** | `🌊 FLOW` | 🌊 | `#017cee` |
| **dbt** | `🔨 DBT` | 🔨 | `#ff694b` |
| **Pandas** | `🐼 PD` | 🐼 | `#150458` |

---

## AI/ML Frameworks

| Framework | Icon Text | Emoji | Color |
|-----------|-----------|-------|-------|
| **TensorFlow** | `🧠 TF` | 🧠 | `#ff6f00` |
| **PyTorch** | `🔥 TORCH` | 🔥 | `#ee4c2c` |
| **Langchain** | `🔗 LC` | 🔗 | `#7c3aed` |
| **LlamaIndex** | `🦙 LI` | 🦙 | `#7c3aed` |
| **OpenAI** | `✨ AI` | ✨ | `#412991` |
| **Anthropic Claude** | `🤖 CL` | 🤖 | `#7c3aed` |

---

## BI & Visualization

| Tool | Icon Text | Emoji | Color |
|------|-----------|-------|-------|
| **Looker** | `📊 LOOK` | 📊 | `#4285f4` |
| **Looker Studio** | `📈 LS` | 📈 | `#4285f4` |
| **Tableau** | `📊 TAB` | 📊 | `#e97627` |
| **Power BI** | `📊 PBI` | 📊 | `#f2c811` |
| **Metabase** | `📊 MB` | 📊 | `#509ee3` |

---

## DevOps & Infrastructure

| Tool | Icon Text | Emoji | Color |
|------|-----------|-------|-------|
| **Docker** | `🐳 DOC` | 🐳 | `#2496ed` |
| **Kubernetes** | `☸ K8S` | ☸ | `#326ce5` |
| **Terraform** | `🏗️ TF` | 🏗️ | `#7b42bc` |
| **GitHub** | `🐙 GH` | 🐙 | `#181717` |
| **GitLab** | `🦊 GL` | 🦊 | `#fc6d26` |
| **Jenkins** | `⚙️ JEN` | ⚙️ | `#d24939` |

---

## Icon Placement Patterns

### Pattern 1: Top-Center (Recommended)

```javascript
// Component box
{
  id: "component_box",
  type: "rectangle",
  x: 100,
  y: 100,
  width: 200,
  height: 100
}

// Icon text at top center
{
  id: "icon_text",
  type: "text",
  x: 150,           // Center: box.x + (box.width / 2) - (icon.width / 2)
  y: 110,           // Top: box.y + 10
  width: 100,
  height: 20,
  text: "☁ GCS",
  fontSize: 12,
  fontFamily: 3,
  textAlign: "center",
  opacity: 70,
  strokeColor: "#718096"
}

// Main label below icon
{
  id: "label_text",
  type: "text",
  x: 120,
  y: 135,
  width: 160,
  height: 55,
  text: "Cloud Storage\nBronze / Raw",
  fontSize: 16,
  textAlign: "center",
  strokeColor: "#1a73e8"
}
```

### Pattern 2: Left-Aligned

```javascript
// Icon on left
{
  id: "icon_text",
  x: 110,           // Left: box.x + 10
  y: 125,
  width: 40,
  height: 20,
  text: "☁",
  fontSize: 18,
  textAlign: "left"
}

// Label next to icon
{
  id: "label_text",
  x: 155,           // After icon: icon.x + icon.width + 5
  y: 125,
  width: 130,
  text: "Cloud Storage",
  fontSize: 16,
  textAlign: "left"
}
```

---

## Icon Generation Helper

### Function to Create Icon Text Element

```javascript
function createIconText(parentBox, iconText, position = "top-center") {
  const positions = {
    "top-center": {
      x: parentBox.x + (parentBox.width - 80) / 2,
      y: parentBox.y + 10
    },
    "top-left": {
      x: parentBox.x + 10,
      y: parentBox.y + 10
    },
    "center": {
      x: parentBox.x + (parentBox.width - 80) / 2,
      y: parentBox.y + (parentBox.height - 20) / 2
    }
  };

  return {
    id: `icon_${parentBox.id}`,
    type: "text",
    ...positions[position],
    width: 80,
    height: 20,
    angle: 0,
    strokeColor: "#718096",
    backgroundColor: "transparent",
    fillStyle: "solid",
    strokeWidth: 1,
    strokeStyle: "solid",
    roughness: 0,
    opacity: 70,
    groupIds: [],
    roundness: null,
    seed: Math.floor(Math.random() * 10000),
    version: 1,
    versionNonce: Math.floor(Math.random() * 10000),
    isDeleted: false,
    boundElements: null,
    updated: Date.now(),
    link: null,
    locked: false,
    text: iconText,
    fontSize: 12,
    fontFamily: 3,  // Monospace
    textAlign: "center",
    verticalAlign: "top",
    baseline: 12,
    containerId: null,
    originalText: iconText
  };
}
```

---

## Technology Detection

### Detect Technologies from Project

```javascript
const techDetection = {
  // Python imports
  "import pandas": "🐼 PD",
  "import numpy": "🔢 NP",
  "import tensorflow": "🧠 TF",
  "import torch": "🔥 TORCH",
  "from langchain": "🔗 LC",
  "from google.cloud import storage": "☁ GCS",
  "from google.cloud import bigquery": "📊 BQ",

  // SQL patterns
  "CREATE TABLE": "📊 SQL",
  "SELECT FROM": "📊 SQL",

  // Config files
  "requirements.txt": "🐍 PY",
  "package.json": "JS/TS",
  "Dockerfile": "🐳 DOC",
  "terraform": "🏗️ TF",

  // GCP services (from configs)
  "cloudfunctions": "⚡ CF",
  "cloud-run": "🏃 RUN",
  "bigquery": "📊 BQ",
  "cloud-storage": "☁ GCS",
  "pubsub": "📬 PS"
};
```

---

## Icon Usage Guidelines

### ✅ Do

- Use icons consistently throughout diagram
- Place icons in same position for similar components
- Use appropriate icon size (12px for small, 18px for featured)
- Match icon color to component color scheme
- Use text-based icons for MVP (fast, no licensing issues)

### ❌ Don't

- Mix different icon styles in same diagram
- Use overly large icons that dominate the component
- Use low-contrast icons (minimum 70% opacity)
- Place icons randomly without alignment
- Use copyrighted logos without permission

---

## Future Enhancements

### Real Logo Integration (Post-MVP)

When implementing real logos:

1. **Source logos:**
   - Official brand assets (with permission)
   - Open-source icon libraries (Font Awesome, Material Icons)
   - Custom-created icons

2. **Format:**
   - SVG preferred (scalable, small file size)
   - PNG with transparency (base64 encode)
   - Embed in `files` object of Excalidraw JSON

3. **Licensing:**
   - Verify license for each logo
   - Prefer open-source or public domain
   - Attribute when required

4. **Example structure:**
```javascript
{
  "files": {
    "gcp_logo": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQi..."
  },
  "elements": [
    {
      "type": "image",
      "fileId": "gcp_logo",
      "x": 100,
      "y": 100,
      "width": 50,
      "height": 50
    }
  ]
}
```

---

## Icon Quick Reference

### Most Common (Top 20)

1. `☁ GCS` - Cloud Storage
2. `📊 BQ` - BigQuery
3. `⚡ CF` - Cloud Functions
4. `🐍 PY` - Python
5. `📊 SQL` - SQL/Database
6. `🐘 PG` - PostgreSQL
7. `🤖 AI` - AI/ML Services
8. `🔗 MCP` - Model Context Protocol
9. `📚 KB` - Knowledge Base
10. `🌊 FLOW` - Data Flow/Pipeline
11. `📦 S3` - AWS S3 or Storage
12. `🐳 DOC` - Docker
13. `☸ K8S` - Kubernetes
14. `🔥 FIRE` - Firebase/Firestore
15. `📬 PS` - Pub/Sub
16. `🦙 LLM` - Large Language Model
17. `📈 BI` - Business Intelligence
18. `⚙️ PROC` - Processing/Compute
19. `🔍 SEARCH` - Search/Elasticsearch
20. `📋 LOG` - Logging/Monitoring

---

## Example: Component with Icon

```javascript
[
  // Background box
  {
    id: "service_gcs",
    type: "rectangle",
    x: 100,
    y: 100,
    width: 200,
    height: 100,
    strokeColor: "#4285f4",
    backgroundColor: "#bbdefb",
    // ... other properties
  },
  // Icon
  {
    id: "icon_gcs",
    type: "text",
    x: 150,
    y: 110,
    width: 100,
    height: 20,
    text: "☁ GCS",
    fontSize: 12,
    fontFamily: 3,
    textAlign: "center",
    strokeColor: "#718096",
    opacity: 70,
    // ... other properties
  },
  // Main label
  {
    id: "label_gcs",
    type: "text",
    x: 120,
    y: 135,
    width: 160,
    height: 55,
    text: "Cloud Storage\nBronze / Raw Zone",
    fontSize: 16,
    fontFamily: 1,
    textAlign: "center",
    strokeColor: "#1a73e8",
    // ... other properties
  }
]
```

---

**Last Updated:** 2026-01-30
**Version:** 1.0 (Text-based icons for MVP)
