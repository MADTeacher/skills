# Workflow: From Brief To Clean Diagram

Use this guide when the task is not only to write valid draw.io XML, but to
deliver a diagram that is structurally sound, route-readable, and ready for the
user's real viewing mode.

## Ask Questions In One Batch

For a new or fuzzy diagram request, ask one short batch of questions instead of
stretching the brief across many tiny follow-ups. You can skip questions for
small edits when the user already gave a precise file, target change, and output
format.

## Hard Rules

- Keep exactly one working `.drawio` file as the source of truth.
- Before visual review, list nearby `*.drawio` files and remove or quarantine
  disposable siblings such as `*.skill-test.drawio` or `*.tmp.drawio`.
- Structural validation is mandatory for every final `.drawio` file.
- Layout validation is mandatory for every final `.drawio` file after
  structural validation and before visual QA.
- Visual QA is mandatory for presentation-facing diagrams, review or validation
  requests, and whenever PNG, JPG, or PDF is requested for human inspection.
- Route readability outranks density. If arrows still overlap foreign shapes,
  hide each other, or make ownership unclear after a first routing pass, stop
  tightening edges and change the layout, spacing, lanes, or page split.
- `edges[].points` are mandatory for every non-trivial route: obstacle
  avoidance, axis changes, lane or zone crossings, perimeter return loops, and
  links between non-adjacent nodes.
- Use `entryX`, `entryY`, `exitX`, and `exitY` when the side of attachment
  matters for legibility.
- Default spacing thresholds:
  - at least `24 px` between peer non-container nodes
  - at least `24 px` from any node to the page edge
  - at least `32 px` from any node to a swimlane border
  - treat `12 px` edge-to-shape clearance as the minimum warning threshold
- Do not auto-launch the draw.io desktop app for export or review images on any
  OS unless the user explicitly opts into desktop export, or `DRAWIO_CMD`
  points to a safer wrapper or renderer instead of the official desktop binary.
  Desktop builds can crash, hang, or require a GUI session under automation. On
  this macOS host, the observed failure mode is a system crash dialog.
- If `scripts/export_drawio.py` blocks desktop export and the task still
  requires PNG, JPG, PDF, or visual QA, immediately request approval to rerun
  the same helper with `--allow-desktop-export`. Use the command approval flow
  itself as the explicit opt-in. Do not switch to `qlmanage`, Quick Look,
  browser rendering, Playwright screenshots, Preview thumbnails, or any other
  substitute renderer.
- Review only the latest export generated from the current working source. Do
  not compare against memory or stale screenshots unless the user explicitly
  asked for a comparison.
- Keep review artifacts ephemeral. Use
  `scripts/cleanup_drawio_review_artifacts.py prepare <file.drawio>` before each
  review cycle and export temporary review images only into the returned temp
  directory.
- Delete intermediate review artifacts after each cycle. Keep a final export
  beside the source only when the user explicitly wants one.
- If the user will consume the diagram in draw.io or diagrams.net, or they gave
  an editor screenshot, reopen the `.drawio` file and inspect the editor canvas
  as a second mandatory view.
- Do not call the diagram ready while any visible defect remains in the latest
  export or, when applicable, in the reopened editor canvas.
- Do not hand off while `scripts/check_drawio_layout.py` still reports a `FAIL`
  or an unresolved warning.

## Mandatory Question Groups

### 1. Goal And Audience

- What should the viewer understand, decide, or do after seeing the diagram?
- Who is the audience: engineers, executives, students, operators, customers,
  or mixed readers?
- Is this a reference diagram, an explanation diagram, a review artifact, or a
  presentation visual?

### 2. Source Material And Structure

- Is there an existing `.drawio` file, screenshot, markdown outline, system
  description, or hand sketch?
- What entities, steps, systems, actors, or states are mandatory?
- Does the content naturally belong on one page, or should it split into
  overview and detail pages?

### 3. Delivery And Review Mode

- What final artifacts are needed: `.drawio`, PNG, SVG, PDF, or JPG?
- Will the user edit the file in draw.io or diagrams.net after delivery?
- Is visual polish more important than density, or is this primarily a working
  technical map?

## Brief Template

```markdown
Before I build or revise the diagram, please answer in one message:

1. Diagram type and goal:
2. Audience:
3. Existing source file, screenshot, or outline:
4. Required systems, steps, states, or actors:
5. One page or overview + detail pages:
6. Final artifacts needed: .drawio / PNG / SVG / PDF / JPG:
7. Will you review or edit this inside draw.io/diagrams.net?
8. If style is flexible, should I keep it business-safe, explanatory, or more expressive?
```

## Before Drawing: Choose A Visual Direction

If style is not fixed, select from `references/design-directions.md`.

- Propose three contrasting directions:
  - one safe or business-like
  - one explanatory or editorial
  - one more expressive but still appropriate
- Each direction must change the page structure, spacing, line weight, label
  density, and color semantics. A palette swap alone is not a direction.
- Lock the direction before building dense pages. It is cheap to change early
  and expensive after connector geometry is tuned.

## Phase 1: Plan The Diagram

Translate the request into:

- diagram family
- pages
- nodes
- edges
- containers or swimlanes
- color semantics
- label language
- review mode requirements

Prefer multiple pages when the same canvas would otherwise mix overview,
explanation, and dense technical detail.

## Phase 2: Route Plan Before Draw

Before touching XML geometry, lock the route strategy:

- Choose one dominant reading direction: top-to-bottom or left-to-right.
- Assign lanes, zones, or separate pages before placing dense nodes.
- Classify every edge as one of:
  - primary flow
  - secondary dependency
  - return loop
  - async path
- Choose the entry side, exit side, and corridor for every non-trivial edge.
- Route long return loops around the outer perimeter instead of through the
  middle of the core content area.
- Prefer node movement, spacing changes, lane changes, or page split before
  adding complicated detours.
- Treat edge-edge crossings as a last resort. Edge-vertex crossings are
  defects, not tradeoffs.
- If the first routing pass still leaves more than one conflicting crossing in
  the core content area, or more than two long back-edges through the center of
  the page, split the content into overview and detail pages instead of forcing
  a denser single-page layout.

## Phase 3: Choose The Authoring Path

Use direct XML editing when:

- the user already has a `.drawio` file
- the change is targeted or layout-specific
- true nesting, special ports, or hand-authored geometry matter

Use the builder script when:

- the request is a new diagram
- the structure maps cleanly to pages, nodes, and edges
- you want repeatable generation from a JSON spec

Example commands:

```bash
python3 scripts/build_drawio.py --example
python3 scripts/build_drawio.py spec.json output.drawio
```

## Phase 4: Structural Validation

Run this on the working source before claiming success:

```bash
python3 scripts/validate_drawio.py path/to/file.drawio
```

What this guarantees:

- XML parses
- required root cells exist
- every page contains an `mxGraphModel`
- edge references are valid
- every edge has a child `mxGeometry`
- duplicate IDs are rejected

What this does not guarantee:

- clean spacing
- readable line routing
- non-overflowing labels
- editor-canvas fit

That is why layout review and visual QA are separate gates.

## Phase 5: Layout Gate

Run the heuristic geometry review immediately after structural validation:

```bash
python3 scripts/check_drawio_layout.py path/to/file.drawio
```

Hard failures:

- peer non-container vertex bounding boxes overlap
- an authored edge segment intersects an unrelated non-container vertex
- a waypoint lies inside an unrelated non-container vertex

Warnings:

- missing explicit waypoint arrays for non-trivial routes
- peer gaps below `24 px`
- node-to-page-edge gaps below `24 px`
- node-to-swimlane-border gaps below `32 px`
- edge-to-shape clearance below `12 px`
- edge-edge crossings remaining in the core content area
- multiple one-directional edges collapsing into the same corridor without
  visible offset
- page density suggesting a split because too many long return loops or core
  crossings remain

Warnings do not fail the command, but they do fail the handoff until they are
fixed or proven false positives against the latest export and, when required,
the reopened editor canvas.

## Phase 6: Export-Inspect-Fix Loop

### 1. Prepare A Clean Review Directory

```bash
python3 scripts/cleanup_drawio_review_artifacts.py prepare path/to/file.drawio
```

This returns JSON with:

- `review_dir`
- `png_pattern`
- `jpg_pattern`
- removed stale artifacts

Use the returned temp directory for intermediate review images.

### 2. Export The Latest Diagram

Typical review exports:

```bash
python3 scripts/export_drawio.py path/to/file.drawio --format png --page-index 1 --output /tmp/drawio-review-gate/file/file-page1.png
python3 scripts/export_drawio.py path/to/file.drawio --format jpg --page-index 1 --output /tmp/drawio-review-gate/file/file-page1.jpg
python3 scripts/export_drawio.py path/to/file.drawio --format pdf --all-pages --output /tmp/drawio-review-gate/file/file.pdf
```

The helper may intentionally block desktop export. Treat that as a safety stop,
not as something to auto-bypass. Only rerun with `--allow-desktop-export` when
the user explicitly accepts the desktop-app risk tradeoff, or when they have
configured a safer renderer via `DRAWIO_CMD` instead of the official desktop
binary.

If the task still requires visual QA or requested export artifacts, the next
action is not an improvised fallback. The next action is to request approval and
rerun this exact helper with `--allow-desktop-export`. Do not substitute
`qlmanage`, browser automation, screenshots of another viewer, or any other
non-draw.io export path.

Use PNG for most review loops. Use JPG only when image viewing works better that
way or the user explicitly wants lossy output.

### 3. Inspect The Latest Export Only

Review against `references/checklist.md`.

If editor rendering matters, reopen the `.drawio` file in draw.io or
diagrams.net and inspect the same page there as well. Use the stricter result.

### 4. Fix Visible Defects And Unresolved Warnings

Typical defects:

- arrows crossing shapes, labels, or notes
- lines visually merging with swimlane borders
- clipped borders or shapes too close to the page edge
- text overflow in export or editor view
- weak default-thin lines on a dense diagram
- empty detours that obscure the main reading path
- ambiguous arrow ownership where two routes visually merge
- layout-gate warnings that survive the latest export or editor check

### 5. Re-Export And Recheck

Repeat the loop in this order until the diagram is clean:

1. author or edit `.drawio`
2. run `scripts/validate_drawio.py`
3. run `scripts/check_drawio_layout.py`
4. export the latest PNG
5. inspect the latest export
6. if editor use matters, inspect the reopened editor canvas

The task is not done until the latest cycle has `0 FAIL` and `0 unresolved
warnings`. If export stays blocked because approval was denied or no safe
renderer exists, stop and report that visual QA is still incomplete.

### 6. Clean Up Temporary Artifacts

```bash
python3 scripts/cleanup_drawio_review_artifacts.py cleanup path/to/file.drawio
```

Keep a final export beside the source only if the user asked for it.

## Phase 7: Final Exports And Handoff

After the latest review pass is clean, generate the requested deliverables:

```bash
python3 scripts/export_drawio.py diagram.drawio --format png
python3 scripts/export_drawio.py diagram.drawio --format svg --page-index 1
python3 scripts/export_drawio.py diagram.drawio --format pdf --all-pages
```

In the final handoff, report:

- the path to the final `.drawio` file
- the paths to any requested exports
- whether structural validation passed
- the layout gate result in this exact form:
  - `layout gate: 0 fails, 0 unresolved warnings`
- which viewing modes were checked: export only, or export + reopened editor
- any honest limitations, such as export blocked because the draw.io CLI was not
  available or intentionally blocked in safety mode to avoid desktop-app failures
