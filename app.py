import ast
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

from analyzer import CodeAnalyzer

st.set_page_config(
    page_title="Nodes & Logic",
    page_icon="N&L",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --bg: #0b1020;
        --panel: #121a2e;
        --panel-soft: #18233f;
        --text: #e7ecf6;
        --muted: #9fb0d0;
        --line: #2a3759;
        --accent: #3aa3ff;
        --success: #31c48d;
    }

    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}

    .stApp {
        background:
            radial-gradient(900px 420px at 85% -5%, rgba(58,163,255,0.18), transparent 55%),
            radial-gradient(800px 380px at -5% 10%, rgba(49,196,141,0.10), transparent 55%),
            var(--bg);
        color: var(--text);
    }

    .app-shell {
        border: 1px solid var(--line);
        background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 14px;
    }

    .app-title {
        font-size: 1.35rem;
        font-weight: 700;
        letter-spacing: 0.2px;
        margin: 0;
        color: var(--text);
    }

    .app-sub {
        margin-top: 4px;
        color: var(--muted);
        font-size: 0.93rem;
    }

    .section-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--text);
        margin-bottom: 10px;
    }

    .status-row {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 4px 0 8px 0;
    }

    .status-title {
        font-size: 1rem;
        font-weight: 700;
        color: var(--text);
    }

    .status-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
    }

    .status-dot.pulse {
        background: #5dade2;
        box-shadow: 0 0 0 0 rgba(93, 173, 226, 0.7);
        animation: pulseGlow 1.3s infinite;
    }

    .status-dot.done {
        background: #2ecc71;
        box-shadow: 0 0 8px rgba(46, 204, 113, 0.55);
    }

    .status-dot.idle {
        background: #6b7280;
    }

    @keyframes pulseGlow {
        0% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(93, 173, 226, 0.7);
        }
        70% {
            transform: scale(1.0);
            box-shadow: 0 0 0 12px rgba(93, 173, 226, 0);
        }
        100% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(93, 173, 226, 0);
        }
    }

    .stTextArea textarea {
        background: #0e162c !important;
        color: #eaf1ff !important;
        border: 1px solid var(--line) !important;
        border-radius: 10px !important;
        font-family: "JetBrains Mono", "SFMono-Regular", Menlo, Consolas, monospace !important;
        font-size: 0.9rem !important;
    }

    div[data-testid="stMetric"] {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 6px;
    }

    .stButton > button {
        border-radius: 10px;
        border: 1px solid #2f5ea1;
        background: linear-gradient(180deg, #2f7ed8, #225ea5);
        color: #ffffff;
        font-weight: 600;
    }

    .stButton > button:hover {
        border-color: #5ea8ff;
        background: linear-gradient(180deg, #3a8de6, #2a6db9);
        color: #ffffff;
    }

    section[data-testid="stSidebar"] {
        border-right: 1px solid var(--line);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="app-shell">
      <p class="app-title">Nodes & Logic</p>
      <p class="app-sub">Interactive Python code-to-architecture visualizer with AST analysis and LLM insights.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "do_analyze" not in st.session_state:
    st.session_state.do_analyze = False

if "last_summary" not in st.session_state:
    st.session_state.last_summary = ""

if "analysis_error" not in st.session_state:
    st.session_state.analysis_error = ""

if "nodes_data" not in st.session_state:
    st.session_state.nodes_data = []

if "edges_data" not in st.session_state:
    st.session_state.edges_data = []

if "class_count" not in st.session_state:
    st.session_state.class_count = 0

if "fn_count" not in st.session_state:
    st.session_state.fn_count = 0

if "edge_count" not in st.session_state:
    st.session_state.edge_count = 0

if "analysis_status" not in st.session_state:
    st.session_state.analysis_status = "idle"

if "pending_run" not in st.session_state:
    st.session_state.pending_run = False

if "pending_request" not in st.session_state:
    st.session_state.pending_request = {}

# --- Sidebar ---
with st.sidebar:
    st.markdown("### Workspace Settings")

    provider_label = st.selectbox(
        "Provider",
        ["OpenAI", "Anthropic", "Ollama (Local)"],
        index=2,
    )

    provider = {
        "OpenAI": "openai",
        "Anthropic": "anthropic",
        "Ollama (Local)": "ollama",
    }[provider_label]

    if provider == "openai":
        api_key = st.text_input("OpenAI API Key", type="password")
        model_choice = st.text_input("Model", value="gpt-4o")
        ollama_base_url = "http://localhost:11434"
    elif provider == "anthropic":
        api_key = st.text_input("Anthropic API Key", type="password")
        model_choice = st.text_input("Model", value="claude-3-5-sonnet")
        ollama_base_url = "http://localhost:11434"
    else:
        api_key = ""
        model_choice = st.text_input("Ollama Model", value="llama3.1:8b-instruct-q4_K_M")
        ollama_base_url = st.text_input("Ollama Base URL", value="http://localhost:11434")

    st.divider()
    accent_color = st.color_picker("Graph Accent", "#3AA3FF")
    show_internal = st.checkbox("Show built-in calls", value=False)
    st.markdown("### Complexity Legend")
    st.markdown("- `Green (#00FFA3)`: CC 1-5")
    st.markdown("- `Yellow (#FFD700)`: CC 6-10")
    st.markdown("- `Red (#FF4B4B)`: CC 11+")
    st.markdown("- `Neutral (#9CA3AF)`: CC unavailable")

# --- Top Dashboard / Insights ---
if st.session_state.analysis_error:
    st.error(st.session_state.analysis_error)

if st.session_state.analysis_status in {"running", "done"} and not st.session_state.analysis_error:
    dot_class = "pulse" if st.session_state.analysis_status == "running" else "done"
    st.markdown(
        f"""
        <div class="status-row">
            <span class="status-dot {dot_class}"></span>
            <span class="status-title">Dashboard & LLM Insights</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Dashboard & LLM Insights", expanded=True):
        m1, m2, m3 = st.columns(3)
        m1.metric("Classes", st.session_state.class_count)
        m2.metric("Functions", st.session_state.fn_count)
        m3.metric("Links", st.session_state.edge_count)

        st.markdown('<div class="section-title">LLM Insights</div>', unsafe_allow_html=True)
        st.info(st.session_state.last_summary or "No insight generated yet.")

# --- Main Layout ---
left_col, right_col = st.columns([0.45, 0.55], gap="large")

with left_col:
    st.markdown('<div class="section-title">Source Code</div>', unsafe_allow_html=True)
    code_input = st.text_area(
        "Python Code",
        value="",
        height=500,
        placeholder="Paste your Python module here...",
        label_visibility="collapsed",
    )

    analyze_clicked = st.button("Analyze Architecture", use_container_width=True, type="primary")
    if analyze_clicked:
        if not code_input.strip():
            st.error("Paste Python code to start analysis.")
            st.session_state.do_analyze = False
            st.session_state.analysis_error = ""
            st.session_state.analysis_status = "idle"
        else:
            st.session_state.pending_request = {
                "code_input": code_input,
                "api_key": api_key,
                "model_choice": model_choice,
                "provider": provider,
                "ollama_base_url": ollama_base_url,
                "show_internal": show_internal,
            }
            st.session_state.pending_run = True
            st.session_state.analysis_status = "running"
            st.session_state.analysis_error = ""
            st.session_state.do_analyze = False
            st.rerun()

with right_col:
    st.markdown('<div class="section-title">Architecture Map</div>', unsafe_allow_html=True)

    if st.session_state.analysis_status == "running":
        st.info("Analysis in progress...")

    if st.session_state.do_analyze and st.session_state.nodes_data:
        nodes = [
            Node(
                id=n["id"],
                label=n["label"],
                size=24,
                color=n["color"] if n["color"] != "#1C83E1" else accent_color,
                title=n.get("title", n["label"]),
            )
            for n in st.session_state.nodes_data
        ]
        edges = [
            Edge(source=e["source"], target=e["target"], color="#7d8fb3")
            for e in st.session_state.edges_data
        ]

        graph_config = Config(
            width="100%",
            height=500,
            directed=True,
            physics=True,
            hierarchical=False,
            nodeHighlightBehavior=True,
            highlightColor="#ffffff",
            collapsible=True,
        )

        agraph(nodes=nodes, edges=edges, config=graph_config)
    else:
        st.info("Run analysis to render graph and architecture insights.")

if st.session_state.pending_run:
    request = st.session_state.pending_request
    analyzer = CodeAnalyzer(
        request.get("code_input", ""),
        request.get("api_key", ""),
        request.get("model_choice", ""),
        provider=request.get("provider", "openai"),
        ollama_base_url=request.get("ollama_base_url", "http://localhost:11434"),
    )

    try:
        with st.spinner("Building graph and generating LLM insight..."):
            nodes_data, edges_data = analyzer.get_structure(
                show_internal=request.get("show_internal", False)
            )
            summary = analyzer.get_llm_summary()

        st.session_state.nodes_data = nodes_data
        st.session_state.edges_data = edges_data
        st.session_state.class_count = sum(
            1 for n in nodes_data if str(n.get("label", "")).startswith("Class:")
        )
        st.session_state.fn_count = sum(
            1 for n in nodes_data if str(n.get("label", "")).startswith("fn:")
        )
        st.session_state.edge_count = len(edges_data)
        st.session_state.last_summary = summary
        st.session_state.analysis_error = ""
        st.session_state.do_analyze = True
        st.session_state.analysis_status = "done"
    except SyntaxError as error:
        st.session_state.analysis_error = (
            f"Syntax error at line {error.lineno}, column {error.offset}: {error.msg}. "
            "Please fix the code and try again."
        )
        st.session_state.do_analyze = False
        st.session_state.nodes_data = []
        st.session_state.edges_data = []
        st.session_state.analysis_status = "idle"
    except Exception as error:
        st.session_state.analysis_error = f"Analysis failed: {error}"
        st.session_state.do_analyze = False
        st.session_state.nodes_data = []
        st.session_state.edges_data = []
        st.session_state.analysis_status = "idle"
    finally:
        st.session_state.pending_run = False
        st.session_state.pending_request = {}

    st.rerun()
