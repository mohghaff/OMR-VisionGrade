import os
import io
import base64

import pandas as pd
import numpy as np
from PIL import Image

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import fitz  # PyMuPDF


CORRECT_ANS = [
    "D", "D", "A", "C", "B", "C", "B", "B", "C", "C",
    "A", "C", "B", "C", "B", "A", "D", "A", "A", "A",
    "B", "B", "B", "D", "A", "D", "B", "C", "C", "A",
    "A", "B", "C", "C", "C", "D", "B", "A", "C", "C"
]

# Cached Resources & Data
@st.cache_resource
def get_openai_client() -> OpenAI:
    """Initialize and cache the OpenAI client."""
    load_dotenv()
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        st.error("❌ OPENAI_API_KEY not found. Please check your .env file.")
        st.stop()
    return OpenAI(api_key=key)

@st.cache_data
def pdf_to_pil_image(pdf_bytes: bytes, dpi: int = 300) -> Image.Image:
    """Convert first page of PDF bytes to a PIL Image."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pix = doc[0].get_pixmap(dpi=dpi)
    return Image.open(io.BytesIO(pix.tobytes("png")))

@st.cache_data
def encode_image_for_api(_img: Image.Image) -> str:
    """
    Encode a PIL Image to a base64 JPEG string for minimal payload.
    The leading underscore tells Streamlit not to hash this argument.
    """
    buf = io.BytesIO()
    _img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

#  Grading Functions
def analyze_question(
    b64_image: str,
    question_number: int,
    model: str = "gpt-4.1-mini"
) -> str:
    """
    Send a single-question prompt + image to OpenAI and return the detected letter.
    """
    prompt = (
        f"This is a scanned image of a multiple-choice answer sheet. "
        f"Focus on question {question_number}. "
        "Options are A, B, C, and D. Identify which bubble is filled. "
        "If none are filled, reply with '–'. Return only the single uppercase letter."
    )
    client = get_openai_client()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert at reading OMR sheets."},
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
            ]}
        ],
        max_tokens=1
    )
    return resp.choices[0].message.content.strip().upper()

def grade_sheet(
    img: Image.Image,
    correct_answers: list[str],
    model: str
) -> list[str]:
    """
    Loop over each question, call the API, and collect detected answers.
    Shows a Streamlit progress bar.
    """
    b64 = encode_image_for_api(img)
    detected = []
    prog = st.progress(0)
    total = len(correct_answers)

    for i in range(total):
        detected.append(analyze_question(b64, i + 1, model))
        prog.progress((i + 1) / total)

    return detected

# Streamlit UI 
st.set_page_config(page_title="OMR Answer Sheet Grader")
st.title("📄 OMR Answer Sheet Grader")

# Refresh button
if st.button("🔁 Start Over / Refresh"):
    st.experimental_rerun()

# Sidebar controls
model_choice = st.sidebar.selectbox(
    "Choose model",
    ["gpt-4.1-mini", "o3", "gpt-4.1", "gpt-4.1-nano"]
)

# File uploader
uploaded = st.file_uploader(
    "Upload the filled answer sheet (1-page PDF)",
    type=["pdf"]
)

if uploaded:
    with st.spinner("Reading PDF and grading..."):
        img = pdf_to_pil_image(uploaded.read(), dpi=300)
        detected_answers = grade_sheet(img, CORRECT_ANS, model_choice)
        score = sum(d == c for d, c in zip(detected_answers, CORRECT_ANS))

    st.success(f"✅ Final Score: **{score} / 40**")

    # Build results DataFrame
    df = (
        pd.DataFrame({
            "Question": range(1, len(CORRECT_ANS) + 1),
            "Detected": detected_answers,
            "Correct": CORRECT_ANS
        })
        .assign(Status=lambda d: np.where(d.Detected == d.Correct, "✅", "❌"))
    )

    # Display styled table without the auto-index
    st.markdown("### Detected vs Correct Answers")
    styled = (
        df.style
          # color-code the Status column
          .map(
              lambda v: "color: green; font-weight: bold"
                        if v == "✅"
                        else ("color: red; font-weight: bold" if v == "❌" else ""),
              subset=["Status"]
          )
          # hide the Streamlit auto-generated index
          .set_table_styles([
              {"selector": "th.row_heading", "props": [("display", "none")]},
              {"selector": "td.row_heading", "props": [("display", "none")]}
          ])
    )
    st.dataframe(styled, use_container_width=True)

    # Excel export
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Results")
    st.download_button(
        label="⬇️ Download Results as Excel",
        data=buffer.getvalue(),
        file_name="OMR_Results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
