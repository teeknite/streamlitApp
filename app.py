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
        
    return pdf.output(dest='S')

# --- STREAMLIT UI ---
st.set_page_config(page_title="CSV to PDF Converter", layout="wide")

st.title("📄 CSV to Individual PDF App")
st.write("Upload a CSV file to generate standalone, formatted documents for each row.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    headers = df.columns.tolist()
    
    st.write("### Data Preview")
    st.dataframe(df.head())

    st.divider()
    
    st.write("### Generate Documents")
    
    # Option to select a specific row or all rows
    row_to_gen = st.selectbox("Select a row to generate (by index)", df.index)
    
    if st.button(f"Generate PDF for Row {row_to_gen}"):
        selected_row = df.iloc[row_to_gen]
        pdf_bytes = create_pdf(selected_row, headers)
        
        # Determine a filename based on the first column or index
        filename = f"Record_{row_to_gen}.pdf"
        
        st.success(f"PDF Generated for {filename}!")
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf"
        )

    st.info("Tip: To share this with others, deploy this script to Streamlit Cloud.")