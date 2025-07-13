# main.py
import os
import re
import string
import collections
import csv
from PyPDF2 import PdfReader  # Install with: pip install PyPDF2

STOP_WORDS = [
    'the', 'and', 'is', 'in', 'to', 'of', 'for', 'with', 'on', 'a', 'an',
    'by', 'at', 'as', 'it', 'this', 'that', 'from', 'or', 'be', 'are',
    'was', 'were', 'has', 'have', 'had', 'but', 'not', 'your', 'you', 'our',
    'we', 'they', 'he', 'she', 'him', 'her', 'his', 'their', 'will', 'can',
    'if', 'about', 'which', 'more', 'also', 'so', 'than', 'other', 'when'
    # ...expand as needed
]
