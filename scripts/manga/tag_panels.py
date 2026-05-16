import os
import json
import time
import base64
import requests
import re
from datetime import datetime, timedelta

# ================= CONFIGURATION =================
VOLUME = "buddha_v01"
BASE_DIR = rf"data/raw/manga/panels/{VOLUME}/panels/image panels"
DICT_FILE = "data/clean_dictionary.txt" # Using the cleaned text file now
LIMIT = 50
MODEL = "llava"

EMOJIS = ["🕉️", "🧘", "🪷", "☸️", "🕯️", "🏮", "📜", "🏯", "🐘", "🌳"]
# =================================================

def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def load_clean_dictionary():
    print(f"📖 Loading legit dictionary from {DICT_FILE}...")
    try:
        with open(DICT_FILE, 'r', encoding='utf-8') as f:
            return [line.strip().lower() for line in f if line.strip()]
    except Exception as e:
        print(f"❌ Dictionary file missing! Run the cleaning script first. Error: {e}")
        return []

def tag_image_local(image_path, dictionary):
    base64_image = get_base64_image(image_path)

    # We give the model a a hint of the dictionary to guide it
    dict_sample = ", ".join(dictionary[:50])
    prompt = (
        f"Analyze this image. Use ONLY these legit English words for tags: {dict_sample}... "
        f"Return only the words separated by commas. NO Pali, NO accents, NO coordinates."
    )

    try:
        response = requests.post('http://localhost:11434/api/generate',
            json={"model": MODEL, "prompt": prompt, "images": [base64_image], "stream": False},
            timeout=300)

        if response.status_code == 200:
            raw_tags = response.json().get('response', '')
            # Clean up: only keep words found in our dictionary
            found_tags = []
            for word in re.split(r'[, \n]+', raw_tags.lower()):
                clean_word = re.sub(r'[^a-z]', '', word)
                if clean_word in dictionary:
                    found_tags.append(clean_word)
            return list(set(found_tags))
        return []
    except Exception as e:
        print(f"❌ Error tagging {image_path.name}: {e}")
        return []

def main():
    print(f"🚀 Starting Tagging for {VOLUME}...")
    dictionary = load_clean_dictionary()
    if not dictionary: return

    image_dir = Path(BASE_DIR)
    if not image_dir.exists():
        print(f"❌ Directory not found: {BASE_DIR}")
        return

    all_images = sorted(list(image_dir.glob("*.png")))
    print(f"📸 Found {len(all_images)} panels.")

    for i, img_path in enumerate(all_images[:LIMIT], 1):
        json_path = img_path.with_suffix(".json")

        # Skip if already tagged
        if json_path.exists():
            try:
                data = json.loads(json_path.read_text())
                if data.get("tags"): continue
            except: pass

        print(f"[{i}/{LIMIT}] Tagging {img_path.name}...")
        tags = tag_image_local(img_path, dictionary)

        if tags:
            emoji = EMOJIS[i % len(EMOJIS)]
            print(f"   {emoji} Tags: {', '.join(tags)}")

            # Save or update JSON
            data = {}
            if json_path.exists():
                try: data = json.loads(json_path.read_text())
                except: pass

            data["tags"] = tags
            data["tagged_at"] = datetime.now().isoformat()
            json_path.write_text(json.dumps(data, indent=2))

    print("\n✅ Tagging session complete.")

if __name__ == "__main__":
    from pathlib import Path
    main()
