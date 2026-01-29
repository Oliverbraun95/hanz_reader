let currentMode = 'url';

function switchTab(mode) {
    currentMode = mode;
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`.tab-btn[onclick="switchTab('${mode}')"]`).classList.add('active');

    if (mode === 'url') {
        document.getElementById('url-input-section').style.display = 'block';
        document.getElementById('text-input-section').style.display = 'none';
        document.getElementById('url-input').focus();
    } else {
        document.getElementById('url-input-section').style.display = 'none';
        document.getElementById('text-input-section').style.display = 'block';
        document.getElementById('text-input').focus();
    }
}

async function analyze() {
    const loader = document.getElementById('loader');
    const resultArea = document.getElementById('results-area');
    const errorMsg = document.getElementById('error-msg');

    loader.style.display = 'block';
    resultArea.style.display = 'none';
    errorMsg.style.display = 'none';

    let payload = {};
    let endpoint = '';

    if (currentMode === 'url') {
        const url = document.getElementById('url-input').value.trim();
        if (!url) {
            showError("Please enter a URL");
            return;
        }
        payload = { url: url };
        endpoint = '/api/v1/analyze/url';
    } else {
        const content = document.getElementById('text-input').value.trim();
        if (!content) {
            showError("Please enter some text");
            return;
        }
        payload = { content: content };
        endpoint = '/api/v1/analyze';
    }

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Analysis failed');
        }

        renderResults(data);

    } catch (e) {
        showError(e.message);
    } finally {
        loader.style.display = 'none';
    }
}

function showError(msg) {
    const el = document.getElementById('error-msg');
    el.textContent = msg;
    el.style.display = 'block';
    document.getElementById('loader').style.display = 'none';
}

function renderResults(data) {
    const resultArea = document.getElementById('results-area');

    // Fill Basic Stats
    document.getElementById('res-title').textContent = data.title || "Text Analysis";
    document.getElementById('res-url').textContent = data.url || (currentMode === 'url' ? document.getElementById('url-input').value : "Raw Text Input");

    document.getElementById('score-val').textContent = data.difficulty_score;
    // Map score colors
    const scoreVal = document.getElementById('score-val');
    scoreVal.className = 'stat-value'; // Reset
    // Could add color classes based on Score magnitude basically 1=Green, 6=Pink

    document.getElementById('tokens-val').textContent = data.total_tokens;
    document.getElementById('unknown-val').textContent = formatPercent(data.unknown_coverage);

    // Render Bars
    const barsContainer = document.getElementById('coverage-bars');
    barsContainer.innerHTML = '';

    const levels = [
        { id: 1, key: 'hsk_1_coverage', label: 'HSK 1', class: 'hsk-1' },
        { id: 2, key: 'hsk_2_coverage', label: 'HSK 2', class: 'hsk-2' },
        { id: 3, key: 'hsk_3_coverage', label: 'HSK 3', class: 'hsk-3' },
        { id: 4, key: 'hsk_4_coverage', label: 'HSK 4', class: 'hsk-4' },
        { id: 5, key: 'hsk_5_coverage', label: 'HSK 5', class: 'hsk-5' },
        { id: 6, key: 'hsk_6_coverage', label: 'HSK 6', class: 'hsk-6' },
        { id: 0, key: 'unknown_coverage', label: 'Unknown', class: 'hsk-unknown' }
    ];

    levels.forEach(lvl => {
        const val = data[lvl.key] || 0;
        if (val > 0.001 || lvl.id === 0) { // Show if non-zero
            const percent = (val * 100).toFixed(1) + '%';

            const html = `
                <div class="bar-container ${lvl.class}">
                    <div class="bar-label">
                        <span>${lvl.label}</span>
                        <span>${percent}</span>
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill" style="width: ${percent}"></div>
                    </div>
                </div>
            `;
            barsContainer.innerHTML += html;
        }
    });

    resultArea.style.display = 'block';
}

function formatPercent(val) {
    return (val * 100).toFixed(1) + '%';
}
