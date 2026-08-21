import re
import math
from typing import List, Dict, Any, Tuple
from backend.models import HadithItem
from backend.database import get_all_hadiths, get_sharh_by_hadith_id

CONCEPT_VOCABULARY = {
    "intention": ["intention", "niyyah", "motivation", "sincerite", "coeur", "acte", "nawaa", "نية", "الأعمال", "النيات"],
    "foi": ["foi", "iman", "croire", "credo", "piliers", "anges", "livres", "destin", "إيمان", "تؤمن", "بالله"],
    "comportement": ["comportement", "morale", "ethique", "colere", "vulgaire", "poids", "balance", "خلق", "حسن الخلق", "البذيء"],
    "emigration": ["emigration", "hijrah", "medine", "mecque", "volonte", "quitter", "هجرة", "هاجر"],
    "revelation": ["revelation", "prophete", "ange", "gabriel", "jibril", "wahee", "وحى", "الوحي"],
    "jeune": ["jeune", "ramadan", "jeûne", "soym", "صوم", "الصيام"],
    "prière": ["prière", "salat", "priere", "صلاة", "الصلاة"],
    "zakat": ["zakat", "aumone", "aumône", "زكاة", "الزكاة"]
}

def normalize_text(text: str) -> str:
    tashkeel_pattern = re.compile(r'[\u0617-\u061A\u064B-\u0652]')
    text = re.sub(tashkeel_pattern, '', text)
    text = text.lower()
    text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
    return text

def compute_text_vector(text: str) -> Dict[str, float]:
    norm = normalize_text(text)
    words = set(norm.split())
    vector = {}
    
    for concept, terms in CONCEPT_VOCABULARY.items():
        score = 0.0
        for term in terms:
            if term in norm:
                score += 1.0
        if score > 0:
            vector[concept] = score
            
    magnitude = math.sqrt(sum(v ** 2 for v in vector.values()))
    if magnitude > 0:
        for k in vector:
            vector[k] /= magnitude
            
    return vector

def cosine_similarity(v1: Dict[str, float], v2: Dict[str, float]) -> float:
    dot_product = sum(v1.get(k, 0.0) * v2.get(k, 0.0) for k in set(v1) | set(v2))
    return dot_product

def intelligent_search(
    query: str, 
    collection_filter: str = "all", 
    grade_filter: str = "all"
) -> List[Dict[str, Any]]:
    all_hadiths = get_all_hadiths()

    if not query.strip():
        results = []
        for h in all_hadiths:
            if collection_filter != "all" and h.collection_id != collection_filter:
                continue
            if grade_filter != "all" and h.grade.lower() != grade_filter.lower():
                continue
            results.append({
                "hadith": h,
                "score": 100,
                "match_type": "Par Défaut",
                "matched_concepts": []
            })
        return results

    query_norm = normalize_text(query)
    query_vec = compute_text_vector(query)
    query_tokens = set(query_norm.split())

    search_results = []

    for hadith in all_hadiths:
        hadith_id = f"{hadith.collection_id}:{hadith.hadith_number}"
        if collection_filter != "all" and hadith.collection_id != collection_filter:
            continue
        if grade_filter != "all" and hadith.grade.lower() != grade_filter.lower():
            continue

        sharh_data = get_sharh_by_hadith_id(hadith_id)
        full_document_text = f"{hadith.arabic_text} {hadith.french_translation} {hadith.english_translation} "
        if sharh_data:
            full_document_text += f"{sharh_data.overall_summary} "
            for insight in sharh_data.key_insights:
                full_document_text += f"{insight.topic} {insight.summary} "

        doc_norm = normalize_text(full_document_text)
        doc_vec = compute_text_vector(full_document_text)

        sem_sim = cosine_similarity(query_vec, doc_vec)

        doc_tokens = set(doc_norm.split())
        token_overlap = len(query_tokens & doc_tokens) / max(len(query_tokens), 1)

        hybrid_score = (sem_sim * 60) + (token_overlap * 40)
        
        match_type = "Sémantique (Sens)"
        if token_overlap > 0.4:
            match_type = "Mot-clé Exact + Sémantique"
        elif sem_sim > 0.2:
            match_type = "Concept Sémantique"

        if hybrid_score > 5 or token_overlap > 0:
            matched_concepts = [k for k in query_vec if k in doc_vec]
            search_results.append({
                "hadith": hadith,
                "score": min(round(hybrid_score * 100), 99),
                "match_type": match_type,
                "matched_concepts": matched_concepts
            })

    search_results.sort(key=lambda x: x["score"], reverse=True)
    return search_results
