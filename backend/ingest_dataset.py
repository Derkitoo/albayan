import sys
import os
import sqlite3
import urllib.request
import json
import re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(__file__), "sunnah.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table for Hadiths
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hadiths (
        hadith_id TEXT PRIMARY KEY,
        collection_id TEXT,
        collection_name TEXT,
        hadith_number INTEGER,
        chapter_title_ar TEXT,
        chapter_title_en TEXT,
        chapter_title_fr TEXT,
        arabic_text TEXT,
        english_translation TEXT,
        french_translation TEXT,
        grade TEXT,
        narrator TEXT
    )
    """)
    
    # Table for Isnad Chains
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS isnad (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hadith_id TEXT,
        step INTEGER,
        transmission TEXT,
        rijal_id TEXT,
        name_ar TEXT,
        name_en TEXT,
        role TEXT,
        city TEXT,
        grade TEXT
    )
    """)
    
    conn.commit()
    conn.close()

def download_json(url):
    print(f"Téléchargement : {url} ...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def populate_database():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Download Nawawi 40 Hadiths (Arabic, French, English)
        ara_nawawi = download_json("https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-nawawi.json")
        fra_nawawi = download_json("https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/fra-nawawi.json")
        eng_nawawi = download_json("https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/eng-nawawi.json")

        hadith_list_ara = ara_nawawi.get("hadiths", [])
        hadith_list_fra = fra_nawawi.get("hadiths", [])
        hadith_list_eng = eng_nawawi.get("hadiths", [])

        count = 0
        for i in range(len(hadith_list_ara)):
            h_ar = hadith_list_ara[i]
            h_fr = hadith_list_fra[i] if i < len(hadith_list_fra) else {}
            h_en = hadith_list_eng[i] if i < len(hadith_list_eng) else {}

            num = i + 1
            hadith_id = f"nawawi:{num}"

            ar_text = h_ar.get("text", "")
            fr_text = h_fr.get("text", "")
            en_text = h_en.get("text", "")

            narrator = "Compagnon du Prophète (رضي الله عنه)"
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
                "nawawi",
                "40 Hadiths Nawawi",
                num,
                f"الأربعون النواوية - الحديث {num}",
                f"Forty Hadith Nawawi - Hadith #{num}",
                f"Les 40 Hadiths de Nawawi - Hadith #{num}",
                ar_text,
                en_text,
                fr_text,
                "Sahih",
                narrator
            ))
            count += 1

        conn.commit()
        print(f"SUCCESS: {count} Hadiths de l'Imam an-Nawawi importés dans SQLite (sunnah.db) !")

    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    populate_database()
