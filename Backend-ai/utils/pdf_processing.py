import fitz  # PyMuPDF

def extract_clauses_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"
    clauses = [clause.strip() for clause in full_text.split('\n') if len(clause.strip()) > 30]
    return clauses
