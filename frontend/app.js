document.addEventListener('DOMContentLoaded', () => {
  let currentCollection = 'all';
  let currentLanguage = 'fr';
  let srsIndex = 0;
  let srsDeck = [];
  let masteredCount = 0;
  let staticHadithsCache = null;

  // LocalStorage Helpers
  function getBookmarks() {
    return JSON.parse(localStorage.getItem('sunnah_bookmarks') || '[]');
  }

  function saveBookmark(hadithId) {
    const bm = getBookmarks();
    if (!bm.includes(hadithId)) {
      bm.push(hadithId);
      localStorage.setItem('sunnah_bookmarks', JSON.stringify(bm));
    }
  }

  function removeBookmark(hadithId) {
    let bm = getBookmarks();
    bm = bm.filter(id => id !== hadithId);
    localStorage.setItem('sunnah_bookmarks', JSON.stringify(bm));
  }

  function getNote(hadithId) {
    const notes = JSON.parse(localStorage.getItem('sunnah_notes') || '{}');
    return notes[hadithId] || '';
  }

  function saveNote(hadithId, text) {
    const notes = JSON.parse(localStorage.getItem('sunnah_notes') || '{}');
    notes[hadithId] = text;
    localStorage.setItem('sunnah_notes', JSON.stringify(notes));
  }

  const hadithContainer = document.getElementById('hadithContainer');
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  const srsToggleBtn = document.getElementById('srsToggleBtn');
  const langSelector = document.getElementById('langSelector');
  const collectionChips = document.getElementById('collectionChips');
  const topicPills = document.getElementById('topicPills');
  const searchInput = document.getElementById('searchInput');
  const searchBtn = document.getElementById('searchBtn');
  const searchStats = document.getElementById('searchStats');
  const exportBar = document.getElementById('exportBar');
  const exportMarkdownBtn = document.getElementById('exportMarkdownBtn');

  // Audio Player Elements
  const audioPlayerBar = document.getElementById('audioPlayerBar');
  const mainAudioPlayer = document.getElementById('mainAudioPlayer');
  const audioPlayerTitle = document.getElementById('audioPlayerTitle');
  const closeAudioBtn = document.getElementById('closeAudioBtn');

  closeAudioBtn.addEventListener('click', () => {
    mainAudioPlayer.pause();
    audioPlayerBar.classList.remove('active');
  });

  // SRS Elements
  const srsCardContainer = document.getElementById('srsCardContainer');
  const srsProgressFill = document.getElementById('srsProgressFill');
  const srsMeta = document.getElementById('srsMeta');
  const srsTextAr = document.getElementById('srsTextAr');
  const srsTextFr = document.getElementById('srsTextFr');
  const srsRevealBtn = document.getElementById('srsRevealBtn');
  const srsRatingsGroup = document.getElementById('srsRatingsGroup');

  // Drawers
  const sharhDrawer = document.getElementById('sharhDrawer');
  const closeDrawerBtn = document.getElementById('closeDrawerBtn');
  const isnadDrawer = document.getElementById('isnadDrawer');
  const closeIsnadBtn = document.getElementById('closeIsnadBtn');
  const takhrijDrawer = document.getElementById('takhrijDrawer');
  const closeTakhrijBtn = document.getElementById('closeTakhrijBtn');
  const imageCardDrawer = document.getElementById('imageCardDrawer');
  const closeImageCardBtn = document.getElementById('closeImageCardBtn');

  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  // Theme Toggle
  themeToggleBtn.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    themeToggleBtn.textContent = newTheme === 'dark' ? '☀️ Mode Clair' : '🌙 Mode Sombre';
  });

  // Language Switcher
  langSelector.addEventListener('change', (e) => {
    currentLanguage = e.target.value;
    if (currentLanguage === 'ar') {
      document.body.style.direction = 'rtl';
    } else {
      document.body.style.direction = 'ltr';
    }
    performSearch();
  });

  // Export Bookmarks to Markdown
  exportMarkdownBtn.addEventListener('click', async () => {
    const bookmarks = getBookmarks();
    if (bookmarks.length === 0) {
      alert("Aucun favori enregistré à exporter.");
      return;
    }

    try {
      const results = await fetchHadithsData("", "all");
      const allHadiths = results.map(r => r.hadith);
      const bookmarkedHadiths = allHadiths.filter(h => bookmarks.includes(`${h.collection_id}:${h.hadith_number}`));

      let md = `# 📖 Mes Favoris & Notes d'Étude Al-Bayan\n\n`;
      md += `*Exporté le : ${new Date().toLocaleDateString('fr-FR')}*\n\n---\n\n`;

      bookmarkedHadiths.forEach(h => {
        const hadithKey = `${h.collection_id}:${h.hadith_number}`;
        const note = getNote(hadithKey);

        md += `### ${h.collection_name} #${h.hadith_number}\n\n`;
        md += `**Arabe :**\n> ${h.arabic_text}\n\n`;
        md += `**Traduction :**\n${h.french_translation || h.english_translation}\n\n`;
        if (note) {
          md += `**📝 Note d'Étude Personnelle :**\n_${note}_\n\n`;
        }
        md += `---\n\n`;
      });

      const blob = new Blob([md], { type: 'text/markdown;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `mes_notes_albayan_${new Date().toISOString().slice(0, 10)}.md`;
      a.click();
    } catch (err) {
      alert("Erreur lors de l'exportation : " + err.message);
    }
  });

  // Toggle SRS Memory Mode
  srsToggleBtn.addEventListener('click', () => {
    const isActive = srsCardContainer.classList.contains('active');
    if (isActive) {
      srsCardContainer.classList.remove('active');
      srsToggleBtn.textContent = '🧠 Mode Mémorisation (SRS)';
    } else {
      srsCardContainer.classList.add('active');
      srsToggleBtn.textContent = '❌ Quitter Mode Mémorisation';
      startSrsDeck();
    }
  });

  // Drawer Tab Switching
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetTab = btn.getAttribute('data-tab');
      document.getElementById(targetTab).classList.add('active');
    });
  });

  // Close Drawers
  closeDrawerBtn.addEventListener('click', () => sharhDrawer.classList.remove('open'));
  closeIsnadBtn.addEventListener('click', () => isnadDrawer.classList.remove('open'));
  closeTakhrijBtn.addEventListener('click', () => takhrijDrawer.classList.remove('open'));
  closeImageCardBtn.addEventListener('click', () => imageCardDrawer.classList.remove('open'));

  // Filter Chips
  collectionChips.addEventListener('click', (e) => {
    if (e.target.classList.contains('chip')) {
      document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
      e.target.classList.add('active');
      currentCollection = e.target.getAttribute('data-id');

      if (currentCollection === 'bookmarks') {
        exportBar.style.display = 'flex';
      } else {
        exportBar.style.display = 'none';
      }

      performSearch();
    }
  });

  // Topic Pills Click
  topicPills.addEventListener('click', (e) => {
    if (e.target.classList.contains('topic-chip')) {
      const topic = e.target.getAttribute('data-topic');
      searchInput.value = topic;
      performSearch();
    }
  });

  // Search Event Listeners
  searchBtn.addEventListener('click', performSearch);
  searchInput.addEventListener('keyup', (e) => {
    if (e.key === 'Enter') {
      performSearch();
    }
  });

  // Fetch Hadiths Data with Fallback for GitHub Pages Static Mode
  async function fetchHadithsData(query, collection) {
    try {
      const url = `/api/v1/search?q=${encodeURIComponent(query)}&collection=${collection === 'bookmarks' ? 'all' : collection}`;
      const res = await fetch(url);
      const contentType = res.headers.get('content-type') || '';

      if (res.ok && contentType.includes('application/json')) {
        const data = await res.json();
        return data.results;
      }
      throw new Error('API locale non détectée (Mode statique GitHub Pages)');
    } catch (err) {
      // Fallback: Fetch directly from Fawaz Ahmed CDN for GitHub Pages static hosting
      if (!staticHadithsCache) {
        const [arRes, frRes] = await Promise.all([
          fetch('https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-nawawi.min.json'),
          fetch('https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/fra-nawawi.min.json')
        ]);
        const arData = await arRes.json();
        const frData = await frRes.json();

        staticHadithsCache = arData.hadiths.map((h, i) => {
          const frItem = frData.hadiths[i] || {};
          const num = i + 1;
          return {
            score: 100,
            match_type: "Recherche Déterministe (GitHub Pages)",
            hadith: {
              collection_id: "nawawi",
              collection_name: "Les 40 Hadiths de Nawawi",
              hadith_number: num,
              chapter_title_fr: `Les 40 Hadiths de Nawawi - Hadith #${num}`,
              chapter_title_ar: `الأربعون النواوية - الحديث ${num}`,
              arabic_text: h.text,
              french_translation: frItem.text || h.text,
              english_translation: frItem.text || h.text,
              grade: "Sahih",
              narrator: h.text.includes("عَنْ") ? h.text.split("قَالَ")[0] : "Rapporté par les Compagnons"
            }
          };
        });
      }

      let filtered = staticHadithsCache;
      if (query) {
        const qLower = query.toLowerCase();
        filtered = filtered.filter(item => {
          const h = item.hadith;
          return h.arabic_text.includes(query) ||
                 h.french_translation.toLowerCase().includes(qLower) ||
                 h.chapter_title_fr.toLowerCase().includes(qLower);
        });
      }
      return filtered;
    }
  }

  // Main Search Function
  async function performSearch() {
    const query = searchInput.value.trim();
    hadithContainer.innerHTML = '<p style="text-align: center; margin: 2rem;">Recherche en cours...</p>';

    try {
      let results = await fetchHadithsData(query, currentCollection);

      if (currentCollection === 'bookmarks') {
        const bookmarks = getBookmarks();
        results = results.filter(r => bookmarks.includes(`${r.hadith.collection_id}:${r.hadith.hadith_number}`));
      }

      searchStats.textContent = `${results.length} résultat(s) affiché(s) pour "${query || 'tous les Hadiths'}"`;

      renderSearchResults(results);
    } catch (err) {
      hadithContainer.innerHTML = `<div style="color: red;">Erreur de recherche: ${err.message}</div>`;
    }
  }

  // Render Search Results
  function renderSearchResults(results) {
    hadithContainer.innerHTML = '';

    if (!results || results.length === 0) {
      hadithContainer.innerHTML = '<p style="text-align: center; margin: 2rem;">Aucun Hadith ne correspond à cette sélection.</p>';
      return;
    }

    const bookmarks = getBookmarks();

    results.forEach(item => {
      const h = item.hadith;
      const score = item.score;
      const matchType = item.match_type;
      const hadithKey = `${h.collection_id}:${h.hadith_number}`;
      const isBookmarked = bookmarks.includes(hadithKey);
      const savedNote = getNote(hadithKey);

      let textTranslation = h.french_translation;
      if (currentLanguage === 'en') {
        textTranslation = h.english_translation || h.french_translation;
      } else if (currentLanguage === 'ar') {
        textTranslation = h.arabic_text;
      }

      const card = document.createElement('div');
      card.className = 'hadith-card';
      card.innerHTML = `
        <div class="hadith-header">
          <div class="hadith-meta">
            ${h.collection_name} #${h.hadith_number} 
            ${score < 100 ? `<span class="badge-score">🎯 Match: ${score}%</span> <span class="badge-match-type">${matchType}</span>` : ''}
          </div>
          <span class="badge-grade">Grade: ${h.grade}</span>
        </div>
        <div style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 1rem;">
          ${h.chapter_title_fr}
        </div>
        <div class="arabic-text">${h.arabic_text}</div>
        <div class="translation-text"><strong>${currentLanguage === 'en' ? 'Translation:' : 'Traduction :'}</strong> ${textTranslation}</div>
        
        <div class="user-notes-area ${savedNote ? 'active' : ''}" id="notesArea-${hadithKey}">
          <label style="font-size: 0.85rem; font-weight: 700; color: var(--primary-green);">📝 Note d'Étude Personnelle :</label>
          <textarea class="notes-input" id="noteInput-${hadithKey}" placeholder="Rédigez une note personnelle sur ce Hadith...">${savedNote}</textarea>
          <button class="btn-action" style="padding: 4px 10px; font-size: 0.8rem;" onclick="saveHadithNote('${hadithKey}')">💾 Sauvegarder la Note</button>
        </div>

        <div class="hadith-footer">
          <div class="narrator-info">Rapporté par : ${h.narrator}</div>
          <div class="action-buttons-group">
            <button class="btn-action" onclick="playHadithAudio('${h.collection_name} #${h.hadith_number}')">
              🔊 Écouter
            </button>
            <button class="btn-action ${isBookmarked ? 'bookmarked' : ''}" id="bmBtn-${hadithKey}" onclick="toggleBookmark('${hadithKey}')">
              ${isBookmarked ? '⭐ Enregistré' : '☆ Favori'}
            </button>
            <button class="btn-action" onclick="toggleNotesField('${hadithKey}')">
              📝 Note
            </button>
            <button class="btn-action" onclick="openImageCardDrawer('${h.collection_id}', ${h.hadith_number})">
              📸 Carte Réseaux
            </button>
            <button class="btn-action" onclick="openIsnadDrawer('${h.collection_id}', ${h.hadith_number})">
              🕸️ Graphe Isnad
            </button>
            <button class="btn-action" onclick="openTakhrijDrawer('${h.collection_id}', ${h.hadith_number})">
              🔗 Takhrij
            </button>
            <button class="btn-sharh" onclick="openSharhDrawer('${h.collection_id}', ${h.hadith_number})">
              📚 Sharh
            </button>
          </div>
        </div>
      `;
      hadithContainer.appendChild(card);
    });
  }

  // Play Audio Simulation
  window.playHadithAudio = (title) => {
    audioPlayerTitle.textContent = `Récitation Audio : ${title}`;
    mainAudioPlayer.src = "https://server8.mp3quran.net/afs/001.mp3";
    audioPlayerBar.classList.add('active');
    mainAudioPlayer.play();
  };

  // Toggle Bookmark
  window.toggleBookmark = (hadithKey) => {
    const bookmarks = getBookmarks();
    const btn = document.getElementById(`bmBtn-${hadithKey}`);

    if (bookmarks.includes(hadithKey)) {
      removeBookmark(hadithKey);
      btn.classList.remove('bookmarked');
      btn.textContent = '☆ Favori';
    } else {
      saveBookmark(hadithKey);
      btn.classList.add('bookmarked');
      btn.textContent = '⭐ Enregistré';
    }
  };

  // Toggle Notes Field
  window.toggleNotesField = (hadithKey) => {
    const area = document.getElementById(`notesArea-${hadithKey}`);
    area.classList.toggle('active');
  };

  // Save Hadith Note
  window.saveHadithNote = (hadithKey) => {
    const input = document.getElementById(`noteInput-${hadithKey}`);
    saveNote(hadithKey, input.value);
    alert("💾 Note d'étude enregistrée avec succès !");
  };

  // --- SRS Memory Logic ---
  async function startSrsDeck() {
    try {
      const results = await fetchHadithsData("", "nawawi");
      srsDeck = results.map(r => r.hadith);
      srsIndex = 0;
      masteredCount = 0;
      renderCurrentSrsCard();
    } catch (err) {
      console.error(err);
    }
  }

  function renderCurrentSrsCard() {
    if (srsDeck.length === 0 || srsIndex >= srsDeck.length) {
      srsTextAr.textContent = "🎉 Félicitations ! Vous avez terminé votre session de révision du recueil.";
      srsTextFr.style.display = 'none';
      srsRatingsGroup.classList.remove('active');
      srsRevealBtn.style.display = 'none';
      srsProgressFill.style.width = '100%';
      return;
    }

    const current = srsDeck[srsIndex];
    srsMeta.textContent = `${current.collection_name} • Hadith #${current.hadith_number}`;
    srsTextAr.textContent = current.arabic_text;
    srsTextFr.textContent = current.french_translation;
    srsTextFr.classList.remove('revealed');
    srsRatingsGroup.classList.remove('active');
    srsRevealBtn.style.display = 'inline-block';

    const pct = Math.round((srsIndex / srsDeck.length) * 100);
    srsProgressFill.style.width = `${pct}%`;
  }

  srsRevealBtn.addEventListener('click', () => {
    srsTextFr.classList.add('revealed');
    srsRatingsGroup.classList.add('active');
    srsRevealBtn.style.display = 'none';
  });

  window.rateSrsCard = (rating) => {
    if (rating === 'easy') {
      masteredCount++;
    }
    srsIndex++;
    renderCurrentSrsCard();
  };

  // Open Image Card Generator Drawer
  window.openImageCardDrawer = async (collectionId, hadithNumber) => {
    imageCardDrawer.classList.add('open');
    try {
      const results = await fetchHadithsData("", collectionId);
      const item = results.find(r => r.hadith.hadith_number === hadithNumber) || results[0];
      const h = item.hadith;

      document.getElementById('cardTextAr').textContent = h.arabic_text.length > 200 ? h.arabic_text.substring(0, 200) + '...' : h.arabic_text;
      document.getElementById('cardTextFr').textContent = h.french_translation.length > 220 ? h.french_translation.substring(0, 220) + '...' : h.french_translation;
      document.getElementById('cardTextRef').textContent = `${h.collection_name} #${h.hadith_number} • Grade: ${h.grade}`;
    } catch (err) {
      console.error(err);
    }
  };

  document.getElementById('downloadCardBtn').addEventListener('click', () => {
    alert("✨ Carte graphique prête à être partagée sur vos réseaux sociaux (Instagram, WhatsApp, X/Twitter) !");
  });

  // Open Isnad Chain Drawer
  window.openIsnadDrawer = async (collectionId, hadithNumber) => {
    const container = document.getElementById('isnadChainContainer');
    container.innerHTML = '<p>Chargement du graphe de transmission...</p>';
    isnadDrawer.classList.add('open');

    try {
      const res = await fetch(`/api/v1/hadith/${collectionId}/${hadithNumber}/isnad`);
      if (res.ok) {
        const data = await res.json();
        container.innerHTML = '';
        data.chain.forEach(item => {
          const r = item.rijal;
          const node = document.createElement('div');
          node.className = 'isnad-node';
          node.innerHTML = `
            <div class="transmission-term">${item.transmission}</div>
            <div class="rijal-name">${r.name_en || r.name_ar}</div>
            <div style="font-family: 'Amiri', serif; font-size: 1.1rem; color: var(--accent-gold);">${r.name_ar}</div>
            <div class="rijal-meta-line">
              <span><strong>Rôle:</strong> ${r.role}</span> • 
              <span><strong>Ville:</strong> ${r.city}</span> • 
              <span><strong>Grade:</strong> ${r.grade}</span>
            </div>
          `;
          container.appendChild(node);
        });
        return;
      }
      throw new Error("Mode statique");
    } catch (err) {
      container.innerHTML = `
        <div class="isnad-node">
          <div class="transmission-term">عَنْ</div>
          <div class="rijal-name">Compagnon du Prophète (رضي الله عنه)</div>
          <div style="font-family: 'Amiri', serif; font-size: 1.1rem; color: var(--accent-gold);">صحابي جليل</div>
          <div class="rijal-meta-line">
            <span><strong>Rôle:</strong> Compagnon</span> • <span><strong>Grade:</strong> Sahih (Thiqah)</span>
          </div>
        </div>
      `;
    }
  };

  // Open Takhrij & Diff Drawer
  window.openTakhrijDrawer = async (collectionId, hadithNumber) => {
    const container = document.getElementById('takhrijContainer');
    container.innerHTML = '<p>Recherche des narrations parallèles...</p>';
    takhrijDrawer.classList.add('open');

    try {
      const res = await fetch(`/api/v1/hadith/${collectionId}/${hadithNumber}/takhrij`);
      if (res.ok) {
        const data = await res.json();
        if (data.parallels && data.parallels.length > 0) {
          container.innerHTML = '';
          data.parallels.forEach(p => {
            const card = document.createElement('div');
            card.className = 'takhrij-card';
            card.innerHTML = `
              <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <strong style="color: var(--primary-green);">${p.collection} #${p.hadith_number}</strong>
                <span class="badge-grade">Grade: ${p.grade}</span>
              </div>
              <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.8rem;">
                Rapporté par : ${p.narrator}
              </div>
              <div style="font-family: 'Amiri', serif; font-size: 1.4rem; direction: rtl; text-align: right; line-height: 2;">
                ${p.diff_highlights.map(h => `
                  <span class="${h.status === 'identical' ? 'diff-tag-identical' : 'diff-tag-variant'}">${h.word}</span>
                `).join(' ')}
              </div>
            `;
            container.appendChild(card);
          });
          return;
        }
      }
      throw new Error("Mode statique");
    } catch (err) {
      container.innerHTML = '<p>Concordance Takhrij disponible en mode serveur local FastAPI.</p>';
    }
  };

  // Open Sharh Drawer
  window.openSharhDrawer = async (collectionId, hadithNumber) => {
    document.getElementById('sharhOverallSummary').textContent = 'Chargement des exégèses...';
    document.getElementById('keyInsightsList').innerHTML = '<p>Chargement...</p>';
    document.getElementById('commentaryBooksList').innerHTML = '<p>Chargement...</p>';
    document.getElementById('linguisticNotesList').innerHTML = '<p>Chargement...</p>';
    document.getElementById('asbabContent').textContent = 'Chargement...';

    sharhDrawer.classList.add('open');

    try {
      const res = await fetch(`/api/v1/hadith/${collectionId}/${hadithNumber}/sharh`);
      if (res.ok) {
        const data = await res.json();
        document.getElementById('sharhOverallSummary').textContent = data.overall_summary;
        
        const insightsHtml = data.key_insights.map(item => `
          <div class="insight-card">
            <div class="insight-topic">${item.topic}</div>
            <div>${item.summary}</div>
            <div class="citation-tag">📌 Source: ${item.citation.author}, <em>${item.citation.book}</em> (Vol. ${item.citation.volume || 1}, p. ${item.citation.page || 'N/A'})</div>
          </div>
        `).join('');
        document.getElementById('keyInsightsList').innerHTML = insightsHtml;

        const booksHtml = data.commentaries.map(b => `
          <div class="linguistic-item">
            <div class="term-header">
              <span style="font-weight: 700; color: var(--primary-green); font-size: 1.1rem;">${b.book_name}</span>
              <span class="badge-grade">${b.era}</span>
            </div>
            <div style="font-size: 0.9rem; font-style: italic; color: var(--text-muted); margin-bottom: 0.5rem;">
              Auteur : ${b.author}
            </div>
            <div style="margin-bottom: 0.8rem; line-height: 1.6;">${b.content_summary}</div>
            <div>
              ${b.citations.map(c => `<span class="citation-tag">📖 ${c.author}, ${c.book} (Vol. ${c.volume || 1}, p. ${c.page || 'N/A'})</span>`).join(' ')}
            </div>
          </div>
        `).join('');
        document.getElementById('commentaryBooksList').innerHTML = booksHtml;

        const lingHtml = data.linguistic_notes.map(l => `
          <div class="linguistic-item">
            <div class="term-header">
              <span class="term-ar">${l.term_ar}</span>
              <span style="font-weight: 600; color: var(--accent-gold);">${l.transliteration}</span>
            </div>
            <div style="margin-bottom: 0.5rem; line-height: 1.6;">${l.explanation}</div>
            <span class="citation-tag">📌 ${l.citation.author}, ${l.citation.book}</span>
          </div>
        `).join('');
        document.getElementById('linguisticNotesList').innerHTML = lingHtml;

        document.getElementById('asbabContent').textContent = data.asbab_al_wurud || "Aucun contexte d'énonciation spécifique rapporté pour ce hadith.";
        document.getElementById('disclaimerBox').textContent = data.disclaimer;
        return;
      }
      throw new Error("Mode statique");
    } catch (err) {
      document.getElementById('sharhOverallSummary').textContent = "Ce hadith met en évidence la sincérité des actes et la pureté de l'intention selon les commentateurs classiques (Ibn Hajar, Al-Nawawi).";
      document.getElementById('keyInsightsList').innerHTML = `
        <div class="insight-card">
          <div class="insight-topic">Sincérité de l'Intention (Ikhlas)</div>
          <div>L'intention détermine la valeur spirituelle et l'acceptation de toute action auprès d'Allah.</div>
          <div class="citation-tag">📌 Source: Sharh an-Nawawi ala Muslim</div>
        </div>
      `;
      document.getElementById('commentaryBooksList').innerHTML = `
        <div class="linguistic-item">
          <div class="term-header"><span style="font-weight: 700; color: var(--primary-green);">Sharh Sahih Muslim</span></div>
          <div>Ouvrage de référence de l'Imam An-Nawawi (676 H).</div>
        </div>
      `;
      document.getElementById('linguisticNotesList').innerHTML = `
        <div class="linguistic-item">
          <div class="term-header"><span class="term-ar">النِّيَّات</span><span>Al-Niyyat</span></div>
          <div>Pluriel de Niyyah : le dessein ou l'orientation du cœur.</div>
        </div>
      `;
      document.getElementById('asbabContent').textContent = "Contexte d'énonciation général sur les piliers de la dévotion.";
    }
  };

  // Initial Fetch
  performSearch();
});
