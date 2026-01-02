# Local Fitness Coach

A local-first FastAPI application that turns a persistent system prompt, structured inputs, and your history into calm, opinionated coaching for training and nutrition.

## Run locally

```bash
# from repo root
cd coach_app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# optional: configure your LLM endpoint
export LLM_API_KEY="sk-..."           # required to call a real API; omit to use offline stub
export LLM_MODEL="gpt-4o-mini"        # override if desired
export LLM_API_URL="https://api.openai.com/v1/chat/completions"  # override if self-hosted

# start the API
uvicorn coach_app.app.main:app --reload --port 8000
```

The API seeds a default user profile and system prompt on startup. Primary endpoints:

- `POST /coach` – submit structured daily inputs and receive recommendations (also persisted).
- `GET/PUT /profile` – view or update the persistent profile.
- `GET/PUT /system-prompt` – inspect or adjust the coaching system prompt.
- `GET /logs` – retrieve stored daily logs, workouts, and meals.

The local dashboard is served at `http://localhost:8000/` (static HTML/JS/CSS under `app/static`). Submit the daily form to `POST /coach`; responses render into four panels: recommendation, reasoning, calorie estimate, and next steps. Loading/error states are shown in the header status pill.

FastAPI will expose interactive docs at `http://localhost:8000/docs` for quick testing. The SQLite database (`fitness.db`) lives next to the app by default and is created automatically on first run.
