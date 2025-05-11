import os
import io
import base64
from PIL import Image
import streamlit as st
from dotenv import load_dotenv
import fitz  # PyMuPDF
from openai import OpenAI

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# 🔐 Debug check
if not api_key:
    st.error("❌ OPENAI_API_KEY not found. Please check your .env file.")
    st.stop()

# Initialize OpenAI client with API key
client = OpenAI(api_key=api_key)

def encode_image(image: Image.Image) -> str:
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def analyze_bubble_region(image: Image.Image, question_number: int) -> str:
    base64_image = encode_image(image)
    prompt = (
        f"This is a scanned image of multiple-choice bubbles for question {question_number}. "
        "The answer options are A, B, C, and D. Identify which bubble is filled. "
        "If none are filled, respond with '–'. Return only the selected letter."
    )
    response = client.chat.completions.create(
        model="gpt-4.1-mini",  
        messages=[
            {"role": "system", "content": "You are an expert at reading multiple-choice answer sheets."},
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
            ]}
        ],
        max_tokens=10
    )
    return response.choices[0].message.content.strip()

# Streamlit App UI
st.set_page_config(page_title="OMR Answer Sheet Reader")
st.title("📄 OMR Answer Sheet Reader")
uploaded_pdf = st.file_uploader("Upload a PDF answer sheet", type=["pdf"])

if uploaded_pdf:
    pdf_bytes = uploaded_pdf.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    selected_page = st.selectbox("Select page number", list(range(len(doc))))
    page = doc[selected_page]
    pix = page.get_pixmap(dpi=300)
    image = Image.open(io.BytesIO(pix.tobytes("png")))

    st.image(image, caption=f"Page {selected_page}", use_column_width=True)
    question_number = st.number_input("Question number:", min_value=1, max_value=100, value=1)

    if st.button("Detect Answer"):
        with st.spinner("Analyzing..."):
            result = analyze_bubble_region(image, question_number)
        st.success(f"✅ Detected Answer: **{result}**")
