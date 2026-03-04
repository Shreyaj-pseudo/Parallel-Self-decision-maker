# 🧠 Parallel Self — Multi-Persona Decision Engine

> *Stop asking AI for answers. Start having a debate.*

Parallel Self is a full-stack AI application that simulates an internal debate between four distinct reasoning personas to help you make smarter, more considered decisions. Instead of getting a single generic AI response, your topic is analyzed sequentially by a Risk Analyst, an Optimist, a Strategist, and a Moderator — each one building on the last — producing a layered, nuanced recommendation that reflects the real complexity of your choices.

Built for people who think seriously about their decisions.

---

## What Makes This Different

Most AI tools give you one answer from one perspective. Parallel Self gives you four — in sequence, each aware of what the others said. The Risk Self warns you. The Optimist challenges that. The Strategist maps the trade-offs. The Moderator synthesizes it all into a verdict.

The result is closer to thinking than to querying.

### Key Differentiators

**Sequential Reasoning Architecture** — Each persona reads the previous one's output before responding. This isn't just four parallel prompts; it's a genuine chain of thought across distinct cognitive frames.

**Persistent Long-Term Memory** — The AI remembers who you are across sessions. Your background, your priorities, your past decisions — all woven into every debate automatically via RAG (Retrieval-Augmented Generation).

**Stateful Session Management** — Every debate is saved to a thread. Come back tomorrow, resume the same conversation, and the AI picks up exactly where it left off.

**Real-Time Streaming UI** — Watch each persona think and respond live. The dashboard lights up panel by panel as the debate unfolds.

---


### How a Debate Works (Lifecycle)

```
User submits topic
        │
        ▼
[Risk Analyst]
Identifies dangers, hidden costs, worst-case scenarios
Ends with one critical question the user must answer
        │
        ▼
[Opportunity Finder]
Reads the Risk analysis. Finds the genuine upside.
Maps career capital, network potential, 2-year outcomes.
        │
        ▼
[Strategist]
Reads both. Cuts through emotion.
Compares options on concrete dimensions — timeline, upside ceiling, downside floor.
        │
        ▼
[Moderator]
Synthesizes everything. Makes a decision.
States recommendation, the condition that would change it,
and one concrete next step for this week.
        │
        ▼
Thread saved → Resume anytime
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| AI Provider | Backboard | Assistant hosting, thread memory, RAG |
| Backend | FastAPI (Python) | REST API + Server-Sent Events |
| Frontend | Vanilla HTML/CSS/JS | Zero-dependency dashboard |
| Session Store | JSON (local file) | Lightweight thread persistence |
| Streaming | SSE (EventSource) | Live panel-by-panel updates |
| Memory | Backboard Memory API | Long-term user context |
| Config | python-dotenv | Environment variable management |

---

## Prerequisites

- Python 3.10+
- A Backboard account with an API key
- pip

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/parallel-self.git
cd "parallel-self"
```

### 2. Install backend dependencies

```bash
cd backend
pip install fastapi uvicorn python-dotenv requests
```

### 3. Configure environment variables

Create a `.env` file inside the Parent folder:

```env
BACKBOARD_API_KEY=your_backboard_api_key_here
BACKBOARD_ASSISTANT_ID=your_assistant_id_here
```

> **Note:** The `BACKBOARD_ASSISTANT_ID` is generated on first run if not provided. The terminal will print the new ID and instruct you to paste it into your `.env` file. This only happens once — after that, the assistant persists forever.

### 4. (Optional) Configure model settings

Edit `config.py` to change the default model or provider:

```python
DEFAULT_MODEL = "your-preferred-model"
DEFAULT_PROVIDER = "your-provider"
```

---

## Running the Application

Run the `start.bat` file you should see **two terminals** open simultaneously.

### Terminal 1 — The Backend API

you should see

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [31832] using StatReload
INFO:     Started server process [7424]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```


### Terminal 2 — Serve the Frontend

you should see 

```
Serving HTTP on :: port 3000 (http://[::]:3000/) ...
```

### Open the App

Navigate to `http://localhost:3000` in your browser.

> **Why can't I just open the HTML file directly?** Browsers block fetch requests from `file://` URLs due to CORS policy. The Python HTTP server bypasses this.

---

## Using Parallel Self

### Starting a New Debate

1. Type your decision or topic in the top input bar
2. Give the session a name (e.g. "Summer Internship Decision")
3. Click **Run Debate →**
4. Watch each panel light up as the personas respond in sequence

### Resuming a Past Debate

1. Click a session name in the left sidebar — it loads automatically
2. Enter a new topic or follow-up question
3. The AI picks up from the exact thread where you left off, with full context of the previous debate

### Managing Your Memory

Your assistant has long-term memory — facts about you that persist across every session and debate.

Click **Manage Memories →** in the sidebar to:
- **View** all stored memories
- **Add** new context ("I just got rejected from X", "I'm now considering Y")
- **Delete** memories that are no longer relevant

The richer your memory, the more personalized every debate becomes.

### Reading Full Responses

Each panel has an **expand** button (appears on hover) that opens the full response in a dedicated reading window — useful when a persona gives a long, detailed analysis that's hard to read in a narrow column.

---

## API Endpoints

The FastAPI backend exposes the following endpoints:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/sessions` | List all saved session names |
| `GET` | `/debate/stream` | SSE stream — runs the full 4-persona debate live |
| `POST` | `/debate/new` | Non-streaming — runs debate and returns all results |
| `POST` | `/debate/resume` | Resume an existing thread (non-streaming) |
| `GET` | `/memory/list` | Fetch all long-term memories |
| `POST` | `/memory/add` | Add a new memory |
| `DELETE` | `/memory/{memory_id}` | Delete a memory by ID |

You can explore all endpoints interactively via the auto-generated docs at:
```
http://localhost:8000/docs
```

---

## The Personas

Each persona is carefully engineered to play a specific cognitive role and explicitly build on the output of the previous one.

**The Risk Analyst** is the skeptic. It identifies dangers, hidden costs, opportunity costs, and worst-case scenarios without sugarcoating. It ends every response with one key question the user must answer before proceeding.

**The Opportunity Finder** has read what the Risk Analyst said and refuses to ignore it — but finds the genuine upside anyway. It maps career capital, doors that could open, and what the best version of this decision looks like two years from now.

**The Strategist** is cold and precise. It reads both previous responses and maps concrete trade-offs: timeline, effort required, upside ceiling, downside floor. It identifies what you would need to believe for each path to be the right one.

**The Moderator** synthesizes the full debate. It makes a decisive recommendation, states the condition that would change that recommendation, and gives you one concrete next step to take this week.

---

## How Memory Works

When you interact with Parallel Self, the Backboard assistant automatically extracts and stores facts about you — your background, your goals, your constraints, your past decisions. This is called Auto-RAG (Retrieval-Augmented Generation).

On every debate turn, the assistant silently retrieves relevant memories and injects them into its reasoning. This means:

- The Risk Analyst knows you're a second-year student with limited runway
- The Optimist knows you've been burned by over-commitment before
- The Moderator knows your actual priorities, not just the ones you stated today

You can also manually add memories via the **Manage Memories** panel — for example, after a major life event ("I just accepted an offer at X") or a change in priorities.

---

## Running the CLI Version

If you prefer working in the terminal, the original CLI is still fully functional:

```bash
cd backend
python main.py
```

This runs the same debate engine without the web interface, saving sessions to `sessions.json` the same way.

---

## Project Philosophy

Most decision-support tools either give you information or give you an answer. Parallel Self does neither — it gives you a *structured argument*, one that forces the competing considerations of your situation into the open where you can actually see them.

The goal isn't to make decisions for you. It's to make sure that when you decide, you've genuinely reckoned with the risk, the opportunity, and the strategy — not just the first thing that came to mind.

---

## Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.

---

## License

MIT

---

*Built by a UofT student who got tired of asking ChatGPT for advice and getting the same answer every time.*
