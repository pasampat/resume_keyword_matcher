import streamlit as st
from io import BytesIO
from PyPDF2 import PdfReader
from text_utils import clean_text, extract_keywords, extract_nouns_verbs, match_keywords, calculate_match_percent
from stopwords import STOP_WORDS
import collections
import pandas as pd
import os

# ========== file reading helpers ==========

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
    

def read_sample_file(filepath):
    """Read a local sample text file (always as UTF-8)."""
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    if ext == ".txt":
        with open(filepath, encoding="utf-8") as f:
            return f.read()
    elif ext == ".pdf":
        pdf = PdfReader(filepath)
        return "\n".join(page.extract_text() or "" for page in pdf.pages)
    else:
        return "[Unsupported sample file type]"

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

st.subheader("Resume Keyword Matcher")

st.markdown("""
Upload a job description and 1–3 resumes (PDF or TXT).
You'll see a summary table and a side-by-side keyword matrix for comparison.
Matched/missing keywords for each resume can be viewed by expanding the details.
""")

# ====== SAMPLE DATA SETTINGS ======
SAMPLE_JOB = "test_files/job1.txt"
SAMPLE_RESUMES = [
    "test_files/resume1.pdf",
    "test_files/resume2.txt",
]

# Session state to remember sample/demo button usage
if "use_samples" not in st.session_state:
    st.session_state["use_samples"] = False

# Button for user to load sample/demo data
if st.button("Use Sample Data (for demo/testing)", help="See a demo with example files!"):
    st.session_state["use_samples"] = True

# --- DATA INPUTS: handle both sample and uploaded files ---
if st.session_state["use_samples"]:
    # Load from repo/sample files
    job_text = read_sample_file(SAMPLE_JOB)
    resume_texts = [read_sample_file(p) for p in SAMPLE_RESUMES]
    resume_labels = [os.path.basename(p) for p in SAMPLE_RESUMES]
    st.info(
        "Sample data loaded! (1 Job Description TXT + 1 PDF resume + 1 TXT resume).\n "
        "Click **Analyze** below to see a demo."
    )
else:
    # Upload widgets
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
    # For uploaded files, extract text and make labels
    job_text = read_uploaded_file(job_file) if job_file else None
    resume_texts = [read_uploaded_file(f) for f in resume_files] if resume_files else []
    resume_labels = [f.name for f in resume_files] if resume_files else []

# ====== MODE SELECTOR ======
mode = st.radio(
    "Keyword extraction mode",
    ["All words (default)", "Only nouns/verbs (recommended for most jobs)"]
)

# ====== ANALYZE BUTTON LOGIC ======
if st.button("Analyze"):
    # --- Validation ---
    if not job_text:
        st.error("Please upload a job description or use the sample data.")
    elif not resume_texts or len(resume_texts) == 0:
        st.error("Please upload at least one resume or use the sample data.")
    elif len(resume_texts) > 3:
        st.error("Please upload no more than 3 resumes.")
    else:
        # --- SHOW JOB DESCRIPTION ---
        with st.expander("Job Description", expanded=False):
            st.text(job_text if len(job_text) < 5000 else job_text[:5000] + "\n...[truncated]")

        # --- EXTRACT JD KEYWORDS ---
        jd_mode = "all" if mode.startswith("All") else "nouns_verbs"
        jd_keywords, jd_word_counts = extract_keywords_from_jd(job_text, jd_mode)

        # --- ANALYZE EACH RESUME, SHOW RESUME TEXTS ---
        summary_rows = []
        resume_counts_list = []
        matched_missing_per_resume = []

        for idx, resume_text in enumerate(resume_texts):
            # Show resume text in expander, label by file name or "Resume 1"
            label = resume_labels[idx] if idx < len(resume_labels) else f"Resume {idx+1}"
            with st.expander(f"Resume: {label}", expanded=False):
                st.text(resume_text if len(resume_text) < 5000 else resume_text[:5000] + "\n...[truncated]")
            # Analyze
            matched, missing, match_percent, resume_counts = analyze_resume(resume_text, jd_keywords)
            summary_rows.append({
                "Resume": label,
                "Match %": f"{match_percent:.1f}",
                "#Matched": len(matched),
                "#Missing": len(missing)
            })
            resume_counts_list.append(resume_counts)
            matched_missing_per_resume.append((matched, missing))

        # --- SUMMARY TABLE ---
        st.markdown("##### Resume Match Summary")
        st.table(summary_rows)

        # --- MATCHED/MISSING DETAILS FOR EACH RESUME ---
        for idx, label in enumerate(resume_labels):
            matched, missing = matched_missing_per_resume[idx]
            st.markdown(f"##### Matched & Missing Keywords for {label}")
            with st.expander(f"View matched and missing keywords for {label}", expanded=False):
                matched_table = [{"Keyword": w, "Frequency in JD": jd_word_counts[w]}
                                 for w in sorted(matched, key=lambda x: (-jd_word_counts[x], x))]
                missing_table = [{"Keyword": w, "Frequency in JD": jd_word_counts[w]}
                                 for w in sorted(missing, key=lambda x: (-jd_word_counts[x], x))]
                st.markdown("**Matched Keywords**")
                st.table(matched_table if matched_table else [{"Keyword": "None", "Frequency in JD": "-"}])
                st.markdown("**Missing Keywords**")
                st.table(missing_table if missing_table else [{"Keyword": "None", "Frequency in JD": "-"}])

        # --- KEYWORD COMPARISON MATRIX ---
        data = []
        sorted_keywords = sorted(jd_keywords, key=lambda w: (-jd_word_counts[w], w))
        for keyword in sorted_keywords:
            row = {"Keyword": keyword}
            for i, counts in enumerate(resume_counts_list):
                row[resume_labels[i]] = counts.get(keyword, 0)
            data.append(row)
        df = pd.DataFrame(data)
        for col in resume_labels:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        st.markdown("##### Keyword Comparison Matrix")
        st.dataframe(df, use_container_width=True)

# For devs/users: show reminder
st.markdown("""
---
_ℹ️ To run this app: open a terminal and type:_  
`streamlit run app.py`
""")


