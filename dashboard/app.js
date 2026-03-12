const COLORS = {
    danger: '#ef4444',
    warning: '#f59e0b',
    secondary: '#3b82f6',
    success: '#10b981',
    purple: '#a855f7',
    muted: '#8888aa',
    text: '#e0e0ff',
    card: '#12122a',
    grid: '#2a2a4a',
};

Chart.defaults.color = COLORS.text;
Chart.defaults.borderColor = COLORS.grid;
Chart.defaults.font.family = "'Inter', sans-serif";

const DATA = {};

async function loadJSON(name) {
    const res = await fetch(`data/${name}.json`);
    return res.json();
}

async function loadAllData() {
    const files = [
        'metrics_comparison', 'for_distribution', 'trust_evolution',
        'label_noise_experiment', 'dispatch_results', 'scenario_presets',
        'merchant_profiles',
    ];
    const results = await Promise.all(files.map(f => loadJSON(f).catch(() => null)));
    files.forEach((f, i) => { DATA[f] = results[i]; });
}

function renderHeroStats() {
    const m = DATA.metrics_comparison;
    if (!m) return;
    const blMAE = m.mae[0], kpMAE = m.mae[m.mae.length - 1];
    const blP90 = m.p90_error[0], kpP90 = m.p90_error[m.p90_error.length - 1];
    const maeDrop = Math.round((1 - kpMAE / blMAE) * 100);
    const p90Drop = Math.round((1 - kpP90 / blP90) * 100);
    document.getElementById('stat-mae-drop').textContent = `↓${maeDrop}%`;
    document.getElementById('stat-p90-drop').textContent = `↓${p90Drop}%`;
    document.getElementById('stat-orders').textContent = '304K';
}

function renderMAEChart() {
    const m = DATA.metrics_comparison;
    if (!m) return;
    const ctx = document.getElementById('chart-mae').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: m.models,
            datasets: [{
                data: m.mae,
                backgroundColor: [COLORS.danger, COLORS.warning, COLORS.secondary, COLORS.success],
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => `MAE: ${ctx.raw.toFixed(1)} min`
                    }
                }
            },
            scales: {
                y: { beginAtZero: true, title: { display: true, text: 'MAE (minutes)' } }
            }
        }
    });
}

function renderP90Chart() {
    const m = DATA.metrics_comparison;
    if (!m) return;
    const ctx = document.getElementById('chart-p90').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: m.models,
            datasets: [{
                data: m.p90_error,
                backgroundColor: [COLORS.danger, COLORS.warning, COLORS.secondary, COLORS.success],
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => `P90 Error: ${ctx.raw.toFixed(1)} min`
                    }
                }
            },
            scales: {
                y: { beginAtZero: true, title: { display: true, text: 'P90 Error (minutes)' } }
            }
        }
    });
}

function renderAccuracyChart() {
    const m = DATA.metrics_comparison;
    if (!m) return;
    const ctx = document.getElementById('chart-accuracy').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: m.models,
            datasets: [
                {
                    label: 'Within ±3min',
                    data: m.within_3min.map(v => v * 100),
                    backgroundColor: COLORS.success + '99',
                    borderRadius: 6,
                },
                {
                    label: 'Within ±5min',
                    data: m.within_5min.map(v => v * 100),
                    backgroundColor: COLORS.secondary + '99',
                    borderRadius: 6,
                },
            ]
        },
        options: {
            responsive: true,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: ctx => `${ctx.dataset.label}: ${ctx.raw.toFixed(0)}%`
                    }
                }
            },
            scales: {
                y: { beginAtZero: true, max: 100, title: { display: true, text: '% Orders' } }
            }
        }
    });
}

function renderTailChart() {
    const m = DATA.metrics_comparison;
    if (!m) return;
    const ctx = document.getElementById('chart-tail').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: m.models,
            datasets: [
                { label: 'P90', data: m.p90_error, backgroundColor: COLORS.warning + 'CC', borderRadius: 4 },
                { label: 'P95', data: m.models.map((_, i) => (DATA.metrics_comparison.p90_error[i] * 1.15)), backgroundColor: COLORS.danger + 'CC', borderRadius: 4 },
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true, title: { display: true, text: 'Error (minutes)' } }
            }
        }
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
        const minIdx = row.key.includes('within') ? vals.indexOf(Math.max(...vals)) : vals.indexOf(Math.min(...vals));
        const cells = vals.map((v, i) => {
            const cls = i === minIdx ? ' class="best-metric"' : '';
            return `<td${cls}>${row.fmt(v)}</td>`;
        }).join('');
        return `<tr><td>${row.label}</td>${cells}</tr>`;
    }).join('');
}

function renderFORPie() {
    const d = DATA.for_distribution;
    if (!d) return;
    const ctx = document.getElementById('chart-for-pie').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Honest', 'Rider-Triggered', 'Lazy/Late', 'Missing'],
            datasets: [{
                data: [d.honest_pct, d.rider_triggered_pct, d.lazy_pct, d.missing_pct],
                backgroundColor: [COLORS.success, COLORS.danger, COLORS.warning, COLORS.muted],
                borderColor: '#0a0a1a',
                borderWidth: 3,
            }]
        },
        options: {
            responsive: true,
            cutout: '65%',
            plugins: {
                legend: { position: 'bottom', labels: { padding: 16, font: { size: 12 } } },
                tooltip: {
                    callbacks: {
                        label: ctx => `${ctx.label}: ${ctx.raw}%`
                    }
                }
            }
        }
    });
}

function renderFORCards() {
    const container = document.getElementById('for-cards');
    const cards = [
        { cls: 'for-honest', title: `✅ Honest (~30%)`, desc: 'Merchant presses "Food Ready" when food is actually ready. Closest to ground truth.' },
        { cls: 'for-rider', title: `🔴 Rider-Triggered (~35%)`, desc: 'Merchant presses FOR only after rider arrives and asks — timestamp reflects rider arrival, not food readiness.' },
        { cls: 'for-lazy', title: `🟡 Lazy/Late (~20%)`, desc: 'Merchant presses FOR minutes after food is ready — creates artificial delay in the signal.' },
        { cls: 'for-missing', title: `⚪ Missing (~15%)`, desc: 'Merchant never presses FOR — no signal available at all for these orders.' },
    ];
    container.innerHTML = cards.map(c =>
        `<div class="for-card-item ${c.cls}"><h4>${c.title}</h4><p>${c.desc}</p></div>`
    ).join('');
}

function renderTrustEvolution() {
    const te = DATA.trust_evolution;
    if (!te || te.length === 0) return;

    const container = document.getElementById('trust-selector');
    container.innerHTML = te.map((m, i) =>
        `<button class="trust-btn${i === 0 ? ' active' : ''}" data-idx="${i}">${m.archetype} #${m.merchant_id}</button>`
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
            backgroundColor: 'transparent',
            borderWidth: 2.5,
            pointRadius: 4,
            tension: 0.3,
        }));

        const ctx = document.getElementById('chart-trust-evolution').getContext('2d');
        if (chart) chart.destroy();
        chart = new Chart(ctx, {
            type: 'line',
            data: { labels, datasets },
            options: {
                responsive: true,
                scales: {
                    x: { title: { display: true, text: 'Orders Processed' } },
                    y: { min: 0, max: 0.65, title: { display: true, text: 'Signal Weight' } },
                },
                plugins: {
                    legend: { position: 'bottom', labels: { padding: 12 } }
                }
            }
        });
    }

    drawTrust(0);

    container.addEventListener('click', e => {
        const btn = e.target.closest('.trust-btn');
        if (!btn) return;
        container.querySelectorAll('.trust-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        drawTrust(parseInt(btn.dataset.idx));
    });
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

    const datasets = signals.map((s, j) => ({
        label: s.toUpperCase(),
        data: matrix.map(row => parseFloat(row[j].toFixed(3))),
        backgroundColor: [COLORS.danger + 'CC', COLORS.secondary + 'CC', COLORS.warning + 'CC', COLORS.success + 'CC', COLORS.muted + 'CC'][j],
        borderRadius: 4,
    }));

    const ctx = document.getElementById('chart-archetype-heatmap').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: { labels: archLabels, datasets },
        options: {
            responsive: true,
            scales: {
                x: { stacked: true },
                y: { stacked: true, max: 1, title: { display: true, text: 'Weight Share' } },
            },
            plugins: {
                legend: { position: 'bottom', labels: { padding: 12 } }
            }
        }
    });
}

function renderNoiseChart() {
    const n = DATA.label_noise_experiment;
    if (!n) return;
    const ctx = document.getElementById('chart-noise').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: n.map(r => r.noise_pct_label),
            datasets: [
                {
                    label: 'MAE',
                    data: n.map(r => r.mae),
                    borderColor: COLORS.danger,
                    backgroundColor: COLORS.danger + '33',
                    fill: true,
                    borderWidth: 3,
                    pointRadius: 6,
                    tension: 0.3,
                },
                {
                    label: 'P90 Error',
                    data: n.map(r => r.p90_error),
                    borderColor: COLORS.warning,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [6, 4],
                    pointRadius: 5,
                    tension: 0.3,
                },
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: { title: { display: true, text: 'Error (minutes)' } }
            },
            plugins: {
                legend: { position: 'bottom' },
                annotation: {}
            }
        }
    });
}

function renderDispatchCharts() {
    const d = DATA.dispatch_results;
    if (!d) return;
    const names = Object.keys(d);
    const colors = [COLORS.danger, COLORS.warning, COLORS.secondary, COLORS.success];

    const ctx1 = document.getElementById('chart-rider-wait').getContext('2d');
    new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: names,
            datasets: [{
                data: names.map(n => d[n].avg_rider_wait),
                backgroundColor: colors.slice(0, names.length),
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, title: { display: true, text: 'Avg Rider Wait (min)' } }
            }
        }
    });

    const ctx2 = document.getElementById('chart-food-cool').getContext('2d');
    new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: names,
            datasets: [{
                data: names.map(n => d[n].avg_food_cool),
                backgroundColor: colors.slice(0, names.length),
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, title: { display: true, text: 'Avg Food Cooling (min)' } }
            }
        }
    });
}

function renderScenarios() {
    const s = DATA.scenario_presets;
    if (!s) return;
    const grid = document.getElementById('scenario-grid');
    grid.innerHTML = s.map(item => {
        const sc = item.result || item;
        const name = item.name || sc.name || 'Scenario';
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
                <div class="scenario-detail"><span class="label">Baseline Pred</span><span class="value bad">${blPred.toFixed(1)} min (err: ${blErr.toFixed(1)})</span></div>
                <div class="scenario-detail"><span class="label">KP Pred</span><span class="value ${improved ? 'good' : ''}">${kpPred.toFixed(1)} min (err: ${kpErr.toFixed(1)})</span></div>
                <div class="scenario-detail"><span class="label">Verdict</span><span class="value ${improved ? 'good' : 'bad'}">${improved ? '✅ KP Wins' : '⚠️ Baseline closer'}</span></div>
            </div>
        `;
    }).join('');
}

// Navigation
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

// Main
async function init() {
    await loadAllData();
    renderHeroStats();
    renderMAEChart();
    renderP90Chart();
    renderAccuracyChart();
    renderTailChart();
    renderMetricsTable();
    renderFORPie();
    renderFORCards();
    renderTrustEvolution();
    renderArchetypeHeatmap();
    renderNoiseChart();
    renderDispatchCharts();
    renderScenarios();
    setupNav();
}

init();
