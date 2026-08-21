import sys
import os
import sqlite3
import urllib.request
import json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(__file__), "sunnah.db")

COLLECTIONS = [
    {
        "id": "bukhari",
        "name": "Sahih al-Bukhari",
        "ar_url": "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-bukhari.min.json",
        "fra_url": "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/fra-bukhari.min.json",
        "eng_url": "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/eng-bukhari.min.json",
        "grade": "Sahih"
    },
    {
        "id": "muslim",
        "name": "Sahih Muslim",
        "ar_url": "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-muslim.min.json",
        "fra_url": "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/fra-muslim.min.json",
        "eng_url": "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/eng-muslim.min.json",
        "grade": "Sahih"
    },
    {
        "id": "abudawud",
        "name": "Sunan Abu Dawud",
        "ar_url": "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-abudawud.min.json",
        "fra_url": None,
        "eng_url": "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/eng-abudawud.min.json",
        "grade": "Sahih / Hasan"
    },
    {
        "id": "tirmidhi",
        "name": "Jami` at-Tirmidhi",
        "ar_url": "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-tirmidhi.min.json",
        "fra_url": None,
        "eng_url": "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/eng-tirmidhi.min.json",
        "grade": "Hasan / Sahih"
    },
    {
        "id": "nasai",
        "name": "Sunan an-Nasa'i",
        "ar_url": "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-nasai.min.json",
        "fra_url": None,
        "eng_url": "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/eng-nasai.min.json",
        "grade": "Sahih"
    },
    {
        "id": "ibnmajah",
        "name": "Sunan Ibn Majah",
        "ar_url": "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-ibnmajah.min.json",
        "fra_url": None,
        "eng_url": "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/eng-ibnmajah.min.json",
        "grade": "Hasan / Sahih"
    }
]

def download_json(url):
    if not url:
        return {}
    try:
        print(f"Téléchargement : {url} ...", flush=True)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Avertissement : Impossible de charger {url} ({e})", flush=True)
        return {}

def populate_all_hadiths():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable SQLite speed optimizations
    cursor.execute("PRAGMA synchronous = OFF;")
    cursor.execute("PRAGMA journal_mode = MEMORY;")

    total_added = 0

    for col in COLLECTIONS:
        print(f"\n--- Ingestion COMPLÈTE de {col['name']} ---", flush=True)
        ara_data = download_json(col["ar_url"])
        fra_data = download_json(col["fra_url"]) if col["fra_url"] else {}
        eng_data = download_json(col["eng_url"]) if col["eng_url"] else {}

        h_ara = ara_data.get("hadiths", [])
        h_fra = fra_data.get("hadiths", [])
        h_eng = eng_data.get("hadiths", [])

        batch = []
        for i in range(len(h_ara)):
            item_ar = h_ara[i]
            item_fr = h_fra[i] if i < len(h_fra) else {}
            item_en = h_eng[i] if i < len(h_eng) else {}

            num = item_ar.get("hadithnumber", i + 1)
            hadith_id = f"{col['id']}:{num}"

            ar_text = item_ar.get("text", "")
            fr_text = item_fr.get("text", "")
            en_text = item_en.get("text", "")

            narrator = "Compagnon du Prophète (رضي الله عنهم)"
            if "عَنْ" in ar_text:
                parts = ar_text.split("قَالَ")
                narrator = parts[0].strip() if len(parts) > 1 else "Compagnon (رضي الله عنه)"

            batch.append((
                hadith_id,
                col["id"],
                col["name"],
                num,
                f"{col['name']} - الحديث {num}",
                f"{col['name']} - Hadith #{num}",
                f"{col['name']} - Hadith #{num}",
                ar_text,
                en_text,
                fr_text if fr_text else en_text,
                col["grade"],
                narrator
            ))

        cursor.executemany("""
        INSERT OR REPLACE INTO hadiths (
            hadith_id, collection_id, collection_name, hadith_number,
            chapter_title_ar, chapter_title_en, chapter_title_fr,
            arabic_text, english_translation, french_translation, grade, narrator
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, batch)

        conn.commit()
        print(f"SUCCESS: {len(batch)} Hadiths insérés pour {col['name']} !", flush=True)
        total_added += len(batch)

    print(f"\n🎉 TOTAL GÉNÉRAL INGÉRÉ : {total_added} Hadiths intégralement stockés dans la base SQLite (sunnah.db) !", flush=True)
    conn.close()

if __name__ == "__main__":
    populate_all_hadiths()
