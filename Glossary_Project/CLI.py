import json
import difflib
from Levenshtein import distance as levenshtein

with open("glossary_filled.json", "r", encoding="utf-8") as f:
    glossary_all = json.load(f)

with open("filtered_term_freq.json", "r", encoding="utf-8") as tf:
    term_freq = json.load(tf)

glossary = []
for entry in glossary_all:
    if entry["definition"].strip():
        freq = term_freq.get(entry["term"], 0)
        entry["frequency"] = freq
        glossary.append(entry)


term_map = {entry["term"]: entry for entry in glossary}
all_terms = list(term_map.keys())

def list_terms(by_freq=False):
    if by_freq:
        sorted_terms = sorted(glossary, key=lambda x: -x["frequency"])
    else:
        sorted_terms = sorted(glossary, key=lambda x: x["term"])
    for entry in sorted_terms:
        print(f"{entry['term']} ({entry['frequency']} freq, {len(entry['variants'])} variants)")

def define(term):
    entry = term_map.get(term)
    if not entry:
        match = difflib.get_close_matches(term, all_terms, n=1)
        if match:
            entry = term_map[match[0]]
            print(f"Closest match: {entry['term']}")
        else:
            print("Term not found.")
            return
    print(f"\nCanonical: {entry['term']}")
    print(f"Definition: {entry['definition']}")
    print(f"Example: {entry['example']}")
    print(f"Variants: {', '.join(entry['variants']) or 'None'}\n")

def search(term):
    best = min(all_terms, key=lambda t: levenshtein(term, t))
    print(f"Closest match: {best}")

def main():
    print("Glossary CLI — type 'help' for commands.")
    while True:
        try:
            command = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if command == "exit":
            break
        elif command == "help":
            print("Commands:\n  list\n  list freq\n  define <term>\n  search <partial_term>\n  exit")
        elif command.startswith("list"):
            list_terms(by_freq="freq" in command)
        elif command.startswith("define "):
            term = command[len("define "):].strip()
            define(term)
        elif command.startswith("search "):
            term = command[len("search "):].strip()
            search(term)
        else:
            print("Unknown command. Type 'help'.")

if __name__ == "__main__":
    main()