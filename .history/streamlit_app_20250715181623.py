import streamlit as st
from io import BytesIO
from PyPDF2 import PdfReader



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
        st.success("Files uploaded! (Backend logic goes here)")
        # For now, just show filenames and a preview of each
        st.markdown("**Job Description:**")
        st.write(job_file.name)
        st.markdown("**Resumes:**")
        for f in resume_files:
            st.write(f.name)
        # (Add a preview of first 300 chars of text if txt file)
        if job_file.type == "text/plain":
            job_text = job_file.read().decode("utf-8")
            st.markdown("**Job Description Preview:**")
            st.text(job_text[:300])
        for f in resume_files:
            if f.type == "text/plain":
                text = f.read().decode("utf-8")
                st.markdown(f"**Preview of {f.name}:**")
                st.text(text[:300])

# For dev: remind user how to run the app
st.markdown("""
---
_ℹ️ To run this app: open a terminal and type:_  
`streamlit run streamlit_app.py`
""")
