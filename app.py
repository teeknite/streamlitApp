import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

# --- PDF GENERATION LOGIC ---
class CSVToPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Entry Record Document', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf(row, headers):
    pdf = CSVToPDF()
    pdf.add_page()
    
    # Requirement 1: Reduce font size to 10pt
    pdf.set_font("Arial", size=10)
    
    # Requirement 3: 2-Column Setup parameters
    col_width = 92  # Width of each column 
    x_left = 10     # Left margin
    x_right = 108   # Starts right after the left column + small gap
    
    # Track starting vertical position
    y_current = pdf.get_y()
    max_y_in_row = y_current
    
    for i, header in enumerate(headers):
        # Requirement 2: Title and value on the same line
        value = str(row[header])
        text = f"{header}: {value}"
        
        is_left_column = (i % 2 == 0)
        
        # Handle Page Breaks if we get too close to the bottom of the page
        if y_current > 265 and is_left_column:
            pdf.add_page()
            y_current = pdf.get_y()
            max_y_in_row = y_current
            
        # Set the horizontal (X) and vertical (Y) position
        if is_left_column:
            pdf.set_xy(x_left, y_current)
        else:
            pdf.set_xy(x_right, y_current)
            
        # Draw the text box. 'multi_cell' automatically wraps long text!
        # Note: A light grey background (fill) is added to make the blocks distinct
        pdf.set_fill_color(245, 245, 245)
        pdf.multi_cell(col_width, 6, text, border=0, fill=True)
        
        # Check how far down the text wrapped to prevent overlapping rows
        end_y = pdf.get_y()
        if end_y > max_y_in_row:
            max_y_in_row = end_y
            
        # If we are on the right column (or it's the very last item), 
        # push the current Y down to start the next row
        if not is_left_column or i == len(headers) - 1:
            y_current = max_y_in_row + 4 # 4mm vertical padding between rows
            max_y_in_row = y_current
            
    return pdf.output()

# --- STREAMLIT UI ---
st.set_page_config(page_title="CSV to PDF Converter", layout="wide")

st.title("📄 CSV to Individual PDF App")
st.write("Upload a CSV file to generate standalone, formatted documents for each row.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    headers = df.columns.tolist()
    
    st.write("### Data Preview")
    st.dataframe(df, height=400)

    st.divider()
    
    st.write("### Generate Documents")
    
    row_to_gen = st.selectbox("Select a row to generate", df.index, format_func=lambda x: f"Row {x}")
    
    selected_row = df.iloc[row_to_gen]
    pdf_output = create_pdf(selected_row, headers)
    filename = f"Record_Row_{row_to_gen}.pdf"
    
    st.download_button(
        label=f"📥 Download PDF for Row {row_to_gen}",
        data=bytes(pdf_output),
        file_name=filename,
        mime="application/pdf"
    )
