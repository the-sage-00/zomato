const COLORS = {
    danger: '#E23744', warning: '#f59e0b', secondary: '#e0e0e0',
    success: '#2ecc71', purple: '#E23744', muted: '#777',
    text: '#f5f5f5', card: '#141414', grid: '#2a2a2a',
};
Chart.defaults.color = COLORS.text;
Chart.defaults.borderColor = COLORS.grid;
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.maintainAspectRatio = false;

const DATA = {};

async function loadJSON(name) {
    const res = await fetch(`data/${name}.json`);
    return res.json();
}

async function loadAllData() {
    const files = [
        'metrics_comparison', 'for_distribution', 'trust_evolution',
        'label_noise_experiment', 'dispatch_results', 'scenario_presets',
        'merchant_profiles', 'sample_orders', 'biryani_story', 'for_examples',
    ];
    const results = await Promise.all(files.map(f => loadJSON(f).catch(() => null)));
    files.forEach((f, i) => { DATA[f] = results[i]; });
}

/* ==================== SECTION 1: HERO ==================== */
function renderHeroStats() {
    const m = DATA.metrics_comparison;
    if (!m) return;
    const blMAE = m.mae[0], kpMAE = m.mae[m.mae.length - 1];
    const blP90 = m.p90_error[0], kpP90 = m.p90_error[m.p90_error.length - 1];
    
    const elements = document.querySelectorAll('.animate-num');
    if (elements.length >= 2) {
        elements[0].setAttribute('data-target', Math.round((1 - kpMAE / blMAE) * 100));
        elements[1].setAttribute('data-target', Math.round((1 - kpP90 / blP90) * 100));
    }
}

/* ==================== SECTION 2: DATA ==================== */
function renderSampleData() {
    const d = DATA.sample_orders;
    if (!d) return;
    const tbody = document.getElementById('sample-tbody');
    tbody.innerHTML = d.map(row => {
        let gapCls = 'gap-missing';
        let gapText = '—';
        if (row.for_gap !== null) {
            if (row.for_gap <= 2) { gapCls = 'gap-good'; gapText = `${row.for_gap} min ✅`; }
            else if (row.for_gap <= 5) { gapCls = 'gap-warn'; gapText = `${row.for_gap} min ⚠️`; }
            else { gapCls = 'gap-bad'; gapText = `${row.for_gap} min ❌`; }
        }
        const forText = row.for_timestamp !== null ? `${row.for_timestamp}` : '—';
        const forCls = row.for_timestamp === null ? 'gap-missing' : '';
        return `<tr>
            <td>${row.archetype.replace('_', ' ')}</td>
            <td>${row.for_behavior}</td>
            <td><strong>${row.true_kpt}</strong></td>
            <td class="${forCls}">${forText}</td>
            <td class="${gapCls}">${gapText}</td>
            <td>${row.rider_arrival}</td>
            <td>${row.ack_latency}s</td>
        </tr>`;
    }).join('');
}

/* ==================== SECTION 3: FOR PROBLEM ==================== */
function renderFORPie() {
    const d = DATA.for_distribution;
    if (!d) return;
    new Chart(document.getElementById('chart-for-pie').getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: ['Honest', 'Rider-Triggered', 'Lazy/Late', 'Missing'],
            datasets: [{
                data: [d.honest_pct, d.rider_triggered_pct, d.lazy_pct, d.missing_pct],
                backgroundColor: [COLORS.success, COLORS.danger, COLORS.warning, COLORS.muted],
                borderColor: '#0a0a1a', borderWidth: 3,
            }]
        },
        options: {
            responsive: true, cutout: '65%',
            plugins: {
                legend: { position: 'bottom', labels: { padding: 16, font: { size: 11 } } },
                tooltip: { callbacks: { label: ctx => `${ctx.label}: ${ctx.raw}%` } }
            }
        }
    });
}

/* renderFORExamples removed — no matching DOM element exists */

function renderFORCards() {
    const container = document.getElementById('for-cards');
    const d = DATA.for_distribution;
    const h = d ? Math.round(d.honest_pct) : 52;
    const r = d ? Math.round(d.rider_triggered_pct) : 26;
    const l = d ? Math.round(d.lazy_pct) : 10;
    const m = d ? Math.round(d.missing_pct) : 12;
    const cards = [
        { cls: 'for-honest', title: `✅ Honest (~${h}%)`, desc: 'Presses FOR when food is actually ready. Closest to ground truth.' },
        { cls: 'for-rider', title: `🔴 Rider-Triggered (~${r}%)`, desc: 'Presses only after rider arrives and asks — timestamp = rider arrival.' },
        { cls: 'for-lazy', title: `🟡 Lazy/Late (~${l}%)`, desc: 'Presses FOR minutes after food is ready — artificial delay.' },
        { cls: 'for-missing', title: `⚪ Missing (~${m}%)`, desc: 'Never presses FOR — no signal available at all.' },
    ];
    container.innerHTML = cards.map(c =>
        `<div class="for-card-item ${c.cls}"><h4>${c.title}</h4><p>${c.desc}</p></div>`
    ).join('');
}

/* ==================== SECTION 4: SOLUTION ==================== */
function renderTrustEvolution() {
    const te = DATA.trust_evolution;
    if (!te || te.length === 0) return;
    const container = document.getElementById('trust-selector');
    container.innerHTML = te.map((m, i) =>
        `<button class="trust-btn${i === 0 ? ' active' : ''}" data-idx="${i}">${m.archetype.replace('_',' ')} #${m.merchant_id}</button>`
    ).join('');
    let chart = null;
    function drawTrust(idx) {
        const m = te[idx];
        const hist = m.weight_history;
        const labels = hist.map(h => h.at_order);
        const datasets = ['for', 'dwell', 'behavior', 'akai', 'external'].map((sig, i) => ({
            label: sig.toUpperCase(),
            data: hist.map(h => h.weights[sig] || 0),
            borderColor: [COLORS.danger, COLORS.secondary, COLORS.warning, COLORS.success, COLORS.muted][i],
            backgroundColor: 'transparent', borderWidth: 2.5, pointRadius: 4, tension: 0.3,
        }));
        const ctx = document.getElementById('chart-trust-evolution').getContext('2d');
        if (chart) chart.destroy();
        chart = new Chart(ctx, {
            type: 'line', data: { labels, datasets },
            options: {
                responsive: true,
                scales: { x: { title: { display: true, text: 'Orders' } }, y: { min: 0, max: 0.65, title: { display: true, text: 'Weight' } } },
                plugins: { legend: { position: 'bottom', labels: { padding: 12 } } }
            }
        });
    }
    drawTrust(0);
    container.addEventListener('click', e => {
        const btn = e.target.closest('.trust-btn');
        if (!btn || btn.id === 'btn-autoplay') return;
        container.querySelectorAll('.trust-btn:not(#btn-autoplay)').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        drawTrust(parseInt(btn.dataset.idx));
    });

    let autoPlayInterval = null;
    const btnAutoplay = document.getElementById('btn-autoplay');
    if (btnAutoplay) {
        btnAutoplay.addEventListener('click', () => {
            if (autoPlayInterval) {
                clearInterval(autoPlayInterval);
                autoPlayInterval = null;
                btnAutoplay.textContent = '▶ Auto-Play';
                btnAutoplay.style.color = 'var(--success)';
                btnAutoplay.style.borderColor = 'var(--success)';
            } else {
                btnAutoplay.textContent = '⏸ Pause';
                btnAutoplay.style.color = 'var(--warning)';
                btnAutoplay.style.borderColor = 'var(--warning)';
                let currentIdx = Array.from(container.querySelectorAll('.trust-btn:not(#btn-autoplay)')).findIndex(b => b.classList.contains('active'));
                autoPlayInterval = setInterval(() => {
                    const buttons = container.querySelectorAll('.trust-btn:not(#btn-autoplay)');
                    currentIdx = (currentIdx + 1) % buttons.length;
                    if (buttons[currentIdx]) buttons[currentIdx].click();
                }, 2000); // Change chart every 2 seconds
            }
        });
    }
}

function renderArchetypeHeatmap() {
    const profiles = DATA.merchant_profiles;
    if (!profiles) return;
    const archetypes = ['cloud_kitchen', 'qsr_chain', 'dine_in', 'street_food'];
    const archLabels = ['Cloud Kitchen', 'QSR Chain', 'Dine-in', 'Street Food'];
    const signals = ['for', 'dwell', 'behavior', 'akai', 'external'];
    const matrix = Array.from({ length: 4 }, () => Array(5).fill(0));
    const counts = Array(4).fill(0);
    profiles.forEach(p => {
        const ai = archetypes.indexOf(p.archetype);
        if (ai < 0) return;
        signals.forEach((s, j) => { matrix[ai][j] += (p.current_weights[s] || 0); });
        counts[ai]++;
    });
    for (let i = 0; i < 4; i++) if (counts[i] > 0) matrix[i] = matrix[i].map(v => v / counts[i]);

    new Chart(document.getElementById('chart-archetype-heatmap').getContext('2d'), {
        type: 'bar',
        data: {
            labels: archLabels,
            datasets: signals.map((s, j) => ({
                label: s.toUpperCase(),
                data: matrix.map(row => parseFloat(row[j].toFixed(3))),
                backgroundColor: [COLORS.danger + 'CC', COLORS.secondary + 'CC', COLORS.warning + 'CC', COLORS.success + 'CC', COLORS.muted + 'CC'][j],
                borderRadius: 4,
            }))
        },
        options: {
            responsive: true,
            scales: { x: { stacked: true }, y: { stacked: true, max: 1, title: { display: true, text: 'Weight Share' } } },
            plugins: { legend: { position: 'bottom', labels: { padding: 12 } } }
        }
    });
}

/* ==================== SECTION 5: RESULTS ==================== */
function renderMAEChart() {
    const m = DATA.metrics_comparison;
    if (!m) return;
    new Chart(document.getElementById('chart-mae').getContext('2d'), {
        type: 'bar',
        data: {
            labels: m.models,
            datasets: [{ data: m.mae, backgroundColor: [COLORS.danger, COLORS.warning, COLORS.secondary, COLORS.success], borderRadius: 8, borderSkipped: false }]
        },
        options: { responsive: true, plugins: { legend: { display: false }, tooltip: { callbacks: { label: ctx => `MAE: ${ctx.raw.toFixed(1)} min` } } }, scales: { y: { beginAtZero: true, title: { display: true, text: 'MAE (minutes)' } } } }
    });
}

function renderP90Chart() {
    const m = DATA.metrics_comparison;
    if (!m) return;
    new Chart(document.getElementById('chart-p90').getContext('2d'), {
        type: 'bar',
        data: {
            labels: m.models,
            datasets: [{ data: m.p90_error, backgroundColor: [COLORS.danger, COLORS.warning, COLORS.secondary, COLORS.success], borderRadius: 8, borderSkipped: false }]
        },
        options: { responsive: true, plugins: { legend: { display: false }, tooltip: { callbacks: { label: ctx => `P90: ${ctx.raw.toFixed(1)} min` } } }, scales: { y: { beginAtZero: true, title: { display: true, text: 'P90 Error (minutes)' } } } }
    });
}

function renderAccuracyChart() {
    const m = DATA.metrics_comparison;
    if (!m) return;
    new Chart(document.getElementById('chart-accuracy').getContext('2d'), {
        type: 'bar',
        data: {
            labels: m.models,
            datasets: [
                { label: 'Within ±3min', data: m.within_3min.map(v => v * 100), backgroundColor: COLORS.success + '99', borderRadius: 6 },
                { label: 'Within ±5min', data: m.within_5min.map(v => v * 100), backgroundColor: COLORS.secondary + '99', borderRadius: 6 },
            ]
        },
        options: { responsive: true, scales: { y: { beginAtZero: true, max: 100, title: { display: true, text: '% Orders' } } } }
    });
}

function renderTailChart() {
    const m = DATA.metrics_comparison;
    if (!m) return;
    new Chart(document.getElementById('chart-tail').getContext('2d'), {
        type: 'bar',
        data: {
            labels: m.models,
            datasets: [
                { label: 'P90', data: m.p90_error, backgroundColor: COLORS.warning + 'CC', borderRadius: 4 },
                { label: 'P95', data: m.p95_error, backgroundColor: COLORS.danger + 'CC', borderRadius: 4 },
            ]
        },
        options: { responsive: true, scales: { y: { beginAtZero: true, title: { display: true, text: 'Error (minutes)' } } } }
    });
}

function renderMetricsTable() {
    const m = DATA.metrics_comparison;
    if (!m) return;
    const tbody = document.getElementById('metrics-tbody');
    const rows = [
        { label: 'MAE (min)', key: 'mae', fmt: v => v.toFixed(1) },
        { label: 'Median Error', key: 'p50_error', fmt: v => v.toFixed(1) },
        { label: 'P90 Error', key: 'p90_error', fmt: v => v.toFixed(1) },
        { label: 'Within ±3min', key: 'within_3min', fmt: v => (v * 100).toFixed(0) + '%' },
        { label: 'Within ±5min', key: 'within_5min', fmt: v => (v * 100).toFixed(0) + '%' },
        { label: 'ETA Volatility', key: 'avg_eta_volatility', fmt: v => v.toFixed(2) },
    ];
    tbody.innerHTML = rows.map(row => {
        const vals = m[row.key];
        if (!vals) return '';
        const bestIdx = row.key.includes('within') ? vals.indexOf(Math.max(...vals)) : vals.indexOf(Math.min(...vals));
        const cells = vals.map((v, i) => `<td${i === bestIdx ? ' class="best-metric"' : ''}>${row.fmt(v)}</td>`).join('');
        return `<tr><td>${row.label}</td>${cells}</tr>`;
    }).join('');
}

/* ==================== SECTION 6: BIRYANI ==================== */
function renderBiryaniTimeline() {
    const story = DATA.biryani_story;
    if (!story) return;
    const container = document.getElementById('biryani-container');

    function makePanel(timeline, cls) {
        const predError = Math.abs(timeline.prediction - story.true_kpt).toFixed(1);
        const errCls = predError > 5 ? 'bad' : 'good';
        const waitCls = timeline.rider_wait > 5 ? 'bad' : 'good';
        return `
            <div class="timeline-panel">
                <div class="timeline-title ${cls}">${timeline.label}</div>
                <div class="biryani-stats-grid">
                    <div class="biryani-stat">
                        <span class="biryani-stat-label">Predicted KPT</span>
                        <span class="biryani-stat-val">${timeline.prediction} min</span>
                    </div>
                    <div class="biryani-stat">
                        <span class="biryani-stat-label">Actual KPT</span>
                        <span class="biryani-stat-val">${story.true_kpt} min</span>
                    </div>
                    <div class="biryani-stat">
                        <span class="biryani-stat-label">Prediction Error</span>
                        <span class="biryani-stat-val ${errCls}">${predError} min</span>
                    </div>
                    <div class="biryani-stat">
                        <span class="biryani-stat-label">Rider Wait</span>
                        <span class="biryani-stat-val ${waitCls}">${timeline.rider_wait} min</span>
                    </div>
                </div>
            </div>
        `;
    }
    container.innerHTML = makePanel(story.without_kp, 'bad') + makePanel(story.with_kp, 'good');
}

function renderDispatchCharts() {
    const d = DATA.dispatch_results;
    if (!d) return;
    const names = Object.keys(d);
    const colors = [COLORS.danger, COLORS.warning, COLORS.secondary, COLORS.success];

    new Chart(document.getElementById('chart-rider-wait').getContext('2d'), {
        type: 'bar',
        data: { labels: names, datasets: [{ data: names.map(n => d[n].avg_rider_wait), backgroundColor: colors, borderRadius: 8, borderSkipped: false }] },
        options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, title: { display: true, text: 'Avg Rider Wait (min)' } } } }
    });
    new Chart(document.getElementById('chart-food-cool').getContext('2d'), {
        type: 'bar',
        data: { labels: names, datasets: [{ data: names.map(n => d[n].avg_food_cool), backgroundColor: colors, borderRadius: 8, borderSkipped: false }] },
        options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, title: { display: true, text: 'Avg Food Cooling (min)' } } } }
    });
}

/* ==================== SECTION 7: SCIENCE ==================== */
function renderNoiseChart() {
    const n = DATA.label_noise_experiment;
    if (!n) return;
    new Chart(document.getElementById('chart-noise').getContext('2d'), {
        type: 'line',
        data: {
            labels: n.map(r => r.noise_pct_label),
            datasets: [
                { label: 'MAE', data: n.map(r => r.mae), borderColor: COLORS.danger, backgroundColor: COLORS.danger + '33', fill: true, borderWidth: 3, pointRadius: 6, tension: 0.3 },
                { label: 'P90 Error', data: n.map(r => r.p90_error), borderColor: COLORS.warning, backgroundColor: 'transparent', borderWidth: 2, borderDash: [6, 4], pointRadius: 5, tension: 0.3 },
            ]
        },
        options: {
            responsive: true,
            scales: { y: { title: { display: true, text: 'Error (minutes)' } } },
            plugins: { legend: { position: 'bottom' } }
        }
    });
}

function renderScenarios() {
    const s = DATA.scenario_presets;
    if (!s) return;
    const grid = document.getElementById('scenario-grid');
    grid.innerHTML = s.map(item => {
        const sc = item.result || item;
        const name = item.name || 'Scenario';
        const trueKpt = sc.true_kpt;
        const blPred = sc.baseline_prediction || sc.baseline_pred || 0;
        const kpPred = sc.kp_prediction || sc.kp_pred || 0;
        const blErr = Math.abs(blPred - trueKpt);
        const kpErr = Math.abs(kpPred - trueKpt);
        const improved = kpErr < blErr;
        return `
            <div class="scenario-card">
                <div class="scenario-name">${name}</div>
                <div class="scenario-detail"><span class="label">True KPT</span><span class="value">${trueKpt.toFixed(1)} min</span></div>
                <div class="scenario-detail"><span class="label">Baseline</span><span class="value bad">${blPred.toFixed(1)} min (err: ${blErr.toFixed(1)})</span></div>
                <div class="scenario-detail"><span class="label">KP Pred</span><span class="value ${improved ? 'good' : ''}">${kpPred.toFixed(1)} min (err: ${kpErr.toFixed(1)})</span></div>
                <div class="scenario-detail"><span class="label">Verdict</span><span class="value ${improved ? 'good' : 'bad'}">${improved ? '✅ KP Wins' : '⚠️ Baseline closer'}</span></div>
            </div>
        `;
    }).join('');
}

/* ==================== NAV ==================== */
function setupNav() {
    const links = document.querySelectorAll('.nav-link');
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                links.forEach(l => l.classList.remove('active'));
                const link = document.querySelector(`.nav-link[data-section="${entry.target.id}"]`);
                if (link) link.classList.add('active');
            }
        });
    }, { threshold: 0.3 });
    document.querySelectorAll('.section').forEach(s => observer.observe(s));
}

/* ==================== ANIMATIONS ==================== */
function initAnimations() {
    // 1. Scroll Reveal (Intersection Observer)
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, { threshold: 0.15 });
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

    // 2. Number Counter Animation
    const animateNumber = (el, target, isRaw) => {
        let current = 0;
        const increment = target / 60; // 60 frames approx 1 sec
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            if (isRaw) {
                el.textContent = Math.floor(current).toLocaleString();
            } else {
                el.textContent = '↓' + Math.floor(current) + '%';
            }
        }, 16);
    };

    const numObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.classList.contains('counted')) {
                entry.target.classList.add('counted');
                const target = parseInt(entry.target.getAttribute('data-target'));
                if (!isNaN(target)) {
                    animateNumber(entry.target, target, entry.target.classList.contains('animate-num-raw'));
                }
            }
        });
    }, { threshold: 0.5 });
    document.querySelectorAll('.animate-num, .animate-num-raw').forEach(el => numObserver.observe(el));
}

/* ==================== SCROLL PROGRESS + SCROLL-TO-TOP ==================== */
function initScrollFeatures() {
    const progressBar = document.getElementById('scroll-progress');
    const scrollTopBtn = document.getElementById('scroll-top');

    window.addEventListener('scroll', () => {
        // Progress bar
        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
        if (progressBar) progressBar.style.width = progress + '%';

        // Scroll-to-top button
        if (scrollTopBtn) {
            if (scrollTop > 400) {
                scrollTopBtn.classList.add('visible');
            } else {
                scrollTopBtn.classList.remove('visible');
            }
        }
    }, { passive: true });

    if (scrollTopBtn) {
        scrollTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
}

/* ==================== LOADING OVERLAY ==================== */
function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('hidden');
        setTimeout(() => overlay.remove(), 700);
    }
}

/* ==================== INIT ==================== */
async function init() {
    initAnimations();
    initScrollFeatures();

    await loadAllData();

    renderHeroStats();
    renderSampleData();
    renderFORPie();
    /* renderFORExamples removed */
    renderFORCards();
    renderTrustEvolution();
    renderArchetypeHeatmap();
    renderMAEChart();
    renderP90Chart();
    renderAccuracyChart();
    renderTailChart();
    renderMetricsTable();
    renderBiryaniTimeline();
    renderDispatchCharts();
    renderNoiseChart();
    renderScenarios();
    setupNav();

    hideLoadingOverlay();
}
init();

