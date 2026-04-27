# Real Google Sign-In (Bundle F) — Design Spec

**Date:** 2026-04-27
**Author:** Claude (sonnet-4.7) under brainstorming skill, ratified by user
**Repo:** `D:\kill-cont-fresh`
**Branch base:** `second_branch`
**Predecessor specs:**
- [`2026-04-26-fix-incompleteness-design.md`](2026-04-26-fix-incompleteness-design.md) (Bundles B/A/C/D, all landed)
- [`2026-04-27-live-cascade-and-duplicates-design.md`](2026-04-27-live-cascade-and-duplicates-design.md) (Bundle E, landed)
- S5 (Firebase Google sign-in frontend, landed 2026-04-25)

---

## 1. Goal in one sentence

Operators (judges, teammates, anyone with a Google account) can sign in to KillCont with one click on "Continue with Google" — while the offline-demo flow at `AUTH_BACKEND=demo` keeps working unchanged.

## 2. What's already done (S5, 2026-04-25)

- **Frontend:** `apps/web/src/lib/firebase.ts` — full Google popup + token rotation. `SignInPage.tsx` shows "Continue with Google" when `VITE_AUTH_MODE=firebase`. `useAuth.ts` reads the ID token from `localStorage[FIREBASE_ID_TOKEN_KEY]`.
- **Backend:** `apps/api/app/services/authn.py::verify_firebase_id_token` validates Firebase ID tokens via `firebase-admin`. `routes/session.py::login` accepts `id_token`, dispatches by `auth_backend()`, calls `repos.upsert_user(org_id=demo_org_id)`. The middleware in `main.py` already routes via `authenticate_request_token`.

**The wiring is complete.** What's missing is provisioning + documentation + a small handful of UX tightening.

## 3. User-facing decisions (locked during brainstorming)

| # | Decision | Choice |
|---|---|---|
| Q1 | Who is allowed to sign in? | **A** — open access, any verified Google account auto-joined to demo org as `operator` |
| Q2 | Firebase project provisioning | **A** — fresh start, write `infra/google-cloud/SETUP.md` walkthrough |
| Q3 | Backend Firebase Admin credentials | **A** — service account JSON at `apps/api/service-account.json`, `FIREBASE_CREDENTIALS_PATH=service-account.json` |
| Q4 | Default auth mode for local dev | **A** — `AUTH_BACKEND=demo` stays default; firebase is opt-in |

## 4. Architecture

Three pieces are already load-bearing and untouched by this spec:

- **`app/services/authn.py::authenticate_request_token`** — already dispatches by `auth_backend()`. No change.
- **`app/api/routes/session.py::login`** — already handles both modes. Small role-default tweak only.
- **`apps/web/src/lib/firebase.ts`** — already wires Google popup + token rotation. No change.

What this spec adds:

1. **`infra/google-cloud/SETUP.md`** — the missing operator-facing provisioning doc.
2. **Role default of `"operator"` for new Google sign-ins** (was implicitly `"admin"`).
3. **Startup auth config sanity check** — warn loudly if `AUTH_BACKEND=firebase` but the credentials path is broken, instead of silently failing on first sign-in.
4. **Sign-in popup cancel error handling** — show a clean inline message when the user dismisses the Google popup.
5. **`.env.example` pointer comments** — make the firebase env vars discoverable.

### 4.1 Component diagram (text)

```
Browser
  │
  │  click "Continue with Google" (only rendered when VITE_AUTH_MODE=firebase)
  │
  ▼
firebase.ts::signInWithGoogle()
  │
  │  signInWithPopup(GoogleAuthProvider)
  │
  ▼
Google OAuth flow (Firebase-managed popup)
  │
  │  returns ID token (1h validity, auto-rotated by onIdTokenChanged)
  │
  ▼
useAuth.signIn() → POST /api/v1/session/login {id_token}
  │
  ▼
session.py::login (NEW: role="operator" for firebase mode)
  │
  │  authn.verify_firebase_id_token(id_token)  ──── firebase-admin SDK
  │  ↓                                              uses service-account.json
  │  claims = {uid, email, name, ...}              from FIREBASE_CREDENTIALS_PATH
  │
  │  repos.upsert_user(user_id=uid, ..., role="operator", org_id=demo_org_id)
  │
  ▼
returns {token: <id_token>, user: {...}}

Subsequent API calls
  │
  │  Authorization: Bearer <id_token>
  │
  ▼
main.py middleware → authn.authenticate_request_token
  │
  ▼
verify_firebase_bearer → returns AuthIdentity
  │
  ▼
request.state.user_id = identity.user_id
```

### 4.2 Data model touchpoints

**No schema migration.** The `users.role` column already exists with default `"admin"`. We just stop forcing all Google sign-ins to inherit `"admin"` by:

1. Adding an optional `role` kwarg to `repos.upsert_user(...)` (sqlite + firestore).
2. Passing `role="operator"` from `session.py::login` when the request comes via firebase mode.
3. Demo mode keeps the implicit `"admin"` default for backward compatibility.

The `org_id` for every Google user is `settings.demo_org_id` ("org-demo-1") per Q1's open-access decision. Multi-tenant org provisioning is explicitly deferred (§7).

## 5. Component-level design

### 5.1 Backend: `repos.upsert_user` accepts `role` kwarg

`apps/api/app/services/repos/_sqlite.py`:

```python
def upsert_user(
    user_id: str,
    email: str,
    display_name: str,
    org_id: str,
    role: str | None = None,  # NEW
) -> dict:
    with get_conn() as conn:
        existing = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if existing:
            # Don't overwrite role on existing users — preserves any manual promotions.
            conn.execute(
                "UPDATE users SET email = ?, display_name = ?, org_id = ? WHERE id = ?",
                (email, display_name, org_id, user_id),
            )
        else:
            conn.execute(
                "INSERT INTO users (id, email, display_name, org_id, role) "
                "VALUES (?, ?, ?, ?, ?)",
                (user_id, email, display_name, org_id, role or "admin"),
            )
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return row
```

Mirror in `_firestore.py` — adds `"role": role or "admin"` to the insert payload, leaves existing user rows alone.

The signature stays backward-compatible: callers that don't pass `role` get the existing `"admin"` default.

### 5.2 Backend: `session.py::login` passes `role="operator"` for firebase mode

```python
if mode == "firebase":
    # ...existing token verification, claims extraction unchanged...
    user = repos.upsert_user(
        user_id=user_id,
        email=email,
        display_name=display_name,
        org_id=settings.demo_org_id,
        role="operator",  # NEW — Google sign-ins are operators by default
    )
else:
    # Demo mode unchanged — implicit "admin" default
    user = repos.upsert_user(
        user_id=user_id,
        email=email,
        display_name=display_name,
        org_id=settings.demo_org_id,
    )
```

### 5.3 Backend: startup auth config check

`apps/api/app/main.py` — add a startup hook that logs a clear status line. Does NOT crash; we want the API to come up so the smoke harness's `/health` still works. Logs are visible in `/tmp/api.log` and Cloud Run logs.

```python
@app.on_event("startup")
async def _verify_auth_config():
    settings = get_settings()
    log = logging.getLogger("killcont.startup")
    if settings.auth_backend == "firebase":
        if settings.firebase_credentials_path:
            path = Path(settings.firebase_credentials_path)
            if not path.is_absolute():
                path = API_ROOT / path
            if path.exists():
                log.info("AUTH_BACKEND=firebase using credentials at %s", path)
            else:
                log.warning(
                    "AUTH_BACKEND=firebase but FIREBASE_CREDENTIALS_PATH=%s does not exist — sign-in will fail until this is fixed",
                    settings.firebase_credentials_path,
                )
        else:
            log.info("AUTH_BACKEND=firebase using Application Default Credentials")
    else:
        log.info("AUTH_BACKEND=%s (demo mode — anyone can sign in with email+name)", settings.auth_backend)
```

(API_ROOT is already imported elsewhere in main.py / config.py.)

### 5.4 Frontend: SignInPage popup-cancel error handling

`apps/web/src/features/auth/SignInPage.tsx` — wrap `signInWithGoogle()` calls in try/catch, render an inline `.auth-panel__error` for known cancel cases. Firebase's popup-cancel maps to error codes like `auth/popup-closed-by-user` and `auth/cancelled-popup-request`.

```typescript
async function handleGoogle() {
  try {
    setError("");
    setSubmitting(true);
    const result = await signInWithGoogle();
    await signIn(result.email, result.displayName);
    navigate("/app/overview");
  } catch (err: unknown) {
    const code = (err as { code?: string })?.code ?? "";
    if (code === "auth/popup-closed-by-user" || code === "auth/cancelled-popup-request") {
      setError("Sign-in cancelled. Try again, or pick a different account.");
    } else if (code === "auth/popup-blocked") {
      setError("Browser blocked the popup. Please allow popups for this site and retry.");
    } else {
      setError(err instanceof Error ? err.message : "Sign-in failed. Please try again.");
    }
  } finally {
    setSubmitting(false);
  }
}
```

(Existing `setError` and `submitting` state already exist in SignInPage.)

### 5.5 `.env.example` pointer comments

`apps/api/.env.example` — add a comment block above `AUTH_BACKEND`:

```
# Auth backend: demo or firebase
# To enable real Google sign-in, see infra/google-cloud/SETUP.md
# (10-minute walkthrough: Firebase project + service-account.json + env vars)
AUTH_BACKEND=demo
```

`apps/web/.env.example` — same pattern above `VITE_AUTH_MODE`.

### 5.6 `infra/google-cloud/SETUP.md` (the deliverable)

Markdown walkthrough with an explicit "you will need:" preamble, then numbered steps. Each step:

- States the click target verbatim (e.g., "Console → Authentication → Sign-in method → Google → Enable")
- Tells you what to expect (e.g., "you'll see a green status bar saying Google is now enabled")
- Tells you what to copy/save (e.g., "save the JSON as `apps/api/service-account.json` — it's gitignored by `*.json`")

Sections (top-level):

1. **Prerequisites** — Google account, ~10 min, no payment required (Spark plan)
2. **Create a Firebase project**
3. **Enable Authentication + Google sign-in provider**
4. **Add a Web App and copy its config**
5. **Generate a service account key**
6. **Wire up `apps/api/.env`**
7. **Wire up `apps/web/.env`**
8. **First sign-in** — restart both servers, navigate to `/sign-in`, click "Continue with Google"
9. **Troubleshooting** — popup blocked, "Firebase: Error (auth/unauthorized-domain)", "service account file not found", token rotation
10. **Future: production deploy** — pointer to S12 deploy scripts and what extra Authorized Domain entries to add

Total length ~250–350 lines including code blocks.

## 6. Verification matrix

| Action | Expected result |
|---|---|
| Run with `AUTH_BACKEND=demo` (default) | Sign-in page shows email + name form. Submit → demo bearer token. **Must not regress.** |
| Run with `AUTH_BACKEND=firebase` + valid `service-account.json` + populated `apps/web/.env` | Sign-in page shows "Continue with Google" only. Click → popup → user signs in → `/app/overview` loads with their real email + name from Google. |
| Run with `AUTH_BACKEND=firebase` but `service-account.json` missing | Startup logs a clear warning. First sign-in attempt fails with HTTP 500 + clear message ("firebase auth backend requires firebase-admin package" or similar). |
| Sign in with a fresh Google account | New user row appears in `users` table with `role="operator"`, `org_id="org-demo-1"`. |
| Sign in twice with the same Google account | `upsert_user` updates email + display_name (Google may have changed them), preserves existing `role` (no admin → operator demotion if you manually promoted). |
| Click "Sign out" while signed in via Google | Calls `signOutGoogle()`, clears `localStorage[FIREBASE_ID_TOKEN_KEY]` AND `[TOKEN_KEY]`. Returns to `/sign-in`. |
| Cancel the Google popup mid-flow | Inline error: *"Sign-in cancelled. Try again, or pick a different account."* No crash, no state corruption. |
| Browser blocks the popup | Inline error: *"Browser blocked the popup. Please allow popups for this site and retry."* |
| Token expiration (~1h) | `onIdTokenChanged` re-stashes the rotated token automatically; next API call uses the fresh one. No user-visible signal. |

## 7. Out of scope (intentionally rejected or deferred)

- **Multi-tenant org provisioning.** Every Google user joins `org-demo-1`. Per-user orgs deferred to post-hackathon.
- **Email allowlist / domain allowlist.** Open access per Q1 — anyone with a Google account can sign in.
- **Server-side token revocation / kicked-user flow.** Sign-out is purely client-side. Firebase tokens expire in ~1h naturally. To kick someone faster, use Firebase Console → Authentication → Users → Disable.
- **Email-link, magic-link, SMS, MFA, other providers.** Just Google OAuth.
- **Cloud Run + Firebase Hosting deploy execution.** That's S12, the next phase. This phase verifies auth works LOCALLY against a real Firebase project. Deploy artifacts (`Dockerfile`, `deploy-api.sh`, `firebase.json`, `deploy-web.sh`) already exist from S10/S11.
- **CI/CD.** Explicit project rule.

## 8. Risks & mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| User commits `service-account.json` accidentally | Medium | `apps/api/.gitignore` already includes `*.json` and `service-account.json` literal. SETUP.md repeats the warning. |
| User confused why "Continue with Google" doesn't appear | Medium | The button only renders when `VITE_AUTH_MODE === "firebase"` AND `isFirebaseConfigured()` returns true. SETUP.md step 7 makes this explicit. |
| Authorized Domain misconfig blocks the popup with "auth/unauthorized-domain" | High during first attempt | SETUP.md §9 troubleshooting addresses this; says exactly what error to look for and how to add `localhost` |
| Service account key has too many permissions | Low | The default Firebase-generated key is scoped to the Firebase project only. Documented in §3 of SETUP.md. |
| Existing demo users get promoted to operator on first firebase sign-in | None — different `user_id` namespace | Demo user_ids look like `demo-user-1`; Firebase user_ids look like `oauth2|googleId` or a UUID. No collision. |
| Role downgrade if existing admin signs in via Google twice | Low | `upsert_user` on update path doesn't touch the role column. Only inserts use the role kwarg. |

## 9. Implementation phasing

Single phase, 7 tasks, all on `second_branch`. Each independently committable.

1. **F-T1** — `upsert_user` accepts `role` kwarg (sqlite + firestore + __init__ verified)
2. **F-T2** — `/session/login` passes `role="operator"` for firebase mode
3. **F-T3** — Startup auth config check + log line
4. **F-T4** — SignInPage popup-cancel error handling
5. **F-T5** — `.env.example` pointer comments to SETUP.md
6. **F-T6** — Write `infra/google-cloud/SETUP.md` (the big one — ~250 lines)
7. **F-T7** — Verification gate: smoke harness re-run + manual end-to-end flow against a test Firebase project + docs roll-forward (status + logbook + CLAUDE)

After F-T7 lands, the user runs the SETUP.md walkthrough on their own machine, provisions Firebase, populates `.env`, and exercises the real sign-in flow. Bugs surfaced there get fixed in follow-up commits.

After the auth phase verifies clean, S12 (deploy) runs as a separate plan: user runs `bash infra/google-cloud/deploy-api.sh` and `bash infra/google-cloud/deploy-web.sh` against the same Firebase project.

## 10. Files touched (forecast)

**New (1 file):**
- `infra/google-cloud/SETUP.md`

**Modified (~6 files):**
- `apps/api/app/services/repos/_sqlite.py` — `upsert_user` role kwarg
- `apps/api/app/services/repos/_firestore.py` — same
- `apps/api/app/api/routes/session.py` — pass `role="operator"` for firebase mode
- `apps/api/app/main.py` — startup auth config check + log line
- `apps/web/src/features/auth/SignInPage.tsx` — popup-cancel error handling
- `apps/api/.env.example` + `apps/web/.env.example` — pointer comments

No schema migration. No new dependencies. `firebase-admin` and the firebase web SDK are both already installed.

---

**Spec status:** ratified during 2026-04-27 brainstorm. Ready for the writing-plans skill.
