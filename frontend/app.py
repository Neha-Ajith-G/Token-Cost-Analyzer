"""
Token Cost Analyzer — Streamlit Frontend
Connects to a FastAPI backend running at BASE_URL.
"""

import os
import streamlit as st
import requests
import pandas as pd

# ── Configuration ──────────────────────────────────────────────────────────────
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# ── Page setup ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Token Cost Analyzer",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global styles ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ---------- font & base ---------- */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] {
    background: #0d0d0d;
    border-right: 1px solid #1f1f1f;
}
[data-testid="stSidebar"] * {
    color: #e0e0e0 !important;
}
[data-testid="stSidebar"] .stRadio label {
    font-size: 0.9rem;
    letter-spacing: 0.04em;
    padding: 6px 0;
}

/* ---------- main canvas ---------- */
[data-testid="stAppViewContainer"] {
    background: #f7f6f2;
}

/* ---------- page title ---------- */
.tca-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2rem;
    font-weight: 600;
    color: #0d0d0d;
    letter-spacing: -0.03em;
    margin-bottom: 0;
}
.tca-sub {
    font-size: 0.85rem;
    color: #888;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-top: 2px;
}

/* ---------- metric cards ---------- */
.metric-card {
    background: #ffffff;
    border: 1px solid #e8e6e0;
    border-radius: 10px;
    padding: 18px 22px;
    margin-bottom: 12px;
}
.metric-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #888;
    margin-bottom: 4px;
}
.metric-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.5rem;
    font-weight: 600;
    color: #0d0d0d;
}
.metric-delta-pos {
    font-size: 0.78rem;
    color: #22a06b;
    margin-top: 2px;
}
.metric-delta-neg {
    font-size: 0.78rem;
    color: #e03737;
    margin-top: 2px;
}

/* ---------- section dividers ---------- */
.section-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #aaa;
    border-bottom: 1px solid #e0ddd6;
    padding-bottom: 6px;
    margin: 28px 0 16px;
}

/* ---------- text panels ---------- */
.text-panel {
    background: #fff;
    border: 1px solid #e8e6e0;
    border-radius: 10px;
    padding: 16px 20px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    color: #333;
    line-height: 1.65;
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 240px;
    overflow-y: auto;
}

/* ---------- tag badge ---------- */
.badge {
    display: inline-block;
    background: #0d0d0d;
    color: #f7f6f2;
    font-size: 0.7rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 4px;
    margin-bottom: 8px;
}
.badge-green {
    background: #dcfce7;
    color: #166534;
}

/* ---------- buttons ---------- */
.stButton > button {
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 500;
    letter-spacing: 0.02em;
    transition: opacity 0.15s;
}
.stButton > button:hover { opacity: 0.85; }

/* ---------- sidebar logo mark ---------- */
.logo-mark {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.1rem;
    font-weight: 600;
    color: #ffffff !important;
    letter-spacing: -0.02em;
    padding: 6px 0 20px;
    display: block;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# API HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def api_get_models() -> list[str]:
    """Return list of model names from GET /models."""
    r = requests.get(f"{BASE_URL}/models", timeout=10)
    r.raise_for_status()
    return r.json().get("models", [])


def api_analyze(text: str, model: str) -> dict:
    """POST /analyze — returns analysis without saving."""
    r = requests.post(f"{BASE_URL}/analyze", json={"text": text, "model": model}, timeout=30)
    r.raise_for_status()
    return r.json()


def api_save_analysis(text: str, model: str) -> dict:
    """POST /analyzedtexts — saves and returns the record."""
    r = requests.post(f"{BASE_URL}/analyzedtexts", json={"text": text, "model": model}, timeout=30)
    r.raise_for_status()
    return r.json()


def api_get_all(model_filter: str | None = None) -> list[dict]:
    """GET /analyzedtexts — all records, with optional model filter."""
    params = {}
    if model_filter:
        params["model"] = model_filter
    r = requests.get(f"{BASE_URL}/analyzedtexts", params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def api_get_by_id(record_id: int) -> dict:
    """GET /analyzedtexts/{id}."""
    r = requests.get(f"{BASE_URL}/analyzedtexts/{record_id}", timeout=10)
    r.raise_for_status()
    return r.json()


def api_update(record_id: int, text: str | None, model: str | None) -> dict:
    """PUT /analyzedtexts/{id}."""
    payload = {}
    if text is not None:
        payload["text"] = text
    if model is not None:
        payload["model"] = model
    r = requests.put(f"{BASE_URL}/analyzedtexts/{record_id}", json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


def api_delete(record_id: int) -> dict:
    """DELETE /analyzedtexts/{id}."""
    r = requests.delete(f"{BASE_URL}/analyzedtexts/{record_id}", timeout=10)
    r.raise_for_status()
    return r.json()


# ══════════════════════════════════════════════════════════════════════════════
# UI HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def metric_card(label: str, value: str, delta: str | None = None, delta_positive: bool = True):
    delta_class = "metric-delta-pos" if delta_positive else "metric-delta-neg"
    delta_html = f'<div class="{delta_class}">{delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def section_label(text: str):
    st.markdown(f'<div class="section-label">{text}</div>', unsafe_allow_html=True)


def fmt_cost(cost: float) -> str:
    return f"${cost:.6f}"


def pct_reduction(original: float, optimized: float) -> float:
    if original == 0:
        return 0.0
    return (original - optimized) / original * 100


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE DEFAULTS
# ══════════════════════════════════════════════════════════════════════════════

for key, default in {
    "analysis_result": None,
    "analysis_text": "",
    "analysis_model": None,
    "saved_records": [],
    "selected_record_id": None,
    "edit_mode_id": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown('<span class="logo-mark">⬡ TCA</span>', unsafe_allow_html=True)
    page = st.radio(
        "Navigate",
        ["Analyze Text", "Saved Analyses", "About"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown(
        '<span style="font-size:0.72rem;color:#555;letter-spacing:0.05em;">'
        f'API  ·  <code style="color:#888">{BASE_URL}</code></span>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ANALYZE TEXT
# ══════════════════════════════════════════════════════════════════════════════

if page == "Analyze Text":
    st.markdown('<div class="tca-title">Token Cost Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="tca-sub">Estimate & optimize prompt token usage</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Input form ────────────────────────────────────────────────────────────
    section_label("Input")

    # Load model list
    try:
        with st.spinner("Loading models…"):
            models = api_get_models()
    except Exception as e:
        st.error(f"Could not reach the API — is the backend running? ({e})")
        models = []

    col_text, col_opts = st.columns([3, 1], gap="large")

    with col_text:
        input_text = st.text_area(
            "Prompt / text to analyze",
            height=220,
            placeholder="Paste your prompt here…",
            value=st.session_state.analysis_text,
            label_visibility="collapsed",
        )

    with col_opts:
        if models:
            selected_model = st.selectbox("Model", models)
        else:
            selected_model = st.selectbox("Model", ["(no models)"], disabled=True)
            selected_model = None

        st.markdown("<br>", unsafe_allow_html=True)
        analyze_clicked = st.button("⬡ Analyze", use_container_width=True, type="primary")

    # ── Run analysis ──────────────────────────────────────────────────────────
    if analyze_clicked:
        if not input_text.strip():
            st.warning("Please enter some text before analyzing.")
        elif not selected_model:
            st.warning("No models available from the API.")
        else:
            try:
                with st.spinner("Analyzing…"):
                    result = api_analyze(input_text, selected_model)
                st.session_state.analysis_result = result
                st.session_state.analysis_text = input_text
                st.session_state.analysis_model = selected_model
                st.rerun()  # force re-render so results appear immediately
            except requests.HTTPError as e:
                st.error(f"API error {e.response.status_code}: {e.response.text}")
            except Exception as e:
                st.error(f"Request failed: {e}")

    # ── Display results ───────────────────────────────────────────────────────
    result = st.session_state.analysis_result

    if result:
        # API returns nested: {"original": {text, token_count, estimated_cost}, "optimized": {...}}
        original  = result.get("original", {})
        optimized = result.get("optimized", {})

        orig_tokens = original.get("token_count", 0)
        opt_tokens  = optimized.get("token_count", 0)
        orig_cost   = original.get("estimated_cost", 0.0)
        opt_cost    = optimized.get("estimated_cost", 0.0)
        orig_text   = original.get("text", st.session_state.analysis_text)
        opt_text    = optimized.get("text", "")

        token_pct = pct_reduction(orig_tokens, opt_tokens)
        cost_pct  = pct_reduction(orig_cost, opt_cost)

        section_label("Results")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            metric_card("Original tokens", f"{orig_tokens:,}")
        with c2:
            metric_card(
                "Optimized tokens", f"{opt_tokens:,}",
                delta=f"▼ {token_pct:.1f}% fewer tokens",
                delta_positive=True,
            )
        with c3:
            metric_card("Original cost", fmt_cost(orig_cost))
        with c4:
            metric_card(
                "Optimized cost", fmt_cost(opt_cost),
                delta=f"▼ {cost_pct:.1f}% cost saved",
                delta_positive=True,
            )

        section_label("Text comparison")

        tcol1, tcol2 = st.columns(2, gap="large")
        with tcol1:
            st.markdown('<span class="badge">Original</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="text-panel">{orig_text}</div>', unsafe_allow_html=True)
        with tcol2:
            st.markdown('<span class="badge badge-green">Optimized</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="text-panel">{opt_text}</div>', unsafe_allow_html=True)

        # ── Save button ───────────────────────────────────────────────────────
        section_label("Save")
        if st.button("Save this analysis →", use_container_width=False):
            try:
                with st.spinner("Saving…"):
                    saved = api_save_analysis(
                        st.session_state.analysis_text,
                        st.session_state.analysis_model,
                    )
                st.success(f"Saved as record #{saved.get('id')}.")
            except requests.HTTPError as e:
                st.error(f"Save failed ({e.response.status_code}): {e.response.text}")
            except Exception as e:
                st.error(f"Save failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SAVED ANALYSES
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Saved Analyses":
    st.markdown('<div class="tca-title">Saved Analyses</div>', unsafe_allow_html=True)
    st.markdown('<div class="tca-sub">Browse, inspect, edit, or delete saved records</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Filters + refresh ─────────────────────────────────────────────────────
    section_label("Filters")
    f_col1, f_col2 = st.columns([2, 1], gap="medium")
    with f_col1:
        filter_model = st.text_input("Filter by model name", placeholder="e.g. gpt-4o")
    with f_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("↺ Refresh", use_container_width=True):
            st.session_state.selected_record_id = None
            st.session_state.edit_mode_id = None

    # ── Fetch records ─────────────────────────────────────────────────────────
    try:
        with st.spinner("Loading records…"):
            records = api_get_all(model_filter=filter_model.strip() or None)
    except Exception as e:
        st.error(f"Could not load records: {e}")
        records = []

    if not records:
        st.info("No saved analyses yet. Analyze some text and save it!")
    else:
        # Build display dataframe
        df = pd.DataFrame([
            {
                "ID": r["id"],
                "Model": r["model"],
                "Orig tokens": r["original_token_count"],
                "Opt tokens":  r["optimized_token_count"],
                "Orig cost":   fmt_cost(r["original_cost"]),
                "Opt cost":    fmt_cost(r["optimized_cost"]),
                "Token saved": f"{pct_reduction(r['original_token_count'], r['optimized_token_count']):.1f}%",
            }
            for r in records
        ])

        section_label("Records")
        st.dataframe(df, use_container_width=True, hide_index=True)

        # ── Select record ─────────────────────────────────────────────────────
        section_label("Inspect / Edit / Delete")
        record_ids = [r["id"] for r in records]
        selected_id = st.selectbox(
            "Select a record ID",
            options=record_ids,
            index=record_ids.index(st.session_state.selected_record_id)
                  if st.session_state.selected_record_id in record_ids else 0,
        )
        st.session_state.selected_record_id = selected_id

        # Fetch full detail for selected record
        try:
            rec = api_get_by_id(selected_id)
        except Exception as e:
            st.error(f"Could not load record {selected_id}: {e}")
            rec = None

        if rec:
            # ── Detail view ───────────────────────────────────────────────────
            with st.expander(f"Record #{rec['id']} — detail", expanded=True):
                d1, d2, d3, d4 = st.columns(4)
                with d1:
                    metric_card("Model", rec["model"])
                with d2:
                    metric_card("Original tokens", f"{rec['original_token_count']:,}")
                with d3:
                    metric_card("Optimized tokens", f"{rec['optimized_token_count']:,}")
                with d4:
                    metric_card(
                        "Cost saved",
                        f"{pct_reduction(rec['original_cost'], rec['optimized_cost']):.1f}%",
                    )

                tcol1, tcol2 = st.columns(2, gap="large")
                with tcol1:
                    st.markdown('<span class="badge">Original text</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="text-panel">{rec["text"]}</div>', unsafe_allow_html=True)
                with tcol2:
                    st.markdown('<span class="badge badge-green">Optimized text</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="text-panel">{rec["optimized_text"]}</div>', unsafe_allow_html=True)

            # ── Action buttons ────────────────────────────────────────────────
            act_col1, act_col2, _ = st.columns([1, 1, 4], gap="small")
            with act_col1:
                edit_clicked = st.button("✏ Edit record", use_container_width=True)
            with act_col2:
                delete_clicked = st.button("✕ Delete record", use_container_width=True, type="secondary")

            if edit_clicked:
                st.session_state.edit_mode_id = selected_id

            # ── Edit form ─────────────────────────────────────────────────────
            if st.session_state.edit_mode_id == selected_id:
                section_label("Edit record")
                with st.form("edit_form"):
                    # Load available models for the dropdown
                    try:
                        avail_models = api_get_models()
                    except Exception:
                        avail_models = [rec["model"]]

                    new_text = st.text_area("Text", value=rec["text"], height=160)
                    current_model_idx = avail_models.index(rec["model"]) if rec["model"] in avail_models else 0
                    new_model = st.selectbox("Model", avail_models, index=current_model_idx)
                    submitted = st.form_submit_button("Save changes", type="primary")

                    if submitted:
                        try:
                            with st.spinner("Updating…"):
                                api_update(selected_id, new_text, new_model)
                            st.success("Record updated.")
                            st.session_state.edit_mode_id = None
                            st.rerun()
                        except requests.HTTPError as e:
                            st.error(f"Update failed ({e.response.status_code}): {e.response.text}")
                        except Exception as e:
                            st.error(f"Update failed: {e}")

            # ── Delete confirmation ───────────────────────────────────────────
            if delete_clicked:
                st.session_state[f"confirm_delete_{selected_id}"] = True

            if st.session_state.get(f"confirm_delete_{selected_id}"):
                st.warning(
                    f"Delete record #{selected_id}? This cannot be undone.",
                    icon="⚠️",
                )
                yes_col, no_col, _ = st.columns([1, 1, 5])
                with yes_col:
                    if st.button("Yes, delete", key="confirm_yes", type="primary"):
                        try:
                            with st.spinner("Deleting…"):
                                api_delete(selected_id)
                            st.success(f"Record #{selected_id} deleted.")
                            st.session_state[f"confirm_delete_{selected_id}"] = False
                            st.session_state.selected_record_id = None
                            st.rerun()
                        except requests.HTTPError as e:
                            st.error(f"Delete failed: {e.response.text}")
                        except Exception as e:
                            st.error(f"Delete failed: {e}")
                with no_col:
                    if st.button("Cancel", key="confirm_no"):
                        st.session_state[f"confirm_delete_{selected_id}"] = False
                        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ABOUT
# ══════════════════════════════════════════════════════════════════════════════

elif page == "About":
    st.markdown('<div class="tca-title">About</div>', unsafe_allow_html=True)
    st.markdown('<div class="tca-sub">Token Cost Analyzer — how it works</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
**Token Cost Analyzer** helps you understand the real cost of your prompts before they hit production.

Paste any prompt text, pick a model, and TCA returns:

- **Original token count** — what you'd pay with your raw prompt.
- **Optimized token count** — after lossless compression removes redundant whitespace and tokens.
- **Cost estimates** — both figures in USD using up-to-date per-token pricing.

Use **Saved Analyses** to build a history of prompts you've measured, compare token efficiency across models, and iterate toward leaner, cheaper prompts.
    """)

    section_label("API endpoints")
    st.markdown(f"""
| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/models` | List available models |
| `POST` | `/analyze` | Analyze without saving |
| `POST` | `/analyzedtexts` | Analyze and save |
| `GET` | `/analyzedtexts` | List all saved records |
| `GET` | `/analyzedtexts/{{id}}` | Fetch one record |
| `PUT` | `/analyzedtexts/{{id}}` | Update a record |
| `DELETE` | `/analyzedtexts/{{id}}` | Delete a record |

Backend base URL: `{BASE_URL}`
    """)
