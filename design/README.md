# Design Documents

> Architecture design documents and technical specifications

---

## Purpose

This directory contains technical design documents that capture architecture decisions, system requirements, and implementation specifications created during the project lifecycle.

---

## Naming Convention

```text
{{feature-name}}-design.md          # Technical design
{{feature-name}}-requirements.md    # Feature requirements
{{system-name}}-architecture.md     # System architecture
```

---

## Template

Each design document should include:

1. **Overview** - What this design covers
2. **Context** - Why this is needed
3. **Architecture** - System diagram and components
4. **Key Decisions** - Design choices with rationale
5. **API/Interface** - External interfaces
6. **Data Model** - Data structures and storage
7. **Security** - Security considerations
8. **Testing Strategy** - How to validate

---

## Relationship to SDD

Design documents in this folder are **informal** technical specs. For features that require full traceability, use the SDD workflow:

```text
This folder:     Informal design docs (quick reference)
.claude/sdd/:    Formal DEFINE → DESIGN → BUILD pipeline
```

Both can coexist. Use this folder for high-level architecture overviews and the SDD pipeline for feature-level specifications.
