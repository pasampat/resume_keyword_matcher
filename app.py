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


def analyze_and_render(job_text, resume_texts, resume_labels, mode_label):
    """
    Run the full keyword analysis pipeline and render results in the Streamlit app.

    This function takes the job description text and one or more resumes,
    extracts keywords, and displays:
      - The job description text (inside an expander).
      - A summary table showing match %, number of matched keywords,
        and number of missing keywords for each resume.
      - Expandable sections for each resume with detailed lists of
        matched and missing keywords (with frequencies from the JD).
      - A keyword comparison matrix showing keyword counts across resumes.

    Parameters
    ----------
    job_text : str
        The text of the job description (raw).
    resume_texts : list[str]
        A list of resume texts (already extracted from PDF/TXT).
    resume_labels : list[str]
        Display labels for each resume (usually filenames).
    mode_label : str
        The selected keyword extraction mode label ("All words ..." or "Only nouns/verbs ...").

    """
   # --- SHOW JOB DESCRIPTION ---
    with st.expander("Job Description", expanded=False):
        st.text(job_text if len(job_text) < 5000 else job_text[:5000] + "\n...[truncated]")

    # --- EXTRACT JD KEYWORDS ---
    jd_mode = "all" if mode_label.startswith("All") else "nouns_verbs"
    jd_keywords, jd_word_counts = extract_keywords_from_jd(job_text, jd_mode)

    # --- ANALYZE EACH RESUME, SHOW RESUME TEXTS ---
    summary_rows = []
    resume_counts_list = []
    matched_missing_per_resume = []

    for idx, resume_text in enumerate(resume_texts):
        label = resume_labels[idx] if idx < len(resume_labels) else f"Resume {idx+1}"
        # Keep full resume text tucked away
        with st.expander(f"Resume: {label}", expanded=False):
            st.text(resume_text if len(resume_text) < 5000 else resume_text[:5000] + "\n...[truncated]")

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
    st.markdown("##### ✅ Resume Match Summary")
    st.table(summary_rows)

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

    st.markdown("##### 📊 Keyword Comparison Matrix")
    st.dataframe(
        df,
        use_container_width=True,
        height=min(420, 56 + 28 * min(len(df), 10)),  # keep compact; adjust as you like
    )

    # --- QUICK INSIGHT: Top gaps across resumes ---
    all_missing_counts = collections.Counter()
    for matched, missing in matched_missing_per_resume:
        all_missing_counts.update(missing)

    top_gaps = sorted(
        all_missing_counts,
        key=lambda w: (-all_missing_counts[w], -jd_word_counts[w], w)
    )[:8]

    if top_gaps:
        st.markdown("##### 🔎 Top gaps across resumes")
        st.table([
            {"Keyword": w, "#Resumes without keyword": all_missing_counts[w], "Freq in Job Description": jd_word_counts[w]}
            for w in top_gaps
        ])

   


# ========== STREAMLIT APP UI ==========

st.markdown(
    """
    <div style="text-align:center; margin-top: -10px;">
      <h4>Resume Keyword Matcher</h2>
      <p style="font-size:16px; margin-bottom: 8px;">
        <b>Check how well your resume matches a job description using keyword comparison.</b>
      </p>
      <div style="display:inline-block; text-align:left; font-size:15px; line-height:1.5;">
        <ul style="margin: 0; padding-left: 18px;">
          <li>✅ <b>Match %</b> — quick compatibility score</li>
          <li>📊 <b>Keyword matrix</b> — side-by-side frequency comparison</li>
          <li>🔎 <b> Top gaps — what resumes miss most often</li>
        </ul>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ====== SAMPLE DATA SETTINGS (robust paths) ======
from pathlib import Path
BASE = Path(__file__).parent
SAMPLE_JOB = str(BASE / "test_files/job1.txt")
SAMPLE_RESUMES = [
    str(BASE / "test_files/resume1.pdf"),
    str(BASE / "test_files/resume3.txt"),
]

# ====== SESSION STATE ======
# Tracks whether we've already shown the auto demo this session
if "auto_demo_ran" not in st.session_state:
    st.session_state["auto_demo_ran"] = False

# (Optional legacy flag you had; safe to keep but unused by the new flow)
if "use_samples" not in st.session_state:
    st.session_state["use_samples"] = False

# ====== KEYWORD MODE (simplified label + tooltip) ======
mode = st.radio(
    "How keywords are chosen",
    ["All words (default)", "Only nouns/verbs (recommended)"],
    help="Choose whether to consider all words or only nouns/verbs (often better for job relevance)."
)

# ====== INSTANT DEMO ON FIRST LOAD ======
if not st.session_state["auto_demo_ran"]:
    # Load samples and render immediately so viewers see results without any clicks
    job_text_demo = read_sample_file(SAMPLE_JOB)
    resume_texts_demo = [read_sample_file(p) for p in SAMPLE_RESUMES]
    resume_labels_demo = [os.path.basename(p) for p in SAMPLE_RESUMES]

    st.success("Showing demo with sample data.")
    analyze_and_render(job_text_demo, resume_texts_demo, resume_labels_demo, mode)
    st.session_state["auto_demo_ran"] = True
else:
    # Let users quickly re-run the demo after trying uploads or changing mode
    if st.button("Replay Demo with Sample Data"):
        job_text_demo = read_sample_file(SAMPLE_JOB)
        resume_texts_demo = [read_sample_file(p) for p in SAMPLE_RESUMES]
        resume_labels_demo = [os.path.basename(p) for p in SAMPLE_RESUMES]
        analyze_and_render(job_text_demo, resume_texts_demo, resume_labels_demo, mode)

# ====== USER UPLOADS (de-emphasized in an expander) ======
with st.expander("🔽 Try with your own files"):
    job_file = st.file_uploader(
        "Upload Job Description",
        type=["txt", "pdf"],
        help="Accepted formats: .txt, .pdf",
        key="jobdesc",
    )
    resume_files = st.file_uploader(
        "Upload 1–3 Resumes",
        type=["txt", "pdf"],
        accept_multiple_files=True,
        help="Accepted formats: .txt, .pdf",
        key="resumes",
    )

    # Extract text + labels from uploads
    job_text = read_uploaded_file(job_file) if job_file else None
    resume_texts = [read_uploaded_file(f) for f in resume_files] if resume_files else []
    resume_labels = [f.name for f in resume_files] if resume_files else []

    # Run analysis on user data
    if st.button("Analyze"):
        if not job_text:
            st.error("Please upload a job description.")
        elif not resume_texts:
            st.error("Please upload at least one resume.")
        elif len(resume_texts) > 3:
            st.error("Please upload no more than 3 resumes.")
        else:
            analyze_and_render(job_text, resume_texts, resume_labels, mode)



# For devs/users: show reminder
st.markdown("""
---
_ℹ️ To run this app: open a terminal and type:_  
`streamlit run app.py`
""")


