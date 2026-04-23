# KillCont

KillCont is a web application for digital sports media protection.

It is designed for the Google Solution Challenge and focuses on three demo pillars:

1. Detect reused clips and images across the web.
2. Catch edited or re-uploaded content using AI similarity search.
3. Give operators a live monitoring dashboard with a threat map, evidence, and action workflows.

The product direction in this repo intentionally blends:

- Provenance and authenticity through C2PA-style content credentials.
- Perceptual and semantic detection through multimodal embeddings.
- Operator-grade incident handling through a real-time command center.

This repository is currently in an active scaffold state with the first frontend and backend foundations in place.

There is no CI/CD setup by design for this hackathon project.

## Primary Stack Direction

- Frontend: React + Vite + TypeScript
- Backend: FastAPI + Python
- Auth and realtime data: Firebase Authentication + Firestore
- File storage: Firebase Storage / Google Cloud Storage
- AI: Vertex AI multimodal embeddings + Gemini on Vertex AI
- Background processing: Pub/Sub + Cloud Run style services
- Maps: Google Maps platform for the threat map experience

## Product Thesis

Most tools do one of two things:

- watermark and hope the watermark survives, or
- scan for similar content and leave humans to sort out the rest.

KillCont should stand out by combining three layers in one experience:

- Trust: prove official origin when credentials exist.
- Detection: identify likely reused or transformed media even when credentials are stripped.
- Action: give operators a fast path to review, prioritize, and respond.

## What To Read First

- [Master planning mindset](D:/KillCont/docs/mindset.md)
- [Architecture](D:/KillCont/docs/architecture.md)
- [Design direction](D:/KillCont/docs/design-direction.md)
- [Website blueprint](D:/KillCont/docs/website-blueprint.md)
- [Research notes](D:/KillCont/docs/research-notes.md)
- [Status tracker](D:/KillCont/docs/status.md)
- [Team logbook](D:/KillCont/docs/logbook.md)

## Repository Layout

```text
KillCont/
  apps/
    api/
    web/
  assets/
    branding/
    demo-media/
  data/
    simulated-feeds/
  docs/
  infra/
    google-cloud/
  packages/
    contracts/
    design-system/
  scripts/
```

## Working Rules For This Project

- Keep the MVP strictly hackathon-sized.
- Do not add CI/CD.
- Do not plan for custom model training.
- Prefer Google Cloud managed services when they reduce implementation burden.
- Build for sports first, but keep naming and architecture reusable for other media verticals later.
- Update `docs/status.md` and `docs/logbook.md` after every meaningful implementation milestone.

## Recommended Build Order

1. Finalize product flow and UI blueprint.
2. Scaffold the React and FastAPI apps.
3. Implement Google login and protected app shell.
4. Build asset registration and ingestion.
5. Build embedding generation and similarity matching.
6. Build realtime incident feed and dashboard.
7. Add simulated live feed and threat map.
8. Add provenance indicators and evidence workflow.
9. Polish demo storytelling and performance.

## Notes

- A `Design.md` from your side can later refine visual direction and component detail.
- The planning docs already assume a corporate sports-tech visual language with room to expand beyond sports.
- Mixed real plus simulated feeds are a deliberate product decision, not a compromise. They make the demo believable while keeping the team inside hackathon scope.
