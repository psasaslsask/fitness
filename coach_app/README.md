# Local Fitness Coach

A local-first FastAPI application that turns a persistent system prompt, structured inputs, and your history into calm, opinionated coaching for training and nutrition.

## Run locally

```bash
pip install -r requirements.txt
uvicorn coach_app.app.main:app --reload
```

The API seeds a default user profile and system prompt on startup. Use the `/coach` endpoint to submit structured daily inputs and receive recommendations, and `/profile` or `/system-prompt` to adjust your context.
