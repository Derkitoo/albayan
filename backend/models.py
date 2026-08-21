from pydantic import BaseModel, Field
from typing import List, Optional

class Citation(BaseModel):
    author: str = Field(..., description="Nom du savant (ex: Ibn Hajar al-Asqalani)")
    book: str = Field(..., description="Titre de l'ouvrage classique (ex: Fath al-Bari)")
    volume: Optional[int] = Field(None, description="Numéro du volume")
    page: Optional[int] = Field(None, description="Numéro de la page")

class KeyInsight(BaseModel):
    topic: str
    summary: str
    citation: Citation

class LinguisticNote(BaseModel):
    term_ar: str
    transliteration: str
    explanation: str
    citation: Citation

class CommentaryBook(BaseModel):
    book_name: str
    author: str
    era: str
    content_summary: str
    citations: List[Citation]

class HadithItem(BaseModel):
    collection_id: str
    collection_name: str
    hadith_number: int
    chapter_title_ar: str
    chapter_title_en: str
    chapter_title_fr: str
    arabic_text: str
    english_translation: str
    french_translation: str
    grade: str  # Sahih, Hasan, Da'if
    narrator: str

class SharhResponse(BaseModel):
    hadith_id: str
    collection_name: str
    hadith_number: int
    overall_summary: str
    key_insights: List[KeyInsight]
    linguistic_notes: List[LinguisticNote]
    asbab_al_wurud: Optional[str] = None
    commentaries: List[CommentaryBook]
    disclaimer: str = (
        "⚠️ Ce résumé est généré par IA à partir d'exégèses classiques numérisées (Fath al-Bari, Sharh an-Nawawi, Ma'alim al-Sunan) "
        "à des fins uniquement pédagogiques et académiques. Il ne constitue en aucun cas une Fatwa ou un avis juridique personnel."
    )
