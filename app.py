import streamlit as st
from PIL import Image
from groq import Groq
from dotenv import load_dotenv
import os
import base64

# =========================
# Load Environment Variables
# =========================
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY not found in .env file")
    st.stop()

# =========================
# Initialize Groq Client
# =========================
client = Groq(api_key=GROQ_API_KEY)

# =========================
# Page Configuration
# =========================
st.set_page_config(
    page_title="LaTeX OCR AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# Custom CSS Styling
# =========================
st.markdown(
    """
    <style>

    /* Global App Styling */
    .stApp {
        background-color: #f8fafc;
        color: #111827;
    }

    /* Main Container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Hero Section */
    .hero-section {
        text-align: center;
        padding: 2.5rem 1rem;
        margin-bottom: 2rem;
        margin-top: 2rem;
        border-radius: 24px;
        background: white;
        border: 1px solid #e5e7eb;
        box-shadow: 0 8px 25px rgba(0,0,0,0.05);
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        color: #111827;
        margin-bottom: 0.5rem;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        color: #4b5563;
    }

    /* Card Styling */
    .custom-card {
        background: white;
        border-radius: 22px;
        padding: 1.5rem;
        border: 1px solid #e5e7eb;
        box-shadow: 0 6px 20px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }

    /* File Uploader */
    [data-testid="stFileUploader"] {
        border-radius: 18px;
        background: #f9fafb;
        border: 2px dashed #cbd5e1;
        padding: 1rem;
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 14px;
        border: none;
        padding: 0.85rem 1rem;
        font-size: 1rem;
        font-weight: 700;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #16a34a, #22c55e);
        color: white;
        box-shadow: 0 4px 14px rgba(34,197,94,0.25);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        background: linear-gradient(135deg, #15803d, #16a34a);
        box-shadow: 0 8px 20px rgba(34,197,94,0.35);
    }

    /* Latex Render Box */
    .latex-container {
        background: #f9fafb;
        border-radius: 18px;
        padding: 1.5rem;
        text-align: center;
        margin-top: 1rem;
        border: 1px solid #e5e7eb;
    }

    /* Info Boxes */
    [data-testid="stAlert"] {
        border-radius: 16px;
    }

    /* Code Block */
    .stCodeBlock {
        border-radius: 18px;
    }

    /* Subheaders */
    h3 {
        color: #111827 !important;
    }

    /* Remove Streamlit Footer */
    footer {
        visibility: hidden;
    }

    /* Responsive Design */
    @media (max-width: 768px) {

        .hero-title {
            font-size: 2rem;
        }

        .hero-subtitle {
            font-size: 0.95rem;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# Hero Section
# =========================
st.markdown(
    """
    <div class="hero-section">
        <div class="hero-title">🛡️ LaTeX OCR AI</div>
        <div class="hero-subtitle">
            Extract Mathematical Equations from Images using Vision Language Models
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# Top Action Bar
# =========================
top_col1, top_col2, top_col3 = st.columns([8, 1.2, 1.2])

with top_col3:
    if st.button("🗑️ Clear"):
        st.session_state.clear()
        st.rerun()

# =========================
# Main Layout
# =========================
left_col, right_col = st.columns([1, 1], gap="large")

# =========================
# Upload Section
# =========================
with left_col:

    st.markdown('<div class="custom-card">', unsafe_allow_html=True)

    st.subheader("📤 Upload Equation Image")

    uploaded_file = st.file_uploader(
        "Upload Equation",
        type=["png", "jpg", "jpeg", "webp"],
        label_visibility="collapsed"
    )

    if uploaded_file is not None:

        image = Image.open(uploaded_file)

        st.image(
            image,
            caption="Uploaded Equation",
            use_container_width=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("⚡ Extract LaTeX"):

            with st.spinner("Analyzing Equation..."):

                try:

                    image_bytes = uploaded_file.getvalue()

                    encoded_image = base64.b64encode(
                        image_bytes
                    ).decode("utf-8")

                    response = client.chat.completions.create(
                        model="meta-llama/llama-4-scout-17b-16e-instruct",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": """
You are a mathematical OCR system.

Extract the mathematical equation from the image and return ONLY valid LaTeX code.

STRICT RULES:
- Return ONLY LaTeX code
- No explanations
- No markdown
- No triple backticks
- No dollar signs
- Preserve equation structure exactly
- Do not simplify equations
- Do not add extra symbols
"""
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{encoded_image}"
                                        }
                                    }
                                ]
                            }
                        ],
                        temperature=0
                    )

                    latex_output = (
                        response.choices[0]
                        .message.content
                        .strip()
                    )

                    st.session_state["latex_output"] = latex_output

                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")

    else:
        st.info(
            "Upload a mathematical equation image to begin OCR extraction."
        )

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# Results Section
# =========================
with right_col:

    st.markdown('<div class="custom-card">', unsafe_allow_html=True)

    st.subheader("📄 OCR Results")

    if "latex_output" in st.session_state:

        st.markdown("### Extracted LaTeX Code")

        st.code(
            st.session_state["latex_output"],
            language="latex"
        )

        st.markdown("### 🧮 Rendered Equation")

        st.markdown(
            '<div class="latex-container">',
            unsafe_allow_html=True
        )

        try:

            cleaned_latex = (
                st.session_state["latex_output"]
                .replace(r"\[", "")
                .replace(r"\]", "")
                .strip()
            )

            st.latex(cleaned_latex)

        except Exception:
            st.warning("Unable to render LaTeX properly.")

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("Your extracted LaTeX result will appear here.")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# Footer
# =========================
st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    """
    <div style="
        text-align:center;
        color:#6b7280;
        padding:1rem;
        font-size:0.95rem;
    ">
        Made with 💖 using Streamlit, Groq API & Vision Language Models
    </div>
    """,
    unsafe_allow_html=True
)