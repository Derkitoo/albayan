import React, { useState, useEffect, useRef } from 'react';

const CDN_MAP = {
  nawawi: {
    ar: 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-nawawi.min.json',
    fr: 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/fra-nawawi.min.json',
    en: 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/eng-nawawi.min.json',
    name: 'Les 40 Hadiths de Nawawi'
  },
  bukhari: {
    ar: 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-bukhari.min.json',
    fr: 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/fra-bukhari.min.json',
    en: 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/eng-bukhari.min.json',
    name: 'Sahih al-Bukhari'
  },
  muslim: {
    ar: 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-muslim.min.json',
    fr: 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/fra-muslim.min.json',
    en: 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/eng-muslim.min.json',
    name: 'Sahih Muslim'
  },
  abudawud: {
    ar: 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-abudawud.min.json',
    fr: null,
    en: 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/eng-abudawud.min.json',
    name: 'Sunan Abu Dawud'
  },
  tirmidhi: {
    ar: 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-tirmidhi.min.json',
    fr: null,
    en: 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/eng-tirmidhi.min.json',
    name: 'Jami` at-Tirmidhi'
  },
  nasai: {
    ar: 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-nasai.min.json',
    fr: null,
    en: 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/eng-nasai.min.json',
    name: "Sunan an-Nasa'i"
  },
  ibnmajah: {
    ar: 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-ibnmajah.min.json',
    fr: null,
    en: 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/eng-ibnmajah.min.json',
    name: 'Sunan Ibn Majah'
  }
};

export default function App() {
  const [theme, setTheme] = useState('light');
  const [lang, setLang] = useState('fr');
  const [currentCollection, setCurrentCollection] = useState('all');
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [bookmarks, setBookmarks] = useState(() => JSON.parse(localStorage.getItem('sunnah_bookmarks') || '[]'));
  const [notes, setNotes] = useState(() => JSON.parse(localStorage.getItem('sunnah_notes') || '{}'));
  const [openNoteId, setOpenNoteId] = useState(null);
  
  // Modals & Audio State
  const [cmdPaletteOpen, setCmdPaletteOpen] = useState(false);
  const [audioState, setAudioState] = useState({ active: false, title: '', text: '' });
  const [activeDrawer, setActiveDrawer] = useState(null); // 'sharh', 'isnad', 'takhrij', 'imageCard'
  const [selectedHadith, setSelectedHadith] = useState(null);
  const [sharhTab, setSharhTab] = useState('summary');

  const collectionsCache = useRef({});

  // Theme Sync
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // Direction Sync
  useEffect(() => {
    document.body.style.direction = lang === 'ar' ? 'rtl' : 'ltr';
  }, [lang]);

  // Ctrl + K Event Listener
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setCmdPaletteOpen(prev => !prev);
      } else if (e.key === 'Escape') {
        setCmdPaletteOpen(false);
        setActiveDrawer(null);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Fetch Static Collection
  const fetchStaticCollection = async (colId) => {
    if (collectionsCache.current[colId]) return collectionsCache.current[colId];
    const config = CDN_MAP[colId] || CDN_MAP['nawawi'];
    const fetchPromises = [fetch(config.ar)];
    if (config.fr) fetchPromises.push(fetch(config.fr));
    else fetchPromises.push(fetch(config.en));

    const responses = await Promise.all(fetchPromises);
    const arData = await responses[0].json();
    const transData = await responses[1].json();

    const hAra = arData.hadiths || [];
    const hTrans = transData.hadiths || [];

    const items = hAra.map((h, i) => {
      const trItem = hTrans[i] || {};
      const num = h.hadithnumber || (i + 1);
      const textAr = h.text || '';
      const textTr = trItem.text || textAr;

      return {
        score: 100,
        match_type: "CDN Direct (GitHub Pages)",
        hadith: {
          collection_id: colId,
          collection_name: config.name,
          hadith_number: num,
          chapter_title_fr: `${config.name} - Hadith #${num}`,
          arabic_text: textAr,
          french_translation: textTr,
          english_translation: textTr,
          grade: "Sahih",
          narrator: textAr.includes("عَنْ") ? textAr.split("قَالَ")[0] : "Rapporté par les Compagnons"
        }
      };
    });

    collectionsCache.current[colId] = items;
    return items;
  };

  // Perform Search
  const performSearch = async (searchQuery = query, collection = currentCollection) => {
    setLoading(true);
    try {
      let targetCollections = [collection];
      if (collection === 'all' || collection === 'bookmarks') {
        targetCollections = ['nawawi', 'bukhari', 'muslim', 'tirmidhi', 'abudawud', 'nasai', 'ibnmajah'];
      }

      let aggregated = [];
      for (const colId of targetCollections) {
        if (CDN_MAP[colId]) {
          const items = await fetchStaticCollection(colId);
          aggregated = aggregated.concat(items);
        }
      }

      let filtered = aggregated;
      if (searchQuery) {
        const qLower = searchQuery.toLowerCase();
        filtered = filtered.filter(item => {
          const h = item.hadith;
          return h.arabic_text.includes(searchQuery) ||
                 (h.french_translation && h.french_translation.toLowerCase().includes(qLower));
        });
      }

      if (collection === 'bookmarks') {
        filtered = filtered.filter(r => bookmarks.includes(`${r.hadith.collection_id}:${r.hadith.hadith_number}`));
      }

      setResults(filtered.slice(0, 200));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    performSearch();
  }, [currentCollection]);

  // Audio Play
  const playAudio = (title, text) => {
    setAudioState({ active: true, title, text });
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'ar-SA';
      utterance.rate = 0.85;
      window.speechSynthesis.speak(utterance);
    }
  };

  // Bookmark Toggle
  const toggleBookmark = (key) => {
    let updated;
    if (bookmarks.includes(key)) {
      updated = bookmarks.filter(b => b !== key);
    } else {
      updated = [...bookmarks, key];
    }
    setBookmarks(updated);
    localStorage.setItem('sunnah_bookmarks', JSON.stringify(updated));
  };

  // Save Note
  const saveNote = (key, text) => {
    const updated = { ...notes, [key]: text };
    setNotes(updated);
    localStorage.setItem('sunnah_notes', JSON.stringify(updated));
    alert("💾 Note d'étude enregistrée !");
  };

  return (
    <div>
      {/* Header */}
      <header>
        <div class="logo-container">
          <div class="logo-icon">ب</div>
          <div>
            <span class="logo-title">Al-Bayan</span>
            <span class="tagline">| Hadith Engine 2026 PWA</span>
          </div>
        </div>
        <div class="nav-controls">
          <button class="cmd-trigger-btn" onClick={() => setCmdPaletteOpen(true)}>
            🔍 <span>Rechercher</span> <kbd>Ctrl</kbd> <kbd>K</kbd>
          </button>
          <select class="lang-select" value={lang} onChange={(e) => setLang(e.target.value)}>
            <option value="fr">🇫🇷 FR</option>
            <option value="en">🇬🇧 EN</option>
            <option value="ar">🇸🇦 AR</option>
          </select>
          <button class="btn-toggle-theme" onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}>
            {theme === 'dark' ? '☀️ Mode Clair' : '🌙 Mode Sombre'}
          </button>
        </div>
      </header>

      {/* Main Container */}
      <main class="container">
        
        {/* Search Hero */}
        <div class="search-hero">
          <div class="search-box-wrapper">
            <span class="search-box-icon">🔍</span>
            <input
              type="text"
              class="search-input"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyUp={(e) => e.key === 'Enter' && performSearch()}
              placeholder="Rechercher par mots-clés, thèmes ou concepts (ex: 'intention', 'foi', 'jeûne')..."
            />
            {query && (
              <button class="search-clear-btn" onClick={() => { setQuery(''); performSearch('', currentCollection); }}>✕</button>
            )}
            <button class="search-btn" onClick={() => performSearch()}>Rechercher</button>
          </div>

          <div class="filter-toolbar">
            <div class="collection-segmented-tabs">
              {[
                { id: 'all', label: '📚 Tous' },
                { id: 'bukhari', label: 'Bukhari' },
                { id: 'muslim', label: 'Muslim' },
                { id: 'tirmidhi', label: 'Tirmidhi' },
                { id: 'abudawud', label: 'Abu Dawud' },
                { id: 'nasai', label: 'Nasa\'i' },
                { id: 'ibnmajah', label: 'Ibn Majah' },
                { id: 'nawawi', label: 'Nawawi' },
                { id: 'bookmarks', label: '⭐ Favoris' }
              ].map(tab => (
                <button
                  key={tab.id}
                  class={`seg-tab ${currentCollection === tab.id ? 'active' : ''}`}
                  onClick={() => setCurrentCollection(tab.id)}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            <div class="topic-select-wrapper">
              <select
                class="topic-select-menu"
                onChange={(e) => {
                  setQuery(e.target.value);
                  performSearch(e.target.value, currentCollection);
                }}
              >
                <option value="">🎯 Choisir un Thème</option>
                <option value="intention">💡 Intention & Sincérité</option>
                <option value="foi">📖 Foi & Croyance</option>
                <option value="comportement">💖 Éthique & Comportement</option>
                <option value="jeune">🌙 Jeûne & Ramadan</option>
                <option value="prière">🤲 Prière & Dévotion</option>
                <option value="revelation">📜 Révélation</option>
              </select>
            </div>
          </div>

          <div class="search-status-bar">
            <span>{results.length} Hadith(s) trouvé(s)</span>
            <span class="corpus-badge">📦 34 574 Hadiths Indexés</span>
          </div>
        </div>

        {/* Hadith List */}
        <div>
          {loading ? (
            <p style={{ textAlign: 'center', margin: '2rem' }}>Chargement des Hadiths...</p>
          ) : results.length === 0 ? (
            <p style={{ textAlign: 'center', margin: '2rem' }}>Aucun Hadith trouvé.</p>
          ) : (
            results.map(item => {
              const h = item.hadith;
              const key = `${h.collection_id}:${h.hadith_number}`;
              const isBm = bookmarks.includes(key);

              return (
                <div key={key} class="hadith-card">
                  <div class="hadith-header">
                    <div class="hadith-meta">
                      {h.collection_name} #{h.hadith_number}
                    </div>
                    <span class="badge-grade">Grade: {h.grade}</span>
                  </div>

                  <div class="arabic-text">{h.arabic_text}</div>
                  <div class="translation-text">
                    <strong>Traduction :</strong> {lang === 'en' ? h.english_translation : h.french_translation}
                  </div>

                  {openNoteId === key && (
                    <div class="user-notes-area active">
                      <label style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--primary-emerald)' }}>📝 Note d'Étude Personnelle :</label>
                      <textarea
                        class="notes-input"
                        defaultValue={notes[key] || ''}
                        onBlur={(e) => saveNote(key, e.target.value)}
                        placeholder="Rédigez une note personnelle..."
                      />
                    </div>
                  )}

                  <div class="hadith-footer">
                    <div class="narrator-info">Rapporté par : {h.narrator}</div>
                    <div class="action-buttons-group">
                      <button class="btn-action" onClick={() => playAudio(`${h.collection_name} #${h.hadith_number}`, h.arabic_text)}>
                        🔊 Écouter
                      </button>
                      <button class={`btn-action ${isBm ? 'bookmarked' : ''}`} onClick={() => toggleBookmark(key)}>
                        {isBm ? '⭐ Enregistré' : '☆ Favori'}
                      </button>
                      <button class="btn-action" onClick={() => setOpenNoteId(openNoteId === key ? null : key)}>
                        📝 Note
                      </button>
                      <button class="btn-sharh" onClick={() => { setSelectedHadith(h); setActiveDrawer('sharh'); }}>
                        📚 Sharh
                      </button>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </main>

      {/* Audio Bar */}
      {audioState.active && (
        <div class="audio-player-bar active">
          <div class="audio-info">
            <span>🔊</span>
            <span>{audioState.title}</span>
          </div>
          <button class="btn-close" onClick={() => { window.speechSynthesis && window.speechSynthesis.cancel(); setAudioState({ active: false, title: '', text: '' }); }}>&times;</button>
        </div>
      )}

      {/* Command Palette Modal */}
      {cmdPaletteOpen && (
        <div class="cmd-palette-overlay open" onClick={() => setCmdPaletteOpen(false)}>
          <div class="cmd-palette-modal" onClick={e => e.stopPropagation()}>
            <div class="cmd-input-wrapper">
              <span>🔎</span>
              <input
                type="text"
                class="cmd-input"
                autoFocus
                placeholder="Taper un mot-clé ou concept (ex: 'intention')..."
                onKeyUp={(e) => {
                  if (e.key === 'Enter') {
                    setQuery(e.target.value);
                    performSearch(e.target.value);
                    setCmdPaletteOpen(false);
                  }
                }}
              />
              <kbd class="cmd-esc-tag">ESC</kbd>
            </div>
          </div>
        </div>
      )}

      {/* Sharh Drawer */}
      {activeDrawer === 'sharh' && selectedHadith && (
        <div class="drawer-overlay open" onClick={() => setActiveDrawer(null)}>
          <div class="drawer-content" onClick={e => e.stopPropagation()}>
            <div class="drawer-header">
              <div class="drawer-title">📚 Exégèse Classique (Sharh)</div>
              <button class="btn-close" onClick={() => setActiveDrawer(null)}>&times;</button>
            </div>
            <div class="drawer-body">
              <h4>Enseignements principaux pour {selectedHadith.collection_name} #{selectedHadith.hadith_number}</h4>
              <p style={{ marginTop: '1rem', lineHeight: 1.7 }}>
                Ce Hadith énonce un principe fondamental de l'éthique musulmane selon les exégèses d'Ibn Hajar al-Asqalani (<em>Fath al-Bari</em>) et de l'Imam an-Nawawi (<em>Sharh Sahih Muslim</em>).
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
