# Draw.io Diagram Patterns

## Table Of Contents

- Flowcharts
- Architecture diagrams
- Sequence-like interaction maps
- State diagrams
- Trees and mind maps
- Org charts
- Containers and nested diagrams
- Edge routing
- Route examples
- Large diagrams

## Flowcharts

- Use a single dominant direction: top-to-bottom or left-to-right.
- Reserve diamond nodes for true branch points only.
- Put yes and no labels on outgoing edges, not inside the diamond.
- Keep step boxes aligned to a coarse grid.
- End each major branch with an explicit terminator or merge.

## Architecture Diagrams

- Start with trust or ownership boundaries: client, edge, application, data, external systems.
- Use containers or swimlanes for zones such as `Frontend`, `Backend`, `Data`, `Third-party`.
- Place high-traffic request paths on the shortest visual route.
- Use dashed edges for async signals, background jobs, and indirect dependencies.
- Put protocols on edges when they add meaning: `HTTPS`, `gRPC`, `Kafka`, `S3 event`.

## Sequence-Like Interaction Maps

- Use vertical swimlanes or tall columns for participants.
- Stack events vertically in time order.
- Use thin, mostly horizontal connectors between participants.
- Prefer numbered edge labels or concise action text such as `1. Submit order`.
- Split very long timelines into phases or pages.

## State Diagrams

- Use a clear dominant flow, usually top-to-bottom.
- Use rounded rectangles or process boxes for states and terminators for explicit start or finish points.
- Put events or conditions on transitions rather than inside state boxes.
- Show retry, wait, or failure loops explicitly so the control cycle is readable at a glance.
- Keep transitions sparse; if every state links to every other state, split the diagram into phases or pages.

## Trees And Mind Maps

- Place the root centrally for mind maps or at the top for hierarchical trees.
- Keep sibling spacing consistent.
- Limit text length per node so the branching structure stays legible.
- Use color sparingly to distinguish depth-one branches or categories.

## Org Charts

- Keep one box size per rank whenever possible.
- Use vertical connectors for reporting lines.
- Put functional notes in smaller secondary boxes or as short subtitles.
- Avoid crossing lines; widen the chart instead.

## Containers And Nested Diagrams

- Use true containment when a visual boundary owns children. Put child cells under the container with `parent="containerId"` and relative coordinates.
- Use `swimlane` when the container needs a visible title bar or when the container itself participates in connections.
- Use a lightweight container or `group;pointerEvents=0;` when you only need grouping and do not want the parent to capture rewired connections.
- Do not add complicated detours just to avoid crossing a parent container when an edge targets a child inside it. Crossing the boundary is expected.

## Edge Routing

- Use one primary edge style within a diagram.
- Prefer elbow edges for simple 0-1 bend routes.
- Prefer orthogonal edges when a route needs 2+ bends around obstacles.
- Avoid edge segments that cut through unrelated nodes.
- Treat edge-vertex crossings as defects. When conflicts are unavoidable, prefer
  edge-edge crossings over edge-vertex crossings.
- Use labels on edges only when they add meaning such as protocol, decision branch, or event name.
- Adjust node layout and spacing first, then encode the accepted route with
  explicit edge geometry.
- Do not leave the final connector path to draw.io auto-routing or post-open
  handle behavior.
- `edges[].points` are mandatory when a route changes axis, bypasses an
  obstacle, crosses lane or zone space, links non-adjacent nodes, or carries a
  return loop around the perimeter.
- Use `entryX`, `entryY`, `exitX`, and `exitY` when the side of attachment
  affects readability.
- Keep at least `24 px` between peer non-container nodes, `24 px` between nodes
  and page edges, `32 px` between nodes and swimlane borders, and `12 px`
  between an edge and an unrelated node whenever possible.
- Route long back-edges around the outside of the page rather than through the
  center of the main reading path.
- If the first routing pass still leaves more than one core crossing or more
  than two long back-edges through the middle, split the material across pages.

## Route Examples

Bad route:

- A return edge leaves the right side of a downstream node, cuts back through
  the middle of the page, and passes over a note or intermediate system.
- Two parallel arrows sit on the same centerline with no offset, so the viewer
  cannot tell which arrow belongs to which source.
- The edge has no explicit waypoints even though it changes axis and crosses a
  lane boundary.

Good route:

- The primary path stays on the shortest visual route through the center.
- The return loop exits from the outer side of the source, travels along a
  perimeter corridor, and re-enters the target from a clearly different side.
- The route uses explicit waypoints plus side anchoring so reopening the file
  does not reroute it through the diagram body.

Good XML example:

```xml
<mxCell id="edge-review-loop" value="revise" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;entryX=0.5;entryY=0;endArrow=block;" edge="1" parent="1" source="verify" target="plan">
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

## Large Diagrams

- Produce an overview page first.
- Break detail into separate pages by subsystem, phase, or persona.
- Add a small legend page when colors, line styles, or icons carry meaning.
- Prefer duplication across pages over extreme connector density.
- Keep each page readable at normal zoom instead of relying on endless canvas size.
