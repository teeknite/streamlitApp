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
    pdf.set_font("Arial", size=12)
    
    # Add a border/box for aesthetic
    pdf.set_draw_color(200, 200, 200)
    
    for header in headers:
        # Header (Bold)
        pdf.set_font("Arial", 'B', 11)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 8, f" {header}", ln=True, fill=True)
        
        # Value (Normal)
        pdf.set_font("Arial", size=12)
        value = str(row[header])
        # Multi_cell handles long text and wraps it
        pdf.multi_cell(0, 8, f" {value}", border='B')
        pdf.ln(4)
    
    # --- CRITICAL FIX HERE ---
    # We output the PDF as bytes directly
    return pdf.output()

# --- STREAMLIT UI ---
st.set_page_config(page_title="CSV to PDF Converter", layout="wide")

st.title("📄 CSV to Individual PDF App")
st.write("Upload a CSV file to generate standalone, formatted documents for each row.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Use 'index_col=False' to ensure the first column isn't eaten as an index
    df = pd.read_csv(uploaded_file)
    headers = df.columns.tolist()
    
    st.write("### Data Preview")
    st.dataframe(df.head())

    st.divider()
    
    st.write("### Generate Documents")
    
    # Option to select a specific row
    row_to_gen = st.selectbox("Select a row to generate", df.index, format_func=lambda x: f"Row {x}")
    
    selected_row = df.iloc[row_to_gen]
    
    # Generate the PDF data
    # We wrap it in bytes() to make sure Streamlit's download button is happy
    pdf_output = create_pdf(selected_row, headers)
    
    # Dynamic filename
    filename = f"Record_Row_{row_to_gen}.pdf"
    
    st.download_button(
        label=f"📥 Download PDF for Row {row_to_gen}",
        data=bytes(pdf_output), # This ensures it's the correct data type
        file_name=filename,
        mime="application/pdf"
    )

    st.info("Everything looks good! Click the button above to grab your file.")
