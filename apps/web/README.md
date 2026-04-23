# Web App

Current frontend stack:

- React
- Vite
- TypeScript
- TanStack Query
- Framer Motion

## Runtime Config

- `VITE_API_BASE_URL`: backend API origin (default local API).
- `VITE_AUTH_MODE`: `demo` or `firebase`.

In `demo` mode, sign-in uses local demo tokens.
In `firebase` mode, sign-in expects a Firebase ID token to be available for login payload handoff.

## Local Run

1. Copy `.env.example` to `.env`.
2. Install dependencies.
3. Start dev server:

```powershell
npm run dev
```

Guiding principle:

- the web app should feel like an operator console, not a generic dashboard template.
