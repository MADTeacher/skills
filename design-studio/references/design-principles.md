# Design Principles

This reference extracts the quality bar from the original system prompt:
content discipline, visual taste, hierarchy, typography, color, accessibility,
feedback, and system thinking.

## No Filler

Every element must earn its place. If it does not communicate something
necessary, advance the narrative, or create needed structure, cut it.

Check each element with these questions:

1. Does it answer a real user question?
2. Does it advance the narrative?
3. Is the page understandable without it?
4. Is there a clearer, shorter way to say this?
5. Does it serve the user or only the designer?

Common filler patterns:

- lorem ipsum where real copy is needed;
- invented stats and claims;
- redundant headline / subhead / paragraph stacks;
- decorative clutter such as meaningless patterns, emoji-for-color, or overlays
  with no job;
- data slop: long tables, extra columns, and 10-item lists that should be 3.

If the design seems to need another section or more copy, ask the user first.
Empty space is a layout challenge, not an excuse to invent content.

## Purposeful Visuals

Every visual decision needs a reason. Do not use trends as autopilot.

Avoid the default AI-slop patterns:

- aggressive gradients;
- decorative emoji;
- `border-left + rounded corners` as the default card formula;
- weak hand-drawn SVG illustration attempts;
- overused default fonts without intent;
- pure white and pure black on large surfaces.

When possible, use real brand values. If you must build a palette from scratch,
keep color discipline:

- one temperature family: warm, cool, or neutral;
- 3-5 core colors at most;
- controlled lightness and chroma;
- subtly toned whites and blacks instead of extremes.

For imagery, an honest placeholder is better than a fake final asset.

## Hierarchy and Rhythm

Hierarchy determines what is seen first, second, and third. Rhythm determines
whether the work feels composed.

Hierarchy signals:

- size;
- color intensity;
- weight;
- position;
- spacing density.

The most important content usually gets several of these signals at once.

For rhythm:

- use a spacing scale instead of random values;
- repeat patterns, then break them strategically;
- limit the number of surface and background treatments;
- keep alignment disciplined.

If the eye path is not clear within 5 seconds, the hierarchy is weak.

## Typography

- keep to 1-2 font families;
- define a real type scale;
- keep body text readable and reserve display styles for short emphasis;
- avoid large all-caps blocks;
- use `text-wrap: pretty` where appropriate.

Practical minimums:

- slides: 24px+ body, ideally 32px+;
- print: 12pt+;
- mobile: 16px+ body;
- touch targets: 44px x 44px+;
- desktop body: typically 14-16px.

## Color System

Define a palette and use it consistently:

- brand colors;
- semantic colors;
- a neutral scale;
- surface, border, and foreground colors.

Do not communicate state with color alone. Avoid difficult combinations such as
red-green, light gray on white, and colored surfaces with nearly identical
lightness.

## Accessibility and Inclusivity

Accessibility is not a later pass. It is part of design quality.

Check:

- WCAG contrast;
- semantic HTML;
- keyboard reachability and logical tab order;
- visible focus rings;
- alt text;
- labels on inputs;
- `prefers-reduced-motion`;
- clear form errors;
- appropriate input types and autocomplete.

If something looks polished but is inaccessible, it is not finished.

## Interaction and Feedback

Every interaction needs feedback:

- default;
- hover;
- active or pressed;
- focus;
- disabled;
- loading, when the action is async.

Transitions should feel responsive without lag. Errors, successes, and
validation states should be visible and tied to the place where the action
happens.

## One Clear CTA

A screen has one primary action. Everything else should support it, not compete
with it.

Default simplifications:

- fewer top-level options;
- fewer fields up front;
- secondary options hidden behind tabs, accordions, or "show more";
- if everything shouts, nothing is primary.

## System Thinking

Design components, not one-off pages.

Define and reuse:

- buttons;
- cards;
- inputs;
- modals;
- toasts;
- table rows;
- layout patterns;
- tokens.

For components, document usage, variants, states, accessibility notes, and
do/don't guidance. That is how a UI becomes a system instead of a pile of
one-offs.
