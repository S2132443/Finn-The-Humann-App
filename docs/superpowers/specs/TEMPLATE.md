# Spec: <slice id and short title>

Roadmap slice: <link to the ROADMAP.md slice, e.g. ROADMAP.md Phase A / A1>
Status: Draft | Approved | Implemented
Research: <link to docs/superpowers/research/YYYY-MM-DD-topic.md sections, or "none">

## Assumptions and Tradeoffs

State assumptions explicitly before any code (Think Before Coding). List the
options considered and why the chosen approach wins. Surface what could make this
the wrong call.

## Success Criteria

Measurable, objectively checkable statements that define done. These drive the
verification checklist at the end. Avoid vague goals.

- [ ] <criterion 1>
- [ ] <criterion 2>

## Design

The minimum design that satisfies the criteria (Simplicity First). Describe the
files and functions to add or change, the data flow, and any schema or migration
work. Keep changes surgical: only what must change.

### Files touched

- `path/to/file` : what changes and why

## Out of Scope

What this slice deliberately does not do, to prevent scope creep.

## Verification Checklist

Concrete, checkable statements a reviewer verifies against the implementation
before merge. Every spec ends here.

- [ ] **KISS:** No unnecessary abstraction; the minimum code solves the problem.
- [ ] **DRY:** No duplicated logic; shared behavior is factored into one source
  of truth.
- [ ] **Modular:** Each new piece does one thing and is deletable without
  breaking unrelated features.
- [ ] **Scalable:** The approach holds as data and usage grow; no obvious
  bottleneck introduced.
- [ ] **Architecture invariants:** Shared logic lives in `services/`; API
  (`api/v1/`) and web (`web/`) stay thin and reuse it. No new service split.
- [ ] **Standards:** black and ruff pass on modified files; lines within 79
  chars; type hints and docstrings present; parameterized SQL; inputs validated;
  no em-dashes.
- [ ] **Tests:** New behavior is covered and the suite passes.
- [ ] **Success criteria above are all met and were verified, not assumed.**
