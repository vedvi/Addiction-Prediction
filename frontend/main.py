import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Ensure backend can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.main import analyze_user
from backend.database import get_or_create_user, save_analysis, get_user_history, get_all_users

# Streamlit Page Config
st.set_page_config(page_title="ScreenTime AI",
                   page_icon="📱", layout="centered")

# ── Premium Custom CSS + Animated Particle Background ─────────────────────────
st.markdown("""
<style>
/* ── Google Font ─────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Root variables ──────────────────────────────────────────────────────── */
:root {
    --accent: #6C63FF;
    --accent-glow: rgba(108, 99, 255, .35);
    --card-bg: rgba(30, 32, 48, .65);
    --card-border: rgba(108, 99, 255, .18);
    --text-primary: #E8E6F0;
    --text-secondary: #9B97B0;
    --success: #34D399;
    --danger: #F87171;
    --warning: #FBBF24;
    --bg-dark: #0E0F1A;
}

/* ── Global ──────────────────────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"], .main {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary) !important;
}

[data-testid="stAppViewContainer"] {
    background: #0E0F1A !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

/* hide default streamlit footer */
footer { visibility: hidden; }

/* ── Particle canvas (positioned behind everything) ─────────────────────── */
#particle-canvas {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    z-index: 0;
    pointer-events: none;
}

/* Ensure streamlit content sits above the canvas */
[data-testid="stAppViewContainer"] > .main {
    position: relative;
    z-index: 1;
}

/* ── Hero header ─────────────────────────────────────────────────────────── */
.hero-header {
    text-align: center;
    padding: 2.5rem 1rem 1rem;
    animation: fadeSlideIn .8s ease-out;
}
.hero-header .emoji {
    font-size: 3.5rem;
    display: inline-block;
    animation: float 3s ease-in-out infinite;
    filter: drop-shadow(0 0 18px var(--accent-glow));
}
.hero-header h1 {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6C63FF, #A78BFA, #F472B6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: .4rem 0 .2rem;
}
.hero-header p {
    color: var(--text-secondary);
    font-size: 1.05rem;
    max-width: 560px;
    margin: 0 auto;
    line-height: 1.6;
}

/* ── Glass card ──────────────────────────────────────────────────────────── */
.glass-card {
    background: var(--card-bg);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--card-border);
    border-radius: 18px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.4rem;
    box-shadow: 0 8px 32px rgba(0,0,0,.25);
    transition: transform .25s ease, box-shadow .25s ease;
}
.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(108,99,255,.18);
}
.glass-card h3 {
    font-weight: 700;
    font-size: 1.15rem;
    color: var(--text-primary);
    margin-bottom: .6rem;
    display: flex;
    align-items: center;
    gap: .5rem;
}

/* ── Divider ─────────────────────────────────────────────────────────────── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--card-border), transparent);
    margin: 1.5rem 0;
}

/* ── Metric card (total hours) ───────────────────────────────────────────── */
.metric-card {
    background: linear-gradient(135deg, rgba(108,99,255,.15), rgba(167,139,250,.08));
    border: 1px solid var(--card-border);
    border-radius: 16px;
    padding: 1.4rem 1.8rem;
    text-align: center;
    margin: 1rem 0 1.5rem;
    box-shadow: 0 0 24px rgba(108,99,255,.12);
    animation: pulse-glow 3s ease-in-out infinite;
}
.metric-card .metric-label {
    font-size: .85rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600;
}
.metric-card .metric-value {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6C63FF, #A78BFA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: .3rem 0;
}

/* ── Result card variants ────────────────────────────────────────────────── */
.result-card {
    border-radius: 16px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1rem;
    border: 1px solid var(--card-border);
    backdrop-filter: blur(12px);
}
.result-card.summary {
    background: linear-gradient(135deg, rgba(108,99,255,.12), rgba(59,130,246,.06));
}
.result-card.addicted {
    background: linear-gradient(135deg, rgba(248,113,113,.12), rgba(239,68,68,.06));
    border-color: rgba(248,113,113,.25);
}
.result-card.healthy {
    background: linear-gradient(135deg, rgba(52,211,153,.12), rgba(16,185,129,.06));
    border-color: rgba(52,211,153,.25);
}
.result-card.insights {
    background: linear-gradient(135deg, rgba(251,191,36,.08), rgba(245,158,11,.04));
    border-color: rgba(251,191,36,.2);
}
.result-card h4 {
    font-weight: 700;
    margin-bottom: .6rem;
    font-size: 1.1rem;
}
.result-card p, .result-card li {
    color: var(--text-secondary);
    line-height: 1.7;
}

/* ── Badge ───────────────────────────────────────────────────────────────── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: .4rem;
    padding: .45rem 1rem;
    border-radius: 50px;
    font-weight: 600;
    font-size: .95rem;
    margin-top: .4rem;
}
.badge.danger { background: rgba(248,113,113,.18); color: #F87171; }
.badge.success { background: rgba(52,211,153,.18); color: #34D399; }

/* ── Streamlit overrides ─────────────────────────────────────────────────── */
/* buttons */
.stButton > button {
    background: linear-gradient(135deg, #6C63FF, #8B5CF6) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: .85rem 2rem !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    letter-spacing: .3px !important;
    transition: all .3s ease !important;
    box-shadow: 0 4px 20px rgba(108,99,255,.35) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(108,99,255,.5) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* inputs */
.stTextInput input {
    background: rgba(30,32,48,.8) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    padding: .7rem 1rem !important;
    transition: border-color .3s ease !important;
}
.stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
}

/* data editor */
[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden;
    border: 1px solid var(--card-border) !important;
}

/* selectbox */
.stSelectbox [data-baseweb="select"] {
    border-radius: 12px !important;
}

/* spinner */
.stSpinner > div {
    border-top-color: var(--accent) !important;
}

/* ── Plotly chart overrides ──────────────────────────────────────────────── */
[data-testid="stPlotlyChart"] {
    border-radius: 16px;
    overflow: hidden;
}

/* ── AI Insights styled table ───────────────────────────────────────────── */
.insights-container {
    background: var(--card-bg);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(251,191,36,.2);
    border-radius: 18px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.4rem;
    box-shadow: 0 8px 32px rgba(0,0,0,.25);
    animation: slideUp .6s ease-out both;
    animation-delay: .4s;
}
.insights-container h4 {
    font-weight: 700;
    font-size: 1.15rem;
    color: #E8E6F0;
    margin-bottom: 1rem;
}

/* Markdown table styling — targets both .insights-table and native Streamlit tables */
.insights-table table,
[data-testid="stMarkdownContainer"] table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(108,99,255,.15);
}
.insights-table thead tr,
[data-testid="stMarkdownContainer"] thead tr {
    background: linear-gradient(135deg, rgba(108,99,255,.22), rgba(167,139,250,.12));
}
.insights-table thead th,
[data-testid="stMarkdownContainer"] thead th {
    padding: .85rem 1.2rem;
    font-weight: 700;
    font-size: .9rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #A78BFA !important;
    border-bottom: 2px solid rgba(108,99,255,.25);
    text-align: left;
}
.insights-table tbody tr,
[data-testid="stMarkdownContainer"] tbody tr {
    transition: background .2s ease;
}
.insights-table tbody tr:nth-child(odd),
[data-testid="stMarkdownContainer"] tbody tr:nth-child(odd) {
    background: rgba(30,32,48,.5);
}
.insights-table tbody tr:nth-child(even),
[data-testid="stMarkdownContainer"] tbody tr:nth-child(even) {
    background: rgba(22,24,38,.5);
}
.insights-table tbody tr:hover,
[data-testid="stMarkdownContainer"] tbody tr:hover {
    background: rgba(108,99,255,.1);
}
.insights-table tbody td,
[data-testid="stMarkdownContainer"] tbody td {
    padding: .75rem 1.2rem;
    color: #9B97B0;
    border-bottom: 1px solid rgba(108,99,255,.08);
    font-size: .92rem;
    line-height: 1.5;
}
.insights-table tbody td:first-child,
[data-testid="stMarkdownContainer"] tbody td:first-child {
    color: #E8E6F0;
    font-weight: 600;
}
.insights-table tbody tr:last-child td,
[data-testid="stMarkdownContainer"] tbody tr:last-child td {
    border-bottom: none;
}

/* ── Animations ──────────────────────────────────────────────────────────── */
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(-20px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 24px rgba(108,99,255,.12); }
    50% { box-shadow: 0 0 36px rgba(108,99,255,.22); }
}
@keyframes slideUp {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* section animation helper */
.animate-in {
    animation: slideUp .6s ease-out both;
}
.animate-in.d1 { animation-delay: .1s; }
.animate-in.d2 { animation-delay: .2s; }
.animate-in.d3 { animation-delay: .3s; }
.animate-in.d4 { animation-delay: .4s; }

/* ── Scrollbar ───────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(108,99,255,.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(108,99,255,.5); }
</style>
""", unsafe_allow_html=True)


# ── Interactive Particle Background (HTML5 Canvas + JS) ───────────────────────
st.markdown("""
<canvas id="particle-canvas"></canvas>
<script>
(function() {
    const canvas = document.getElementById('particle-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let W, H;
    function resize() {
        W = canvas.width  = window.innerWidth;
        H = canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    // Mouse tracking
    let mouse = { x: W / 2, y: H / 2 };
    document.addEventListener('mousemove', e => { mouse.x = e.clientX; mouse.y = e.clientY; });

    // Particles
    const PARTICLE_COUNT = 80;
    const CONNECTION_DIST = 150;
    const particles = [];

    class Particle {
        constructor() {
            this.x = Math.random() * W;
            this.y = Math.random() * H;
            this.vx = (Math.random() - 0.5) * 0.6;
            this.vy = (Math.random() - 0.5) * 0.6;
            this.r = Math.random() * 2 + 1;
        }
        update() {
            // gentle pull toward mouse
            let dx = mouse.x - this.x;
            let dy = mouse.y - this.y;
            let dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 250) {
                this.vx += dx * 0.00004;
                this.vy += dy * 0.00004;
            }
            this.x += this.vx;
            this.y += this.vy;
            // wrap edges
            if (this.x < 0) this.x = W;
            if (this.x > W) this.x = 0;
            if (this.y < 0) this.y = H;
            if (this.y > H) this.y = 0;
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(108, 99, 255, 0.5)';
            ctx.fill();
        }
    }

    for (let i = 0; i < PARTICLE_COUNT; i++) particles.push(new Particle());

    function drawConnections() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                let dx = particles[i].x - particles[j].x;
                let dy = particles[i].y - particles[j].y;
                let dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < CONNECTION_DIST) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(108, 99, 255, ${0.12 * (1 - dist / CONNECTION_DIST)})`;
                    ctx.lineWidth = 0.6;
                    ctx.stroke();
                }
            }
        }
    }

    function animate() {
        ctx.clearRect(0, 0, W, H);
        particles.forEach(p => { p.update(); p.draw(); });
        drawConnections();
        requestAnimationFrame(animate);
    }
    animate();
})();
</script>
""", unsafe_allow_html=True)


# ── Plotly theme helper ───────────────────────────────────────────────────────

CHART_COLORS = [
    '#6C63FF', '#A78BFA', '#F472B6', '#34D399',
    '#FBBF24', '#F87171', '#38BDF8', '#818CF8',
]


def _plotly_dark_layout(fig, title=""):
    """Apply a consistent dark transparent layout to any Plotly figure."""
    fig.update_layout(
        title=dict(text=title, font=dict(
            color='#E8E6F0', size=16, family='Inter')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#9B97B0', family='Inter'),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            bgcolor='rgba(30,32,48,.5)',
            bordercolor='rgba(108,99,255,.18)',
            borderwidth=1,
            font=dict(color='#E8E6F0'),
        ),
    )
    return fig


# ── Hero Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <span class="emoji">📱</span>
    <h1>ScreenTime AI</h1>
    <p>Enter your daily screen time data and let our AI agent analyze your behavior, providing tailored feedback and actionable insights.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── User Information ──────────────────────────────────────────────────────────
st.markdown("""
<div class="glass-card animate-in d1">
    <h3>👤 User Information</h3>
</div>
""", unsafe_allow_html=True)

user_name = st.text_input(
    "Your Name", value="", label_visibility="collapsed", placeholder="Enter your name …")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── App Usage Table (outside form so edits reflect instantly) ─────────────────
st.markdown("""
<div class="glass-card animate-in d2">
    <h3>📊 App Usage Details</h3>
    <p style="color:var(--text-secondary); font-size:.9rem; margin-top:-.2rem;">
        Add, edit, or remove rows — the total updates automatically.
    </p>
</div>
""", unsafe_allow_html=True)

# Empty placeholder rows — fill in your apps, add/delete rows freely
_placeholder_apps = pd.DataFrame(
    [
        {"name": "", "hours": 0.0, "type": "social media"},
        {"name": "", "hours": 0.0, "type": "social media"},
        {"name": "", "hours": 0.0, "type": "social media"},
    ]
)

app_types = ["social media", "education", "games",
             "productivity", "entertainment", "other"]

edited_df = st.data_editor(
    _placeholder_apps,
    column_config={
        "name":  st.column_config.TextColumn("App Name", required=True),
        "hours": st.column_config.NumberColumn("Usage (Hours)", min_value=0.0, max_value=24.0, required=True),
        "type":  st.column_config.SelectboxColumn("App Category", options=app_types, required=True),
    },
    num_rows="dynamic",
    width="stretch",
    key="app_editor",
)

# ── Auto-calculated Total ─────────────────────────────────────────────────────
# Filter out placeholder / unfilled rows (empty name or missing hours)
clean_df = edited_df.dropna(subset=["hours"])
clean_df = clean_df[clean_df["name"].str.strip().astype(bool)]
auto_total = float(clean_df["hours"].sum()) if not clean_df.empty else 0.0

st.markdown(f"""
<div class="metric-card animate-in d3">
    <div class="metric-label">⏱️ Total Daily Usage</div>
    <div class="metric-value">{auto_total:.1f} hrs</div>
    <div style="color:var(--text-secondary); font-size:.8rem;">Auto-calculated from your app table</div>
</div>
""", unsafe_allow_html=True)

# ── Submit ────────────────────────────────────────────────────────────────────
submitted = st.button("✨  Analyze My Screen Time", use_container_width=True, type="primary")  # noqa

if submitted:
    if not user_name.strip():
        st.warning("Please enter your name before analyzing.")
    elif clean_df.empty:
        st.warning("Please add at least one app before analyzing.")
    elif auto_total > 24:
        st.error(
            f"⛔ A day only has 24 hours! You entered {auto_total:.1f} hours of total usage "
            f"— that is not possible. Please correct your app hours and try again."
        )
    else:
        with st.spinner("Agent is analyzing your behavior..."):
            try:
                apps_list = clean_df.to_dict("records")
                db_user_id = get_or_create_user(user_name)

                userusage = {
                    "user_id": str(db_user_id),
                    "daily_usage_hours": auto_total,   # ← always matches the table
                    "apps": apps_list,
                }

                analysis = analyze_user(userusage)

                # ── Results Header ────────────────────────────────────────
                st.markdown("""
                <div class="divider"></div>
                <div class="hero-header" style="padding-top:1rem;">
                    <h1 style="font-size:1.8rem;">📊 Analysis Results</h1>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"""
                    <div class="result-card summary animate-in d1">
                        <h4>📝 Summary</h4>
                        <p>{analysis.summary}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    is_addicted = str(analysis.isAddicted).strip().lower()
                    if is_addicted == "true":
                        st.markdown("""
                        <div class="result-card addicted animate-in d2">
                            <h4>⚠️ Addiction Status</h4>
                            <span class="badge danger">🚨 Highly Dependent</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="result-card healthy animate-in d2">
                            <h4>🛡️ Addiction Status</h4>
                            <span class="badge success">✅ Behavior in Control</span>
                        </div>
                        """, unsafe_allow_html=True)

                # ── Actionable Insights + Charts ──────────────────────────
                st.markdown('<div class="divider"></div>',
                            unsafe_allow_html=True)
                st.markdown("""
                <div class="hero-header" style="padding-top:.5rem; padding-bottom:.2rem;">
                    <h1 style="font-size:1.6rem;">💡 Actionable Insights</h1>
                </div>
                """, unsafe_allow_html=True)

                # --- Charts row ---
                chart_col1, chart_col2 = st.columns(2)

                with chart_col1:
                    # Donut chart — usage share by category
                    cat_df = clean_df.groupby("type", as_index=False)[
                        "hours"].sum()
                    fig_donut = go.Figure(
                        go.Pie(
                            labels=cat_df["type"],
                            values=cat_df["hours"],
                            hole=0.55,
                            marker=dict(colors=CHART_COLORS[:len(cat_df)]),
                            textinfo="label+percent",
                            textfont=dict(color="#E8E6F0", size=12),
                            hovertemplate="<b>%{label}</b><br>%{value:.1f} hrs<br>%{percent}<extra></extra>",
                        )
                    )
                    _plotly_dark_layout(fig_donut, "Usage by Category")
                    fig_donut.update_layout(showlegend=False, height=340)
                    st.plotly_chart(fig_donut, width="stretch")

                with chart_col2:
                    # Horizontal bar — per-app hours
                    sorted_df = clean_df.sort_values("hours", ascending=True)
                    fig_bar = go.Figure(
                        go.Bar(
                            y=sorted_df["name"],
                            x=sorted_df["hours"],
                            orientation="h",
                            marker=dict(
                                color=sorted_df["hours"],
                                colorscale=[[0, '#6C63FF'], [
                                    0.5, '#A78BFA'], [1, '#F472B6']],
                                cornerradius=6,
                            ),
                            text=sorted_df["hours"].apply(
                                lambda v: f"{v:.1f}h"),
                            textposition="outside",
                            textfont=dict(color="#E8E6F0"),
                            hovertemplate="<b>%{y}</b><br>%{x:.1f} hrs<extra></extra>",
                        )
                    )
                    _plotly_dark_layout(fig_bar, "Hours per App")
                    fig_bar.update_yaxes(
                        tickfont=dict(color="#E8E6F0"),
                        gridcolor="rgba(108,99,255,.06)",
                    )
                    fig_bar.update_xaxes(
                        tickfont=dict(color="#9B97B0"),
                        gridcolor="rgba(108,99,255,.06)",
                    )
                    fig_bar.update_layout(height=340)
                    st.plotly_chart(fig_bar, width="stretch")

                # --- Category breakdown radar chart ---
                if len(cat_df) >= 3:
                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(
                        r=cat_df["hours"].tolist() + [cat_df["hours"].iloc[0]],
                        theta=cat_df["type"].tolist(
                        ) + [cat_df["type"].iloc[0]],
                        fill='toself',
                        fillcolor='rgba(108,99,255,.15)',
                        line=dict(color='#6C63FF', width=2),
                        marker=dict(color='#A78BFA', size=7),
                        hovertemplate="<b>%{theta}</b><br>%{r:.1f} hrs<extra></extra>",
                    ))
                    _plotly_dark_layout(fig_radar, "Category Radar")
                    fig_radar.update_layout(
                        polar=dict(
                            bgcolor='rgba(0,0,0,0)',
                            radialaxis=dict(
                                gridcolor='rgba(108,99,255,.12)',
                                color='#9B97B0',
                            ),
                            angularaxis=dict(
                                gridcolor='rgba(108,99,255,.12)',
                                color='#E8E6F0',
                            ),
                        ),
                        height=380,
                    )
                    st.plotly_chart(fig_radar, width="stretch")

                # --- AI text insights (rendered as native markdown for table support) ---
                st.markdown("""
                <div class="insights-container">
                    <h4>🤖 AI Recommendations</h4>
                </div>
                """, unsafe_allow_html=True)

                # Use native st.markdown so pipe-table syntax renders as a real table
                st.markdown(analysis.insights)

                # ── Save to database ──────────────────────────────────
                save_analysis(
                    user_id=db_user_id,
                    daily_hours=auto_total,
                    apps=apps_list,
                    summary=str(analysis.summary),
                    insights=str(analysis.insights),
                    is_addicted=str(analysis.isAddicted),
                )
                st.toast(
                    f"✅ Analysis saved for {user_name.strip()}!", icon="💾")

            except Exception as e:
                st.error(
                    f"An error occurred while generating analysis: {str(e)}")

# ── Past Analysis History ─────────────────────────────────────────────────────
if user_name.strip():
    _uid = get_or_create_user(user_name)
    history = get_user_history(_uid, limit=5)
    if history:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-card animate-in d2">
            <h3>📜 Your Past Analyses</h3>
        </div>
        """, unsafe_allow_html=True)

        for idx, rec in enumerate(history):
            addicted_label = (
                '<span class="badge danger">🚨 Addicted</span>'
                if str(rec["is_addicted"]).strip().lower() == "true"
                else '<span class="badge success">✅ Healthy</span>'
            )
            st.markdown(f"""
            <div class="result-card summary" style="margin-bottom:.8rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:.5rem;">
                    <span style="color:var(--text-secondary); font-size:.82rem;">🕐 {rec["analyzed_at"]}</span>
                    <span style="font-weight:700; color:#A78BFA;">{rec["daily_hours"]:.1f} hrs</span>
                    {addicted_label}
                </div>
                <p style="color:var(--text-secondary); margin-top:.5rem; font-size:.9rem;">{rec["summary"]}</p>
            </div>
            """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="divider"></div>
<div style="text-align:center; padding:1rem 0 2rem;">
    <p style="color:var(--text-secondary); font-size:.8rem;">
        Built with VED ❤️ using <b>DSPy</b> &amp; <b>Streamlit</b> · ScreenTime AI © 2026
    </p>
</div>
""", unsafe_allow_html=True)
