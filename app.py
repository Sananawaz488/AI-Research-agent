import streamlit as st
from agent import run_research, DEFAULT_MODEL

st.set_page_config(page_title="AI Research Agent", page_icon="🔎", layout="centered")

st.title("🔎 AI Research Agent")
st.caption("Single-agent CrewAI researcher · Groq LLM · Free DuckDuckGo search")

# --- API key: read ONLY from Streamlit secrets --------------------------
# Set this in Streamlit Cloud under: App settings -> Secrets
#   GROQ_API_KEY = "gsk_your_real_key_here"
groq_api_key = st.secrets.get("GROQ_API_KEY", None)

# --- Sidebar: settings -------------------------------------------------
with st.sidebar:
    st.header("Settings")

    if groq_api_key:
        st.success("Groq API key loaded from Streamlit secrets ✅")
    else:
        st.error(
            "No GROQ_API_KEY found in Streamlit secrets.\n\n"
            "Add it in your app's **Settings → Secrets** as:\n\n"
            '`GROQ_API_KEY = "gsk_your_real_key_here"`'
        )

    model = st.selectbox(
        "Groq model",
        [
            DEFAULT_MODEL,
            "groq/openai/gpt-oss-20b",
            "groq/llama-3.3-70b-versatile",
            "groq/llama-3.1-8b-instant",
        ],
        index=0,
        help="gpt-oss-120b is a strong, reasoning-capable open model on "
        "Groq. gpt-oss-20b is smaller/faster; llama-3.1-8b-instant is "
        "the fastest but least thorough.",
    )

    st.markdown("---")
    st.markdown(
        "This app uses [CrewAI](https://www.crewai.com/) with **one** "
        "agent that searches the web via DuckDuckGo (free, no API key) "
        "and writes up a report using a Groq-hosted LLM (free tier)."
    )

# --- Main area -----------------------------------------------------------
topic = st.text_input(
    "Research topic",
    placeholder="e.g. Latest trends in solid-state batteries",
)

run_button = st.button("Run Research", type="primary")

if run_button:
    if not groq_api_key:
        st.error(
            "Groq API key is missing. Add GROQ_API_KEY in your Streamlit "
            "app's Settings → Secrets, then reload the app."
        )
    elif not topic.strip():
        st.error("Please enter a research topic.")
    else:
        with st.spinner("Researching... this usually takes 30-90 seconds."):
            try:
                report = run_research(topic, groq_api_key, model)
                st.session_state["report"] = report
                st.session_state["topic"] = topic
            except Exception as e:
                st.error(f"Something went wrong: {e}")

if "report" in st.session_state:
    st.markdown("### Report")
    st.markdown(st.session_state["report"])
    st.download_button(
        "Download report as .md",
        st.session_state["report"],
        file_name=f"{st.session_state.get('topic', 'research')}_report.md",
    )
