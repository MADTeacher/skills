# Visual Checklist

Use this checklist against the latest export. When the user will work in draw.io
or diagrams.net itself, apply the same checklist again to the reopened editor
canvas.

## Source Hygiene

- One working `.drawio` file only.
- No leftover `*.skill-test.drawio` or `*.tmp.drawio` siblings.
- No stale `*.review.jpg`, `*.review.png`, `*.tmp.png`, or `*.tmp.jpg` files
  near the source.

## Layout Gate

- `scripts/check_drawio_layout.py` reports `0 FAIL`.
- Any remaining warning has been fixed or verified as a false positive against
  the latest export and, when required, the reopened editor view.
- Peer non-container nodes keep at least `24 px` of breathing room.
- Nodes stay at least `24 px` from the page edge and `32 px` from swimlane
  borders.
- Edge-to-shape clearance stays above `12 px` unless the latest export proves
  the warning harmless and still clearly readable.

## Edge Quality

- No arrow crosses a node, note, or label.
- No arrow rides on top of a swimlane border.
- No route passes through an unrelated non-container shape, even if the
  resulting line still technically renders.
- No edge label sits directly on another line.
- Line weight and arrowheads are strong enough to read at ordinary zoom without
  squinting.
- Long return lines are avoided unless they are essential and still readable.
- Non-trivial routes use explicit waypoints and, when needed, side anchoring so
  the entry and exit sides are obvious.
- Multiple arrows do not collapse into one shared corridor so tightly that their
  ownership becomes ambiguous.
- Edge-edge crossings are avoided in the core content area unless there is no
  cleaner layout and the result is still unambiguous.

## Shape Quality

- Every shape has visible breathing room from swimlane borders and page edges.
- No shape border is clipped.
- Notes and titles are fully visible.
- Text stays inside its own shape and does not visually spill past borders.
- Neighboring shapes are not so close that their borders visually merge.

## Layout Quality

- The main reading path is obvious.
- Empty space is intentional rather than accidental.
- Visual semantics are consistent within the same file or page family.
- The page is not pretending to be one canvas when it should really be overview
  plus detail pages.
- If the first routing pass would require more than one core crossing or more
  than two long back-edges through the center, the content is split instead of
  squeezed.
- If editor rendering matters, the reopened editor view also passes.
- Do not let a clean export override a dirty editor canvas.

## Exit Rule

Do not finish the task until the latest export and, when applicable, the
reopened editor view both pass every applicable checkpoint above, the layout
gate reports `0 FAIL` and `0 unresolved warnings`, or the user explicitly
accepts a remaining defect.
