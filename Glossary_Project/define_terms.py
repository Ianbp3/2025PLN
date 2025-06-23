import json
import requests
import time
import re

with open("glossary.json", "r", encoding="utf-8") as f:
    glossary = json.load(f)

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3"

def query_ollama(term, variants):
    prompt = (
        f"You are an expert glossary assistant. Given the glossary term \"{term}\" and a list of possible variants {variants}, "
        "identify only the variants that are legitimate spelling variants, inflections, or abbreviations of the term. "
        "Then generate a concise definition (maximum 40 words) and a short example sentence (maximum 25 words). "
        "Do not use markdown formatting or code blocks. Only return raw JSON."
        "Respond ONLY in valid JSON format:\n"
        '{\n'
        '  "definition": "<definition here>",\n'
        '  "example": "<example sentence here>",\n'
        '  "real_variants": ["..."]\n'
        '}\n'
        f'Term: "{term}".'
    )

    response = requests.post(OLLAMA_URL, json={
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    })

    if response.status_code == 200:
        try:
            data = response.json()["response"].strip()
            if data.startswith("```json") or data.startswith("```"):
                data = data.strip("`")
                data = re.sub(r"^json\s*", "", data, flags=re.IGNORECASE).strip()
            if not data:
                print(f"⚠️ Empty response for term '{term}'")
                return "", "", []
            print(f"📥 Raw response for '{term}': {data}")
            result = json.loads(data)

            definition = result.get("definition", "")
            example = result.get("example", "")
            real_variants = result.get("real_variants", [])

            return definition, example, real_variants

        except Exception as e:
            print(f"⚠️ Failed to parse LLM response for term '{term}': {e}")
            return "", "", []
    else:
        print(f"❌ Error querying Ollama: {response.status_code}")
        return "", "", []

for entry in glossary:
    if entry["definition"] and entry["example"]:
        continue

    term = entry["term"]
    variants = entry["variants"]
    definition, example, real_variants = query_ollama(term, variants)

    entry["definition"] = definition
    entry["example"] = example
    entry["variants"] = real_variants

    print(f"✅ {term} — updated with {len(real_variants)} variants.")
    time.sleep(1)

with open("glossary_filled.json", "w", encoding="utf-8") as f:
    json.dump(glossary, f, indent=2, ensure_ascii=False)

print("✅ Glossary enrichment complete.")
