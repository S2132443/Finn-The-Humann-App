# CLAUDE.md (Project)

Extends the global user-level guidelines with this repo's tooling, architecture,
and conventions. Where this file and the global file disagree, this file wins.

## Architecture
> Define the system architecture and its invariants here. The global rule
> "must not violate the system architecture" and the spec verification checklist
> below both point at this section, so it must exist and stay current.

## Spec Verification
**Every spec** (in `docs/superpowers/specs/`) must, where possible, end with a
**verification checklist**: concrete, checkable statements proving the design
follows KISS, DRY, modularity, scalability, the architecture invariants above,
and the rules in this file plus the global file. Reviewers verify the checklist
against the implementation before merge.

## ROADMAP.md Rules
The roadmap repeatedly drifted into "a phase = its numbered slice list" because
new work was appended as unnumbered prose below delivered arcs, where future
sessions never look (audited and restructured 2026-06-12). When touching
ROADMAP.md:

- **A phase is never just its numbered slices.** Capture new work under a heading
  containing the word "Pending" (create one if missing) or as a numbered entry in
  a pending arc. Never append it as bare prose trailing a delivered list or a
  done item.
- **Never mark a phase, arc, or slice done while its section still contains
  Pending headings** or captures of unbuilt work. Relocate or resolve them first.
- **When reading:** the execution-order table is the order, not the inventory.
  Before stating "X is all that remains in a phase", skim that phase's whole
  section for Pending headings, including phases marked done (done phases still
  accumulate follow-up slices, e.g. Phase A core polish, Phase A.5 voice
  expressiveness).

## Research Note Rules
Research findings go in `docs/superpowers/research/YYYY-MM-DD-topic.md`. Discuss
findings in chat first; write the note only when the user asks. Notes record
findings and sources, never decisions (state "No decisions are made here" in the
header paragraph); link sources inline and end with distilled implications plus a
phase mapping. ROADMAP.md captures must link to the relevant note sections: the
note holds the detail, the roadmap holds a dated pointer plus a short summary
under a Pending heading or numbered pending item, per the rules above.

## Python Standards
**CRITICAL: Always format Python code with black and ruff before submitting.**

- **PEP8 Compliance:** Strictly follow PEP8, no exceptions.
- **Line Length:** Maximum 79 characters per line.
- **Formatting Tools:** MANDATORY use of black and ruff on MODIFIED Python files
  only (not the entire project).
- **Imports:** Organize properly (stdlib, third-party, local). No unused imports.
- Use `pathlib` over `os.path`.

### Python Workflow
**MANDATORY before submitting any Python changes:**

```bash
python -m black <filename>.py
python -m ruff check <filename>.py --fix
python -m black <filename>.py --check  # Verify formatting
```

All code must pass `black --check` and `ruff check` with minimal warnings. Then
run static analysis and fix critical issues before finalizing:

```bash
mypy <filename>.py --strict   # type errors, missing hints
pylint <filename>.py          # code smells, potential bugs
bandit -r <directory>         # security vulnerabilities
```