# 📱 ScreenTime AI

> **AI-powered screen time analyzer** — Enter your daily app usage, and an AI agent gives you brutally honest, human-like feedback on your habits. Built with **DSPy**, **Streamlit**, and **Groq**.

---

## ✨ Features

- 🤖 **AI Analysis** — Uses DSPy + Groq LLM to analyze your screen time like a strict but caring friend
- 📊 **Interactive Charts** — Donut chart, bar chart, and radar chart visualize your usage breakdown
- 📝 **Actionable Insights** — AI returns a clear Issue → Action table with no fluff
- ⚠️ **Addiction Detection** — Flags unhealthy behavior (>10h total, >60% social media, gaming >2h, etc.)
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
git clone https://github.com/<your-username>/ScreenTimeAI.git
cd ScreenTimeAI
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
uv pip install streamlit dspy plotly
```

Or using **pip**:

```bash
pip install streamlit dspy plotly
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Run the App

```bash
streamlit run ./frontend/main.py
```

The app will open at **http://localhost:8501** in your browser.

---

## 🧪 How to Use

1. **Enter your name** in the User Information field
2. **Fill in your apps** — type the app name, hours used, and select a category (social media, games, education, etc.)
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

The app uses **SQLite** (zero setup required). A `screentime.db` file is auto-created in the project root on first run.

### Tables

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
| **Frontend** | [Streamlit](https://streamlit.io) |
| **Charts** | [Plotly](https://plotly.com/python/) |
| **Database** | SQLite (built-in Python) |
| **Styling** | Custom CSS — glassmorphism, Inter font, particle canvas |

---

## 👤 Author

**MOHIT** — Built with ❤️ using DSPy & Streamlit

---

> 💡 **Tip:** If you find this useful, give it a ⭐ on GitHub!
