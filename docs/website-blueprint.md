# KillCont Website Blueprint

Last revised: 2026-04-21

## Current Build State (2026-04-21)

- The app shell and page system are implemented and kept visually consistent with the established command-center language.
- Core product pages are wired to backend API data for MVP operator flow.
- Live updates are currently delivered with SSE from the FastAPI runtime.
- The next transition is infrastructure-level (public hosting and cloud backends), not a visual redesign.

## Experience Goal

The website should feel like a modern sports rights command center on a pure-black cinematic canvas:

- premium
- controlled
- trustworthy
- dynamic
- clearly live

It should not feel like:

- a generic SaaS admin template
- a research dashboard
- a developer console
- a legal form system

## Product Shape

The website has two major surfaces:

1. Public marketing and product introduction
2. Authenticated monitoring application

All pages should share one common hero-derived background system so later motion design can be layered in without redesigning every route.

## Public Surface

### Landing Page Goals

- explain the problem fast
- make the product look credible
- set the command-center visual tone
- make the shift from "media chaos" to "visibility and control" memorable

### Landing Sections

1. Hero
2. Signal strip / live incident marquee
3. How KillCont works
4. Why it stands out
5. Command center preview
6. Authenticity plus AI section
7. Sports today, other media tomorrow
8. CTA to sign in or request demo

### Hero Direction

Recommended hero copy angle:

- "Protect official sports media before it disappears into the web."

Visual behavior:

- shared black-background system used everywhere
- subtle radial blue glow
- low-opacity field or arena-grid texture
- one bold dashboard preview card
- restrained floating signal markers

## Authenticated App Information Architecture

Primary navigation:

- Overview
- Assets
- Monitor
- Incidents
- Live Watch
- Evidence
- Settings

Global shell elements:

- top navigation
- live sync badge
- search
- organization switch placeholder
- notification rail
- user avatar

## Screen 1: Overview Dashboard

Purpose:

- answer "what is happening right now?"

Must show:

- active incidents count
- new detections today
- monitored assets count
- average detection latency
- top affected platforms
- active map cluster panel
- live incident stream
- severity distribution

Best layout:

- strong KPI row
- left-column live feed
- center command map
- right-column action queue

## Screen 2: Assets

Purpose:

- manage official protected media

Must show:

- asset cards or table
- upload CTA
- type filters
- event filters
- provenance badge
- monitoring status
- incident count per asset

Asset detail must show:

- preview
- metadata
- embedding status
- provenance summary
- protected segments or keyframes
- related incidents

## Screen 3: Monitor

Purpose:

- show incoming monitored content before or during incident creation

Must show:

- feed source
- timestamp
- source post
- media preview
- similarity pre-score
- status chip

Useful behavior:

- auto-updating rows
- freeze and inspect mode
- filters by platform, severity, asset, and confidence

## Screen 4: Incidents

Purpose:

- be the operator's main workbench

Must show:

- incident list
- severity
- asset matched
- platform
- trust score
- spread score
- triage label
- action state

Incident detail should be the strongest workflow in the product.

It should include:

- side-by-side media comparison
- matched frame strip
- provenance status
- explanation panel
- timeline
- platform metadata
- operator notes
- action buttons

## Screen 5: Live Watch

Purpose:

- prove near-real-time monitoring of short video segments

Must show:

- active event or stream
- latest segments
- live detections
- segment latency
- rolling chart
- "restream suspected" moments

The screen should feel urgent and kinetic.

## Screen 6: Evidence

Purpose:

- bundle findings into something credible and portable

Must show:

- selected incident
- summary
- matched asset
- similarity details
- source details
- provenance details
- export / prepare action panel

Even if legal automation is not fully built, the evidence screen makes the product feel serious.

## Threat Map Blueprint

The threat map is a centerpiece, not a side widget.

### Required Behaviors

- cluster when zoomed out
- pulse active incidents
- connect propagation relationships
- filter by asset, platform, time, and severity
- allow click-through to incident detail

### Map Narrative

The map should answer:

- where suspicious media surfaced first
- where it spread next
- where the current hotspots are

### Data Strategy

Use inferred or simulated coordinates where needed.

This is acceptable because the point is propagation visibility, not forensic geolocation certainty.

## Motion System

Motion must support meaning.

Recommended motion types:

- shared background drift or signal sweeps
- data pulse for live updates
- line sweep for ingestion flow
- card reveal for new incidents
- map pulse for spread hotspots
- timeline scrub motion for incident replay

Avoid:

- random floating animations
- over-bouncy interactions
- excessive blur transitions

## Visual Direction

Tone:

- corporate sports-tech
- broadcast-grade
- premium and product-forward
- dark, precise, and calm under pressure

Recommended palette structure:

- pure black as the main canvas
- pure white for primary text
- electric blue for interactive accent and containment rings
- near-black for elevated panels
- muted silver for secondary text
- restrained semantic states only inside the app:
- muted teal for verified trust
- restrained amber for monitor
- restrained red for strike

Recommended typography:

- display: GT Walsheim if available, otherwise Sora as the closest practical fallback
- body: Inter
- mono: Azeret Mono

Shared background rule:

- all pages should reuse one hero-derived background system
- the background should stay consistent across landing and app pages
- motion can be layered into that shared background later without redesigning each page

## Component Priorities

Highest priority components:

- incident card
- trust badge
- evidence comparison viewer
- upload modal
- map legend
- live feed ticker
- action queue card
- platform pill
- risk meter

## Responsive Behavior

Desktop first, but mobile-safe.

### Desktop

- command center layout
- persistent side panels
- map as primary focus

### Tablet

- stacked incident detail
- map collapses into tab

### Mobile

- simplified overview
- limited evidence comparison
- no assumption of full operator workflow

## UX Rules

- Every alert must answer "why."
- Every score must have plain-language support text.
- Every important page must include one clear primary action.
- Every live update must be visually distinct without being noisy.
- Empty states must still teach the product.
- Demo states must be handcrafted and believable.

## Demo UX Hooks

To impress judges quickly:

- preload one active tournament or match event
- show live signals immediately after sign-in
- make the first incident open with a rich evidence panel
- animate the map and timeline during the demo
- let one click switch from overview to proof

## Future-Proofing Beyond Sports

The UI should mention sports first but not hard-code sports everywhere.

Prefer labels like:

- asset
- rights holder
- campaign
- event
- incident

Over overly narrow labels like:

- match clip only
- goal-only incident

This keeps expansion to news, entertainment, and creator media easier later.
