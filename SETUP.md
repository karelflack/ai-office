# Setup Guide

Get Pathless AI Office running on your machine in a few minutes.

---

## What you need

- **Python 3.11 or newer** — check with `python3 --version`
- **Node.js 18 or newer** — check with `node --version`
- **A Claude API key** — get one at [console.anthropic.com](https://console.anthropic.com)

---

## Steps

### 1. Clone the repo

```bash
git clone https://github.com/karelflack/ai-office.git
cd ai-office
```

### 2. Install Python dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Install Claude Code CLI

```bash
npm install -g @anthropic/claude-code
```

Then authenticate it with your Claude API key:

```bash
claude
```

Follow the prompts to log in. You only need to do this once.

### 4. Set up your environment

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```
ANTHROPIC_API_KEY=your_key_here   # required
OPENAI_API_KEY=your_key_here      # optional — only needed for web search agents
```

Your `ANTHROPIC_API_KEY` is the same key you used to authenticate Claude Code.

### 5. Start the server

```bash
python3 server.py
```

You should see:

```
AI Office server running on http://localhost:8000
```

### 6. Open the dashboard

Go to [http://localhost:8000](http://localhost:8000) in your browser.

Login with:
- **Username:** admin
- **Password:** office

---

## Running the tests

```bash
python3 -m pytest tests/test_core.py
```

---

## Optional: Web search for agents

Some agents (Else, Halvard, Magnus, etc.) can search the web using OpenAI. This requires an OpenAI API key in your `.env` file. If you don't have one, everything still works — those agents just won't have access to live web data.

---

## Troubleshooting

**"claude: command not found"** — Claude Code CLI isn't installed or not in your PATH. Re-run the npm install step.

**Agents don't start** — Make sure you've authenticated Claude Code (`claude` in terminal) and that your `ANTHROPIC_API_KEY` is set in `.env`.

**Port 8000 already in use** — Something else is running on that port. You can change the port at the bottom of `server.py`.
