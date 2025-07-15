import streamlit as st
from io import BytesIO
from PyPDF2 import PdfReader

def read_uploaded_file(uploaded_file):
    """Reads and returns the text content of an uploaded .txt or .pdf file."""
    if uploaded_file.type == "text/plain":
        return uploaded_file.read().decode("utf-8")
    elif uploaded_file.type == "application/pdf":
        try:
            pdf = PdfReader(BytesIO(uploaded_file.read()))
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as e:
            return f"[Error reading PDF: {e}]"
    else:
        return "[Unsupported file type]"


st.title("Resume Keyword Matcher")

st.markdown("""
Upload a job description and 1–3 resumes (PDF or TXT).
You’ll be able to analyze keyword overlap after uploading files.
""")

# Upload job description
job_file = st.file_uploader(
    "Upload Job Description (.txt or .pdf)", 
    type=["txt", "pdf"], 
    key="jobdesc"
)

# Upload 1-3 resumes
resume_files = st.file_uploader(
    "Upload 1 to 3 Resumes (.txt or .pdf)", 
    type=["txt", "pdf"], 
    accept_multiple_files=True, 
    key="resumes"
)

# Extraction mode selector
mode = st.radio(
    "Keyword extraction mode",
    ["All words (default)", "Only nouns/verbs (recommended for most jobs)"]
)

# Analyze button

# For dev: remind user how to run the app
st.markdown("""
---
_ℹ️ To run this app: open a terminal and type:_  
`streamlit run streamlit_app.py`
""")
