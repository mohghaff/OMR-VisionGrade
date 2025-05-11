import os
import io
import base64
import pandas as pd
from PIL import Image
import streamlit as st
from dotenv import load_dotenv
import fitz  # PyMuPDF
from openai import OpenAI

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("❌ OPENAI_API_KEY not found. Please check your .env file.")
    st.stop()

client = OpenAI(api_key=api_key)

# Correct answer key
correct_answers = [
    "D", "D", "A", "C", "B", "C", "B", "B", "C", "C",
    "A", "C", "B", "C", "B", "A", "D", "A", "A", "A",
    "B", "B", "B", "D", "A", "D", "B", "C", "C", "A",
    "A", "B", "C", "C", "C", "D", "B", "A", "C", "C"
]

def encode_image(image: Image.Image) -> str:
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def analyze_question(image: Image.Image, question_number: int) -> str:
    base64_image = encode_image(image)
    prompt = (
        f"This is a scanned image of a full multiple-choice answer sheet. "
        f"Focus on question {question_number}. The options are A, B, C, and D. "
        f"Identify which bubble is filled. If none are filled, respond with '–'. "
        f"Return only the selected letter."
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
    return response.choices[0].message.content.strip().upper()

# UI Setup
st.set_page_config(page_title="OMR Answer Sheet Grader")
st.title("📄 OMR Answer Sheet Grader")

# Refresh Button
if st.button("🔁 Start Over / Refresh"):
    st.rerun()

# File upload
uploaded_pdf = st.file_uploader("Upload the filled answer sheet (1-page PDF)", type=["pdf"])

if uploaded_pdf:
    with st.spinner("Reading PDF and grading..."):
        pdf_bytes = uploaded_pdf.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[0]  # Always first page
        pix = page.get_pixmap(dpi=600)
        full_image = Image.open(io.BytesIO(pix.tobytes("png")))

        score = 0
        detected_answers = []

        for i in range(40):
            q_num = i + 1
            detected = analyze_question(full_image, q_num)
            detected_answers.append(detected)
            if detected == correct_answers[i]:
                score += 1

        st.success(f"✅ Final Score: **{score} / 40**")

        # Create DataFrame for table
        results = []
        for i in range(40):
            correct = correct_answers[i]
            detected = detected_answers[i]
            results.append({
                "Question": i + 1,
                "Detected Answer": detected,
                "Correct Answer": correct,
                "Status": "✅" if detected == correct else "❌"
            })

        df = pd.DataFrame(results)

        # Display styled table
        def highlight_correct(val, correct):
            color = 'green' if val == correct else 'red'
            return f'color: {color}; font-weight: bold'

        st.markdown("### Detected vs Correct Answers")
        st.dataframe(
            df.style.apply(lambda row: [
                highlight_correct(row["Detected Answer"], row["Correct Answer"]) if col == 'Detected Answer' else ''
                for col in df.columns
            ], axis=1),
            use_container_width=True
        )

        # Export to Excel
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Results")
        st.download_button(
            label="⬇️ Download Results as Excel",
            data=excel_buffer.getvalue(),
            file_name="OMR_Results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
