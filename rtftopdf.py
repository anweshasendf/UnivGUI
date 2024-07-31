import os
from striprtf.striprtf import rtf_to_text
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def rtf_to_pdf(rtf_path, pdf_path):
    # Read and convert RTF content
    with open(rtf_path, 'r', encoding='utf-8') as rtf_file:
        rtf_content = rtf_file.read()
    plain_text = rtf_to_text(rtf_content)

    # Create PDF
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    flowables = [Paragraph(line, styles['Normal']) for line in plain_text.split('\n')]
    doc.build(flowables)

def convert_directory(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.rtf'):
            rtf_path = os.path.join(input_dir, filename)
            pdf_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.pdf")
            rtf_to_pdf(rtf_path, pdf_path)
            print(f"Converted {filename} to PDF")

if __name__ == "__main__":
    input_directory = r"C:\Users\U436445\Downloads\RTF"
    output_directory = r"C:\Users\U436445\OneDrive - Danfoss\Documents\GitHub\Single"
    convert_directory(input_directory, output_directory)