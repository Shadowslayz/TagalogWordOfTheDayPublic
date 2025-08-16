import json
import os

# JSON file location
JSON_FILE = "TagalogWordOfTheDay/tagalog_words.json"

# New words to add
NEW_WORDS = [
]





def load_existing_words():
    """Load existing words from the JSON file."""
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as file:
            try:
                return json.load(file)  # Load existing data
            except json.JSONDecodeError:
                return []  # Return an empty list if file is corrupted
    return []  # Return an empty list if file doesn't exist

def save_words_to_json(words):
    """Save words back to the JSON file."""
    with open(JSON_FILE, "w", encoding="utf-8") as file:
        json.dump(words, file, indent=4, ensure_ascii=False)
    print(f"✅ Updated {JSON_FILE} with new words!")

def add_new_words():
    """Add new words to the JSON file without duplicates."""
    words = load_existing_words()
    existing_words = {word["word"].lower() for word in words}  # Set for fast lookup

    for new_word in NEW_WORDS:
        if new_word["word"].lower() not in existing_words:  # Avoid duplicates
            words.append(new_word)
            print(f"➕ Added: {new_word['word']}")
        else:
            print(f"⚠️ Skipped (already exists): {new_word['word']}")

    save_words_to_json(words)

# Run the function to add new words
add_new_words()
