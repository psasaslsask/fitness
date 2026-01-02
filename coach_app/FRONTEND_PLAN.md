# Frontend Direction (v0.1)

## Architecture Recommendation
- **Approach:** Plain HTML + minimal JS using `fetch`.
- **Why:**
  - Keeps bundle-free, easy to serve via FastAPI static files.
  - Simple to inspect/hack by a single developer.
  - No build toolchain; works out-of-the-box with `python -m uvicorn app.main:app`.
- **Structure:**
  - `app/static/index.html` — single-page dashboard shell served by FastAPI.
  - `app/static/styles.css` — light styling for panels and forms.
  - `app/static/app.js` — form handling, API calls, and rendering of results.
- **Data flow:**
  - User fills daily form ➜ `POST /coach` (JSON) ➜ response rendered into four panels (Recommendation, Reasoning, Calorie Estimate, Next Steps).
  - On load, fetch `/profile` to prefill context (e.g., height/goal) and `/logs` for recent entries (optional sidebar/table later).
- **State management:**
  - In-page state only (no client-side routing). Persisted data lives in SQLite via API.
  - Show loading/error states per request; keep strict JSON shapes aligned with backend schemas.

## Minimal UI Wireframe (text)
```
-----------------------------------------------------------
| Local Fitness Coach                                     |
| [Date][Weight][Activity][Hunger 1-10][Food][Workout]   |
| [Submit] [Reset]                                        |
|                                                         |
| Status: [Idle / Loading / Error message]                |
|                                                         |
| Recommendation  | Reasoning                             |
| ----------------+-------------------------------------- |
| - bullet/para   | - bullet/para                         |
|                 |                                        |
| Calorie Estimate| Next Steps                            |
| ----------------+-------------------------------------- |
| - number/notes  | - checklist bullets                   |
-----------------------------------------------------------
```
- Single column on mobile; two-column grid on desktop for panels.
- Reserve a small status strip for loading/errors.
- Keep fonts and spacing calm/neutral to match coaching tone.

## Next Step
If you approve this direction, I’ll draft `index.html`, `styles.css`, and `app.js` with fetch-based calls to `/coach`, `/profile`, and `/logs`, including loading/error handling and strict JSON contracts.
