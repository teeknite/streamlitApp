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
    
    pdf.set_font("Arial", size=10)
    
    # 2-Column Setup parameters
    col_width = 92  
    x_left = 10     
    x_right = 108   
    
    y_current = pdf.get_y()
    max_y_in_row = y_current
    
    for i, header in enumerate(headers):
        is_left_column = (i % 2 == 0)
        
        # Handle Page Breaks
        if y_current > 265 and is_left_column:
            pdf.add_page()
            y_current = pdf.get_y()
            max_y_in_row = y_current
            
        # Set the correct X and Y position for the grid
        if is_left_column:
            pdf.set_xy(x_left, y_current)
        else:
            pdf.set_xy(x_right, y_current)
            
        # --- SPACER LOGIC ---
        # If pandas named the column "Unnamed:", treat it as an empty space
        if str(header).startswith("Unnamed:"):
            # We don't draw anything, but we account for standard line height
            end_y = y_current + 6
            if end_y > max_y_in_row:
                max_y_in_row = end_y
        else:
            # Clean up the value: if it's empty/NaN, print nothing instead of 'nan'
            val = row[header]
            value = "" if pd.isna(val) else str(val)
            
            text = f"**{header}:** {value}"
            
            pdf.set_fill_color(245, 245, 245)
            pdf.multi_cell(col_width, 6, text, border=0, fill=True, align='L', markdown=True)
            
            end_y = pdf.get_y()
            if end_y > max_y_in_row:
                max_y_in_row = end_y
                
        # Push Y coordinate down to the next row
        if not is_left_column or i == len(headers) - 1:
            y_current = max_y_in_row + 4
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
