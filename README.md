# 📱 ScreenTime AI

> **AI-powered screen time analyzer** — Enter your daily app usage, and an AI agent gives you brutally honest, human-like feedback on your habits. Built with **DSPy**, **FastAPI**, **Streamlit**, and **Groq**.

---

## ✨ Features

- 🤖 **AI Analysis** — Uses DSPy + Groq LLM to analyze your screen time like a strict but caring friend
- 📊 **Interactive Charts** — Donut chart, bar chart, and radar chart visualize your usage breakdown
- 📝 **Actionable Insights** — AI returns a clear Issue → Action table with no fluff
- ⚠️ **Addiction Detection** — Flags unhealthy behavior (>10h total, >60% social media, gaming >2h, etc.)
- 🚀 **FastAPI Backend** — RESTful API server with Swagger docs, ready for deployment
- 💾 **SQLite Database** — Saves user profiles and analysis history across sessions
- 📜 **Past Analyses** — View your last 5 analysis results directly in the app
- 🌌 **Interactive UI** — Dark glassmorphism theme with animated particle background
- 🛡️ **Validation** — Blocks impossible data (e.g., >24 hours in a day)

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **uv** (recommended) or **pip** for package management
- A **Groq API key** (free at [console.groq.com](https://console.groq.com))

### 1. Clone the Repository

```bash
git clone https://github.com/Mohit067/ScreenTime-Analyzer.git
cd ScreenTime-Analyzer
```

### 2. Create a Virtual Environment

Using **uv** (recommended):

```bash
uv venv
```

Or using **Python**:

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (cmd)
.venv\Scripts\activate.bat

# macOS / Linux
source .venv/bin/activate
```

### 3. Install Dependencies

Using **uv**:

```bash
uv pip install streamlit dspy altair fastapi uvicorn requests
```

Or using **pip**:

```bash
pip install streamlit dspy altair fastapi uvicorn requests
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Run the App

You need **two terminals** — one for the backend API and one for the frontend.

**Terminal 1 — Start the FastAPI backend:**

```bash
python -m uvicorn backend.server:app --reload --port 8000
```

**Terminal 2 — Start the Streamlit frontend:**

```bash
streamlit run ./frontend/main.py
```

| Service | URL |
|---|---|
| 🖥️ Frontend (Streamlit) | http://localhost:8501 |
| ⚙️ Backend API | http://localhost:8000 |
| 📖 API Docs (Swagger) | http://localhost:8000/docs |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/analyze` | Run AI analysis (creates user + saves results) |
| `GET` | `/users` | List all registered user names |
| `POST` | `/users?name=X` | Get or create a user by name |
| `GET` | `/history/{user_name}` | Get past analyses for a user |

### Example — Analyze Usage

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "Mohit",
    "daily_usage_hours": 6.5,
    "apps": [
      {"name": "instagram", "hours": 2.0, "type": "social media"},
      {"name": "wikipedia", "hours": 1.5, "type": "education"},
      {"name": "bgmi", "hours": 1.5, "type": "games"},
      {"name": "youtube", "hours": 1.5, "type": "entertainment"}
    ]
  }'
```

---

## 🧪 How to Use

1. **Enter your name** in the User Information field
2. **Fill in your apps** — type the app name, hours used, and select a category
3. **Add or delete rows** using the `+` button or by selecting a row and pressing `Delete`
4. **Click "✨ Analyze My Screen Time"**
5. **View your results:**
   - 📝 **Summary** — A short, honest human-like assessment
   - 🛡️ **Addiction Status** — Healthy or Unhealthy
   - 📊 **Charts** — Donut (category share), Bar (per-app hours), Radar (category overview)
   - 🤖 **AI Recommendations** — Issue → Action table with specific advice
6. **Your analysis is saved** — scroll down to see your past analyses

---

## 🧠 How the AI Agent Works

The backend uses **DSPy** with **Groq's LLM** to run a `ChainOfThought` analysis:

| Output | Description |
|---|---|
| `summary` | 2–3 line honest, human-like feedback |
| `insights` | Markdown table with Issue \| Action columns |
| `isAddicted` | `True` or `False` based on medical-style rules |

### Addiction Rules

| Condition | Result |
|---|---|
| Total screen time > 10 hours | ⚠️ Unhealthy |
| Entertainment + social media > 60% of total | ⚠️ Unhealthy |
| Any single social media app > 3 hours | ⚠️ Unhealthy |
| Gaming > 2 hours | ⚠️ Unhealthy |
| Balanced usage ≤ 10h with productivity apps | ✅ Healthy |

---

## 🗄️ Database

The app uses **SQLite** (zero setup required). A `screentime.db` file is auto-created on first run.

| Table | Columns | Purpose |
|---|---|---|
| `users` | `id`, `name`, `created_at` | Stores unique users by name |
| `analyses` | `id`, `user_id`, `daily_hours`, `apps_json`, `summary`, `insights`, `is_addicted`, `analyzed_at` | Stores every analysis run |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **AI Agent** | [DSPy](https://github.com/stanfordnlp/dspy) with `ChainOfThought` |
| **LLM Provider** | [Groq](https://groq.com) (free tier available) |
| **Backend API** | [FastAPI](https://fastapi.tiangolo.com) + [Uvicorn](https://www.uvicorn.org) |
| **Frontend** | [Streamlit](https://streamlit.io) |
| **Charts** | [Altair](https://altair-viz.github.io) (bundled with Streamlit) |
| **Database** | SQLite (built-in Python) |
| **Styling** | Custom CSS — glassmorphism, Inter font, particle canvas |

---

## 👤 Author

**MOHIT** — Built with ❤️ using DSPy, FastAPI & Streamlit

---

> 💡 **Tip:** If you find this useful, give it a ⭐ on GitHub!
