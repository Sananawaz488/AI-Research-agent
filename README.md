# 🔎 AI Research Agent

A beginner-friendly single-agent AI research tool built with:
- **[CrewAI](https://www.crewai.com/)** — the agent framework
- **[Groq](https://groq.com/)** — free, very fast LLM inference (using the
  `openai/gpt-oss-120b` model)
- **[ddgs](https://pypi.org/project/ddgs/)** — free DuckDuckGo web search (no API key)
- **[Streamlit](https://streamlit.io/)** — the web UI

You type a topic → the agent searches the web a few times → it writes you
a structured markdown report.

This guide skips running it locally and goes straight from GitHub to a
live Streamlit Cloud deployment, using **Streamlit Secrets** for your
Groq API key (the app only reads the key from secrets — there's no
password box in the UI).

## Project structure

```
ai-research-agent/
├── app.py                        # Streamlit UI — the app's entry point
├── agent.py                       # Defines the CrewAI agent, task, and crew
├── tools/
│   ├── __init__.py
│   └── search_tool.py             # Custom free DuckDuckGo search tool
├── requirements.txt
├── .streamlit/
│   └── secrets.toml.example       # Reference only — shows the secrets format
├── .gitignore
└── README.md
```

## Step 1 — Get a free Groq API key

1. Go to https://console.groq.com/keys
2. Sign up (free) and click "Create API Key"
3. Copy the key — it starts with `gsk_...` and keep it somewhere safe.
   You'll paste it into Streamlit Cloud in Step 3, not into any file.

## Step 2 — Push this project to GitHub

1. Create a new empty repository on GitHub (e.g. `ai-research-agent`).
2. From this project folder:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: AI research agent"
   git branch -M main
   git remote add origin https://github.com/<your-username>/ai-research-agent.git
   git push -u origin main
   ```

⚠️ Never commit a real API key. There is no `.env` file in this project
and `.streamlit/secrets.toml` (a real one, if you ever create it) is
already excluded by `.gitignore`. The `secrets.toml.example` file in this
repo is just a reference — it has no real key in it.

## Step 3 — Deploy on Streamlit Community Cloud (free)

1. Go to https://share.streamlit.io and sign in with GitHub.
2. Click **"New app"**, pick your `ai-research-agent` repo, branch `main`,
   and main file path `app.py`.
3. Before clicking Deploy (or any time after), open
   **"Advanced settings" → "Secrets"** and paste:
   ```toml
   GROQ_API_KEY = "gsk_your_real_key_here"
   ```
   (use your real key from Step 1)
4. Click **Deploy**. First build takes a couple of minutes.
5. Once it's live, open the app — the sidebar should show
   "Groq API key loaded from Streamlit secrets ✅". Type a topic and
   click **Run Research**.

If you ever need to change the key later: go to your app on
share.streamlit.io → **Settings → Secrets**, edit it, save, and the app
will restart automatically.

## How it works (quick tour for beginners)

- **`tools/search_tool.py`** — a small class that wraps `ddgs` (DuckDuckGo
  search) so CrewAI's agent can call it like any other tool.
- **`agent.py`** — creates:
  - one `Agent` (the "Senior Research Analyst") with the search tool and a
    Groq LLM attached,
  - one `Task` telling it exactly what to do and what the output should
    look like,
  - one `Crew` that runs that single agent/task pair.
- **`app.py`** — the Streamlit page: reads `GROQ_API_KEY` from
  `st.secrets`, takes your topic, calls `run_research()` from `agent.py`,
  and displays the returned report.

## Customizing

- **Change the model**: edit the dropdown in `app.py` or `DEFAULT_MODEL`
  in `agent.py`. Groq model names always look like `groq/<model-id>`.
  This project defaults to `groq/openai/gpt-oss-120b`.
- **More sources per search**: change `max_results=5` in
  `tools/search_tool.py`.
- **Different report format**: edit the `expected_output` text inside
  `agent.py`'s `Task`.
- **Add a second agent later** (e.g. an "Editor" that polishes the
  report): add another `Agent` + `Task` in `agent.py` and include both in
  the `Crew`'s `agents`/`tasks` lists, in order.

## Troubleshooting

- **Sidebar says "No GROQ_API_KEY found in Streamlit secrets"**: go to
  your app on share.streamlit.io → Settings → Secrets and make sure the
  line is exactly `GROQ_API_KEY = "gsk_..."` (with quotes), then save —
  the app restarts automatically.
- **"Search failed" in the report**: DuckDuckGo occasionally rate-limits
  rapid requests. Wait a few seconds and click Run Research again.
- **Import error for `ddgs`**: make sure `requirements.txt` is at the
  repo root (Streamlit Cloud installs it automatically on deploy). Older
  tutorials mention a package called `duckduckgo_search` — it was renamed
  to `ddgs`, which is what this project already uses.
- **Groq errors about an invalid model**: Groq occasionally retires older
  models. Check current model names at
  https://console.groq.com/docs/models and update `DEFAULT_MODEL` in
  `agent.py` if needed.
- **App is slow / times out**: `gpt-oss-120b` is a reasoning model, so it
  thinks longer than smaller models. Try `groq/openai/gpt-oss-20b` in the
  sidebar dropdown for faster (slightly less thorough) results.
