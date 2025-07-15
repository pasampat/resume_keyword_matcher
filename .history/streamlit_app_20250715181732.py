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
if st.button("Analyze"):
    if not job_file:
        st.error("Please upload a job description.")
    elif not resume_files or len(resume_files) == 0:
        st.error("Please upload at least one resume.")
    elif len(resume_files) > 3:
        st.error("Please upload no more than 3 resumes.")
    else:
        st.success("Files uploaded! (Reading and displaying full text below)")
        # Read and display Job Description
        job_text = read_uploaded_file(job_file)
        with st.expander(f"Job Description: {job_file.name}"):
            st.text(job_text if len(job_text) < 5000 else job_text[:5000] + "\n...[truncated]")
        # Read and display each Resume
        for f in resume_files:
            resume_text = read_uploaded_file(f)
            with st.expander(f"Resume: {f.name}"):
                st.text(resume_text if len(resume_text) < 5000 else resume_text[:5000] + "\n...[truncated]")

# For dev: remind user how to run the app
st.markdown("""
---
_ℹ️ To run this app: open a terminal and type:_  
`streamlit run streamlit_app.py`
""")
