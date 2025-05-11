📝 OMR Answer Sheet Toolkit

Easily generate, fill, and automatically grade multiple-choice answer sheets using pure-Python PDF generation with ReportLab and OpenAI Vision models.

Everything from creating blank forms to scoring scanned sheets is included in this repository.

✨ What's Inside?

File

Purpose

mc_generator.py

Generate a blank 40-question answer sheet (2 columns × 20 rows, A-D bubbles).

answer_generator.py

Create a randomly filled version of the sheet, ideal for demos and testing.

app.py

Interactive Streamlit app: Upload a filled PDF, auto-detect answers, compare with an answer key, display results in a color-coded table, and export the results to Excel.

test_app.py

Streamlit tool for testing single questions, useful for refining prompts or crop logic.

🏗 Project Structure

.
├── .env                  # Store your OpenAI API key here
├── app.py                # Main grading application
├── answer_generator.py   # Generates demo sheets with random answers
├── mc_generator.py       # Generates blank answer sheets
├── test_app.py           # Tests single-question accuracy
└── requirements.txt      # Dependencies

🔧 Prerequisites

Python 3.9+

OpenAI API key with GPT-4 Vision access.

Create .env file in the project root:

OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

📦 Installation

# 1. Clone the repository
git clone https://github.com/mohghaff/OMR-VisionGrade.git
cd OMR-VisionGrade
# 2. Set up virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install required packages
pip install -r requirements.txt

requirements.txt

reportlab
streamlit
openai
python-dotenv
pillow
PyMuPDF          # Imported as fitz
pandas
XlsxWriter

🚀 Usage

1. Generate a blank answer sheet

python mc_generator.py
# Output: answer_sheet/answer_sheet.pdf

2. Create a demo sheet with random answers

python answer_generator.py
# Output: answer_sheet_filled.pdf

3. Launch the automated grading app

streamlit run app.py

Upload a scanned or photographed PDF of the filled sheet (single-page).

App functionality:

Sends the image to GPT-4 Vision model for each of the 40 questions.

Automatically grades against a predefined answer key.

Displays your score, color-coded results table, and allows Excel export.

4. Debug single questions (optional)

streamlit run test_app.py

Choose any page and question to see model predictions clearly.

🖼 Customization Tips

Adjustment

Location

Sheet layout (margins, spacing, columns)

Constants at the top of mc_generator.py & answer_generator.py

Question/options count

questions_per_column and options list (['A', 'B', 'C', 'D']) in the above files

Prompt wording

Functions analyze_question / analyze_bubble_region in app.py & test_app.py

Answer key

correct_answers list in app.py

⚠️ Notes & Limitations

Each question currently sends the entire sheet to the Vision model, with prompts instructing focus on specific questions. Cropping images per question could reduce cost and improve efficiency.

Optimal accuracy achieved with clear scans at 600 DPI.

Currently supports 40 fixed questions (2 columns).