import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

# Define file path for final refined version
file_path = "./answer_sheet_filled.pdf"

# Page setup
page_width, page_height = letter
top_margin = page_height - 1 * inch
bubble_radius = 8  # smaller bubble
horizontal_spacing = 30
vertical_spacing = 28
questions_per_column = 20
start_y = top_margin - 100

# Recalculate centered layout
column_width = 30 + 3 * horizontal_spacing
total_columns_width = 2 * column_width + 40
center_start_x = (page_width - total_columns_width) / 2

# Create canvas
c = canvas.Canvas(file_path, pagesize=letter)

# Header
c.setFont("Helvetica-Bold", 14)
c.drawCentredString(page_width / 2, top_margin, "Multiple Choice Answer Sheet")

c.setFont("Helvetica", 10)
c.drawString(center_start_x, top_margin - 30, "Student Name: ________________")
c.drawString(page_width / 2 + 40, top_margin - 30, "ID: ____________________")
c.drawString(center_start_x, top_margin - 50, "Test Date: ______________")

# Instructions
c.setFont("Helvetica-Oblique", 9)
c.drawString(center_start_x, top_margin - 70, "Instructions: Fill in the bubbles completely using a pencil.")

# Draw and randomly fill questions
for col in range(2):
    x_offset = center_start_x + col * (column_width + 40)
    for i in range(questions_per_column):
        q_number = i + 1 + col * questions_per_column
        y_position = start_y - i * vertical_spacing
        c.setFont("Helvetica", 10)
        c.drawString(x_offset, y_position, f"{q_number:02d}.")
        
        # Randomly choose a filled answer (0-3 for A-D)
        filled_index = random.randint(0, 3)

        for j, option in enumerate(['A', 'B', 'C', 'D']):
            cx = x_offset + 30 + j * horizontal_spacing
            cy = y_position + 2
            if j == filled_index:
                c.setFillColorRGB(0, 0, 0)  # Black fill for selected bubble
                c.circle(cx, cy, bubble_radius, stroke=1, fill=1)
            else:
                c.setFillColorRGB(1, 1, 1)  # White fill for empty bubbles
                c.circle(cx, cy, bubble_radius, stroke=1, fill=0)
            c.setFillColorRGB(0, 0, 0)  # Reset to black for text
            c.setFont("Helvetica", 7)
            c.drawCentredString(cx, cy - 2, option)

# Finalize and save
c.showPage()
c.save()

file_path
