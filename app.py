import streamlit as st
from PIL import Image
from groq import Groq
from dotenv import load_dotenv
import os
import base64
import io

# =========================
# Load Environment Variables
# =========================
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# =========================
# Page Configuration
# =========================
st.set_page_config(
    page_title="LaTeX OCR AI",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# Validate API Key
# =========================
if not GROQ_API_KEY:
    st.error(
        """
        GROQ_API_KEY not found.

        Add it in:
        - Local .env file
        - OR Render Environment Variables
        """
    )
    st.stop()

# =========================
# Initialize Groq Client
# =========================
try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error(f"Failed to initialize Groq Client: {e}")
    st.stop()

# =========================
# Custom CSS Styling
# =========================
st.markdown(
    """
    <style>

    .stApp {
        background-color: #f8fafc;
        color: #111827;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

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

    .custom-card {
        background: white;
        border-radius: 22px;
        padding: 1.5rem;
        border: 1px solid #e5e7eb;
        box-shadow: 0 6px 20px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }

    [data-testid="stFileUploader"] {
        border-radius: 18px;
        background: #f9fafb;
        border: 2px dashed #cbd5e1;
        padding: 1rem;
    }

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
    }

    .latex-container {
        background: #f9fafb;
        border-radius: 18px;
        padding: 1.5rem;
        text-align: center;
        margin-top: 1rem;
        border: 1px solid #e5e7eb;
    }

    footer {
        visibility: hidden;
    }

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
        <div class="hero-title">🧮 LaTeX OCR AI</div>
        <div class="hero-subtitle">
            Extract Mathematical Equations from Images using Groq Vision Models
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
        if "latex_output" in st.session_state:
            del st.session_state["latex_output"]

        if "uploaded_image" in st.session_state:
            del st.session_state["uploaded_image"]

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

        try:

            image = Image.open(uploaded_file)

            # Convert RGBA to RGB
            if image.mode == "RGBA":
                image = image.convert("RGB")

            st.image(
                image,
                caption="Uploaded Equation",
                use_container_width=True
            )

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("⚡ Extract LaTeX"):

                with st.spinner("Analyzing Equation..."):

                    # Convert image to bytes
                    buffered = io.BytesIO()
                    image.save(buffered, format="JPEG")

                    image_bytes = buffered.getvalue()

                    # Limit image size
                    max_size_mb = 4

                    if len(image_bytes) > max_size_mb * 1024 * 1024:
                        st.error("Image size too large. Please upload image below 4MB.")
                        st.stop()

                    encoded_image = base64.b64encode(
                        image_bytes
                    ).decode("utf-8")

                    response = client.chat.completions.create(
                        model="llama-3.2-90b-vision-preview",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": """
You are an advanced mathematical OCR system.

Extract ONLY the mathematical equation from the image.

STRICT RULES:
- Return ONLY valid LaTeX
- No markdown
- No explanations
- No triple backticks
- No dollar signs
- Preserve exact structure
- Do not simplify
- Do not add symbols
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
                        temperature=0,
                        max_tokens=300
                    )

                    latex_output = (
                        response.choices[0]
                        .message.content
                        .strip()
                    )

                    # Clean response
                    latex_output = (
                        latex_output
                        .replace("```latex", "")
                        .replace("```", "")
                        .replace("$", "")
                        .strip()
                    )

                    st.session_state["latex_output"] = latex_output

                    st.success("LaTeX extracted successfully!")

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
        Made with ❤️ using Streamlit + Groq Vision API
    </div>
    """,
    unsafe_allow_html=True
)