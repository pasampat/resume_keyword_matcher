import string
import collections
import csv
from PyPDF2 import PdfReader  # Install with: pip install PyPDF2
import nltk

def clean_text(raw_text, stop_words):
    """
    Lowercases, removes punctuation, splits, and removes stop words.
    Returns a list of cleaned words.
    """
    text = raw_text.lower()
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)
    words = text.split()
    cleaned_words = [word for word in words if word not in stop_words and word.isalpha()]
    return cleaned_words

def extract_keywords(cleaned_words):
    """
    Returns a set of unique keywords from the cleaned job description words.
    """
    return set(cleaned_words)

def match_keywords(job_keywords, resume_words):
    """
    Compares job keywords to resume words.
    Returns two sets: matched keywords and missing keywords.
    """
    resume_words_set = set(resume_words)
    matched = job_keywords & resume_words_set
    missing = job_keywords - resume_words_set
    return matched, missing

def calculate_match_percent(matched, total):
    """
    Returns the match percent as a float (0-100).
    """
    if total == 0:
        return 0.0
    return 100 * len(matched) / total

def extract_nouns_verbs(words):
    """
    Uses NLTK POS tagging to return only nouns and verbs from a word list.
    """
    pos_tags = nltk.pos_tag(words)
    allowed = {'NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'}
    filtered = [word for word, tag in pos_tags if tag in allowed]
    return filtered   