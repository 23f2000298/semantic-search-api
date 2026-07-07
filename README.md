# Semantic Search — Top-K Ranking API

## What this does
POST `/rank` with `{"query_id", "query", "candidates": [...]}`, returns
`{"ranking": [i, j, k]}` — the 3 candidate indices most similar to the query,
per `text-embedding-3-small` cosine similarity.

## Deploy to Render (recommended — you've used this before)

1. **Push to GitHub**
   ```bash
   cd semantic-search-api
   git init
   git add .
   git commit -m "semantic search ranking API"
   gh repo create semantic-search-api --public --source=. --push
   # or manually create a repo on github.com and git push to it
   ```

2. **Create the Render service**
   - Go to https://dashboard.render.com → New → Web Service
   - Connect your GitHub repo
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Instance type: Free is fine

3. **Set the environment variable**
   - In the Render service → Environment tab
   - Add `OPENROUTER_API_KEY` = your OpenRouter key (starts with `sk-or-v1-...`,
     from https://openrouter.ai/keys)
   - Make sure your OpenRouter account has a little credit added — embeddings
     cost about $0.02 per million tokens, so a couple of dollars covers a lot
     of grading requests.

4. **Deploy** — Render gives you a URL like:
   `https://semantic-search-api-xxxx.onrender.com`

   Your submission URL is: `https://semantic-search-api-xxxx.onrender.com/rank`

## Important: avoid cold-start timeouts

Render's free tier sleeps after ~15 min idle, and the first request after
sleeping can take 30-50s to wake up — this can look like a timeout to the
grader. Two options:

- **Before the grader runs**, hit your `/` health endpoint once yourself to
  wake it up.
- **Keep it warm**: use a free pinger like https://cron-job.org to GET your
  `/` endpoint every 10 minutes during the grading window.

## Test locally before deploying

```bash
cd semantic-search-api
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."
uvicorn main:app --reload
```

Then in another terminal:
```bash
curl -X POST http://127.0.0.1:8000/rank \
  -H "Content-Type: application/json" \
  -d '{
    "query_id": "q0",
    "query": "How do I automatically scale the number of pods when CPU usage rises?",
    "candidates": [
      "A valley fold creases the paper so the crease points toward you.",
      "Horizontal Pod Autoscaler adds or removes pods based on observed CPU or custom metrics.",
      "Bake at 180C for twenty five minutes until golden."
    ]
  }'
```

Expected shape of response:
```json
{"ranking": [1, 0, 2]}
```
(exact values depend on your real 18-candidate payload — this 3-candidate
example is just to confirm the server responds correctly)

## Test the deployed version

```bash
curl -X POST https://semantic-search-api-xxxx.onrender.com/rank \
  -H "Content-Type: application/json" \
  -d '{"query_id":"q0","query":"test query","candidates":["a","b","c"]}'
```

If you get a valid JSON `{"ranking": [...]}` back, you're done — submit the
`/rank` URL.
