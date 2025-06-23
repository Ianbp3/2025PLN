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

#Subword Analysis --------------------------------------------------------------------\

vocab = {}
for term, freq in filtered_term_freq.items():
    chars = ' '.join(list(term)) + ' </w>'
    vocab[chars] = freq

def get_stats(vocab):
    pairs = Counter()
    for word, freq in vocab.items():
        symbols = word.split()
        for i in range(len(symbols) - 1):
            pairs[(symbols[i], symbols[i+1])] += freq
    return pairs

def merge_vocab(pair, vocab):
    pattern = re.escape(' '.join(pair))
    replacement = ''.join(pair)
    new_vocab = {}
    for word in vocab:
        new_word = re.sub(rf'\b{pattern}\b', replacement, word)
        new_vocab[new_word] = vocab[word]
    return new_vocab

num_merges = 100
merges = []

for _ in range(num_merges):
    pairs = get_stats(vocab)
    if not pairs:
        break
    best = max(pairs, key=pairs.get)
    merges.append(best)
    vocab = merge_vocab(best, vocab)

def apply_bpe(word, merges):
    tokens = list(word) + ['</w>']
    merge_pairs = {pair: ''.join(pair) for pair in merges}

    while True:
        pairs = [(tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1)]
        match = None
        for pair in pairs:
            if pair in merge_pairs:
                match = pair
                break
        if not match:
            break
        i = 0
        while i < len(tokens) - 1:
            if tokens[i] == match[0] and tokens[i + 1] == match[1]:
                tokens = tokens[:i] + [match[0] + match[1]] + tokens[i + 2:]
                break
            i += 1
    return tokens[:-1]

canonical_terms = list(canonical_map.keys())

print("🧪 BPE Subword Tokens (sample canonical terms):")
for term in canonical_terms[:20]:
    print(f"{term} → {apply_bpe(term, merges)}")

#Glossary Assembly --------------------------------------------------------------------------
glossary = []

for canonical, variants in canonical_map.items():
    tokens = apply_bpe(canonical, merges)
    entry = {
        "term": canonical,
        "variants": sorted(variants),
        "tokens": tokens,
        "definition": "",
        "example": ""
    }
    glossary.append(entry)

with open("glossary.json", "w", encoding="utf-8") as f:
    json.dump(glossary, f, indent=2, ensure_ascii=False)

print(f"✅ Glossary saved with {len(glossary)} entries.")