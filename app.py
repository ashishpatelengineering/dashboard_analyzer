import streamlit as st
import os
from PIL import Image
from io import BytesIO
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.tavily import TavilyTools
from tempfile import NamedTemporaryFile
from constants import SYSTEM_PROMPT, INSTRUCTIONS

# API Keys (Ensure these are stored securely in production)
os.environ['TAVILY_API_KEY'] = st.secrets['TAVILY_API_KEY']
os.environ['GOOGLE_API_KEY'] = st.secrets['GOOGLE_API_KEY']

MAX_IMAGE_WIDTH = 600

def resize_image_for_display(image_file):
    """Resize image for display only, returns bytes"""
    img = Image.open(image_file)
    image_file.seek(0)
    
    aspect_ratio = img.height / img.width
    new_height = int(MAX_IMAGE_WIDTH * aspect_ratio)
    img = img.resize((MAX_IMAGE_WIDTH, new_height), Image.Resampling.LANCZOS)
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

@st.cache_resource
def get_agent():
    """Initialize the AI agent with updated prompts for dashboard analysis"""
    return Agent(
        model=Gemini(id="gemini-2.0-flash-exp"),
        system_prompt=SYSTEM_PROMPT,
        instructions=INSTRUCTIONS,
        tools=[TavilyTools(api_key=os.getenv("TAVILY_API_KEY"))],
        markdown=True,
    )

def analyze_dashboard(image_path):
    """Runs AI analysis on the provided dashboard image"""
    agent = get_agent()
    with st.spinner('🔍 Analyzing dashboard...'):
        response = agent.run(
            "Analyze the given image for dashboard insights, visual effectiveness, and data representation.",
            images=[image_path],
        )
        st.markdown(response.content)

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
        .css-1d391kg {padding: 2rem;}
        .stButton button {width: 100%; border-radius: 8px; font-size: 1.2rem;}
        .stFileUploader div {border-radius: 8px; padding: 10px;}
    </style>
    """, unsafe_allow_html=True)
    
    st.title("📊 Dashboard Analyzer")
    st.markdown("Analyze Power BI, Tableau, or other dashboards for insights and effectiveness.")
    
    uploaded_file = st.file_uploader(
        "Upload a dashboard image (JPG, PNG, JPEG)",
        type=["jpg", "jpeg", "png"],
        help="Ensure the dashboard is **clear and readable**."
    )
    
    if uploaded_file:
        st.markdown("### Uploaded Dashboard")
        resized_image = resize_image_for_display(uploaded_file)
        st.image(resized_image, caption="Dashboard Preview", use_column_width=True)
        
        if st.button("📊 Analyze Dashboard", key="analyze_upload"):
            temp_path = save_uploaded_file(uploaded_file)
            analyze_dashboard(temp_path)
            os.unlink(temp_path)

if __name__ == "__main__":
    main()
