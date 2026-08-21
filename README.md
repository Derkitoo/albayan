# 📖 Sunnah.com - Innovation Suite (34 500+ Hadiths Canoniques)

Une plateforme Web & PWA moderne, ultrarapide et 100% déterministe (sans LLM) pour la recherche sémantique, l'exégèse classique (*Sharh*), l'analyse des chaînes de transmission (*Isnad* & *'Ilm ar-Rijal*), la concordance (*Takhrij*), et la mémorisation (*SRS Flashcards*) des Hadiths de la Sunnah.

---

## 🌟 Fonctionnalités Clés

- **⚡ Recherche Sémantique Hybride Déterministe (< 3 ms) :**
  - Fusionne la recherche vectorielle cosinus sur vocabulaire conceptuel et l'analyse BM25 (sac de mots + racines arabes). 0% d'hallucination, 0% de coût API.
- **📦 34 574 Hadiths Authentiques Indexés (SQLite) :**
  - **Sahih al-Bukhari** (7 589 Hadiths)
  - **Sahih Muslim** (7 563 Hadiths)
  - **Sunan Abu Dawud** (5 274 Hadiths)
  - **Jami` at-Tirmidhi** (3 998 Hadiths)
  - **Sunan an-Nasa'i** (5 765 Hadiths)
  - **Sunan Ibn Majah** (4 343 Hadiths)
  - **Les 40 Hadiths de Nawawi** (42 Hadiths)
- **🕸️ Graphe de Transmission (*Isnad* & *'Ilm ar-Rijal*) :**
  - Visualisation dynamique sous forme d'arbre et fiches biographiques des rapporteurs.
- **🔗 Concordance & Diff-Viewer (*Takhrij*) :**
  - Surbrillance des variantes lexicales entre les récits parallèles.
- **📚 Tiroir Exégétique Classique (*Sharh*) :**
  - Extrait authentifié des grands commentaires classiques (*Fath al-Bari*, *Sharh an-Nawawi*).
- **📸 Générateur de Cartes Réseaux Sociaux (`📸 Carte Réseaux`) :**
  - Exportation de cartes haute résolution pour Instagram, WhatsApp et X.
- **🧠 Module SRS de Mémorisation (Flashcards) :**
  - Répétition espacée interactive avec auto-évaluation (🔴/🟡/🟢) pour réviser les Hadiths.
- **📝 Carnet d'Étude & Prise de Notes (`LocalStorage`) :**
  - Marque-pages favoris et notes d'étude annotées sous chaque Hadith.
- **📥 Exportation Markdown (`.md`) :**
  - Téléchargement en 1 clic de votre carnet d'étude au format `.md`.
- **🔊 Lecteur Audio Flottant (`🔊 Écouter`) :**
  - Écoute des récitations audio originales avec barre de contrôle.
- **📱 PWA Hors-Ligne & Installation Native :**
  - Service Worker (`sw.js`) et Manifest (`manifest.json`) pour un fonctionnement 100% hors-ligne.
- **🐳 Docker Ready :**
  - Déploiement en 1 commande via `docker-compose up -d`.

---

## 🚀 Démarrage Rapide (Local)

### Prérequis
- Python 3.10+
- FastAPI, Uvicorn, Pydantic

### Installation

```bash
git clone https://github.com/votre-compte/sunnah-sharh-ai.git
cd sunnah-sharh-ai

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur
python run_server.py
```

Ouvrez ensuite votre navigateur sur **http://localhost:8000**.

---

## 🐳 Déploiement Docker

```bash
docker-compose up -d
```

---

## 📜 Licence

Projet open-source distribué sous licence **MIT**.
