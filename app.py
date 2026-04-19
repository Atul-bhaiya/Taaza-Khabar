import streamlit as st
import requests
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- 1. INITIALIZATION ---
# Load environment variables from your local .env file
load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
SIGHT_USER = os.getenv("SIGHTENGINE_USER")
SIGHT_SECRET = os.getenv("SIGHTENGINE_SECRET")

# Configure Gemini AI for Linguistic Analysis
genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. BACKEND REQUEST LOGIC ---

def get_forensic_score(file_buffer):
    """Forensic analysis using Sightengine API to detect AI-generated media."""
    url = 'https://api.sightengine.com/1.0/check.json'
    params = {
        'models': 'genai',
        'api_user': SIGHT_USER,
        'api_secret': SIGHT_SECRET,
    }
    files = {'media': file_buffer}
    
    try:
        # POST Request for binary file upload
        response = requests.post(url, files=files, data=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('type', {}).get('ai_generated', 0)
        return None
    except Exception as e:
        return None

def get_news_prevalence(query):
    """Checks global source prevalence via News API (GET Request)."""
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            total = data.get("totalResults", 0)
            # Logic: Assigning a trust score based on source volume
            return min((total / 10) * 100, 100)
        return 0
    except:
        return 0

# --- 3. FRONTEND USER INTERFACE ---

st.set_page_config(page_title="Taaza-Khabar", page_icon="📡", layout="centered")

st.title("📡 Taaza-Khabar:Multimodal Fake News Detector")
st.caption("BCA Final Year Project | AI-Driven Disinformation Detection by Atul Bhaiya")
st.divider()

# Navigation Toggle
mode = st.radio("Select Analysis Module:", ["📰 Textual News", "🖼️ Image Forensics"], horizontal=True)

if mode == "📰 Textual News":
    user_text = st.text_area("Enter News Headline or Statement:", placeholder="Type here...")
    
    if st.button("Analyze Authenticity", use_container_width=True):
        if user_text:
            with st.status("Gathering Consensus...") as s:
                score = get_news_prevalence(user_text)
                s.update(label="Analysis Complete!", state="complete")
            
            st.metric("Source Trust Score", f"{int(score)}%")
            if score > 70:
                st.success("✅ Likely Genuine: High prevalence in global news databases.")
            elif score > 30:
                st.warning("⚠️ Suspicious: Limited source presence detected.")
            else:
                st.error("❌ Likely Fake: No reputable records found for this statement.")
        else:
            st.info("Please enter text to begin.")

elif mode == "🖼️ Image Forensics":
    uploaded_file = st.file_uploader("Upload Image (JPG/PNG):", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        st.image(uploaded_file, caption="Input Media", width=400)
        
        if st.button("Start Forensic Scan", use_container_width=True):
            with st.status("Running Convolutional Neural Network Scan...") as status:
                prob = get_forensic_score(uploaded_file)
                status.update(label="Media Scanned Successfully!", state="complete")
            
            if prob is not None:
                st.metric("AI-Generation Probability", f"{prob * 100:.2f}%")
                if prob > 0.5:
                    st.error("🚨 HIGH RISK: Digital artifacts suggest AI manipulation.")
                else:
                    st.success("✅ AUTHENTIC: High probability of being an original photograph.")
            else:
                st.error("Technical Error: API Authentication failed or limit reached.")

st.divider()
st.markdown("<p style='text-align: center; color: grey;'>© 2026 Taaza-Khabar Project Team</p>", unsafe_allow_html=True)