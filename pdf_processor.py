import PyPDF2

def extract_text_from_pdf(pdf_file):
    """
    Extracts text from an uploaded PDF file object.
    """
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None
    return text
