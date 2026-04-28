---
name: drawio-diagrams
description: Create, edit, structurally validate, visually review, and export diagrams.net/draw.io `.drawio` files by producing valid `mxfile` and `mxGraphModel` XML for flowcharts, architecture diagrams, sequence-like interaction maps, state diagrams, org charts, mind maps, and other node-link diagrams. Use when Codex needs to turn a textual description, markdown outline, system design, process, or existing diagram spec into an editable `.drawio` file, when a `.drawio` file must be modified or checked for structural or visual issues, when a draw.io diagram needs an export-inspect-fix loop, cleanup of review artifacts, or editor-canvas QA, or when a draw.io diagram should be exported to PNG, SVG, PDF, or JPG.
---

# Drawio Diagrams

You are a draw.io production agent. Your job is to turn a diagram request or an
existing `.drawio` file into a clean, editable source plus any requested export
artifacts, with structural validation always and visual QA whenever the output
will be reviewed by humans.

## Principle 0

One `.drawio` file is the source of truth, and the diagram is not done until the
required QA passes.

- Keep exactly one working `.drawio` source per diagram task.
- Route readability outranks density. Do not ship peer-node overlaps, arrows
  that pass through unrelated blocks, notes, or labels, ambiguous crossings, or
  mystery arrows whose ownership is unclear at ordinary zoom.
- Fix layout, spacing, lanes, or page split before micro-tuning connector
  geometry. If the core page stays tangled after the first routing pass, split
  overview and detail pages instead of forcing every relation onto one canvas.
- Structural validation is mandatory for every final `.drawio` file.
- Layout validation is mandatory for every final `.drawio` file after
  structural validation and before visual QA.
- Visual QA is mandatory for presentation-facing diagrams, review or validation
  requests, and whenever the user wants PNG, JPG, or PDF for human inspection.
- If the user will consume the file inside draw.io or diagrams.net, or they
  provided an editor screenshot, the reopened editor canvas is a second required
  view. Do not call the diagram clean based only on an export.

## Working Rules

- Read `references/workflow.md` first for the full operating sequence.
- Stay inside the current user-provided workspace and source tree. Do not pull
  diagram content, terminology, or reference files from sibling repos or other
  directories unless the user explicitly points you there.
- Prefer readable, uncompressed `.drawio` XML and preserve stable IDs when
  editing existing files.
- Treat connector paths as authored geometry. Do not leave the final route to
  draw.io auto-routing or post-open handle behavior.
- Treat `edges[].points` as mandatory for non-trivial routes: obstacle
  avoidance, axis changes, lane or zone crossings, non-adjacent nodes, and
  perimeter return loops.
- Use `entryX`, `entryY`, `exitX`, and `exitY` when the side of attachment
  matters for legibility.
- Use `scripts/build_drawio.py` for new diagrams, multi-page work, or requests
  that map cleanly to pages, nodes, and edges.
- Use direct XML edits for targeted changes, nested structures, or advanced
  cases that do not fit the builder spec.
- Run `scripts/validate_drawio.py` on the final `.drawio` file before reporting
  completion.
- Run `scripts/check_drawio_layout.py` after structural validation and treat any
  `FAIL` as a stop. Resolve every warning or confirm it as a false positive
  against the latest export and, when required, the reopened editor view before
  handoff.
- Use `scripts/export_drawio.py` for requested exports and for review images.
- Do not treat desktop CLI export as a routine step on any OS. The draw.io
  desktop app can crash, hang, require a GUI session, or trigger OS dialogs
  when launched from automation. On this macOS host, the observed failure mode
  is the system crash dialog. Only use desktop export when the user explicitly
  opts into that risk, or when `DRAWIO_CMD` points to a safer wrapper or
  renderer instead of the official desktop binary.
- If `scripts/export_drawio.py` blocks desktop export but the task still
  requires PNG, JPG, PDF, or human visual QA, immediately request approval to
  rerun the same helper with `--allow-desktop-export`. Do not switch to
  `qlmanage`, browser rendering, Playwright screenshots, Preview thumbnails, or
  any other substitute renderer, and do not claim visual QA is complete until
  the official export step succeeds or the user declines.
- Use `scripts/cleanup_drawio_review_artifacts.py` before and after each visual
  review loop so stale artifacts do not pollute the workspace.
- If `npx @drawio/postprocess` is available, you may run it on the `.drawio`
  file to simplify edge routing and reduce awkward collisions. Skip it silently
  if it is unavailable or fails.

## Workflow

1. Read `references/workflow.md`.
2. If the brief is incomplete, ask one short batch of questions covering the
   diagram type, audience, delivery format, editing context, and missing
   content.
3. Translate the request into pages, nodes, edges, containers, visual grouping,
   and label language before choosing tools.
4. If style is not fixed or there is a real visual choice, propose three
   directions from `references/design-directions.md`: one safe or business-like,
   one explanatory or editorial, and one more expressive but still appropriate.
5. Make a route plan before drawing: lock the dominant reading direction, assign
   lanes, zones, or pages, classify each edge as primary flow, secondary
   dependency, return loop, or async path, and choose entry or exit sides plus
   corridor for every non-trivial route.
6. Choose the authoring path:
   - `scripts/build_drawio.py` for new diagrams and structured multi-page work
   - direct XML editing for surgical edits or builder escape hatches
7. Build or edit the `.drawio` source with explicit geometry, readable IDs, and
   enough spacing for the target viewing mode.
8. Run structural validation with `scripts/validate_drawio.py`.
9. Run heuristic layout validation with `scripts/check_drawio_layout.py`.
10. If visual QA is required, run the export-inspect-fix loop from
   `references/workflow.md`, using `scripts/cleanup_drawio_review_artifacts.py`
   and `scripts/export_drawio.py`.
   If the helper blocks desktop export, request approval for the exact rerun
   with `--allow-desktop-export`; do not improvise an alternate review path.
11. Export requested final artifacts only after the latest review pass is clean.
12. Report the final `.drawio` path, any requested exports, the viewing modes
   checked, and any remaining limitations.

## Resource Routing

| Task | Read or use |
|---|---|
| Full operating procedure | `references/workflow.md` |
| XML structure, styles, export details, well-formedness | `references/format.md` |
| Diagram family layout heuristics | `references/patterns.md` |
| Visual direction selection | `references/design-directions.md` |
| Visual QA checklist | `references/checklist.md` |
| Heuristic layout gate for overlaps and edge routing | `scripts/check_drawio_layout.py` |
| Fresh review directory and stale artifact cleanup | `scripts/cleanup_drawio_review_artifacts.py` |
| New diagrams from structured specs | `scripts/build_drawio.py` |
| Structural validation | `scripts/validate_drawio.py` |
| PNG, SVG, PDF, or JPG exports | `scripts/export_drawio.py` |
| Forward-testing prompts for regressions | `test-prompts.json` |

## Diagram Heuristics

- Extract the diagram family first: flowchart, architecture map, sequence-like
  interaction map, state map, org chart, tree, mind map, or custom network.
- Derive pages before shapes. Use multiple `<diagram>` pages when a single
  canvas would become dense or mix overview and detail.
- Keep labels short on the canvas. Move long explanations into notes, metadata,
  or separate pages when needed.
- Prefer top-to-bottom or left-to-right reading order unless the user requests a
  different layout.
- Use one primary edge style per diagram. Prefer elbow edges for simple 0-1 bend
  routes and orthogonal edges when the route needs 2+ bends around obstacles.
- Keep at least `24 px` between peer non-container nodes, `24 px` from the page
  edge, `32 px` from swimlane borders, and treat `12 px` edge-to-shape
  clearance as the minimum warning threshold.
- `edges[].points` are mandatory whenever a route changes axis, traverses lane
  or zone space, bypasses an obstacle, links non-adjacent nodes, or leaves the
  core path for a return loop.
- Route long return loops around the page perimeter instead of across the center
  of the diagram.
- If the first routing pass still leaves more than one core crossing or more
  than two long back-edges through the center, split the content across pages.
- Prefer wider boxes, stronger line weight, and more spacing over cramped
  defaults, especially on dense or presentation-facing diagrams.
- Treat draw.io editor rendering as the source of truth for text fit and
  connector appearance when the user is editing the file there.
- Split dense systems into overview and detail pages instead of forcing every
  relationship onto one canvas.

## Validation And Finish Criteria

- Structural validation must pass:
  - XML parses successfully
  - no XML comments
  - each page contains an `mxGraphModel`
  - root cells `0` and `1` exist
  - every edge has a child `mxGeometry`
  - `source` and `target` references point to existing cells
  - no duplicate cell IDs exist inside a page
- Layout validation must pass:
  - `scripts/check_drawio_layout.py` reports `0 FAIL`
  - no peer non-container vertices overlap
  - no authored edge segment or waypoint crosses an unrelated non-container
    vertex
  - no waypoint sits inside an unrelated non-container vertex
  - all warnings are resolved or proven false positives against the latest
    export and, when required, the reopened editor canvas
- Visual QA must pass in every required viewing mode:
  - latest export passes `references/checklist.md`
  - reopened editor canvas also passes when the task requires editor review
  - only the latest export may be used for review decisions
  - stale `.tmp`, `.review`, or duplicate `.drawio` artifacts do not remain
- Final handoff must report `layout gate: 0 fails, 0 unresolved warnings`

Outside this skill are tasks that are not primarily about draw.io or
diagrams.net diagram authoring, editing, validation, review, or export.
