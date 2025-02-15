import streamlit as st
import os
from PIL import Image
from tempfile import NamedTemporaryFile
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.tavily import TavilyTools
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@st.cache_resource
def get_agent():
    """Initialize the AI agent with updated prompts for dashboard analysis"""
    return Agent(
        model=Gemini(id="gemini-2.0-flash-exp"),
        system_prompt=os.getenv("SYSTEM_PROMPT", "Analyze dashboards"),
        instructions=os.getenv("INSTRUCTIONS", "Provide insights."),
        tools=[TavilyTools(api_key=os.getenv("TAVILY_API_KEY"))],
        markdown=True,
    )

def analyze_dashboard(image_path, user_query):
    """Runs AI analysis on the provided dashboard image with a user query"""
    agent = get_agent()
    with st.spinner('Analyzing dashboard...'):
        try:
            response = agent.run(
                f"Analyze the given image with respect to the user's request: {user_query}",
                images=[image_path],
            )
            st.markdown(response.content)
        except Exception as e:
            st.error(f"Analysis failed: {e}")

def save_uploaded_file(uploaded_file):
    """Save the uploaded image temporarily for processing"""
    with NamedTemporaryFile(dir='.', suffix='.jpg', delete=False) as f:
        f.write(uploaded_file.getbuffer())
        return f.name

def main():
    """Streamlit UI"""
    st.set_page_config(
        page_title="Dashboard Analyzer",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    st.markdown("""
    <style>
        .stButton button {width: 100%; border-radius: 8px; font-size: 1.2rem;}
        .stFileUploader div {border-radius: 8px; padding: 10px;}
        .stTextArea textarea {border-radius: 8px; padding: 10px; font-size: 1rem;}
    </style>
    """, unsafe_allow_html=True)

    st.header("Dashboard Analyzer", divider='rainbow', anchor=None)
    st.markdown("Upload a dashboard image from Power BI, Tableau, or other visualization tools for a comprehensive analysis. Gain insights into key trends, data patterns, and visual effectiveness. Assess the clarity, usability, and overall impact of the dashboard design. Receive data-driven recommendations to enhance interpretation and decision-making.")

    st.sidebar.subheader("Upload Dashboard", divider="blue")
    uploaded_file = st.sidebar.file_uploader(
        "Upload a dashboard image (JPG, PNG, JPEG)",
        type=["jpg", "jpeg", "png"],
        help="Ensure the dashboard is **clear and readable**."
    )

    if uploaded_file:
        st.header("Dashboard Preview", divider='rainbow', anchor=None)
        st.image(uploaded_file, caption="Dashboard Preview", output_format='PNG')

        user_query = st.text_area(
            "What would you like to analyze?",
            placeholder="E.g., Identify trends, check for design effectiveness...",
            key="query_input"
        )

        analyze_disabled = not user_query.strip()  # Disable if query is empty
        analyze_button = st.button("Analyze Dashboard", key="analyze_upload", disabled=analyze_disabled)

        if analyze_button:
            temp_path = save_uploaded_file(uploaded_file)
            try:
                analyze_dashboard(temp_path, user_query)
            finally:
                os.unlink(temp_path)  # Ensure cleanup

if __name__ == "__main__":
    main()
