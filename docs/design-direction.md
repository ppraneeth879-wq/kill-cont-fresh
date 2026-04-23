# KillCont Design Direction

Last revised: 2026-04-14

This document translates the user-provided `Design.md` into a KillCont-specific design system.

The inspiration is Framer's pure-black, product-forward, precision-heavy visual language.

KillCont should adapt that language for a live sports-media protection product.

## Core Visual Thesis

- The website should feel like a premium command center floating in a black void.
- The product UI should act as the hero art.
- Electric blue should remain the main interaction accent.
- Motion should later be added to the shared background layer, not scattered randomly across components.

## Shared Background Rule

- All pages should share one common background system derived from the hero.
- The background should live behind both marketing and authenticated app pages.
- The background should be dark, quiet, and spatial.
- It should support later motion additions without requiring page redesign.

Recommended ingredients:

- pure black base
- subtle radial blue glow
- low-opacity field/grid lines
- faint spotlight behind the primary page content
- no loud gradients

## KillCont-Specific Adaptation

Framer's system uses one accent color almost exclusively.

KillCont should keep that for brand and interaction language:

- blue for links
- blue for focus and borders
- blue for selected and active UI states

But KillCont is also an operational product, so the application needs restrained semantic states:

- verified trust: muted teal-tinted signal
- monitor: restrained amber
- strike / escalate: restrained red

These semantic colors should appear only inside the authenticated product experience where they help operators parse risk.

They should not replace blue as the primary brand accent.

## Typography Direction

Target typography stack:

- display: GT Walsheim if available, otherwise a geometric fallback such as Sora
- body: Inter
- mono: Azeret Mono

Typography rules:

- use compressed, tight display text
- keep headlines bold in form but not heavy in weight
- maintain strong negative letter spacing on major displays
- let body text stay readable and calm

## UI Surface Rules

- pure black page background
- near-black panels
- soft blue ring borders
- pill-shaped interactive elements
- product screenshots and dashboard panels as visual anchors
- glass-like controls only where they improve hierarchy

## Layout Rules

- generous vertical spacing between sections
- tighter density inside cards and dashboard panels
- wide centered marketing container
- side-by-side text and product views on desktop
- stable app shell in the product

## Motion Rules

Motion will be added later, so the structure should already support it.

Reserve motion primarily for:

- global background drift or signal sweeps
- incident arrival
- panel reveal
- map propagation pulses
- live timeline updates

Do not rely on motion for comprehension.

## Product UI Priorities

The most visually important product surfaces should be:

- the overview dashboard
- the incident detail screen
- the threat map
- the live watch screen

These pages should feel like "product as proof," which matches the original design inspiration.

## Screenshots As Product Art

- whenever possible, use real UI panels as the visual centerpiece
- avoid decorative illustrations
- let the dashboard, evidence view, and map act as the hero visuals

## Component Translation

### Buttons

- default interaction shape: full pill
- primary CTA: solid white pill on black
- secondary CTA: frosted white pill
- tertiary action: ghost or text-only

### Cards

- near-black surface
- subtle blue ring border
- rounded but not overly soft

### Navigation

- fixed dark header
- white text
- compact spacing
- pill CTA on the right

### Inputs

- dark fields
- subtle border
- blue focus ring
- soft placeholder contrast

## KillCont Visual Personality

KillCont should feel:

- elite
- deliberate
- technical
- calm under pressure
- designed for rights operations, not consumers

It should not feel:

- playful
- colorful
- warm
- generic
- cyberpunk

## Implementation Note

Because GT Walsheim is not guaranteed to be available in the codebase, the first implementation should use a close fallback for display typography while keeping the same spacing and weight behavior.

The important thing is the silhouette and compression of the headline system, not a perfect font match on day one.
