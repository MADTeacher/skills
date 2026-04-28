# Draw.io Format Notes

## Table Of Contents

- Minimal file skeleton
- Required cell structure
- Routing contract
- HTML labels and line breaks
- Common style fragments
- Edge geometry and waypoints
- Bad vs good route examples
- Multi-page guidance
- Export workflow
- Editing rules
- Troubleshooting
- XML well-formedness

## Minimal File Skeleton

Prefer uncompressed XML for generated files:

```xml
<mxfile host="app.diagrams.net" modified="2026-04-18T12:00:00Z" agent="Codex" version="24.7.17" compressed="false">
  <diagram id="overview-page" name="Overview">
    <mxGraphModel dx="1600" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1600" pageHeight="900" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## Required Cell Structure

Every page needs:

- `mxCell id="0"` as the implicit document root
- `mxCell id="1" parent="0"` as the page layer

Create shapes as vertex cells:

```xml
<mxCell id="api-gateway" value="API Gateway" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
  <mxGeometry x="320" y="120" width="180" height="70" as="geometry" />
</mxCell>
```

Create connectors as edge cells. Prefer explicit route geometry so the path
stays fixed after reopen:

```xml
<mxCell id="edge-client-api" value="HTTPS" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;" edge="1" parent="1" source="client-app" target="api-gateway">
  <mxGeometry relative="1" as="geometry">
    <Array as="points">
      <mxPoint x="250" y="155" />
      <mxPoint x="320" y="155" />
    </Array>
  </mxGeometry>
</mxCell>
```

## Routing Contract

- Treat routing as authored geometry, not a viewer-time decision by draw.io.
- `edges[].points` are mandatory for any non-trivial route:
  - obstacle avoidance
  - axis changes
  - lane or zone crossings
  - non-adjacent node links
  - perimeter return loops
- Adjacent direct edges may omit waypoints only when the route is obviously
  trivial and `scripts/check_drawio_layout.py` produces no waypoint warning.
- Use `entryX`, `entryY`, `exitX`, and `exitY` whenever the side of attachment
  matters for readability or to keep the route out of the core content area.
- Default spacing thresholds:
  - peer non-container node gap: `24 px`
  - node-to-page-edge gap: `24 px`
  - node-to-swimlane-border gap: `32 px`
  - warning threshold for edge-to-shape clearance: `12 px`
- Prefer page split over forced density. If the first routing pass still needs
  more than one core crossing or more than two long back-edges through the
  middle, split the diagram into overview and detail pages.

## HTML Labels And Line Breaks

- Prefer `html=1` in every style so labels render correctly whether they contain plain text or HTML tags.
- Use `<br>` for line breaks in `value` attributes. Do not use literal `\n`.
- Use `fontStyle` for whole-label emphasis such as bold or italic. Use inline HTML only when formatting part of a label.
- Escape special characters in attribute values: `&`, `<`, `>`, and `"`.

## Common Style Fragments

Start most nodes with:

```text
whiteSpace=wrap;html=1;
```

Useful node recipes:

- Process box:
  - `rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;`
- Decision:
  - `shape=rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;`
- Terminator:
  - `shape=mxgraph.flowchart.terminator;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;`
- Database:
  - `shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;fillColor=#d5e8d4;strokeColor=#82b366;`
- Note:
  - `shape=note;whiteSpace=wrap;html=1;backgroundOutline=1;fillColor=#fff2cc;strokeColor=#d6b656;`
- Cloud or external system:
  - `shape=cloud;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;`
- Swimlane:
  - `shape=swimlane;whiteSpace=wrap;html=1;horizontal=0;startSize=28;fillColor=#f5f5f5;strokeColor=#666666;`
- Lightweight container:
  - `rounded=1;whiteSpace=wrap;html=1;container=1;pointerEvents=0;fillColor=#f5f5f5;strokeColor=#666666;`
- Invisible group:
  - `group;pointerEvents=0;`

Useful edge recipes:

- Orthogonal default:
  - `edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;`
- Side-anchored orthogonal route:
  - `edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;entryX=0;entryY=0.5;endArrow=block;`
- Elbow edge for simple 0-1 bend routes:
  - `edgeStyle=elbowEdgeStyle;elbow=vertical;rounded=0;jettySize=auto;html=1;endArrow=block;`
- Dashed dependency:
  - `edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;dashed=1;endArrow=open;`
- Straight relationship:
  - `html=1;endArrow=block;`

## Edge Geometry And Waypoints

- Every edge must contain a child `mxGeometry` element. Self-closing edge cells are invalid.
- Keep `relative="1"` on edge geometry unless you have a specific reason not to.
- Treat routing as part of the authored geometry, not as a viewer-time decision by draw.io.
- Encode the intended path with explicit waypoints and any other needed geometry
  fields so reopening the file does not reroute the edge.
- If the route still changes after reopen, the geometry is underspecified and must be tightened.
- If the route is non-trivial, the lack of an `Array as="points"` is a defect in
  the authored geometry, even when draw.io happens to render a plausible path.

Waypoint example:

```xml
<mxCell id="edge-a-b" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;" edge="1" parent="1" source="a" target="b">
  <mxGeometry relative="1" as="geometry">
    <Array as="points">
      <mxPoint x="420" y="220" />
      <mxPoint x="420" y="360" />
    </Array>
  </mxGeometry>
</mxCell>
```

## Bad Vs Good Route Examples

Bad route:

```xml
<mxCell id="edge-bad-return" value="retry" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;" edge="1" parent="1" source="verify" target="plan">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

Why it is bad:

- no explicit waypoints even though the edge is a long return loop
- no side anchoring, so draw.io may pick a visually different entry or exit
  side after reopen
- the route is likely to cut back through the center of the page

Good route:

```xml
<mxCell id="edge-good-return" value="retry" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;entryX=0.5;entryY=0;endArrow=block;" edge="1" parent="1" source="verify" target="plan">
  <mxGeometry relative="1" as="geometry">
    <Array as="points">
      <mxPoint x="760" y="280" />
      <mxPoint x="760" y="80" />
      <mxPoint x="220" y="80" />
      <mxPoint x="220" y="180" />
    </Array>
  </mxGeometry>
</mxCell>
```

Why it is good:

- the route leaves from the outer side of the source and re-enters from a
  clearly chosen side
- the waypoints move the return loop onto a perimeter corridor instead of
  across the center
- reopening the file preserves the intended path

## Multi-Page Guidance

- Use separate `<diagram>` elements for overview, deep dive, and legend pages.
- Keep page names explicit: `Overview`, `Ingestion Pipeline`, `User Journey`, `Legend`.
- Reuse visual semantics across pages.
- Repeat key systems across pages when necessary instead of overloading a single canvas.

## Export Workflow

Prefer the bundled export helper:

```bash
python3 scripts/export_drawio.py diagram.drawio --format png
python3 scripts/export_drawio.py diagram.drawio --format svg --page-index 1
python3 scripts/export_drawio.py diagram.drawio --format pdf --all-pages
```

The helper locates the draw.io CLI, exports the diagram, and embeds the diagram XML for `png`, `svg`, and `pdf`.

The helper may refuse to launch the desktop app unless you pass
`--allow-desktop-export` or set `DRAWIO_ALLOW_DESKTOP_EXPORT=1`. That block is
intentional when the resolved command is the official desktop binary. If you use
`DRAWIO_CMD`, point it at a safer wrapper or renderer when possible; pointing it
at the official desktop binary will still be treated as desktop export.

If you need the raw CLI:

```bash
/Applications/draw.io.app/Contents/MacOS/draw.io -x -f png -e -b 10 -o diagram.drawio.png diagram.drawio
```

Useful flags:

- `-x`: export mode
- `-f`: output format
- `-e`: embed diagram XML for `png`, `svg`, and `pdf`
- `-b`: border width
- `-s`: scale
- `-t`: transparent background for PNG
- `-a`: export all pages for PDF
- `-p`: export a specific page index, 1-based

## Editing Rules

- Preserve existing IDs when editing a file unless there is a concrete structural problem.
- Keep `parent="1"` unless you intentionally nest cells or assign a custom layer.
- Escape user-provided text through normal XML serialization instead of hand-assembling unsafe strings.
- Prefer readable IDs over random GUIDs for generated files.
- Use `compressed="false"` unless the user explicitly needs the compact encoded representation.

## Troubleshooting

- Diagram opens blank:
  - Check that cells `0` and `1` exist and that shapes use the correct `parent`.
- Edges do not render:
  - Check for a missing child `mxGeometry` or invalid `source` and `target` IDs.
- Edge path changes after reopen:
  - Add explicit waypoints or other edge geometry instead of relying on draw.io auto-routing.
- Arrows are readable in export but still merge through the diagram body:
  - Change layout, spacing, or page split first, then move the route to a
    perimeter corridor with explicit points.
- Literal `\n` appears in labels:
  - Replace it with `<br>` and keep `html=1`.
- Export fails:
  - Confirm the draw.io desktop CLI exists, then retry with `scripts/export_drawio.py --format ...`.
  - If the helper says export is blocked in safety mode, stop and report the
    limitation unless you are actively requesting approval to rerun the same
    helper with `--allow-desktop-export`.
  - Do not substitute `qlmanage`, browser rendering, screenshots from another
    viewer, or any other non-draw.io export path for official visual QA.
- Exported file is not editable in draw.io:
  - Use `png`, `svg`, or `pdf` so the helper can embed the diagram XML.

## XML Well-Formedness

When generating draw.io XML, the output must be well-formed:

- Never include XML comments.
- Escape special characters in attribute values.
- Keep all `mxCell` IDs unique within a page.
- Ensure every edge has a child `mxGeometry`.
- Ensure connector routing is encoded in geometry rather than left to draw.io behavior.
- For non-trivial routes, include explicit waypoint geometry and any needed side
  anchoring rather than hoping draw.io will infer the correct corridor.
