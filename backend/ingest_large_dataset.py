import sys
import os
import sqlite3
import urllib.request
import json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(__file__), "sunnah.db")

def download_json(url):
    print(f"Téléchargement : {url} ...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def populate_large_dataset():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Download Sahih al-Bukhari (Arabic, French, English)
        print("--- Ingestion du recueil Sahih al-Bukhari ---")
        ara_bukhari = download_json("https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-bukhari.min.json")
        fra_bukhari = download_json("https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/fra-bukhari.min.json")
        eng_bukhari = download_json("https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/eng-bukhari.min.json")

        h_ara = ara_bukhari.get("hadiths", [])
        h_fra = fra_bukhari.get("hadiths", [])
        h_eng = eng_bukhari.get("hadiths", [])

        count = 0
        limit = min(len(h_ara), 300)  # Ingest first 300 Sahih al-Bukhari Hadiths for high speed
        for i in range(limit):
            item_ar = h_ara[i]
            item_fr = h_fra[i] if i < len(h_fra) else {}
            item_en = h_eng[i] if i < len(h_eng) else {}

            num = i + 1
            hadith_id = f"bukhari:{num}"

            ar_text = item_ar.get("text", "")
            fr_text = item_fr.get("text", "")
            en_text = item_en.get("text", "")

            narrator = "Compagnon du Prophète (رضي الله عنهم)"
            if "عَنْ" in ar_text:
                parts = ar_text.split("قَالَ")
                narrator = parts[0].strip() if len(parts) > 1 else "Compagnon (رضي الله عنه)"

            cursor.execute("""
            INSERT OR REPLACE INTO hadiths (
                hadith_id, collection_id, collection_name, hadith_number,
                chapter_title_ar, chapter_title_en, chapter_title_fr,
                arabic_text, english_translation, french_translation, grade, narrator
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                hadith_id,
                "bukhari",
                "Sahih al-Bukhari",
                num,
                f"صحيح البخاري - الحديث {num}",
                f"Sahih al-Bukhari - Hadith #{num}",
                f"Sahih al-Bukhari - Hadith #{num}",
                ar_text,
                en_text,
                fr_text,
                "Sahih",
                narrator
            ))
            count += 1

        conn.commit()
        print(f"SUCCESS: {count} Hadiths du recueil Sahih al-Bukhari importés avec succès dans SQLite (sunnah.db) !")

    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    populate_large_dataset()
