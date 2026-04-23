# KillCont Research Notes

Last revised: 2026-04-21

## Execution Update (2026-04-21)

- The branch currently runs a verified local MVP profile:
	- FastAPI backend
	- SQLite metadata
	- local filesystem media storage
	- SSE live update stream
	- deterministic demo auth tokens
- This was a deliberate execution shortcut to guarantee a reliable end-to-end judge flow under tight time.
- Public-hosting migration remains the next track and does not invalidate local architecture decisions.

## Updated Delivery Sequencing

1. Keep local profile stable as baseline demo runtime.
2. Add cloud adapters for Firestore and Cloud Storage behind existing service boundaries.
3. Add Firebase-backed auth path with demo fallback retained.
4. Deploy frontend to Firebase Hosting and backend to Cloud Run.
5. Re-run the same smoke flow on cloud profile before demo hardening.

This note turns raw research into product decisions for the hackathon.

## Research Goal

Find the highest-leverage additions that make KillCont stand out to judges without pushing the team outside hackathon scope.

## Strategic Conclusion

KillCont should not present itself as only:

- a watermarking tool,
- a crawler,
- a vector search demo, or
- a legal dashboard.

It should present itself as a full operator workflow:

1. Register trusted media.
2. Watch for suspicious reuse.
3. Explain why the match matters.
4. Let the operator act quickly.

That workflow is much more memorable to judges than isolated technical features.

## What Makes The Product Stronger Than A Basic “AI Detector”

- It protects official assets before they scatter.
- It catches altered content when provenance is missing or stripped.
- It explains evidence visually, not just numerically.
- It helps the rights holder decide what to ignore, monitor, or escalate.
- It keeps the command center live and event-driven.

## Standout Additions Worth Building

### 1. Dual Trust Model

Combine two confidence channels:

- provenance confidence from C2PA or signed registration data
- similarity confidence from embeddings and segment matching

Why it stands out:

- Most demos choose one or the other.
- KillCont can explain that “this upload is suspicious even though credentials were removed.”

### 2. Incident Evidence Pack

Every incident should include:

- matched asset
- similarity score
- matched keyframes or clip segments
- source platform
- detection time
- propagation history
- provenance status
- suggested action

Why it stands out:

- It feels operational and legally useful.
- It turns a model output into an actionable case file.

### 3. Trust Gap Indicator

Add a simple visual badge:

- Credential intact
- Credential stripped
- No credential available
- Edited derivative

Why it stands out:

- Judges immediately understand why the system is useful.
- It creates a clear story around authenticity and tampering.

### 4. Segment-Level Live Monitoring

Instead of saying “we support live media,” demonstrate:

- a simulated live feed
- short segment processing
- incident creation with delay metrics

Why it stands out:

- It gives the dashboard urgency.
- It demonstrates near-real-time relevance for sports media.

### 5. Operator-Facing Explainability

Do not show raw embeddings.

Show:

- matched frames
- confidence band
- what changed
- why the case was classified as high or low risk

Why it stands out:

- It removes black-box fear.
- It makes AI feel usable rather than magical.

### 6. Threat Map With Propagation Story

The map should not be decorative.

It should show:

- where the first suspicious post appeared
- how quickly it spread
- which regions or clusters are active
- which incidents belong to the same campaign

Why it stands out:

- It gives strategic value beyond takedown lists.
- It looks impressive while still serving a product purpose.

### 7. Action Routing, Not Just Alerts

Actions should include:

- Ignore
- Watchlist
- Prepare notice
- Escalate

Why it stands out:

- A polished decision workflow often scores better than extra raw AI features.

## Strong MVP Positioning

KillCont is not trying to monitor the entire internet in six days.

KillCont is proving that a sports rights holder can:

- register trusted assets,
- detect suspicious re-use quickly,
- understand how a clip is spreading,
- and respond with confidence.

That is a realistic and judge-friendly framing.

## Recommended Google Cloud Shape

### Use For MVP

- Firebase Authentication for Google sign-in
- Firestore for metadata and realtime updates
- Firebase Storage / GCS for media storage
- Vertex AI multimodal embeddings for semantic similarity
- Gemini on Vertex AI for incident summarization and action recommendation
- Cloud Run style services for API and worker endpoints
- Pub/Sub for event fan-out
- Google Maps for the threat map

### Use As Optional Stretch

- Cloud Tasks for retryable notice generation or background actions
- Video Intelligence API for shot detection and explainable video slicing
- BigQuery for later-stage analytics and campaign investigation
- Vertex AI Vector Search for scale beyond MVP

## Recommended MVP Search Strategy

Use Firestore vector search first.

Why:

- It keeps the stack consistent with Firebase.
- It reduces infrastructure complexity.
- It is enough for hackathon-scale datasets.
- It supports filtered nearest-neighbor patterns that fit asset type and org filtering.

Upgrade path:

- Move to Vertex AI Vector Search when scale, throughput, or index-management needs outgrow Firestore.

## Recommended Demo Connector Strategy

Build a balanced monitoring story:

- one or two real public connectors
- one or two rich simulated connectors
- one simulated live segment source

Good real candidates:

- YouTube metadata and clips where terms and APIs allow
- Reddit public post feeds

Good simulated candidates:

- “fan clips” feed
- “piracy mirror” feed
- “live segment relay” feed

This mixed setup feels credible and keeps the build manageable.

## Website Experience Conclusions

- The landing page should sell confidence and visibility, not generic AI claims.
- The signed-in product should feel like a broadcast security console.
- Motion should communicate signal flow, not just decoration.
- The dashboard should privilege live state, time, and severity.
- Incident review should be the strongest screen in the app.

## Current Official Source Takeaways

- Firestore vector search supports vector fields and nearest-neighbor queries, making it a strong MVP fit for small-to-medium hackathon datasets.
- Vertex AI multimodal embeddings provide aligned embeddings across media and are a natural fit for similarity workflows.
- Firebase Authentication supports Google sign-in, which matches the requested MVP auth flow.
- Firestore supports realtime listeners, which matches the live dashboard requirement.
- C2PA has official open standards and open-source tooling that strengthen KillCont’s authenticity story.
- Google Maps heatmap support has changed, so the map should use clusters, arcs, and WebGL-driven layers rather than a legacy heatmap implementation.

## References

Official or primary sources used in this planning pass:

- [C2PA official site](https://c2pa.org/)
- [Content Authenticity Initiative GitHub organization](https://github.com/contentauth)
- [Firestore vector search documentation](https://firebase.google.com/docs/firestore/vector-search)
- [Firestore realtime listeners documentation](https://firebase.google.com/docs/firestore/query-data/listen)
- [Firebase Authentication Google sign-in documentation](https://firebase.google.com/docs/auth/web/google-signin)
- [Vertex AI multimodal embeddings documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings/get-multimodal-embeddings)
- [Vertex AI Vector Search documentation](https://cloud.google.com/vertex-ai/docs/vector-search/overview)
- [Cloud Run documentation](https://cloud.google.com/run/docs/)
- [Google Maps JavaScript API deprecations](https://developers.google.com/maps/deprecations)

## Product Decision Result

KillCont should be built as:

- a polished web control room,
- powered by managed cloud services,
- grounded in explainable detection,
- with one visible authenticity layer and one visible AI layer,
- and a clear path from detection to response.
