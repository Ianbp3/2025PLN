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

#Variant Consolidation -----------------------------------------------------------------------

terms = list(filtered_term_freq.keys())
visited = set()
clusters = []

for i, term in enumerate(terms):
    if term in visited:
        continue
    cluster = [term]
    visited.add(term)
    for j in range(i + 1, len(terms)):
        other = terms[j]
        if other not in visited and Levenshtein.distance(term, other) <= 3:
            cluster.append(other)
            visited.add(other)
    clusters.append(cluster)

canonical_map = {}
for cluster in clusters:
    canonical = max(cluster, key=lambda x: filtered_term_freq.get(x, 0))
    canonical_map[canonical] = sorted(set(cluster) - {canonical})

for canonical, variants in list(canonical_map.items())[:5]:
    print(f"Canonical: '{canonical}'")
    print(f"Variants: {variants}\n")

