# KillCont Mindset

Last revised: 2026-04-21

## Current Execution Reality (2026-04-21)

- The local-first MVP flow is implemented and verified end-to-end on the active branch workspace.
- Runtime today is FastAPI + SQLite + local media + SSE, with demo bearer-token auth.
- Frontend operator surfaces are wired to live backend routes (not scaffold-only mock state).
- The immediate next phase is public deployment profile work:
	- Firebase Hosting (web)
	- Cloud Run (API)
	- Firestore (metadata)
	- Cloud Storage (media)
- Local mode remains mandatory for fast demo reset and offline fallback.

This document is the master planning brain for KillCont.

It exists so the team can move fast without drifting.

It is intentionally detailed.

It should be treated as:

- the product direction document
- the implementation planning document
- the scope guardrail document
- the demo narrative document
- the team alignment document

## 0. Document Rules

- Read this before implementing new features.
- Update `docs/status.md` when a module changes state.
- Update `docs/logbook.md` after every meaningful build session.
- If a decision here becomes wrong, change this file instead of keeping invisible assumptions in chat.
- Keep the product hackathon-sized.
- Never add CI/CD to this project.
- Never plan for training our own LLMs or custom foundation models.
- Prefer managed services when they save time.
- Favor one polished flow over three half-finished flows.
- Favor explainability over raw algorithmic complexity.
- Favor evidence-centered UX over back-office admin features.

## 1. Project Identity

- Project name: KillCont
- Product category: digital media protection platform
- Launch context: Google Solution Challenge hackathon
- Primary industry: sports media
- Expansion direction: news, entertainment, creator content, education, brand media
- Main interface: web application
- Demo audience: hackathon judges, mentors, potential operators, technical reviewers
- Core user: rights holder operations lead
- Supporting users: digital rights analyst, content protection lead, media integrity reviewer, tournament admin

## 2. One-Line Positioning

- KillCont helps rights holders authenticate official media, detect altered or redistributed copies, and act from one live command center.

## 3. Short Pitch

- Sports organizations lose visibility the moment official media spreads across the internet.
- KillCont restores that visibility.
- It combines provenance, AI similarity matching, and realtime monitoring into one operator workflow.
- Official assets are registered and optionally tied to authenticity metadata.
- Monitored images, clips, and live segments are converted into embeddings and matched against protected assets.
- Suspicious content becomes incidents with trust signals, evidence, spread context, and action recommendations.

## 4. Judge-Friendly Story

- Step one: this is a real problem with clear economic and reputational impact.
- Step two: current approaches are fragmented.
- Step three: KillCont solves the visibility gap with a layered trust model.
- Step four: we built a working operator experience, not just a model demo.
- Step five: the product uses Google Cloud services in a purposeful way.
- Step six: the system is realistic for sports now and extensible beyond sports later.

## 5. Core Product Thesis

- The project should not behave like a feature list.
- The project should behave like a chain of confidence.
- Trust starts at asset registration.
- Detection starts when outside content is observed.
- Proof is built from multiple signals.
- Action becomes possible only after confidence is understandable.
- The UI should tell that story without requiring a long verbal explanation.

## 6. The Strongest Version Of The Product

- The strongest version of KillCont is not the one with the most connectors.
- The strongest version is the one where a judge can follow one suspicious clip from detection to evidence to decision in under 60 seconds.
- If a judge remembers one thing, it should be that KillCont makes invisible media spread visible and actionable.

## 7. Product Principles

- Principle: operator-first
- Meaning: design for the person responsible for deciding what to do next

- Principle: evidence before action
- Meaning: do not ask users to trust an unexplained score

- Principle: layered confidence
- Meaning: combine provenance, similarity, source context, and spread behavior

- Principle: live by default
- Meaning: the product should feel current, not batch-only

- Principle: premium clarity
- Meaning: the interface should feel calm, deliberate, and controlled even while showing active threats

- Principle: sports now, platform later
- Meaning: every naming and architecture decision should allow later expansion beyond sports

- Principle: hackathon realism
- Meaning: only build what can be implemented and demonstrated convincingly in six days

## 8. Problem Statement In Product Language

- High-value sports media is created at speed.
- That media travels fast across social platforms, short-video apps, messaging channels, and repost networks.
- Once it escapes the original distribution path, rights holders lose visibility.
- Traditional hash-based methods fail after simple edits.
- Logo-based protection fails when logos are cropped or blurred.
- Manual review is too slow for live or near-live media.
- Platform-specific tooling is fragmented and incomplete.
- Rights holders need a system that helps them know:
- what official asset is being reused
- where it is appearing
- whether it is likely harmful
- how fast it is spreading
- what evidence exists
- what action makes sense next

## 9. Why Sports Is A Strong Entry Point

- Sports media is high frequency.
- Sports media is time sensitive.
- Sports clips spread globally during active events.
- Broadcast and licensing rights are commercially valuable.
- Unauthorized highlights and rebroadcasts are common.
- The emotional intensity of sports creates rapid fan sharing and piracy simultaneously.
- That makes sports a perfect proving ground for a trust-plus-detection product.

## 10. Why This Can Expand Beyond Sports

- The core unit is a digital asset, not a sports-only object.
- The core workflow is authenticity, monitoring, incident review, and action.
- The core AI work is multimodal similarity and bounded reasoning.
- The dashboard pattern applies to brands, newsrooms, studios, and creators.
- Therefore the sports framing should be strong in copy, but the system model should remain category-flexible.

## 11. Target User Personas

### Persona 1: Rights Protection Lead

- Owns: enforcement quality
- Cares about: unauthorized distribution, evidence, speed
- Pain: too many feeds, weak proof, too much manual triage
- Needs from KillCont:
- confidence in official assets
- fast detection
- clear severity ranking
- simple next actions

### Persona 2: Broadcast Operations Analyst

- Owns: monitoring during events
- Cares about: live visibility, stream restreams, region spread
- Pain: incidents appear faster than manual teams can track
- Needs from KillCont:
- live segment alerting
- timeline playback
- map awareness
- latency metrics

### Persona 3: Brand or League Stakeholder

- Owns: business trust and partner confidence
- Cares about: product credibility and reporting
- Pain: fragmented evidence and unclear scale
- Needs from KillCont:
- executive-level overview
- incident trends
- proof that official content is monitored

### Persona 4: Judge

- Owns: evaluation outcome
- Cares about: innovation, implementation reality, clarity, impact
- Pain: hearing vague AI claims with no grounded workflow
- Needs from KillCont:
- one clear problem
- one clear user
- one clear flow
- believable use of cloud services
- visible working demo

## 12. Jobs To Be Done

- When I publish official media, I want it registered and protected so I have a trusted reference point later.
- When a suspicious upload appears, I want the system to identify likely matches so I can review the case quickly.
- When a clip has been edited, I want the system to still recognize it so protection does not collapse after trivial transformations.
- When media starts spreading live, I want the dashboard to surface it quickly so my team can respond before the wave grows.
- When I open an incident, I want a clear evidence summary so I can decide whether to ignore, monitor, or escalate.
- When I report progress to stakeholders, I want visibility into spread patterns and detection performance so the system feels strategic, not reactive.

## 13. User Outcomes

- Outcome: regain visibility
- Outcome: reduce uncertainty
- Outcome: act faster
- Outcome: justify decisions
- Outcome: preserve value of official media

## 14. Non-Goals

- Build a universal social media crawler covering every platform
- Replace legal counsel
- Build a general-purpose moderation system
- Create a creator economy platform
- Train custom AI models
- Win by stacking buzzwords without product clarity
- Build deep enterprise workflows that dilute the MVP

## 15. Product Scope Guardrails

- The MVP is a control room, not a full rights management suite.
- The MVP needs one powerful incident detail workflow.
- The MVP needs only enough connectors to prove the concept.
- The MVP must support image and video assets.
- The MVP should simulate live segment monitoring convincingly.
- The MVP must use Google login.
- The MVP must feel polished on the web.
- The MVP must not depend on CI/CD.

## 16. The Three Pillars To Actually Win With

### Pillar A: Trust

- Official media gets registered.
- Provenance can be surfaced when available.
- The platform makes authenticity visible.

### Pillar B: Detection

- Similarity search finds altered or redistributed copies.
- Detection works even when metadata is gone.
- Segment-level analysis helps with live or short-form reuse.

### Pillar C: Action

- Incidents appear in a live dashboard.
- Evidence is human-readable.
- Operators can classify and route cases fast.

## 17. The Product Message

- “KillCont restores control over digital media after publication.”
- “We do not wait for stolen content to stay unchanged.”
- “We detect transformed reuse and explain it.”
- “We combine authenticity and similarity instead of choosing one.”

## 18. Naming Strategy

- Keep the brand name KillCont.
- Let the sub-features carry descriptive names.
- Good internal feature labels:
- Trust Layer
- Signal Feed
- Live Watch
- Evidence Pack
- Threat Map
- Propagation Lens
- Action Queue

## 19. Brand Tone

- confident
- precise
- modern
- responsible
- alert but not alarmist
- premium but not theatrical

## 20. Copy Rules

- Avoid empty AI claims.
- Avoid saying “revolutionary” or “disruptive.”
- Prefer verbs like verify, detect, surface, compare, explain, and respond.
- Use short headline language.
- Use operational nouns like asset, incident, feed, evidence, and signal.
- Keep platform names secondary to the user’s operational outcome.

## 21. Why C2PA Matters In This Product

- It gives official media a verifiable authenticity layer.
- It helps KillCont start from a trusted source of truth.
- It helps explain why a repost with missing credentials is suspicious.
- It gives judges a standards-based story instead of a custom proprietary narrative.
- It makes the product feel forward-looking and aligned with industry provenance efforts.

## 22. Why C2PA Is Not The Whole Product

- Credentials can be stripped.
- Not all monitored content will preserve manifests.
- Some platforms transform uploads heavily.
- Therefore KillCont must not depend entirely on credential survival.
- This is why embeddings are essential.

## 23. Why Embeddings Matter In This Product

- They create a transform-resistant similarity layer.
- They allow reuse detection even after cropping, mirroring, compression, or overlay changes.
- They let the product work on both images and video-derived frames or segments.
- They create a clean AI narrative that is understandable and practical.

## 24. Why Gemini Matters In This Product

- Gemini should not be presented as an all-knowing judge.
- Gemini should be used where natural language reasoning adds operator value.
- Good usage:
- summarize the suspicious post
- classify likely intent or severity band
- explain signals in plain language
- draft action recommendations
- Bad usage:
- full legal determination
- broad autonomous agent behavior
- vague “AI decided everything” storytelling

## 25. Why Firestore Vector Search Is The MVP Call

- It reduces infrastructure sprawl.
- It fits the Firebase-first choice.
- It is enough for a hackathon dataset.
- It supports a clean developer mental model.
- It keeps the search story grounded in managed Google tooling.
- It can be replaced later if the product grows.

## 26. Why Vertex AI Vector Search Is A Future Path

- It is stronger for larger scale and more specialized vector workloads.
- It gives a credible scale story.
- It is probably more than the MVP needs in six days.
- Therefore it should be documented as an upgrade path, not the first delivery target.

## 27. Why The Threat Map Must Exist

- It makes propagation visible in a way that judges instantly understand.
- It turns a content matching product into an intelligence product.
- It helps differentiate KillCont from basic upload-match dashboards.
- It creates a strong visual anchor during the demo.

## 28. Why The Threat Map Must Not Be Decorative

- If the map is just dots, it will feel superficial.
- It must answer a product question.
- Good product questions:
- where did this incident appear first
- what regions are active now
- how fast did spread happen
- which incidents belong to the same wave

## 29. Why The Incident Detail Screen Is More Important Than The Landing Page

- The landing page gets attention.
- The incident detail screen earns credibility.
- Judges will remember the product based on whether the evidence workflow feels real.
- Therefore the incident view should receive disproportionate polish.

## 30. What “Near Real-Time” Should Mean In The Demo

- The demo does not need sub-second detection.
- The demo needs visibly fresh updates.
- A believable target is:
- ingestion acknowledgement quickly
- analysis in a short async window
- incident appearance with a visible live update moment

## 31. Live Segment Monitoring Philosophy

- Live segment support should be shown through a controlled simulation.
- The point is to demonstrate the workflow and latency model.
- The point is not to claim internet-scale live capture coverage.
- Segment-level monitoring matters because sports value is time-sensitive.

## 32. The MVP Product Loop

1. User signs in.
2. User sees a live overview.
3. User uploads or reviews protected assets.
4. System ingests monitored feed items.
5. System computes similarity.
6. System creates incidents.
7. User opens incident evidence.
8. User chooses action state.
9. Dashboard reflects current operational picture.

## 33. The Best Demo Flow

1. Start on the landing page for ten seconds.
2. Enter the app with Google login already known or fast.
3. Show overview KPI change in real time.
4. Open one live incident from the stream.
5. Show matched media and confidence explanation.
6. Show provenance gap or credential insight.
7. Jump to the map and spread timeline.
8. Return to evidence and action decision.
9. End with why this matters for sports and beyond.

## 34. Feature Hierarchy

### Tier 1: Must feel complete

- Auth
- Dashboard shell
- Asset registration
- Monitoring feed
- Similarity incident generation
- Incident detail
- Threat map

### Tier 2: Strong differentiators

- Provenance summary
- Live segment demo
- Evidence pack
- Triage explanation

### Tier 3: Nice-to-have

- Automated notice drafting
- Team comments
- Campaign analytics
- More connectors

## 35. Scope Compression Strategy

- If behind schedule, do not remove incident detail polish.
- If behind schedule, reduce connector breadth.
- If behind schedule, simplify live stream handling before simplifying the evidence panel.
- If behind schedule, keep one polished map mode instead of multiple.
- If behind schedule, turn advanced legal action into a recommendation card.

## 36. Emotional Design Goal

- The user should feel:
- informed
- in control
- faster than the problem
- supported by the system

The judge should feel:

- this could actually be used
- this team understands the workflow
- this is more than a model wrapper

## 37. Visual Identity Direction

- Primary mood: broadcast security control room
- Secondary mood: sports command analytics
- Surface style: pure black cinematic canvas with product UI as the hero
- Avoid: neon hacker aesthetic
- Avoid: generic blue enterprise dashboard
- Avoid: colorful gradient AI template look

## 38. Color Strategy

- Use pure black as the base.
- Use electric blue as the main interaction and containment accent.
- Use near-black panels for elevated surfaces.
- Use muted silver for secondary text.
- Use restrained semantic states only where the product needs operational clarity.
- Use muted teal for verified provenance.
- Use amber for monitor states.
- Use red carefully for escalated threats.

## 39. Typography Strategy

- Use a compressed geometric display face.
- Use GT Walsheim where available, otherwise Sora as the closest practical fallback.
- Use Inter for body and interface text.
- Use Azeret Mono for technical micro-labels where helpful.
- Keep display tracking tight and high-impact.

## 40. Motion Strategy

- Motion should indicate signal flow.
- Motion should indicate system freshness.
- Motion should reward user navigation.
- Motion should not compete with the data.
- Animation types should map to meaning:
- pulse equals new signal
- sweep equals ingestion or flow
- expand equals drill-down
- arc animation equals spread path

## 41. Sound Product Rule

- Every screen should answer one primary question.

### Overview

- What is happening right now?

### Assets

- What are we protecting?

### Monitor

- What is entering the system?

### Incidents

- What needs attention?

### Live Watch

- What is happening in motion right now?

### Evidence

- Why do we believe this case matters?

## 42. Landing Page Mindset

- The landing page is not the main product.
- It exists to frame the problem and make the product feel coherent.
- It should be short, strong, and visual.
- It should get out of the way quickly.

## 43. App Shell Mindset

- The app shell should feel stable.
- The shell should remain calm while live content updates.
- Live updates should be visible but not chaotic.
- Panels should feel intentional and dense in a premium way.

## 44. Navigation Mindset

- Avoid too many top-level items.
- Prefer meaningful nouns.
- Keep the operator’s core path close:
- overview
- incidents
- evidence
- assets

## 45. Data Freshness UX

- Show a live sync indicator.
- Show the most recent ingest timestamp.
- Show when an incident list is actively updating.
- Show latency or freshness metrics in the live watch experience.

## 46. Upload Experience Mindset

- Uploading an official asset should feel important.
- It should feel like placing a valuable object under protection.
- The upload flow should capture enough metadata to make later incidents meaningful.
- The upload flow should not be bloated.

## 47. Asset Registration Fields For MVP

- title
- sport
- event
- event date
- asset type
- short description
- rights owner
- optional provenance check or manifest presence

## 48. Asset Registration UX Rules

- Do not ask for too much metadata up front.
- Prefer a concise wizard or focused modal.
- Show immediate status states after upload:
- uploaded
- processing
- embedding ready
- watch enabled

## 49. Asset Detail UX Rules

- Lead with media preview.
- Show provenance and protection badges high on the page.
- Show incident count and monitoring status visibly.
- Show a simple list of protected segments or representative frames for videos.

## 50. Monitor Feed UX Rules

- The feed should feel alive.
- It should not overwhelm the operator with every low-confidence item.
- It should allow filtering and freezing.
- It should show enough metadata to understand context quickly.

## 51. Incident List UX Rules

- The list must be scannable.
- Severity, platform, and matched asset should be visible instantly.
- Trust score and spread score should be legible.
- Triage labels should use clear language.
- New incidents should animate in lightly.

## 52. Incident Detail UX Rules

- Start with what matched.
- Then show why it matched.
- Then show how risky it is.
- Then show what to do next.
- Keep supporting details visible but secondary.
- Make the evidence legible without making the page feel forensic or intimidating.

## 53. Evidence Screen UX Rules

- Evidence must be exportable in concept even if not fully automated.
- It must feel like a case summary.
- It must combine structured data and visual proof.
- It must help the user explain the case to someone else.

## 54. Threat Map UX Rules

- The map should be tappable and useful.
- The map should not become a static image.
- The active selection should link back to incident detail.
- The legend should be obvious.
- Severity and spread should be encoded consistently.

## 55. Live Watch UX Rules

- Use a split view if helpful:
- segment stream on one side
- active detections or timeline on the other
- Show a sense of the last few minutes.
- Make the latency story visible.
- Make the “restream suspected” moment memorable.

## 56. Accessibility Rules

- Respect contrast.
- Do not rely only on color for severity.
- Keyboard navigation should remain usable on the main workflows.
- Motion should not hinder readability.
- Use captions or labels around charts and maps.

## 57. Data Density Rules

- This is a control room, so some density is good.
- Density without hierarchy is not good.
- Big picture first, evidence second, raw details third.

## 58. The Product Must Avoid These Traps

- Trap: generic SaaS dashboard look
- Trap: too many tabs with weak content
- Trap: AI explained only through buzzwords
- Trap: map added only for visual impact
- Trap: too many half-real integrations
- Trap: legal claims the product cannot support
- Trap: overly complex architecture that slows building

## 59. North Star Metrics For The Demo

- number of protected assets
- number of monitored feed items
- number of active incidents
- average detection latency
- number of live detections during demo
- number of incidents classified by severity

## 60. Product Success Criteria

- A judge understands the product in under one minute.
- The demo shows live or fresh movement.
- The core similarity use case feels believable.
- The incident evidence view makes the product feel credible.
- The stack choices feel intentional and hackathon-appropriate.
- The overall website feels more polished than the average hackathon project.

## 61. The “Why Now” Argument

- AI-generated manipulation and fast redistribution make authenticity harder.
- Sports media is increasingly clipped, remixed, and redistributed across fragmented platforms.
- Rights holders need a system that does not depend on perfect metadata retention.
- Standards like C2PA make authenticity more visible, while embeddings make altered-copy detection more practical.
- The combination is timely and compelling.

## 62. What Makes KillCont Different

- It starts with trusted assets, not just suspicious uploads.
- It combines provenance and similarity.
- It treats the dashboard as the product, not as an afterthought.
- It visualizes propagation, not just detection.
- It focuses on operator decisions, not only model output.

## 63. Core Value Proposition

- “KillCont protects the value of official media after publication.”

Supporting proof points:

- similarity survives common transformations
- incidents arrive in a live workflow
- authenticity can be surfaced when available
- evidence is visible and explainable

## 64. One Sentence On Impact

- By restoring visibility and response speed around official media, KillCont can help sports organizations protect revenue, trust, and the integrity of what audiences consume.

## 65. SDG Framing Options

- SDG 8: protects value chains around creative and sports media work
- SDG 9: strengthens digital media infrastructure and innovation
- SDG 16: supports trusted digital information and authenticity

Recommended main framing:

- lead with SDG 9 for innovation and infrastructure
- support with SDG 8 for economic protection
- mention SDG 16 if the authenticity angle becomes strong in the final narrative

## 66. Solution Challenge Positioning Rule

- Do not oversell the exact SDG mapping.
- Instead:
- show the real-world problem
- show who benefits
- show why the build is realistic
- show how Google technologies are meaningfully used

## 67. The Product Does Not Need To Prove Everything

- It does not need full internet coverage.
- It does not need enterprise legal automation.
- It does not need perfect geolocation.
- It does not need perfect fair-use reasoning.
- It needs one convincing product loop with enough breadth to show the vision.

## 68. Platform Connector Philosophy

- Real connectors increase credibility.
- Simulated connectors increase control and polish.
- The winning balance is mixed.
- Real connectors should be chosen for feasibility and demonstrability.
- Simulated connectors should be designed to feel plausible.

## 69. Good Connector Candidates

- Reddit public sources
- YouTube metadata flows
- simulated short-video feed
- simulated live segment relay
- optional simulated messaging repost feed

## 70. Connector Anti-Patterns

- claiming deep platform integration when only scraping screenshots
- relying on fragile selectors for critical demo paths
- over-investing in a connector that does not improve the core incident workflow

## 71. The Product Needs A Scenario Anchor

- Pick one event context for the demo.
- Example types:
- football finals weekend
- cricket tournament day
- basketball playoff night

The scenario anchor helps:

- asset naming
- incident relevance
- map narrative
- live watch storyline

## 72. Recommended Scenario Shape

- one official short highlight clip
- one official image asset
- one official longer video or event stream slice
- several monitored derivatives:
- fan meme
- commentary snippet
- unauthorized repost
- live segment relay

## 73. Why Mixed Harm Levels Matter

- If every incident is a severe violation, the system feels naive.
- A better product shows nuanced triage.
- Some content should be low risk.
- Some content should be monitor-only.
- Some content should clearly deserve escalation.

## 74. Triage Categories

- Ignore
- Monitor
- Strike

### Ignore

- likely harmless fan engagement
- short meme-style reuse
- low spread and low risk

### Monitor

- commentary or borderline use
- moderate spread
- unclear commercial intent

### Strike

- direct repost
- monetized reuse
- sustained or high-spread clip reuse
- likely unauthorized live restream

## 75. The Triage UI Must Be Clear

- Use plain labels.
- Use color carefully.
- Show why the category was chosen.
- Do not let the labels feel arbitrary.

## 76. Trust Score Philosophy

- The trust score is not magic.
- It is a summary of confidence factors.
- Good inputs:
- provenance presence
- similarity strength
- source context
- media edit pattern
- spread behavior

## 77. Spread Score Philosophy

- Spread score answers how operationally urgent the incident feels.
- It should incorporate:
- number of sightings
- rate of new sightings
- regional spread
- source type severity

## 78. Severity Philosophy

- Severity should reflect likely harm to rights holders.
- Severity is not the same as similarity.
- A strong match with low spread may still be moderate.
- A moderate match in a high-risk live relay might be severe.

## 79. Evidence Philosophy

- The product should make evidence feel inspectable.
- Judges trust what they can see.
- Operators trust what they can explain.
- Therefore visual proof matters as much as numeric proof.

## 80. Explainability Philosophy

- Explainability is product design, not a separate feature.
- Every important score should have a plain-language reason.
- Every important state should be traceable to visible signals.
- The best explanation is a combination of side-by-side visuals, concise text, and structured factors.

## 81. Product Trust Philosophy

- Trust in KillCont comes from:
- standards-aligned provenance
- understandable AI usage
- controlled UX
- concrete evidence
- consistent state changes

## 82. What The Homepage Hero Must Promise

- not “AI for media”
- not “future of content”
- but:
- protection
- visibility
- speed
- control

## 83. What The Homepage Hero Must Show

- a protected official asset
- a spreading suspicious signal
- a resolved operational view

## 84. The Homepage Should Use Motion Like This

- background network or field lines
- subtle tracking sweeps
- incident pulse markers
- scroll reveal into dashboard cards

## 85. The Homepage Should Avoid This

- slow cinematic loading
- giant abstract blobs
- vague illustrations with no product relevance
- empty fake metrics

## 86. Dashboard First Impression

- On first load, the dashboard should already feel active.
- Show:
- KPIs
- a few active incidents
- map activity
- one highlighted event or live watch card

## 87. Dashboard Information Priority

- Primary: active risks
- Secondary: protected assets and coverage
- Tertiary: historical reporting

## 88. Data Storytelling Rule

- The system should always move from summary to proof.
- Example:
- KPI spike
- incident list item
- incident detail
- evidence panel
- map/timeline confirmation

## 89. Product Operations Rule

- Every major state should be representable in Firestore documents.
- This keeps the dashboard reactive and the data model simple.

## 90. Engineering Simplicity Rule

- Prefer one backend service with clear modules over many tiny services.
- Use async workers only where they reduce user wait time.
- Avoid premature microservices.

## 91. Future Scalability Story

- Today:
- Firestore metadata
- Firestore vector search
- managed embeddings
- simulated and limited real feeds

- Later:
- Vertex AI Vector Search
- more connectors
- deeper provenance workflows
- campaign analytics
- expanded sectors

## 92. Why This Story Works For Judges

- It is honest.
- It is ambitious but credible.
- It shows a clear MVP-to-scale path.

## 93. Technical Honesty Rule

- Never say “internet-wide” without qualification in the demo script.
- Say:
- “mixed real and simulated monitoring inputs”
- “designed for scalable expansion”
- “hackathon MVP proves the pipeline and operator workflow”

## 94. Design Honesty Rule

- Never fake too many screens with static imagery.
- Build fewer screens, but make them interactive and believable.

## 95. Product Success Hierarchy

- First: comprehension
- Second: credibility
- Third: delight
- Fourth: breadth

## 96. If We Have To Drop Something

- drop extra connectors before dropping evidence quality
- drop advanced exports before dropping incident detail
- drop historical analytics before dropping live watch
- drop configuration surfaces before dropping map clarity

## 97. Team Coordination Rule

- Every teammate should know:
- what the main product story is
- what the current highest-value screen is
- what is in scope
- what is no longer in scope

## 98. Documentation Coordination Rule

- `mindset.md` is strategic truth
- `architecture.md` is system truth
- `website-blueprint.md` is UX truth
- `status.md` is current state truth
- `logbook.md` is execution history truth

## 99. Working With AI Rule

- Use AI to accelerate implementation, not to replace judgment.
- Keep prompts grounded in these docs.
- Review outputs against scope and product clarity.

## 100. Build Mindset

- We are not building a research paper.
- We are not building a backend demo.
- We are building a product.

## 101. Repository Shape Mindset

- The repo should be easy for AI coding tools to understand.
- Keep the folder layout explicit.
- Separate web and API concerns cleanly.
- Reserve packages for shared contracts and design tokens.
- Keep scripts in one place.

## 102. Frontend Stack Recommendation

- React
- Vite
- TypeScript
- React Router
- TanStack Query
- Firebase Web SDK
- Framer Motion
- Google Maps JavaScript API
- lightweight charting library if needed

## 103. Frontend State Philosophy

- Server state belongs in Firestore subscriptions and query hooks.
- UI state belongs in component state or a very small shared store.
- Avoid over-engineering frontend state.
- Use derived selectors where possible.

## 104. Frontend Routing Philosophy

- Public routes:
- landing page
- sign-in

- Protected routes:
- overview
- assets
- incidents
- live watch
- evidence
- settings

## 105. Frontend Layout Philosophy

- Use one strong authenticated shell.
- Avoid route-level layout fragmentation.
- Keep nav stable.
- Let content panels do the storytelling.

## 106. Frontend Component Philosophy

- Build reusable primitives for panels, pills, badges, and headers.
- Do not abstract too early.
- Abstract the things that visually repeat.

## 107. Frontend Data Fetching Philosophy

- Use query hooks for API fetches.
- Use Firestore listeners for live surfaces.
- Keep write actions explicit through the API.
- Do not let the frontend own business logic.

## 108. Frontend Motion Philosophy

- Motion should emphasize state change.
- Use page transitions lightly.
- Focus motion on incident arrival, panel reveal, map activity, and timeline feedback.

## 109. Frontend Map Philosophy

- Keep the base map muted.
- Let signals and arcs stand out.
- Use clustering.
- Use selected incident states.
- Keep pan and zoom smooth.

## 110. Frontend Chart Philosophy

- Use charts only where they answer a question.
- Do not build an analytics page unless it supports the demo.
- Good chart candidates:
- latency over time
- incidents by severity
- spread trend for selected incident

## 111. Backend Stack Recommendation

- FastAPI
- Pydantic
- Firebase Admin
- Google Cloud SDK clients
- Vertex AI SDK
- structured logging

## 112. Backend Architecture Philosophy

- One API service
- One worker code path
- Shared domain models
- Clear service modules

## 113. Backend Module Boundaries

- `api`
- route handlers

- `core`
- config
- auth verification
- logging

- `domain`
- domain logic and entity behavior

- `schemas`
- request and response models

- `services`
- cloud clients and orchestration

- `workers`
- background event handlers

## 114. API Design Philosophy

- Keep endpoints resource-oriented.
- Use async jobs for heavy tasks.
- Return state references quickly.
- Let the frontend observe progress from Firestore or status endpoints.

## 115. Storage Philosophy

- Media goes to Storage.
- Metadata goes to Firestore.
- Derived evidence assets also go to Storage.
- Keep the metadata path human-readable.

## 116. Storage Path Philosophy

- Use consistent storage path conventions:
- `orgs/{orgId}/assets/{assetId}/original`
- `orgs/{orgId}/assets/{assetId}/preview`
- `orgs/{orgId}/assets/{assetId}/frames/...`
- `orgs/{orgId}/feed-items/{feedItemId}/raw`
- `orgs/{orgId}/feed-items/{feedItemId}/normalized`
- `orgs/{orgId}/incidents/{incidentId}/evidence/...`

## 117. Firestore Collection Philosophy

- Collections should mirror product nouns.
- Avoid hidden denormalization that the team cannot reason about.
- Duplicate small read-critical fields when it improves dashboard performance.

## 118. Firestore Document Philosophy

- Documents should support the screens.
- Store pre-computed summary fields for dashboard responsiveness.
- Keep detail records separate from quick-list records if needed.

## 119. Firestore Realtime Philosophy

- Use realtime listeners on:
- incidents
- dashboard counters
- live watch sessions
- maybe feed previews

- Do not use realtime listeners on everything.
- Keep subscription scope intentional.

## 120. Firestore Vector Search Philosophy

- Use vector fields on assets and possibly segments.
- Use nearest-neighbor queries for initial retrieval.
- Use filtered vector search by organization and asset type.
- Persist candidate results so the UI does not depend on live vector queries.

## 121. Asset Data Model Mindset

- Assets are the trusted anchor objects.
- They should be rich enough to power evidence later.
- They should not require too much manual entry.

## 122. Asset Status States

- uploaded
- processing
- ready
- error
- watching
- archived

## 123. Provenance Status States

- verified
- present
- missing
- suspected_removed
- unknown

## 124. Feed Item Status States

- captured
- normalized
- embedded
- candidate_found
- no_match
- incident_created
- dismissed

## 125. Incident Status States

- new
- reviewing
- monitoring
- escalated
- resolved
- ignored

## 126. Live Watch Session States

- inactive
- primed
- streaming
- incident-active
- paused
- completed

## 127. Organization Model Mindset

- For MVP, use one demo organization.
- Structure the data so multi-org is possible later.
- Never hard-code single-tenant assumptions into names.

## 128. User Model Mindset

- Keep it simple:
- user id
- display name
- email
- role
- organization id

## 129. User Roles For MVP

- admin
- analyst
- viewer

## 130. Role Behavior For MVP

- admin can register assets and change incident state
- analyst can review incidents and use evidence views
- viewer can browse the overview and assets

## 131. Authentication Strategy

- Use Firebase Authentication with Google sign-in.
- Verify ID tokens in FastAPI.
- Create or sync user profile in Firestore on first login.

## 132. Authorization Strategy

- The frontend should never be trusted for org scoping.
- API should enforce org membership.
- Firestore and Storage rules should align with the same org scope.

## 133. Upload Flow Strategy

- Create asset draft record.
- Upload media to Storage.
- Update asset record with storage path.
- Emit processing event.
- Show processing state in the UI immediately.

## 134. Upload UX Detail

- Show upload progress.
- Show processing steps:
- upload complete
- generating preview
- generating embeddings
- watch ready

## 135. Media Normalization Philosophy

- Normalize monitored media before analysis where feasible.
- Standardize:
- dimensions
- frame sampling approach
- preview extraction
- clip duration windows

## 136. Image Analysis Strategy

- Generate one main embedding per image.
- Keep optional resized preview.
- If needed, allow region-specific or crop-based evidence later.

## 137. Video Analysis Strategy

- Generate one coarse video embedding.
- Generate representative frame or segment embeddings.
- Use short windows for live or clip-style media.
- Keep frame references for explainability.

## 138. Why Two-Stage Video Matching Matters

- Full frame-by-frame matching is too heavy.
- A coarse retrieval step narrows candidates.
- A fine step improves confidence and evidence quality.

## 139. Video Sampling Strategy For MVP

- Sample representative frames at meaningful intervals.
- Prefer event-aware or shot-aware sampling if feasible.
- If not feasible, fixed interval sampling is acceptable.
- Keep the plan simple enough to implement quickly.

## 140. Video Intelligence API Decision

- Treat Video Intelligence as optional.
- If it speeds up explainable sampling and is easy to wire, use it.
- If it slows delivery, do not block the MVP on it.

## 141. Live Segment Strategy

- Pre-segment or simulate an event feed into short media units.
- Publish segments on a timed schedule.
- Analyze each segment like a monitored clip.
- Attach detections to one live incident thread or event cluster.

## 142. Why Simulation Is Acceptable

- The point of the hackathon MVP is to prove the workflow.
- A controlled simulation lets the team focus on product value.
- Judges care more about clarity and credibility than literal production coverage.

## 143. Simulation Quality Rule

- Simulations should be believable.
- Use realistic timestamps.
- Use realistic source labels.
- Use plausible geographies.
- Use realistic progression from fan sharing to suspicious reposting.

## 144. Real Feed Connector Rule

- Choose connectors with low integration friction.
- Prefer APIs or public feeds that are easy to explain.
- If a connector is unstable, isolate it from the core demo path.

## 145. Feed Connector Data Contract

- Every connector should output:
- source platform
- source url
- author or account label
- published time
- caption text if available
- media location
- region hint if available
- source type

## 146. Normalized Feed Item Contract

- media normalized path
- preview path
- content type
- caption
- region
- capture mode
- ingest time
- original metadata

## 147. Matching Threshold Philosophy

- Keep thresholds configurable.
- Use conservative thresholds for incident creation.
- Use lower thresholds for monitor feed visibility if helpful.
- Never rely on one raw number alone.

## 148. Matching Confidence Factors

- embedding similarity
- segment overlap
- asset type match
- caption clues
- event time alignment
- provenance state
- source risk

## 149. Candidate To Incident Rule

- Not every match candidate becomes an incident.
- Use rules to promote only meaningful cases.
- The operator experience improves when weak noise stays in the monitor layer.

## 150. Incident Promotion Rules For MVP

- promote when similarity is high
- promote when medium similarity combines with high spread or live risk
- promote when provenance signals strengthen the case
- suppress when evidence is too weak

## 151. Incident Clustering Philosophy

- One asset can have multiple sightings.
- Multiple sightings can belong to one operational incident cluster.
- The dashboard should distinguish between:
- individual feed items
- grouped incident activity

## 152. Incident Cluster Inputs

- asset id
- event id
- platform family
- temporal proximity
- source overlap
- propagation relation

## 153. Evidence Pack Contents

- incident summary
- matched asset summary
- feed item summary
- side-by-side previews
- matched frames or segments
- trust score components
- spread summary
- provenance note
- action recommendation

## 154. Evidence Pack Output Philosophy

- For MVP, an on-screen evidence view is enough.
- Export to PDF can be stretch if time allows.
- The evidence view itself should feel export-ready.

## 155. Triage Prompt Philosophy

- Prompts should be narrow and structured.
- Ask for classification and explanation.
- Do not ask the model for legal certainty.
- Keep outputs machine-parseable.

## 156. Triage Prompt Inputs

- asset metadata summary
- detected platform
- caption text
- similarity features
- provenance status
- spread indicators

## 157. Triage Prompt Outputs

- triage label
- short reason
- detailed reason
- operator guidance
- risk factors

## 158. Triage Safety Rule

- The model output must always be framed as recommendation or classification support.
- The UI should make this clear.

## 159. Action Queue Philosophy

- The action queue is the operator’s short list.
- It should show:
- high severity incidents
- incidents needing manual review
- incidents with high spread velocity

## 160. Action Types For MVP

- mark ignore
- mark monitor
- mark escalate
- add note
- open evidence

## 161. Automation Philosophy

- Avoid full automated takedown systems in the MVP.
- Drafting support is acceptable.
- Human approval should remain visible.

## 162. Why Human Approval Matters In The Demo

- It shows responsibility.
- It keeps the product credible.
- It prevents overclaiming legal automation.

## 163. Map Data Philosophy

- Source geolocation may be imperfect.
- Use best-available or simulated coordinates.
- Always prioritize a coherent operational story.

## 164. Map Visual Encoding

- marker size reflects spread
- color reflects severity
- pulse reflects freshness
- arcs reflect propagation relation

## 165. Map Interaction Model

- hover for summary
- click for incident focus
- filter controls nearby
- timeline scrub affects visible incidents

## 166. Timeline Philosophy

- Time is central to media misuse.
- Use timeline views in:
- overview
- incident detail
- live watch

## 167. Overview Timeline Role

- show recent incident arrivals
- show detection momentum

## 168. Incident Timeline Role

- show asset publication
- show suspicious sighting sequence
- show spread moments
- show operator actions

## 169. Live Watch Timeline Role

- show recent segments
- show match latency
- show escalation windows

## 170. Search And Filtering Philosophy

- Filters should support operator speed.
- Useful filters:
- sport
- event
- platform
- severity
- triage label
- asset type
- live only

## 171. Notification Philosophy

- Notifications should not be the main product.
- They support the dashboard.
- Use them for:
- new severe incident
- live watch escalation
- processing failure

## 172. Error State Philosophy

- Error states should still look premium.
- They should help the user recover.
- Good examples:
- asset processing failed
- map data unavailable
- feed connector delayed

## 173. Empty State Philosophy

- Empty states should teach the product.
- Example:
- no incidents yet
- protect your first official asset to begin monitoring

## 174. Seeding Philosophy

- Seed realistic demo data early.
- Do not wait until the end to craft the demo world.
- The product will feel more coherent if seeded data drives design choices.

## 175. Demo Data Categories

- official assets
- monitored feed items
- live segments
- incident records
- geographic points
- operator notes

## 176. Demo Data Quality Rules

- consistent event names
- consistent timestamps
- varied severity levels
- plausible captions
- visible visual differences between media copies

## 177. Asset Variety Rules

- include at least one image asset
- include at least one short clip
- include at least one event-linked video asset

## 178. Monitored Item Variety Rules

- include direct repost
- include cropped or overlaid derivative
- include meme or commentary-style low-risk use
- include live segment relay style case

## 179. Narrative Ladder

- protected media
- suspicious content appears
- system detects
- system explains
- user acts

## 180. Product Demo Sentence

- “This is not just a detector. It is an operational visibility layer for protected media.”

## 181. Performance Budget Philosophy

- Performance must support trust.
- Slow tools feel uncertain.
- Keep the UI responsive even when analysis is async.

## 182. Frontend Performance Targets

- shell render under 2 seconds
- route changes feel instant once data is loaded
- map interactions stay smooth
- heavy media views lazy load

## 183. Backend Performance Targets

- API write endpoints return quickly
- async queues handle heavy tasks
- incident creation feels near-real-time at demo scale

## 184. Media Processing Budget

- avoid long synchronous processing
- generate only necessary previews
- use representative frames rather than exhaustive extraction

## 185. Cost Mindset

- Stay within free or low-cost hackathon-friendly managed usage where possible.
- Use smaller demo datasets.
- Reuse derived previews.
- Avoid unnecessary re-embedding loops.

## 186. Observability Philosophy

- Basic logging is enough for MVP.
- Log:
- asset processing steps
- feed ingestion steps
- matching outcomes
- triage outputs
- live watch events

## 187. Logging Rule

- Every background task should log:
- what started
- what completed
- what failed
- what entity id was involved

## 188. Retry Philosophy

- Retries matter for background tasks.
- If time allows, use retry-safe worker behavior.
- If time is short, at least log failures clearly and expose manual re-run options.

## 189. Manual Recovery Philosophy

- The MVP should support manual retry for:
- asset processing
- feed ingestion
- live scenario reset

## 190. Testing Philosophy

- Test the product loop, not every implementation detail.
- Prioritize:
- auth flow
- asset upload flow
- incident creation flow
- incident display flow
- live watch scenario

## 191. Test Layers

- smoke tests
- manual scenario tests
- a few focused unit tests if time allows

## 192. Demo Reliability Rule

- Anything shown live should have a backup path.
- Seeded data is not cheating.
- It is resilience.

## 193. Backup Demo Rule

- Have pre-seeded incidents.
- Have a ready live watch scenario.
- Have static fallback screenshots or video only as emergency backup.
- Prefer using the actual app for all primary demo moments.

## 194. Security Philosophy

- The product handles valuable media.
- Even in hackathon mode, do not make everything public.
- Keep sensitive originals protected.
- Expose previews intentionally.

## 195. Privacy Philosophy

- Use only safe demo content.
- Avoid risky personal data.
- Keep public-source ingestion limited and transparent.

## 196. Legal Honesty Philosophy

- KillCont can support evidence and response.
- KillCont does not replace legal review.
- Keep that language disciplined.

## 197. Demo Risk Register Philosophy

- The risk register should be active, not decorative.
- If a risk grows, scope should shrink somewhere else.

## 198. Product Review Cadence

- review scope daily
- review demo path daily
- review blockers daily
- update docs after major shifts

## 199. Design Review Cadence

- review homepage
- review overview
- review incidents
- review live watch
- ensure one consistent visual language

## 200. End-State Vision

- By the end of the six days, KillCont should look like a polished category-defining prototype, not a pile of disconnected hackathon features.

## 201. Six-Day Delivery Strategy

- Day 1 is for architecture and scaffold stability.
- Day 2 is for auth and asset flow.
- Day 3 is for similarity detection pipeline.
- Day 4 is for dashboard and map maturity.
- Day 5 is for provenance, evidence, and live watch polish.
- Day 6 is for demo hardening, bug fixing, and presentation.

## 202. Day 1 Goal

- end the day with a stable repo structure
- shared docs in place
- app scaffold ready
- auth strategy clear
- seed data strategy clear

## 203. Day 1 Tasks

- scaffold React + Vite app
- scaffold FastAPI app
- configure Firebase project basics
- configure Firestore collections plan
- define env variables
- seed initial demo asset metadata
- confirm visual direction with first shell mock

## 204. Day 1 Success Criteria

- frontend runs
- backend runs
- docs are aligned
- no major architectural uncertainty remains

## 205. Day 2 Goal

- end the day with usable login and upload

## 206. Day 2 Tasks

- implement Google sign-in
- protect app routes
- implement app shell
- implement asset upload form
- store media in Storage
- write asset documents to Firestore
- show upload processing states

## 207. Day 2 Success Criteria

- a logged-in user can enter the app
- a protected asset can be added
- the asset appears in the assets page

## 208. Day 3 Goal

- end the day with a believable detection pipeline

## 209. Day 3 Tasks

- implement embedding generation flow
- store embeddings
- implement first vector search path
- ingest simulated and at least one real feed item
- generate match candidates
- promote candidates into incidents

## 210. Day 3 Success Criteria

- at least one monitored item becomes an incident end-to-end
- the UI can display the incident

## 211. Day 4 Goal

- end the day with a strong command center

## 212. Day 4 Tasks

- build overview dashboard
- build incident list
- build incident detail
- build threat map
- add realtime subscriptions
- add severity and spread visual states

## 213. Day 4 Success Criteria

- the app already feels like a product
- new or seeded incidents appear live in the dashboard

## 214. Day 5 Goal

- end the day with differentiation and polish

## 215. Day 5 Tasks

- add provenance summary layer
- add evidence pack view
- add live watch scenario
- add motion polish
- improve copy and empty states
- improve signal labels and trust language

## 216. Day 5 Success Criteria

- the product has a memorable reason to win
- the evidence workflow feels strong

## 217. Day 6 Goal

- end the day with a demo-ready system

## 218. Day 6 Tasks

- test all main flows
- preload demo data
- improve fallback paths
- fix bugs
- script the judge demo
- capture screenshots or a backup video
- update final docs

## 219. Day 6 Success Criteria

- the team can demo without hesitation
- backup plans are ready
- the product narrative is sharp

## 220. Team Structure For 4 People

- Person A: frontend shell, overview, incidents
- Person B: asset flow, auth, web-to-api integration
- Person C: backend ingestion, embeddings, matching
- Person D: map, live watch, demo data, polish

## 221. Team Flexibility Rule

- If skills overlap, split by ownership of outcomes, not by language preference.
- Each person should own one visible outcome.

## 222. Suggested Ownership Model

### Owner 1

- app shell
- landing page
- design tokens
- layout and navigation

### Owner 2

- assets page
- upload flow
- auth
- asset detail

### Owner 3

- backend services
- embeddings
- matching
- incidents creation

### Owner 4

- map
- live watch
- seeded scenarios
- evidence polish

## 223. Collaboration Rule

- Do not block on perfect separation.
- Merge around the main product flow.
- The incident detail screen is a shared responsibility.

## 224. AI-Assisted Development Rule

- Give AI agents scoped prompts based on this document.
- Ask for bounded modules.
- Always verify generated code against the product story.

## 225. Repo Scaffolding Next Step

- after planning, scaffold:
- `apps/web` actual Vite app
- `apps/api` actual FastAPI service
- shared env and config docs

## 226. Recommended Frontend Folder Detail

- `src/app`
- app routes and providers

- `src/components`
- shared panels, cards, badges, nav, layout pieces

- `src/features/auth`
- sign-in, session hooks

- `src/features/assets`
- upload, asset list, asset detail

- `src/features/monitor`
- feed list, filters, live feed panels

- `src/features/incidents`
- list, detail, evidence widgets

- `src/features/live-watch`
- event selector, segment stream, live timeline

- `src/features/evidence`
- export-ready case layout

## 227. Recommended Backend Folder Detail

- `app/api/routes`
- endpoint modules

- `app/core/config`
- env parsing

- `app/core/auth`
- token verification

- `app/services/storage`
- media upload helpers

- `app/services/firestore`
- data access layer

- `app/services/embeddings`
- Vertex AI calls

- `app/services/matching`
- candidate retrieval and scoring

- `app/services/triage`
- Gemini prompt orchestration

- `app/workers`
- event handlers

## 228. Design System Token Suggestions

- `--color-bg`
- `--color-panel`
- `--color-panel-strong`
- `--color-text`
- `--color-muted`
- `--color-signal`
- `--color-trust`
- `--color-monitor`
- `--color-strike`

## 229. Spacing System Suggestions

- choose one spacing scale
- keep dense panels consistent
- avoid ad hoc spacing everywhere

## 230. Typography Scale Suggestions

- hero display
- section title
- panel title
- body
- caption
- status label

## 231. Panel Design Rule

- panels should feel layered and intentional
- slightly different elevation or border treatments can encode importance
- keep panel chrome restrained

## 232. Card Design Rule

- do not make every surface a card
- use cards where a unit of meaning exists:
- incident
- asset
- live event
- evidence block

## 233. Iconography Rule

- use icons sparingly
- prefer status dots and clear labels over decorative icon overload

## 234. Homepage Section Sequence Rationale

- hero captures urgency
- signal strip creates life
- how-it-works creates clarity
- standout section creates differentiation
- dashboard preview creates credibility
- future expansion section creates ambition

## 235. Homepage Copy Themes

- scattered media
- lost visibility
- protected assets
- trust gap
- signal recovery
- faster action

## 236. Homepage CTA Philosophy

- The CTA should invite users into the product experience.
- Good CTA types:
- open dashboard
- explore demo
- protect assets

## 237. App Overview KPI Candidates

- assets protected
- active incidents
- suspicious uploads in last hour
- average detection latency
- live watch alerts
- platforms active today

## 238. KPI Design Rule

- Use fewer KPIs with stronger meaning.
- Prefer motion on change, not constant animation.

## 239. Overview Layout Option

- top KPI bar
- center-left map
- center-right live incident rail
- lower-left trend strip
- lower-right action queue

## 240. Overview Layout Reasoning

- map anchors the page visually
- live rail gives freshness
- action queue makes it operational

## 241. Assets Page Layout Option

- top filters
- primary table or grid
- sticky upload action
- side drawer or route for asset detail

## 242. Assets Table Columns

- title
- type
- event
- provenance
- watch status
- incidents
- created time

## 243. Asset Detail Sections

- hero preview
- metadata
- trust layer
- embeddings status
- segments or frames
- related incidents
- recent sightings

## 244. Monitor Page Layout Option

- auto-updating feed stream
- filter bar
- selected feed item preview
- candidate confidence sidebar

## 245. Why The Monitor Page Matters

- It proves KillCont sees the world before incidents are finalized.
- It makes the product feel more alive.

## 246. Incidents Page Layout Option

- left: incident list
- center: selected incident detail
- right: action panel or evidence shortcuts

## 247. Incidents Page Reasoning

- supports fast triage
- supports side-by-side comparison
- keeps action nearby

## 248. Live Watch Page Layout Option

- stream or segment rail
- event summary panel
- live detections list
- latency chart
- active map mini-panel

## 249. Live Watch Narrative

- show an event in progress
- show segments arriving
- show suspicious segment match
- show incident escalation

## 250. Evidence Page Layout Option

- top case summary
- left matched asset
- right monitored content
- lower scoring explanation
- lower action notes

## 251. Evidence Page Reasoning

- It acts as the “proof room.”
- It makes the project feel serious and complete.

## 252. Incident Detail Must Answer These Questions

- what official asset is affected
- what content matched
- how strong is the match
- what changed between the copies
- how risky is the spread
- what should the operator do

## 253. Evidence Visualization Options

- side-by-side stills
- frame strip
- highlighted match windows
- overlay difference hints
- timeline markers

## 254. Similarity Explanation Copy Examples

- “High semantic match across protected keyframes.”
- “Credential missing while visual structure strongly matches official media.”
- “Spread accelerating across multiple repost sources.”

## 255. Provenance Explanation Copy Examples

- “Official asset contains verifiable registration metadata.”
- “Monitored copy appears detached from the trust record.”
- “Credential unavailable, similarity evidence used instead.”

## 256. Action Recommendation Copy Examples

- “Likely fan engagement. Monitor only.”
- “High-confidence unauthorized repost. Escalate.”
- “Potential live relay pattern. Prioritize review.”

## 257. Score Presentation Rule

- Avoid too many decimals.
- Use bands:
- low
- medium
- high
- critical

## 258. Badge Language Rule

- concise
- operational
- not vague

Good:

- Verified
- Missing credential
- High spread
- Live risk

## 259. Color Coding Rule

- Use severity colors consistently across list, map, and detail
- Use trust colors consistently across assets and incidents
- Do not overload the palette with too many meaning systems

## 260. Motion Timing Rule

- fast for list updates
- medium for panel transitions
- slowest only for background ambient motion

## 261. Animation Risk Rule

- If motion causes layout shift or distracts from proof, remove it.

## 262. Mobile Scope Rule

- The primary demo is desktop.
- Mobile should not break.
- Mobile does not need feature parity on dense evidence workflows.

## 263. Realtime Architecture Rule

- Never let the UI wait on expensive processing.
- Write intermediate states early.
- Let the user see progress.

## 264. Intermediate Processing States

- queued
- previewing
- embedding
- matching
- triaging
- incident-ready

## 265. Why Intermediate States Matter

- They make the system feel alive.
- They make long operations understandable.
- They build trust.

## 266. API Endpoint Contract Rule

- endpoints should return ids and statuses
- clients should use ids to subscribe to updates or fetch details

## 267. Environment Variable Planning

- frontend firebase config
- maps api key
- backend firebase service credentials
- GCP project id
- Storage bucket
- Vertex region
- feature flags for live demo and simulation

## 268. Feature Flags Philosophy

- use lightweight feature flags
- useful flags:
- enable provenance
- enable live watch
- enable simulated feeds
- enable real connectors

## 269. Development Environment Rule

- keep local setup simple
- do not make the team fight tooling
- one clear startup path per app

## 270. Seed Script Philosophy

- seed scripts are first-class tools
- use them to create believable demo states quickly
- use them to reset the world before presentations

## 271. Seed Data Requirements

- at least one org
- at least one admin user profile
- at least three assets
- at least eight monitored items
- at least four incidents
- at least one live watch sequence

## 272. Seeded Incident Mix

- one ignore
- one monitor
- one strike
- one live escalation

## 273. Seeded Geography Mix

- one local hotspot
- one cross-region spread
- one isolated low-risk signal

## 274. Seeded Platform Mix

- one public social feed
- one short-video style feed
- one repost mirror
- one live relay source

## 275. Backfill Strategy

- seed historical incidents to make charts feel populated
- keep recent incidents for realtime freshness

## 276. Dashboard Snapshot Strategy

- pre-compute dashboard metrics in a snapshot document if needed
- update that document whenever incidents change

## 277. Why Snapshot Docs Help

- simple reads
- fast dashboard load
- predictable UI data shape

## 278. Matching Worker Responsibility

- fetch or receive normalized media
- generate embeddings
- run vector search
- score candidates
- write match candidates
- promote incidents if needed

## 279. Triage Worker Responsibility

- fetch candidate context
- call Gemini
- write triage result
- update incident summary

## 280. Provenance Worker Responsibility

- verify credentials if applicable
- write provenance summary to asset
- optionally record missing or stripped signal observations

## 281. Live Watch Worker Responsibility

- receive segment tick
- normalize segment
- embed segment
- match against active watchlist
- update live incident thread

## 282. Event Naming Rule

- event names should be simple and recognizable
- do not invent overly complex tournament labels

## 283. Asset Naming Rule

- names should feel like real media library assets
- include event and type where helpful

## 284. Incident Title Rule

- use short, descriptive incident titles
- format example:
- “Highlight repost detected on YouTube”
- “Live relay suspected from short clip chain”

## 285. Feed Caption Quality Rule

- captions should feel human
- vary tone
- include some fan-style captions and some commercial-looking captions

## 286. Incident Summary Quality Rule

- summaries should be readable at a glance
- do not dump raw metadata

## 287. Product Copy Quality Rule

- all copy should reinforce confidence and clarity
- avoid being cute when the screen should feel operational

## 288. Presentation Strategy

- open with the problem in one sentence
- show the dashboard quickly
- narrate the three layers:
- trust
- detection
- action

## 289. Presentation Time Budget

- intro: 15 to 20 seconds
- product overview: 30 seconds
- live incident walkthrough: 60 to 90 seconds
- architecture / Google Cloud mention: 20 to 30 seconds
- impact and future scope: 20 seconds

## 290. Judge Demo Must-Haves

- visible login
- visible protected asset
- visible detected incident
- visible map
- visible evidence
- visible action status

## 291. Judge Demo Nice-To-Haves

- provenance badge
- live segment alert
- one real-source connector example

## 292. If The Live Demo Fails

- use seeded incidents
- use the evidence view
- use the map
- still tell the same story

## 293. If The Connector Fails

- switch to simulated feed data
- keep the connector discussed as implemented path, not as the only proof

## 294. If The Embedding Flow Fails

- preload embeddings
- keep UI states believable
- fix after the demo if possible

## 295. If The Map Fails

- fall back to incident detail and propagation timeline
- do not let one visual dependency collapse the narrative

## 296. If Provenance Is Not Ready

- keep the product as detection-first
- mention provenance as an integrated upgrade path
- do not fabricate credential states

## 297. Documentation Update Rule

- At the end of each day:
- update status
- add logbook entry
- record scope changes

## 298. Project Review Checklist

- Does the product still have one main story?
- Does the dashboard still feel premium?
- Does the incident detail still feel like proof?
- Are we spending too much time on invisible plumbing?

## 299. Daily Team Sync Questions

- What became working today?
- What still blocks the demo?
- What should be cut if tomorrow slips?

## 300. Delivery Principle

- Finish the path that judges will actually see before chasing extra capability.
