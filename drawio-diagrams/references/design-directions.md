# Visual Directions For Draw.io Diagrams

Use this guide when the user asks for a cleaner, more polished, more modern, or
more presentation-ready diagram, or when style is not specified and you need to
propose alternatives.

## How To Propose Directions

If style is not fixed, propose three contrasting directions:

- one safe or business-like
- one explanatory or editorial
- one more expressive but still appropriate

Each direction must change how the diagram reads: page structure, spacing, line
weight, typography, color semantics, and label density. Do not present a simple
palette swap as a new direction.

## Direction Matrix

| Direction | Best for | Visual grammar | Diagram families | Editor/export fit | Risk |
|---|---|---|---|---|---|
| Executive Systems Map | board updates, leadership reviews, architecture summaries | high-level zones, strong headers, low label density, clear ownership color | architecture, operating model, capability map | very safe for editor and export | too little detail for engineering readers |
| Technical Systems | engineering architecture, AI pipelines, backend flows | modular boxes, precise routing, semantic color, mono accents only where useful | architecture, state, dependency, platform | very safe for editor and export | too dense if every system gets equal weight |
| Operational Swimlanes | cross-team operations, handoffs, runbooks | swimlanes, phase markers, explicit responsibilities, readable edge labels | process, workflow, incident, approval | very safe for editor and export | lane borders can dominate if spacing is weak |
| Product Journey | user journey, feature walkthroughs, lifecycle views | stage-based storytelling, touchpoints, supporting notes, product-friendly color | journey, service blueprint, flowchart | safe for editor and export | becomes vague if product steps are not concrete |
| Research / Causal Map | research synthesis, hypothesis trees, causes and effects | clustered evidence, causal arrows, note-like callouts, medium label density | causal map, concept map, system map | export-safe, editor-medium when very dense | turns noisy if every relation is shown at once |
| Teaching Visual Guide | classroom diagrams, training, explainers | guided reading path, larger labels, friendly spacing, explicit examples | flowchart, anatomy-like maps, explainers, concept maps | very safe for editor and export | can feel childish if tone is too playful |
| Dataflow Blueprint | data movement, ingestion, analytics pipelines | channels, storage zones, event arrows, stronger line hierarchy | dataflow, platform, integration, ETL | very safe for editor and export | decorative pipe metaphors can distract |
| Concept Poster Diagram | keynote visuals, section openers, one-idea diagrams | bold central statement, sparse nodes, poster rhythm, minimal labels | overview, thesis map, conceptual framing | export-safe, editor-medium | style can overpower substance |

## Executive Systems Map

- Best for: executive briefings, steering committees, status snapshots, and
  overview architecture pages that must reduce complexity quickly.
- Overview page: 4-8 major zones, short labels, and one clear reading direction.
- Dense detail page: only if needed; keep it as a secondary page with preserved
  zone colors and stronger local grouping.
- Typography: strong sans headings, short labels, no decorative mono.
- Line weight: medium to strong for core flows.
- Spacing: generous margins and wide separation between zones.
- Color semantics: ownership or domain color, not technical status color unless
  status is the point.
- Label density: low.
- Split into overview and detail when more than one audience needs the same
  diagram.
- Anti-patterns: squeezing engineering-level dependencies onto the summary page,
  or filling every zone with tiny secondary labels.

## Technical Systems

- Best for: architecture diagrams, AI pipelines, runtime systems, backend and
  platform explanations.
- Overview page: major subsystems, trust boundaries, and the shortest visual path
  for primary traffic.
- Dense detail page: richer connectors, storage, queues, retries, or states, but
  still grouped by subsystem.
- Typography: readable sans with mono only for technical labels that benefit
  from it.
- Line weight: medium by default; stronger for primary paths than for background
  dependencies.
- Spacing: even, modular, and grid-aligned.
- Color semantics: internal systems, external systems, data stores, and async
  paths should have stable meanings.
- Label density: medium.
- Split when the full system would require scrolling or unreadable connectors at
  normal zoom.
- Anti-patterns: twenty equal-weight nodes, pseudo-code as texture, or thin
  arrows that disappear at ordinary zoom.

## Operational Swimlanes

- Best for: approvals, multi-team workflows, incident response, support
  operations, and process ownership maps.
- Overview page: phases or actors across clearly separated lanes with a single
  primary path.
- Dense detail page: exception paths, loops, and escalation branches inside the
  same lane system.
- Typography: steady sans labels with strong lane titles.
- Line weight: medium with clearly readable arrowheads.
- Spacing: extra breathing room near lane borders so lines do not visually merge
  with them.
- Color semantics: one neutral lane system plus one signal color for decisions,
  exceptions, or SLAs.
- Label density: medium.
- Split when one page would mix overview ownership and every exception branch.
- Anti-patterns: treating lane borders as decoration, stacking nodes too close to
  lane edges, or letting edge labels sit on top of borders.

## Product Journey

- Best for: user journeys, onboarding flows, lifecycle experiences, and product
  walkthroughs that need a narrative feel.
- Overview page: stages or milestones with clear progression and a few decisive
  touchpoints.
- Dense detail page: supporting notes, backstage systems, or handoffs beneath
  the main user path.
- Typography: product-friendly sans, short phrases, and helpful subtitles.
- Line weight: medium, with a clear dominant path and quieter secondary links.
- Spacing: airy enough that each stage reads as a chapter.
- Color semantics: stages or personas first, not arbitrary rainbow accents.
- Label density: low to medium.
- Split when one page would have both user path storytelling and system detail.
- Anti-patterns: generic startup gradients, vague verbs, or calling something a
  journey when it is really an internal process map.

## Research / Causal Map

- Best for: research synthesis, causal explanations, hypothesis trees, and
  diagrams that connect evidence to interpretation.
- Overview page: 3-6 clusters with clear causal or thematic links.
- Dense detail page: supporting evidence notes, qualifiers, or sub-clusters that
  preserve the top-level grouping.
- Typography: readable sans with note-like secondary text.
- Line weight: medium for primary causes, lighter for supporting or uncertain
  links.
- Spacing: clustered, but never so tight that notes become a wall of text.
- Color semantics: claim, evidence, risk, and open question can each carry a
  stable role.
- Label density: medium to high.
- Split when causal clarity is lost under too many edges or annotations.
- Anti-patterns: showing every possible relationship, or using identical visual
  weight for certainty and speculation.

## Teaching Visual Guide

- Best for: classroom diagrams, training material, concept explainers, and
  step-by-step educational visuals.
- Overview page: one clear reading path with larger labels and explicit anchors.
- Dense detail page: annotated examples, supporting notes, or decomposed parts
  with stable callouts.
- Typography: larger sans labels and very clear hierarchy.
- Line weight: medium to strong so the reading path survives projection or
  printed review.
- Spacing: roomy and forgiving, especially around notes and examples.
- Color semantics: a small friendly palette with stable roles such as concept,
  example, warning, and result.
- Label density: low to medium.
- Split when the explanatory page would otherwise become a reference sheet.
- Anti-patterns: replacing real explanation with decoration, or making it look
  playful when the audience or topic needs seriousness.

## Dataflow Blueprint

- Best for: ETL flows, ingestion pipelines, event systems, analytics platforms,
  and integration maps.
- Overview page: ingress, transformation, storage, and consumption arranged as
  clearly distinct zones.
- Dense detail page: protocols, queues, jobs, schemas, and failure or retry
  paths.
- Typography: practical sans; use mono sparingly for topic names, schema names,
  or event labels.
- Line weight: strongest on main data paths, lighter on control or metadata
  paths.
- Spacing: wide channels between pipeline stages.
- Color semantics: storage, compute, external source, consumer, and async event
  roles stay consistent.
- Label density: medium.
- Split when the full pipeline has both conceptual overview and operational
  detail.
- Anti-patterns: decorative pipes, forcing every topic name onto the overview
  page, or equal visual emphasis for data and control flows.

## Concept Poster Diagram

- Best for: keynote section openers, conceptual framing pages, one-idea
  diagrams, and diagrams that need to land a strong thesis quickly.
- Overview page: one dominant statement or node with a few supporting relations.
- Dense detail page: usually avoid it; if needed, treat detail as a separate
  explanatory page rather than a denser version of the poster.
- Typography: bold, high-contrast, and intentionally sparse.
- Line weight: strong and simple.
- Spacing: very generous.
- Color semantics: minimal palette with one clear accent.
- Label density: very low.
- Split when the poster concept needs a follow-up explanation page to stay
  honest.
- Anti-patterns: empty spectacle, oversized typography without informational
  value, or calling a dense systems diagram a poster.
