import re
from collections import Counter
import os
import nltk
from nltk.corpus import stopwords
from rapidfuzz.distance import Levenshtein
import json
from collections import defaultdict

#Term Extraction -----------------------------------------------------------------------
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

corpus_folder = './Corpus'

camel_case_pattern = re.compile(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b')
snake_case_pattern = re.compile(r'\b[a-z]+(?:_[a-z]+)+\b')
abbreviation_pattern = re.compile(r'\b[A-Z]{2,}\b')
multiword_pattern = re.compile(r'\b(?:[a-z]{3,}\s+){1,3}[a-z]{3,}\b', re.IGNORECASE)
single_word_pattern = re.compile(r'\b[a-zA-Z_]{3,}\b')

all_terms = []

for filename in os.listdir(corpus_folder):
    if filename.endswith('.txt'):
        with open(os.path.join(corpus_folder, filename), 'r', encoding='utf-8') as file:
            text = file.read()

            all_terms.extend(camel_case_pattern.findall(text))
            all_terms.extend(snake_case_pattern.findall(text))
            all_terms.extend(abbreviation_pattern.findall(text))
            all_terms.extend(multiword_pattern.findall(text))
            all_terms.extend(single_word_pattern.findall(text))

normalized_terms = [term.lower() for term in all_terms]

filtered_terms = [
    term for term in normalized_terms
    if term not in stop_words and len(term) > 2 and not term.isdigit()
]

term_freq = Counter(filtered_terms)

min_freq = 2
filtered_term_freq = {term: freq for term, freq in term_freq.items() if freq >= min_freq}

print("Most common terms:")
for term, freq in term_freq.most_common(20):
    print(f"{term}: {freq}")

unique_terms = list(term_freq.keys())
print("\nSample output:")
print(unique_terms[:20])

