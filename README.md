# Resume Keyword Matcher

*A Python tool to check how well your resume matches a job description using keyword comparison.*
---

🎯 **Try it live:** [Resume Keyword Matcher](https://resumekeywordmatcher-ck8izh5i2kdeatkwxjjvb2.streamlit.app/)
<p align="left">
  <img src="images/resume-keyword-matcher-demo.png" alt="Resume Keyword Matcher Demo" width="450"/>
</p>

---

## 📖 Project Overview

Landing an interview often depends on using the right keywords.  
The **Resume Keyword Matcher** takes the guesswork out of resume tailoring:

- **Upload a job description** and up to **three resumes** (PDF or TXT).  
- Instantly see **keyword matches**, **missing terms**, and an **overall match percentage**.  
- Explore a **keyword frequency matrix** to compare resumes side by side.  

This tool makes it easy for job seekers to **optimize resumes for specific postings** and improve their chances of getting noticed.



## Setup

1. Create and activate virtual environment:
    python -m venv venv
    # On Windows: .venv\Scripts\activate
    # On Mac/Linux: source .venv/bin/activate

2. Install dependencies:
    pip install -r requirements.txt

3. Run the app:
    python main.py

## Inputs
- Accepts .txt and .pdf files for resumes and job postings.

## Output
- Shows match percent and missing keywords in the terminal.
- Optionally outputs results to .txt or .csv.
