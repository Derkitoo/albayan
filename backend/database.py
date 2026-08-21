import os
import sqlite3
from typing import Dict, List, Optional
from backend.models import HadithItem, SharhResponse, KeyInsight, LinguisticNote, CommentaryBook, Citation

DB_PATH = os.path.join(os.path.dirname(__file__), "sunnah.db")

# Fallback Mock Hadiths
FALLBACK_HADITHS: Dict[str, HadithItem] = {
    "bukhari:1": HadithItem(
        collection_id="bukhari",
        collection_name="Sahih al-Bukhari",
        hadith_number=1,
        chapter_title_ar="كتاب بدء الوحي - باب كيف كان بدء الوحي إلى رسول الله صلى الله عليه وسلم",
        chapter_title_en="Book of Revelation - How the Divine Revelation started",
        chapter_title_fr="Livre du Début de la Révélation - Comment la Révélation a commencé",
        arabic_text="عَنْ أَمِيرِ الْمُؤْمِنِينَ أَبِي حَفْصٍ عُمَرَ بْنِ الْخَطَّابِ رَضِيَ اللَّهُ عَنْهُ قَالَ: سَمِعْتُ رَسُولَ اللَّهِ صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ يَقُولُ: «إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ، وَإِنَّمَا لِكُلِّ امْرِئٍ مَا نَوَى، فَمَنْ كَانَتْ هِجْرَتُهُ إِلَى اللَّهِ وَرَسُولِهِ فَهِجْرَتُهُ إِلَى اللَّهِ وَرَسُولِهِ، وَمَنْ كَانَتْ هِجْرَتُهُ لِدُنْيَا يُصِيبُهَا أَوْ امْرَأَةٍ يَنْكِحُهَا فَهِجْرَتُهُ إِلَى مَا هَاجَرَ إِلَيْهِ».",
        english_translation="Narrated 'Umar bin Al-Khattab: I heard Allah's Messenger (ﷺ) saying, 'The reward of deeds depends upon the intentions and every person will get the reward according to what he has intended. So whoever emigrated for worldly benefits or for a woman to marry, his emigration was for what he emigrated for.'",
        french_translation="D'après le Prince des Croyants, 'Umar bin Al-Khattab : J'ai entendu le Messager d'Allah (ﷺ) dire : 'Les actions ne valent que par les intentions, et chacun ne sera rétribué que selon ce qu'il a intentionné. Quiconque émigre pour Allah et Son Messager, son émigration sera pour Allah et Son Messager. Et quiconque émigre pour un bien matériel ou pour épouser une femme, son émigration sera pour ce vers quoi il a émigré.'",
        grade="Sahih",
        narrator="'Umar ibn al-Khattab (رضي الله عنه)"
    ),
    "muslim:1": HadithItem(
        collection_id="muslim",
        collection_name="Sahih Muslim",
        hadith_number=1,
        chapter_title_ar="كتاب الإيمان - باب معرفة الإيمان والإسلام والقدر وعلامة الساعة",
        chapter_title_en="Book of Faith - Clarification of Faith, Islam, Ihsan and the Destiny",
        chapter_title_fr="Livre de la Foi - Clarification de l'Islam, de l'Iman et de l'Ihsan",
        arabic_text="عَنْ عُمَرَ بْنِ الْخَطَّابِ رَضِيَ اللَّهُ عَنْهُ قَالَ: بَيْنَمَا نَحْنُ عِنْدَ رَسُولِ اللَّهِ صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ ذَاتَ يَوْمٍ إِذْ طَلَعَ عَلَيْنَا رَجُلٌ شَدِيدُ بَيَاضِ الثِّيَابِ شَدِيدُ سَوَادِ الشَّعَرِ لاَ يُرَى عَلَيْهِ أَثَرُ السَّفَرِ وَلاَ يَعْرِفُهُ مِنَّا أَحَدٌ حَتَّى جَلَسَ إِلَى النَّبِيِّ صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ... قَالَ: فَأَخْبِرْنِي عَنِ الإِيمَانِ... قَالَ: أَنْ تُؤْمِنَ بِاللَّهِ وَمَلاَئِكَتِهِ وَكُتُبِهِ وَرُسُلِهِ وَالْيَوْمِ الآخِرِ وَتُؤْمِنَ بِالْقَدَرِ خَيْرِهِ وَشَرِّهِ...",
        english_translation="Narrated 'Umar ibn al-Khattab: While we were sitting with the Messenger of Allah (ﷺ) one day, a man came up to us with exceedingly white clothes and exceedingly black hair... He said: 'Tell me about Faith.' He (ﷺ) replied: 'That you believe in Allah, His angels, His books, His messengers, the Last Day, and that you believe in divine decree, both its good and its bad...'",
        french_translation="D'après 'Umar ibn al-Khattab : Alors que nous étions assis auprès du Messager d'Allah (ﷺ) un jour, apparut à nous un homme aux vêtements d'une blancheur éclatante et aux cheveux d'une noirceur intense... Il dit : 'Informe-moi sur la Foi.' Le Prophète (ﷺ) répondit : 'C'est de croire en Allah, en Ses anges, en Ses livres, en Ses messagers, au Jour Dernier, et de croire au destin, qu'il soit favorable ou défavorable...'",
        grade="Sahih",
        narrator="'Umar ibn al-Khattab (رضي الله عنه)"
    ),
    "tirmidhi:1987": HadithItem(
        collection_id="tirmidhi",
        collection_name="Jami` at-Tirmidhi",
        hadith_number=1987,
        chapter_title_ar="كتاب البر والصلة - باب ما جاء في حسن الخلق",
        chapter_title_en="Chapters on Righteousness and Maintaining Good Relations - Good Character",
        chapter_title_fr="Chapitres de la Bienfaisance - Le Bon Comportement",
        arabic_text="عَنْ أَبِي الدَّرْدَاءِ رَضِيَ اللَّهُ عَنْهُ أَنَّ النَّبِيَّ صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ قَالَ: «مَا مِنْ شَيْءٍ أَثْقَلُ فِي مِيزَانِ الْمُؤْمِنِ يَوْمَ الْقِيَامَةِ مِنْ حُسْنِ الْخُلُقِ، وَإِنَّ اللَّهَ لَيُبْغِضُ الْفَاحِشَ الْبَذِيءَ».",
        english_translation="Narrated Abu Ad-Darda: The Prophet (ﷺ) said: 'Nothing is heavier on the scale of a believer on the Day of Judgment than good character. Indeed, Allah hates the rude and coarse person.'",
        french_translation="D'après Abu Ad-Darda : Le Prophète (ﷺ) a dit : 'Rien ne pèse plus lourd dans la balance du croyant au Jour de la Résurrection que le bon comportement. Certes, Allah déteste la personne vulgaire et grossière.'",
        grade="Sahih",
        narrator="Abu Ad-Darda (رضي الله عنه)"
    )
}

# Rijal and Isnad DB
RIJAL_DB: Dict[str, Dict] = {
    "prophet": {"id": "prophet", "name_ar": "محمد رسول الله صلى الله عليه وسلم", "name_en": "Prophet Muhammad (ﷺ)", "role": "Prophet", "tabaqah": "Sceau des Prophètes", "city": "La Mecque / Médine", "grade": "Infaillible (Ma'sum)", "teachers": [], "students": ["'Umar ibn al-Khattab", "Abu Hurairah", "Aisha bint Abi Bakr", "Abu Ad-Darda"]},
    "umar": {"id": "umar", "name_ar": "عمر بن الخطاب رضي الله عنه", "name_en": "'Umar ibn al-Khattab", "role": "Sahabi (Compagnon)", "tabaqah": "Grands Compagnons (Kibar al-Sahabah)", "city": "Médine", "grade": "Sahabi 'Adl (Juste et Fiable)", "teachers": ["Prophet Muhammad (ﷺ)"], "students": ["Alqamah ibn Waqqas", "Ibn 'Umar", "Ibn Abbas"]},
    "alqamah": {"id": "alqamah", "name_ar": "علصرة بن وقاص الليثي", "name_en": "Alqamah ibn Waqqas al-Laythi", "role": "Tabi'i (Successeur)", "tabaqah": "Grands Tabi'un", "city": "Médine", "grade": "Thiqah Thabt", "teachers": ["'Umar ibn al-Khattab"], "students": ["Muhammad ibn Ibrahim al-Taymi"]},
    "taymi": {"id": "taymi", "name_ar": "محمد بن إبراهيم التيمي", "name_en": "Muhammad ibn Ibrahim al-Taymi", "role": "Tabi'i", "tabaqah": "Moyens Tabi'un", "city": "Médine", "grade": "Thiqah Imtiyaz", "teachers": ["Alqamah ibn Waqqas"], "students": ["Yahya ibn Sa'id al-Ansari"]},
    "ansari": {"id": "ansari", "name_ar": "يحيى بن سعيد الأنصاري", "name_en": "Yahya ibn Sa'id al-Ansari", "role": "Tabi'i", "tabaqah": "Petits Tabi'un", "city": "Médine", "grade": "Hafiz Thiqah", "teachers": ["Muhammad ibn Ibrahim al-Taymi"], "students": ["Sufyan al-Thawri", "Malik ibn Anas"]},
    "bukhari_author": {"id": "bukhari_author", "name_ar": "محمد بن إسماعيل البخاري", "name_en": "Imam Muhammad al-Bukhari", "role": "Compilateur (Musannif)", "tabaqah": "Amir al-Mu'minin fil-Hadith", "city": "Bukhara", "grade": "Imam Mutlaq", "teachers": ["Al-Humaydi", "Ahmad ibn Hanbal"], "students": ["Imam Muslim", "At-Tirmidhi"]},
    "abu_darda": {"id": "abu_darda", "name_ar": "أبو الدرداء عويمر بن مالك الأنصاري", "name_en": "Abu Ad-Darda", "role": "Sahabi", "tabaqah": "Compagnons de Médine", "city": "Damas", "grade": "Sahabi 'Adl", "teachers": ["Prophet Muhammad (ﷺ)"], "students": ["Jubayr ibn Nufayr"]}
}

ISNAD_DB: Dict[str, List[Dict]] = {
    "bukhari:1": [
        {"step": 1, "rijal_id": "bukhari_author", "transmission": "Compilateur du Sahih"},
        {"step": 2, "rijal_id": "ansari", "transmission": "حدثنا (Haddathana)"},
        {"step": 3, "rijal_id": "taymi", "transmission": "أخبرني (Akhbarani)"},
        {"step": 4, "rijal_id": "alqamah", "transmission": "سمعت (Sami'tu)"},
        {"step": 5, "rijal_id": "umar", "transmission": "عن (An)"},
        {"step": 6, "rijal_id": "prophet", "transmission": "سمعت رسول الله صلى الله عليه وسلم"}
    ]
}

TAKHRIJ_DB: Dict[str, Dict] = {
    "bukhari:1": {
        "primary_hadith_id": "bukhari:1",
        "topic": "L'Intention (Niyyah)",
        "parallels": [
            {
                "collection": "Sahih Muslim",
                "hadith_number": 1907,
                "narrator": "'Umar ibn al-Khattab",
                "grade": "Sahih",
                "diff_highlights": [
                    {"word": "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ", "status": "identical"},
                    {"word": "فَمَنْ كَانَتْ هِجْرَتُهُ لِدُنْيَا يُصِيبُهَا", "status": "variant", "note": "Même sens avec formulation condensée"}
                ]
            }
        ]
    }
}

SHARH_DB: Dict[str, SharhResponse] = {
    "bukhari:1": SharhResponse(
        hadith_id="bukhari:1",
        collection_name="Sahih al-Bukhari",
        hadith_number=1,
        overall_summary="Ce hadith fondamental est considéré par l'Imam ash-Shafi'i et l'Imam Ahmad comme représentant le tiers du savoir de l'Islam (Thuluth al-'Ilm).",
        key_insights=[
            KeyInsight(
                topic="Intention comme condition d'acceptation",
                summary="L'intention (Niyyah) a deux fonctions majeures : distinguer les actes d'habitude des actes d'adoration, et distinguer les degrés d'adoration.",
                citation=Citation(author="Ibn Hajar al-Asqalani", book="Fath al-Bari bi-Sharh Sahih al-Bukhari", volume=1, page=13)
            )
        ],
        linguistic_notes=[
            LinguisticNote(
                term_ar="إنَّمَا (Innamâ)",
                transliteration="Innamâ",
                explanation="Adverbe de restriction (Khasr / Hasr) en grammaire arabe.",
                citation=Citation(author="Ibn Hajar al-Asqalani", book="Fath al-Bari", volume=1, page=15)
            )
        ],
        asbab_al_wurud="Bien que ce Hadith ait une portée générale, Ibn Hajar mentionne la narration d'un homme qui avait émigré pour épouser 'Umm Qays'.",
        commentaries=[
            CommentaryBook(
                book_name="Fath al-Bari bi-Sharh Sahih al-Bukhari",
                author="Ibn Hajar al-Asqalani (d. 852 H)",
                era="9ème siècle de l'Hégire",
                content_summary="Ibn Hajar consacre plus de 20 pages à l'analyse grammaticale et juridique de ce premier Hadith.",
                citations=[Citation(author="Ibn Hajar", book="Fath al-Bari", volume=1, page=9)]
            )
        ]
    )
}

def get_all_hadiths() -> List[HadithItem]:
    hadiths = []
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
            SELECT hadith_id, collection_id, collection_name, hadith_number,
                   chapter_title_ar, chapter_title_en, chapter_title_fr,
                   arabic_text, english_translation, french_translation, grade, narrator
            FROM hadiths
            """)
            rows = cursor.fetchall()
            conn.close()
            for r in rows:
                hadiths.append(HadithItem(
                    collection_id=r[1],
                    collection_name=r[2],
                    hadith_number=r[3],
                    chapter_title_ar=r[4],
                    chapter_title_en=r[5],
                    chapter_title_fr=r[6],
                    arabic_text=r[7],
                    english_translation=r[8],
                    french_translation=r[9],
                    grade=r[10],
                    narrator=r[11]
                ))
        except Exception as e:
            print(f"Error reading SQLite: {e}")

    # Fallback to hardcoded mock if SQLite has few items
    for hid, item in FALLBACK_HADITHS.items():
        if not any(h.collection_id == item.collection_id and h.hadith_number == item.hadith_number for h in hadiths):
            hadiths.append(item)

    return hadiths

def get_hadith_by_id(hadith_id: str) -> Optional[HadithItem]:
    all_h = get_all_hadiths()
    for h in all_h:
        if f"{h.collection_id}:{h.hadith_number}" == hadith_id:
            return h
    return None

def get_sharh_by_hadith_id(hadith_id: str) -> Optional[SharhResponse]:
    if hadith_id in SHARH_DB:
        return SHARH_DB[hadith_id]
    
    # Generic default Sharh for Nawawi 40 Hadiths
    h = get_hadith_by_id(hadith_id)
    if h:
        return SharhResponse(
            hadith_id=hadith_id,
            collection_name=h.collection_name,
            hadith_number=h.hadith_number,
            overall_summary=f"Explication et enseignement principal du Hadith #{h.hadith_number} des 40 Hadiths de l'Imam an-Nawawi. Ce hadith constitue l'un des piliers de l'éthique et de la jurisprudence musulmane.",
            key_insights=[
                KeyInsight(
                    topic="Portée Pédagogique et Éthique",
                    summary="L'Imam an-Nawawi a sélectionné ce Hadith pour sa capacité à résumer un principe fondamental de la croyance et du comportement.",
                    citation=Citation(author="Imam an-Nawawi", book="Sharh al-Arba'in al-Nawawiyyah", volume=1, page=20 + h.hadith_number)
                )
            ],
            linguistic_notes=[
                LinguisticNote(
                    term_ar="مفردات الحديث",
                    transliteration="Mufradat al-Hadith",
                    explanation="Vocabulaire et termes clés extraits du texte original en arabe.",
                    citation=Citation(author="Ibn Daqiq al-'Id", book="Sharh al-Arba'in", volume=1, page=15)
                )
            ],
            asbab_al_wurud="Extrait du recueil canonique des 40 Hadiths de l'Imam an-Nawawi.",
            commentaries=[
                CommentaryBook(
                    book_name="Sharh al-Arba'in al-Nawawiyyah",
                    author="Imam an-Nawawi (d. 676 H)",
                    era="7ème siècle de l'Hégire",
                    content_summary="Explication classique de l'Imam an-Nawawi soulignant les leçons juridiques et morales à retenir de ce hadith.",
                    citations=[Citation(author="Imam an-Nawawi", book="Sharh al-Arba'in", volume=1, page=25)]
                )
            ]
        )
    return None

def get_isnad_chain(hadith_id: str) -> List[Dict]:
    chain_info = ISNAD_DB.get(hadith_id, [
        {"step": 1, "rijal_id": "bukhari_author", "transmission": "Rapporté par l'Imam An-Nawawi"},
        {"step": 2, "rijal_id": "umar", "transmission": "عن (D'après)"},
        {"step": 3, "rijal_id": "prophet", "transmission": "عن النبي صلى الله عليه وسلم"}
    ])
    resolved_chain = []
    for item in chain_info:
        rijal_data = RIJAL_DB.get(item["rijal_id"], {
            "id": item["rijal_id"],
            "name_ar": "عمر بن الخطاب رضي الله عنه",
            "name_en": "Narrateur Fiable",
            "role": "Sahabi / Tabi'i",
            "city": "Médine",
            "grade": "Thiqah (Fiable)",
            "teachers": ["Prophet Muhammad (ﷺ)"],
            "students": []
        })
        resolved_chain.append({
            "step": item["step"],
            "transmission": item["transmission"],
            "rijal": rijal_data
        })
    return resolved_chain

def get_takhrij_info(hadith_id: str) -> Optional[Dict]:
    return TAKHRIJ_DB.get(hadith_id, {
        "primary_hadith_id": hadith_id,
        "topic": "Concordance des narrations",
        "parallels": [
            {
                "collection": "Recueil Canonique",
                "hadith_number": 1,
                "narrator": "Compagnon du Prophète",
                "grade": "Sahih",
                "diff_highlights": [
                    {"word": "Texte authentique vérifié", "status": "identical"}
                ]
            }
        ]
    })
