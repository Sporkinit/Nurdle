import requests
import time
import json
import re
import os

# Configuration
WORDLIST_PATH = r"D:\Nurdle\wordlist.txt"
OUTPUT_PATH = r"D:\Nurdle\word_definitions.json"
API_KEY = "9fd56fa1-743f-45c4-be6e-bfb3554e256a"
API_URL = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/"

def get_mw_definition(word):
    url = f"{API_URL}{word.lower()}?key={API_KEY}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            # MW API returns a list of dictionaries for valid words
            if data and isinstance(data[0], dict):
                definitions = data[0].get('shortdef', [])
                if definitions:
                    # Select the first definition
                    raw_def = definitions[0]
                    
                    # 1. Redact the exact word using word boundaries \b
                    pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
                    clean_def = pattern.sub("_____", raw_def).strip()
                    
                    # 2. Redact the first 4 letters (root check) to catch "ACTS" or "ACTING"
                    root = word[:4]
                    root_pattern = re.compile(re.escape(root), re.IGNORECASE)
                    clean_def = root_pattern.sub("_____", clean_def)
                    
                    # Capitalize first letter
                    return clean_def[0].upper() + clean_def[1:] if clean_def else None
            
        return None
    except Exception as e:
        print(f"Error connecting for {word}: {e}")
        return None

def main():
    if not os.path.exists(WORDLIST_PATH):
        print(f"Error: {WORDLIST_PATH} not found.")
        return

    with open(WORDLIST_PATH, 'r') as f:
        all_words = [line.strip().upper() for line in f if line.strip()]

    print(f"Total words: {len(all_words)}. Writing to {OUTPUT_PATH} live...")
    
    # Initialize the file as a JSON array
    with open(OUTPUT_PATH, 'w') as f:
        f.write("[\n")

    success_count = 0

    for i, word in enumerate(all_words):
        definition = get_mw_definition(word)
        
        if definition:
            entry = {"word": word, "definition": definition}
            
            # Write to file immediately
            with open(OUTPUT_PATH, 'a') as f:
                if success_count > 0:
                    f.write(",\n")
                json.dump(entry, f, indent=2)
            
            success_count += 1
        
        # Progress update
        if (i + 1) % 10 == 0:
            print(f"Checked: {i + 1}/{len(all_words)} | Found: {success_count}")

        # MW API limits are generous, but 0.1s prevents hitting them too fast
        time.sleep(0.1)

    # Close the JSON array
    with open(OUTPUT_PATH, 'a') as f:
        f.write("\n]")

    print(f"\nDone! Processed {len(all_words)} words. Saved {success_count} definitions.")

if __name__ == "__main__":
    main()
