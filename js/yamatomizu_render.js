
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('content-container');
    const loadingElement = document.getElementById('loading');
    const filterBar = document.getElementById('filter-bar');
    const moodSelect = document.getElementById('mood-select');
    const tagFilterInfo = document.getElementById('tag-filter-info');
    const activeTagName = document.getElementById('active-tag-name');
    const clearTagFilter = document.getElementById('clear-tag-filter');
    const modalOverlay = document.getElementById('modal-overlay');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    const modalClose = document.getElementById('modal-close');

    let allPoems = [];
    let currentSeason = 'all';
    let currentMood = 'all';
    let currentTag = null;

    // Mood keywords mapping
    const moodKeywords = {
        faith: ['信仰', '随順', '惟神', '帰依', '信', '任せ', '従', '敬'],
        hope: ['希望', '光明', '待', '明日', '未来', '夜明け', '虹', '救い', '光'],
        purification: ['浄化', '再生', '清め', '蘇り', '禊', '洗', '雨', '露'],
        harmony: ['調和', '自然', '美', '一体', '融合', '庭園', '造形', '天地'],
        mission: ['経綸', '使命', '神業', '救世', '計画', '建設', '天国', '世界'],
        art: ['言霊', '芸術', '和歌', '美術', '詩歌', '創造', '響き'],
        serenity: ['孤独', '静寂', '寂', '静', 'たたず', '無', '空', '瞑想'],
        love: ['愛', '慈悲', '親心', '慈', '恵', '恩', '情']
    };

    // Tag definitions - nature, spiritual, emotion
    const tagDefinitions = {
        nature: ['雨', '月', '富士', '花', '山', '水', '川', '海', '風', '雲', '虹', '森', '松', '桜', '梅', '露', '雪', '霧', '鳥', '蝶', '蛍'],
        spiritual: ['天国', '神', '光', '魂', '霊', '経綸', '救い', '祈り', '信仰', '真理', '悟り', '仏', '観音'],
        emotion: ['喜び', '悲しみ', '寂', '安らぎ', '希望', '愛', '感謝', '畏敬', '清々']
    };

    fetch('yamatomizu.json')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            allPoems = extractPoems(data);
            renderPoems(allPoems);
            loadingElement.style.display = 'none';
            container.style.opacity = 1;
        })
        .catch(error => {
            console.error('Error loading content:', error);
            loadingElement.innerHTML = `<p style="color: #bf616a;">Error loading content. Please try refreshing.</p>`;
        });

    // Season filter buttons
    filterBar.addEventListener('click', (e) => {
        if (e.target.classList.contains('filter-btn')) {
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');
            currentSeason = e.target.dataset.season;
            applyFilters();
        }
    });

    // Mood filter select
    moodSelect.addEventListener('change', (e) => {
        currentMood = e.target.value;
        applyFilters();
    });

    // Clear tag filter
    clearTagFilter.addEventListener('click', () => {
        currentTag = null;
        tagFilterInfo.classList.remove('active');
        applyFilters();
    });

    // Modal close
    modalClose.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) closeModal();
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });

    function closeModal() {
        modalOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    function openModal(poem) {
        modalTitle.textContent = poem.text;

        let bodyHTML = '';

        // Reading
        if (poem.reading) {
            bodyHTML += `
                <div class="modal-section">
                    <div class="modal-label">読み</div>
                    <div class="modal-reading">${poem.reading}</div>
                </div>
            `;
        }

        // Modern interpretation
        if (poem.meaning) {
            bodyHTML += `
                <div class="modal-section">
                    <div class="modal-label">現代語意訳</div>
                    <div class="modal-meaning">${poem.meaning}</div>
                </div>
            `;
        }

        // Explanations
        if (poem.explanations && poem.explanations.length > 0) {
            bodyHTML += `<div class="modal-section"><div class="modal-label">解説</div>`;
            poem.explanations.forEach(exp => {
                let className = 'modal-explanation';
                if (exp.includes('季語')) className += ' kigo';
                else if (exp.includes('言霊')) className += ' kototama';
                else if (exp.includes('深層') || exp.includes('教訓')) className += ' depth';
                bodyHTML += `<div class="${className}">${exp}</div>`;
            });
            bodyHTML += `</div>`;
        }

        modalBody.innerHTML = bodyHTML;
        modalOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function extractPoems(data) {
        const poems = [];
        let currentSectionTitle = '';
        let poemIndex = 0;

        if (data.data && Array.isArray(data.data)) {
            data.data.forEach(section => {
                // Track section titles for season detection
                if (section.title && section.level === 2) {
                    currentSectionTitle = section.title;
                }

                if (section.content && Array.isArray(section.content)) {
                    let i = 0;
                    while (i < section.content.length) {
                        const item = section.content[i];

                        if (item.type === 'paragraph' && item.text.startsWith("御歌:")) {
                            poemIndex++;
                            const poem = {
                                index: poemIndex,
                                text: item.text.replace("御歌:", "").trim(),
                                sectionTitle: currentSectionTitle,
                                season: detectSeason(currentSectionTitle),
                                reading: null,
                                meaning: null,
                                explanations: [],
                                moods: [],
                                tags: []
                            };

                            i++;

                            // Reading
                            if (i < section.content.length) {
                                const next = section.content[i];
                                if (next.type === 'paragraph' && next.text.startsWith("読み:")) {
                                    poem.reading = next.text.replace("読み:", "").trim();
                                    i++;
                                }
                            }

                            // Meaning
                            if (i < section.content.length) {
                                const next = section.content[i];
                                if (next.type === 'paragraph' && next.text.startsWith("現代語意訳:")) {
                                    let bodyText = next.text.replace("現代語意訳:", "").trim();
                                    i++;

                                    // Check for quoted content in next paragraph
                                    if (!bodyText && i < section.content.length) {
                                        const contentItem = section.content[i];
                                        if (contentItem.type === 'paragraph' && contentItem.text.startsWith("「")) {
                                            bodyText = contentItem.text;
                                            i++;
                                        }
                                    }
                                    poem.meaning = bodyText;
                                }
                            }

                            // Explanations
                            while (i < section.content.length) {
                                const next = section.content[i];
                                if (next.type === 'paragraph') {
                                    const text = next.text;
                                    if (text.startsWith("🍃") || text.startsWith("🎵") || text.startsWith("🏔️")) {
                                        poem.explanations.push(text);

                                        // Detect season from kigo
                                        if (text.includes("季語") && !poem.season) {
                                            poem.season = detectSeasonFromKigo(text);
                                        }

                                        // Extract moods from 深層の教訓
                                        if (text.startsWith("🏔️")) {
                                            poem.moods = extractMoods(text);
                                        }

                                        i++;
                                    } else if (text.startsWith("「") && !poem.meaning) {
                                        i++;
                                    } else {
                                        break;
                                    }
                                } else {
                                    break;
                                }
                            }

                            // Extract tags from poem text and explanations
                            poem.tags = extractTags(poem);

                            poems.push(poem);
                        } else {
                            i++;
                        }
                    }
                }
            });
        }

        return poems;
    }

    function extractMoods(text) {
        const detectedMoods = [];
        for (const [mood, keywords] of Object.entries(moodKeywords)) {
            for (const keyword of keywords) {
                if (text.includes(keyword)) {
                    if (!detectedMoods.includes(mood)) {
                        detectedMoods.push(mood);
                    }
                    break;
                }
            }
        }
        return detectedMoods;
    }

    function extractTags(poem) {
        const tags = [];
        const combinedText = poem.text + ' ' + (poem.meaning || '') + ' ' + poem.explanations.join(' ');

        // Check each tag definition
        for (const [category, keywords] of Object.entries(tagDefinitions)) {
            for (const keyword of keywords) {
                if (combinedText.includes(keyword) && !tags.some(t => t.name === keyword)) {
                    tags.push({ name: keyword, category });
                }
            }
        }

        // Limit to top 5 tags for display
        return tags.slice(0, 5);
    }

    function detectSeason(title) {
        if (!title) return null;
        if (title.includes('春')) return '春';
        if (title.includes('夏')) return '夏';
        if (title.includes('秋')) return '秋';
        if (title.includes('冬')) return '冬';
        return null;
    }

    function detectSeasonFromKigo(text) {
        if (text.includes('春')) return '春';
        if (text.includes('夏') || text.includes('初夏') || text.includes('晩夏')) return '夏';
        if (text.includes('秋') || text.includes('晩秋')) return '秋';
        if (text.includes('冬') || text.includes('初冬') || text.includes('晩冬')) return '冬';
        return null;
    }

    function renderPoems(poems) {
        container.innerHTML = '';

        poems.forEach(poem => {
            const card = document.createElement('div');
            card.className = 'poem-card';
            if (poem.season) card.dataset.season = poem.season;
            if (poem.moods.length > 0) card.dataset.moods = poem.moods.join(',');
            if (poem.tags.length > 0) card.dataset.tags = poem.tags.map(t => t.name).join(',');

            let html = `
                <div class="poem-number">${poem.index}.</div>
                <div class="poem-text">${poem.text}</div>
            `;

            // Season tag
            if (poem.season) {
                html += `<div class="poem-season"><span class="season-tag ${poem.season}">${poem.season}</span></div>`;
            }

            // Poem tags
            if (poem.tags.length > 0) {
                html += `<div class="poem-tags">`;
                poem.tags.forEach(tag => {
                    html += `<span class="poem-tag ${tag.category}" data-tag="${tag.name}">${tag.name}</span>`;
                });
                html += `</div>`;
            }

            card.innerHTML = html;

            // Click on card opens modal
            card.addEventListener('click', (e) => {
                // Don't open modal if clicking a tag
                if (e.target.classList.contains('poem-tag')) {
                    return;
                }
                openModal(poem);
            });

            // Tag click handling
            card.querySelectorAll('.poem-tag').forEach(tagEl => {
                tagEl.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const tagName = tagEl.dataset.tag;
                    currentTag = tagName;
                    activeTagName.textContent = tagName;
                    tagFilterInfo.classList.add('active');
                    applyFilters();
                });
            });

            container.appendChild(card);
        });
    }

    function applyFilters() {
        const cards = container.querySelectorAll('.poem-card');
        cards.forEach(card => {
            let show = true;

            // Season filter
            if (currentSeason !== 'all') {
                if (card.dataset.season !== currentSeason) {
                    show = false;
                }
            }

            // Mood filter
            if (show && currentMood !== 'all') {
                const moods = card.dataset.moods ? card.dataset.moods.split(',') : [];
                if (!moods.includes(currentMood)) {
                    show = false;
                }
            }

            // Tag filter
            if (show && currentTag) {
                const tags = card.dataset.tags ? card.dataset.tags.split(',') : [];
                if (!tags.includes(currentTag)) {
                    show = false;
                }
            }

            if (show) {
                card.classList.remove('hidden');
            } else {
                card.classList.add('hidden');
            }
        });
    }
});
