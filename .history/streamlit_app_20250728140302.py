import streamlit as st
from io import BytesIO
from PyPDF2 import PdfReader
from text_utils import clean_text, extract_keywords, extract_nouns_verbs, match_keywords, calculate_match_percent
from stopwords import STOP_WORDS
import collections
import pandas as pd

# ========== FILE READING HELPERS ==========

def read_uploaded_file(uploaded_file):
    """
    Reads and returns the text content of an uploaded .txt or .pdf file.
    Handles encoding and PDF errors gracefully.
    """
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

# ========== KEYWORD EXTRACTION & MATCHING ==========

def extract_keywords_from_jd(job_text, mode):
    """
    Cleans and processes job description text,
    extracting a set of keywords and their frequencies.
    Mode can be 'all' (all words) or 'nouns_verbs' (only nouns/verbs).
    """
    job_cleaned = clean_text(job_text, STOP_WORDS)
    if mode == "nouns_verbs":
        job_cleaned = extract_nouns_verbs(job_cleaned)
    job_keywords = extract_keywords(job_cleaned)
    job_word_counts = collections.Counter(job_cleaned)
    return job_keywords, job_word_counts

def analyze_resume(resume_text, jd_keywords):
    """
    Cleans a resume and matches it against JD keywords.
    Returns matched/missing sets, match percent, and resume word counts.
    """
    resume_cleaned = clean_text(resume_text, STOP_WORDS)
    matched, missing = match_keywords(jd_keywords, resume_cleaned)
    match_percent = calculate_match_percent(matched, len(jd_keywords))
    resume_counts = collections.Counter(resume_cleaned)
    return matched, missing, match_percent, resume_counts

# ========== STREAMLIT APP UI ==========

st.title("Resume Keyword Matcher")

st.markdown("""
Upload a job description and 1–3 resumes (PDF or TXT).
You'll see a summary table and a side-by-side keyword matrix for comparison.
Matched/missing keywords for each resume can be viewed by expanding the details.
""")

# File uploaders for job description and resumes
job_file = st.file_uploader(
    "Upload Job Description (.txt or .pdf)", 
    type=["txt", "pdf"], 
    key="jobdesc"
)

resume_files = st.file_uploader(
    "Upload 1 to 3 Resumes (.txt or .pdf)", 
    type=["txt", "pdf"], 
    accept_multiple_files=True, 
    key="resumes"
)

# Radio button for extraction mode
mode = st.radio(
    "Keyword extraction mode",
    ["All words (default)", "Only nouns/verbs (recommended for most jobs)"]
)

# Main logic triggered on Analyze button click
if st.button("Analyze"):
    # Error handling for required files
    if not job_file:
        st.error("Please upload a job description.")
    elif not resume_files or len(resume_files) == 0:
        st.error("Please upload at least one resume.")
    elif len(resume_files) > 3:
        st.error("Please upload no more than 3 resumes.")
    else:
        # === READ AND DISPLAY JOB DESCRIPTION ===
        job_text = read_uploaded_file(job_file)
        with st.expander(f"Job Description: {job_file.name}"):
            st.text(job_text if len(job_text) < 5000 else job_text[:5000] + "\n...[truncated]")

        # === EXTRACT KEYWORDS FROM JD ===
        jd_mode = "all" if mode.startswith("All") else "nouns_verbs"
        jd_keywords, jd_word_counts = extract_keywords_from_jd(job_text, jd_mode)

        summary_rows = []
        resume_names = []
        resume_counts_list = []
        matched_missing_per_resume = []

        # === ANALYZE EACH RESUME ===
        for f in resume_files:
            resume_text = read_uploaded_file(f)
            # Display resume text in an expander (truncated for long files)
            with st.expander(f"Resume: {f.name}"):
                st.text(resume_text if len(resume_text) < 5000 else resume_text[:5000] + "\n...[truncated]")
            # Calculate match data
            matched, missing, match_percent, resume_counts = analyze_resume(resume_text, jd_keywords)
            # Store all results for later summary and display
            summary_rows.append({
                "Resume": f.name,
                "Match %": f"{match_percent:.1f}",
                "#Matched": len(matched),
                "#Missing": len(missing)
            })
            resume_names.append(f.name)
            resume_counts_list.append(resume_counts)
            matched_missing_per_resume.append((matched, missing))

        # === SUMMARY TABLE ===
        st.markdown("### Resume Match Summary")
        st.table(summary_rows)

        # === MATCHED/MISSING DETAILS FOR EACH RESUME ===
        for i, f in enumerate(resume_files):
            matched, missing = matched_missing_per_resume[i]
            st.markdown(f"#### Matched & Missing Keywords for {f.name}")
            with st.expander(f"View matched and missing keywords for {f.name}", expanded=False):
                matched_table = [{"Keyword": w, "Frequency in JD": jd_word_counts[w]} for w in sorted(matched, key=lambda x: (-jd_word_counts[x], x))]
                missing_table = [{"Keyword": w, "Frequency in JD": jd_word_counts[w]} for w in sorted(missing, key=lambda x: (-jd_word_counts[x], x))]
                st.markdown("**Matched Keywords**")
                st.table(matched_table if matched_table else [{"Keyword": "None", "Frequency in JD": "-"}])
                st.markdown("**Missing Keywords**")
                st.table(missing_table if missing_table else [{"Keyword": "None", "Frequency in JD": "-"}])

        # === KEYWORD COMPARISON MATRIX ===
        data = []
        # Sort keywords by frequency in JD, then alphabetically
        sorted_keywords = sorted(jd_keywords, key=lambda w: (-jd_word_counts[w], w))
        for keyword in sorted_keywords:
            row = {"Keyword": keyword}
            for i, counts in enumerate(resume_counts_list):
                row[resume_names[i]] = counts.get(keyword, 0)
            data.append(row)

        df = pd.DataFrame(data)
        for col in resume_names:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        st.markdown("### Keyword Comparison Matrix")
        st.dataframe(df, use_container_width=True)

# Reminder for developers/users
st.markdown("""
---
_ℹ️ To run this app: open a terminal and type:_  
`streamlit run streamlit_app.py`
""")
