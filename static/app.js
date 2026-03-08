/* ================================================================
   AI Financial Advisor — Frontend JS
   ================================================================ */

// ---------- THEME ----------
const html = document.documentElement;
const saved = localStorage.getItem('theme');
if (saved) html.setAttribute('data-theme', saved);

// Theme toggle - attached after DOM check
document.addEventListener('DOMContentLoaded', () => {
    const themeBtn = document.getElementById('themeToggle');
    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            const next = html.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
            html.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
        });
    }
});

// ---------- AUTH ----------
const authOverlay = document.getElementById('authOverlay');
const appSidebar = document.getElementById('appSidebar');
const appMain = document.getElementById('appMain');

function switchAuthTab(tab) {
    document.getElementById('loginForm').style.display = tab === 'login' ? 'block' : 'none';
    document.getElementById('signupForm').style.display = tab === 'signup' ? 'block' : 'none';
    document.getElementById('tabLogin').classList.toggle('active', tab === 'login');
    document.getElementById('tabSignup').classList.toggle('active', tab === 'signup');
    document.getElementById('loginMsg').textContent = '';
    document.getElementById('signupMsg').textContent = '';
}
// Make switchAuthTab globally accessible for onclick
window.switchAuthTab = switchAuthTab;

function showApp(username) {
    authOverlay.style.display = 'none';
    appSidebar.style.display = '';
    appMain.style.display = '';
    document.getElementById('displayUser').textContent = username;
    // Auto-load saved profile into the form
    autoLoadProfile();
}

async function autoLoadProfile() {
    try {
        const res = await fetch('/api/profile');
        const data = await res.json();
        if (data.status === 'ok') {
            const u = data.data;
            document.getElementById('pName').value = u.Name || '';
            document.getElementById('pAge').value = u.Age || '';
            document.getElementById('pIncome').value = u.Income || '';
            document.getElementById('pSavings').value = u.Savings || '';
            document.getElementById('pExpenses').value = u.Expenses || '';
        }
    } catch { /* ignore if no profile yet */ }
}

function showAuth() {
    authOverlay.style.display = 'flex';
    appSidebar.style.display = 'none';
    appMain.style.display = 'none';
}

// Check if already logged in
(async function checkSession() {
    try {
        const res = await fetch('/api/me');
        const data = await res.json();
        if (data.status === 'ok' && data.logged_in) {
            showApp(data.username);
        } else {
            showAuth();
        }
    } catch {
        showAuth();
    }
})();

// Login form
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('loginUser').value.trim();
    const password = document.getElementById('loginPass').value;
    const msgEl = document.getElementById('loginMsg');

    const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    const data = await res.json();

    if (data.status === 'ok') {
        msgEl.textContent = data.message;
        msgEl.className = 'msg success';
        showApp(data.username);
    } else {
        msgEl.textContent = data.message;
        msgEl.className = 'msg error';
    }
});

// Signup form
document.getElementById('signupForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('signupUser').value.trim();
    const phone = document.getElementById('signupPhone').value.trim();
    const password = document.getElementById('signupPass').value;
    const password2 = document.getElementById('signupPass2').value;
    const msgEl = document.getElementById('signupMsg');

    if (password !== password2) {
        msgEl.textContent = 'Passwords do not match!';
        msgEl.className = 'msg error';
        return;
    }

    const res = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password, phone })
    });
    const data = await res.json();

    if (data.status === 'ok') {
        msgEl.textContent = data.message;
        msgEl.className = 'msg success';
        showApp(data.username);
    } else {
        msgEl.textContent = data.message;
        msgEl.className = 'msg error';
    }
});

// Logout
document.getElementById('logoutBtn').addEventListener('click', async () => {
    await fetch('/api/logout', { method: 'POST' });
    showAuth();
    document.getElementById('loginUser').value = '';
    document.getElementById('loginPass').value = '';
});

// ---------- NAV ----------
const navBtns = document.querySelectorAll('.nav-btn');
const sections = document.querySelectorAll('.section');
const pageTitle = document.getElementById('pageTitle');
const titles = {
    profile: 'User Profile',
    predictions: 'Market Predictions',
    risk: 'Risk Analysis',
    portfolio: 'Portfolio Allocation',
    charts: 'Live Stock Charts',
    advice: 'AI Advice',
    report: 'Full Report'
};

navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const sec = btn.dataset.section;
        navBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        sections.forEach(s => s.classList.remove('active'));
        document.getElementById('sec-' + sec).classList.add('active');
        pageTitle.textContent = titles[sec] || '';
    });
});

// ---------- HELPERS ----------
function setStatus(loading) {
    const dot = document.getElementById('statusDot');
    const txt = document.getElementById('statusText');
    if (loading) {
        dot.classList.add('loading');
        txt.textContent = 'Loading...';
    } else {
        dot.classList.remove('loading');
        txt.textContent = 'Ready';
    }
}

function showMsg(id, text, type) {
    const el = document.getElementById(id);
    el.textContent = text;
    el.className = 'msg ' + type;
}

function fmt(n) {
    return Number(n).toLocaleString('en-IN');
}

async function api(url, opts) {
    setStatus(true);
    try {
        const res = await fetch(url, opts);
        return await res.json();
    } finally {
        setStatus(false);
    }
}

// ---------- PROFILE ----------
const profileForm = document.getElementById('profileForm');
profileForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const body = {
        name: document.getElementById('pName').value.trim(),
        age: document.getElementById('pAge').value,
        income: document.getElementById('pIncome').value,
        savings: document.getElementById('pSavings').value,
        expenses: document.getElementById('pExpenses').value
    };
    const data = await api('/api/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    if (data.status === 'ok') {
        showMsg('profileMsg', 'Profile saved successfully!', 'success');
    } else {
        showMsg('profileMsg', data.message, 'error');
    }
});

document.getElementById('loadProfileBtn').addEventListener('click', async () => {
    const data = await api('/api/profile');
    if (data.status === 'ok') {
        const u = data.data;
        document.getElementById('pName').value = u.Name || '';
        document.getElementById('pAge').value = u.Age || '';
        document.getElementById('pIncome').value = u.Income || '';
        document.getElementById('pSavings').value = u.Savings || '';
        document.getElementById('pExpenses').value = u.Expenses || '';
        showMsg('profileMsg', 'Profile loaded.', 'success');
    } else {
        showMsg('profileMsg', data.message, 'error');
    }
});

// ---------- PREDICTIONS ----------
document.getElementById('loadPredBtn').addEventListener('click', loadPredictions);

let _autoRefreshTimer = null;
let _countdownTimer = null;
let _countdownSec = 0;

// Fetch fresh data from Yahoo Finance
document.getElementById('fetchDataBtn').addEventListener('click', fetchLiveData);

async function fetchLiveData() {
    const btn = document.getElementById('fetchDataBtn');
    btn.disabled = true;
    btn.textContent = 'Fetching...';
    showMsg('predMsg', 'Fetching live data from Yahoo Finance...', 'success');
    try {
        const res = await fetch('/api/fetch-data', { method: 'POST' });
        const data = await res.json();
        if (data.status === 'ok') {
            showMsg('predMsg', data.message, 'success');
            await loadPredictions();
        } else {
            showMsg('predMsg', data.message, 'error');
        }
    } catch { showMsg('predMsg', 'Failed to fetch data.', 'error'); }
    btn.disabled = false;
    btn.textContent = '\u21BB Fetch Live';
}

// Auto-refresh toggle
document.getElementById('autoRefreshToggle').addEventListener('change', (e) => {
    if (e.target.checked) {
        startAutoRefresh();
    } else {
        stopAutoRefresh();
    }
});

document.getElementById('refreshInterval').addEventListener('change', () => {
    if (document.getElementById('autoRefreshToggle').checked) {
        stopAutoRefresh();
        startAutoRefresh();
    }
});

function startAutoRefresh() {
    const intervalSec = parseInt(document.getElementById('refreshInterval').value);
    const liveBar = document.getElementById('liveBar');
    liveBar.style.display = 'flex';

    // Fetch + load immediately
    fetchAndRefresh();

    _countdownSec = intervalSec;
    _countdownTimer = setInterval(() => {
        _countdownSec--;
        document.getElementById('liveCountdown').textContent = `Next refresh in ${_countdownSec}s`;
        if (_countdownSec <= 0) _countdownSec = intervalSec;
    }, 1000);

    _autoRefreshTimer = setInterval(() => {
        _countdownSec = intervalSec;
        fetchAndRefresh();
    }, intervalSec * 1000);
}

function stopAutoRefresh() {
    clearInterval(_autoRefreshTimer);
    clearInterval(_countdownTimer);
    _autoRefreshTimer = null;
    _countdownTimer = null;
    document.getElementById('liveBar').style.display = 'none';
}

async function fetchAndRefresh() {
    try {
        await fetch('/api/fetch-data', { method: 'POST' });
    } catch { /* ignore fetch errors in auto-mode */ }
    await loadPredictions();
}

async function loadPredictions() {
    const data = await api('/api/predictions');
    if (data.status !== 'ok') {
        showMsg('predMsg', data.message, 'error');
        return;
    }
    const s = data.summary;
    document.getElementById('predSummary').innerHTML =
        `<div class="summary-chip">Total<span class="val">${s.total}</span></div>` +
        `<div class="summary-chip" style="color:var(--green)">BUY<span class="val">${s.buy}</span></div>` +
        `<div class="summary-chip" style="color:var(--red)">SELL<span class="val">${s.sell}</span></div>` +
        `<div class="summary-chip" style="color:var(--yellow)">HOLD<span class="val">${s.hold}</span></div>`;

    const tbody = document.querySelector('#predTable tbody');
    tbody.innerHTML = data.data.map(r => {
        const cls = r.action === 'BUY' ? 'badge-buy' : r.action === 'SELL' ? 'badge-sell' : 'badge-hold';
        return `<tr>
            <td>${r.name}</td>
            <td>${fmt(r.current)}</td>
            <td>${fmt(r.predicted)}</td>
            <td><span class="badge ${cls}">${r.action}</span></td>
        </tr>`;
    }).join('');

    // Update live timestamp
    if (data.last_updated) {
        document.getElementById('liveUpdated').textContent = `Last data: ${data.last_updated}`;
    }
    showMsg('predMsg', '', '');
}

// ---------- RISK ----------
document.getElementById('loadRiskBtn').addEventListener('click', loadRisk);

async function loadRisk() {
    const data = await api('/api/risk');
    if (data.status !== 'ok') { showMsg('riskMsg', data.message, 'error'); return; }
    const r = data.data;
    const u = data.user;
    const barClass = r.level === 'Aggressive' ? 'aggressive' : r.level === 'Moderate' ? 'moderate' : 'conservative';

    document.getElementById('riskContent').innerHTML = `
        <div class="risk-grid">
            <div class="risk-stat"><div class="label">Name</div><div class="value">${u.Name || 'N/A'}</div></div>
            <div class="risk-stat"><div class="label">Age</div><div class="value">${u.Age || 'N/A'}</div></div>
            <div class="risk-stat"><div class="label">Monthly Income</div><div class="value">&#8377;${fmt(u.Income || 0)}</div></div>
            <div class="risk-stat"><div class="label">Total Savings</div><div class="value">&#8377;${fmt(u.Savings || 0)}</div></div>
            <div class="risk-stat"><div class="label">Monthly Expenses</div><div class="value">&#8377;${fmt(u.Expenses || 0)}</div></div>
            <div class="risk-stat"><div class="label">Disposable Income</div><div class="value">&#8377;${fmt(r.disposable_income)}</div></div>
            <div class="risk-stat"><div class="label">Monthly Investable</div><div class="value">&#8377;${fmt(r.monthly_investable)}</div></div>
            <div class="risk-stat"><div class="label">Risk Level</div><div class="value"><span class="badge badge-${barClass === 'aggressive' ? 'sell' : barClass === 'moderate' ? 'hold' : 'buy'}">${r.level}</span></div></div>
        </div>
        <div class="score-bar-wrap">
            <div class="score-bar-label"><span>Risk Score</span><span>${r.score}/100</span></div>
            <div class="score-bar"><div class="score-bar-fill ${barClass}" style="width:${r.score}%"></div></div>
        </div>
    `;
    showMsg('riskMsg', '', '');
}

// ---------- PORTFOLIO ----------
document.getElementById('loadPortBtn').addEventListener('click', loadPortfolio);

async function loadPortfolio() {
    const data = await api('/api/portfolio');
    if (data.status !== 'ok') { showMsg('portMsg', data.message, 'error'); return; }
    const p = data.data;
    const alloc = p.allocation;
    const barColors = { 'Stocks': 'stocks', 'Mutual Funds': 'mf', 'ETFs': 'etf', 'Fixed Deposit': 'fd' };

    let allocHTML = '<div class="alloc-list">';
    for (const [cat, det] of Object.entries(alloc)) {
        allocHTML += `
            <div class="alloc-item">
                <div class="alloc-label">${cat}</div>
                <div class="alloc-bar-wrap"><div class="alloc-bar ${barColors[cat] || 'stocks'}" style="width:${det.percentage}%"></div></div>
                <div class="alloc-pct">${det.percentage}%</div>
                <div class="alloc-amt">&#8377;${fmt(det.amount)}</div>
            </div>`;
    }
    allocHTML += '</div>';

    // Stock picks with details (change %, action)
    const stockDetails = p.stock_details || [];
    const etfDetails = p.etf_details || [];

    let picksHTML = `<h3 style="font-size:14px;color:var(--text-secondary);margin-bottom:8px">Recommended Stocks (${stockDetails.length})</h3>`;
    if (stockDetails.length > 0) {
        picksHTML += '<div class="picks-detail-list">';
        stockDetails.forEach(s => {
            const cls = s.action === 'BUY' ? 'badge-buy' : s.action === 'SELL' ? 'badge-sell' : 'badge-hold';
            const arrow = s.change_pct >= 0 ? '+' : '';
            picksHTML += `<div class="pick-detail-item">
                <span class="pick-name">${s.name}</span>
                <span class="badge ${cls}">${s.action}</span>
                <span class="pick-change" style="color:${s.change_pct >= 0 ? 'var(--green)' : 'var(--red)'}">${arrow}${s.change_pct}%</span>
            </div>`;
        });
        picksHTML += '</div>';
    } else {
        picksHTML += '<div class="picks-row">';
        p.stock_picks.forEach(s => { picksHTML += `<div class="pick-tag">${s}</div>`; });
        picksHTML += '</div>';
    }

    picksHTML += `<h3 style="font-size:14px;color:var(--text-secondary);margin:18px 0 8px">Recommended ETFs (${etfDetails.length})</h3>`;
    if (etfDetails.length > 0) {
        picksHTML += '<div class="picks-detail-list">';
        etfDetails.forEach(e => {
            const cls = e.action === 'BUY' ? 'badge-buy' : e.action === 'SELL' ? 'badge-sell' : 'badge-hold';
            const arrow = e.change_pct >= 0 ? '+' : '';
            picksHTML += `<div class="pick-detail-item">
                <span class="pick-name">${e.name}</span>
                <span class="badge ${cls}">${e.action}</span>
                <span class="pick-change" style="color:${e.change_pct >= 0 ? 'var(--green)' : 'var(--red)'}">${arrow}${e.change_pct}%</span>
            </div>`;
        });
        picksHTML += '</div>';
    } else {
        picksHTML += '<div class="picks-row">';
        p.etf_picks.forEach(s => { picksHTML += `<div class="pick-tag">${s}</div>`; });
        picksHTML += '</div>';
    }

    document.getElementById('portContent').innerHTML = `
        <div class="port-info">
            <div class="port-info-item"><div class="label">Risk Score</div><div class="value">${p.risk_score || 'N/A'}/100</div></div>
            <div class="port-info-item"><div class="label">Monthly Invest</div><div class="value">&#8377;${fmt(p.monthly_investable)}</div></div>
            <div class="port-info-item"><div class="label">Expected Return</div><div class="value">${p.expected_return}</div></div>
        </div>
        <p style="font-size:13px;color:var(--text-muted);margin-bottom:16px">${p.description || ''}</p>
        ${allocHTML}
        ${picksHTML}
    `;
    showMsg('portMsg', '', '');
}

// ---------- AI ADVICE ----------
document.getElementById('loadAdviceBtn').addEventListener('click', loadAdvice);

async function loadAdvice() {
    const box = document.getElementById('adviceContent');
    box.innerHTML = '<span class="spinner"></span> AI se advice le rahe hain, thoda wait karo...';
    const data = await api('/api/advice');
    if (data.status !== 'ok') {
        box.textContent = '';
        showMsg('adviceMsg', data.message, 'error');
        return;
    }
    box.textContent = data.advice;
    showMsg('adviceMsg', '', '');
}

// ---------- REPORT ----------
document.getElementById('genReportBtn').addEventListener('click', async () => {
    const box = document.getElementById('reportContent');
    box.textContent = 'Generating full report... Please wait.';
    const data = await api('/api/report');
    if (data.status !== 'ok') {
        box.textContent = '';
        showMsg('reportMsg', data.message, 'error');
        return;
    }
    box.textContent = data.report;
    showMsg('reportMsg', 'Report generated & saved: ' + data.file, 'success');
});

document.getElementById('dlReportBtn').addEventListener('click', () => {
    window.location.href = '/api/report/download';
});

// ---------- LIVE CHARTS ----------
let _stockChart = null;
let _chartAutoTimer = null;
let _chartCountdownTimer = null;
let _chartCountdownSec = 0;

// Load stock list into dropdown
(async function loadStockList() {
    try {
        const res = await fetch('/api/stock-list');
        const data = await res.json();
        if (data.status === 'ok') {
            const sel = document.getElementById('chartStockSelect');
            data.symbols.forEach(sym => {
                const opt = document.createElement('option');
                opt.value = sym;
                opt.textContent = sym;
                sel.appendChild(opt);
            });
        }
    } catch { /* ignore */ }
})();

document.getElementById('loadChartBtn').addEventListener('click', liveChartRefresh);

document.getElementById('chartStockSelect').addEventListener('change', () => {
    if (document.getElementById('chartStockSelect').value) liveChartRefresh();
});

// Live auto-refresh toggle
document.getElementById('chartAutoToggle').addEventListener('change', (e) => {
    if (e.target.checked) { startChartAutoRefresh(); } else { stopChartAutoRefresh(); }
});
document.getElementById('chartRefreshInterval').addEventListener('change', () => {
    if (document.getElementById('chartAutoToggle').checked) {
        stopChartAutoRefresh(); startChartAutoRefresh();
    }
});

function startChartAutoRefresh() {
    const sym = document.getElementById('chartStockSelect').value;
    if (!sym) { showMsg('chartMsg', 'Select a stock first, then enable Live.', 'error'); document.getElementById('chartAutoToggle').checked = false; return; }
    const intervalSec = parseInt(document.getElementById('chartRefreshInterval').value);
    document.getElementById('chartLiveBar').style.display = 'flex';
    liveChartRefresh();
    _chartCountdownSec = intervalSec;
    _chartCountdownTimer = setInterval(() => {
        _chartCountdownSec--;
        document.getElementById('chartLiveCountdown').textContent = `Next refresh in ${_chartCountdownSec}s`;
        if (_chartCountdownSec <= 0) _chartCountdownSec = intervalSec;
    }, 1000);
    _chartAutoTimer = setInterval(() => {
        _chartCountdownSec = intervalSec;
        liveChartRefresh();
    }, intervalSec * 1000);
}

function stopChartAutoRefresh() {
    clearInterval(_chartAutoTimer); clearInterval(_chartCountdownTimer);
    _chartAutoTimer = null; _chartCountdownTimer = null;
    document.getElementById('chartLiveBar').style.display = 'none';
}

async function liveChartRefresh() {
    const symbol = document.getElementById('chartStockSelect').value;
    if (!symbol) { showMsg('chartMsg', 'Please select a stock first.', 'error'); return; }

    // If auto mode, fetch fresh data first
    if (document.getElementById('chartAutoToggle').checked) {
        try { await fetch('/api/fetch-data', { method: 'POST' }); } catch {}
    }

    const data = await api('/api/chart-data?symbol=' + encodeURIComponent(symbol));
    if (data.status !== 'ok') { showMsg('chartMsg', data.message, 'error'); return; }

    // Info bar
    const diff = data.predicted_next - data.current_price;
    const diffPct = ((diff / data.current_price) * 100).toFixed(2);
    const action = diff > 0 ? 'BUY' : diff < 0 ? 'SELL' : 'HOLD';
    const actionCls = action === 'BUY' ? 'badge-buy' : action === 'SELL' ? 'badge-sell' : 'badge-hold';
    const arrow = diff >= 0 ? '+' : '';

    const infoEl = document.getElementById('chartInfo');
    infoEl.style.display = 'flex';
    infoEl.innerHTML = `
        <div class="chart-stat"><span class="label">Symbol</span><span class="value">${data.symbol}</span></div>
        <div class="chart-stat"><span class="label">Current</span><span class="value">&#8377;${fmt(data.current_price)}</span></div>
        <div class="chart-stat"><span class="label">ML Next Price</span><span class="value" style="color:${diff >= 0 ? 'var(--green)' : 'var(--red)'}">&#8377;${fmt(data.predicted_next)}</span></div>
        <div class="chart-stat"><span class="label">Change</span><span class="value" style="color:${diff >= 0 ? 'var(--green)' : 'var(--red)'}">${arrow}${diffPct}%</span></div>
        <div class="chart-stat"><span class="label">Signal</span><span class="badge ${actionCls}">${action}</span></div>
        <div class="chart-stat"><span class="label">Data</span><span class="value">${data.data_points} pts</span></div>
    `;

    // Technical Indicators Panel
    const ind = data.indicators || {};
    const indEl = document.getElementById('chartIndicators');
    indEl.style.display = 'block';
    const sigColor = (sig) => {
        if (sig === 'Bullish' || sig === 'Oversold' || sig === 'Strong Buy' || sig === 'Buy' || sig === 'Strong Trend') return 'var(--green)';
        if (sig === 'Bearish' || sig === 'Overbought' || sig === 'Strong Sell' || sig === 'Sell') return 'var(--red)';
        return 'var(--yellow)';
    };
    const overallIcon = ind.overall === 'Strong Buy' ? '🟢' : ind.overall === 'Buy' ? '📈' : ind.overall === 'Neutral' ? '⏸' : ind.overall === 'Sell' ? '📉' : '🔴';
    indEl.innerHTML = `
        <div class="ind-header">
            <span class="ind-title">📊 Technical Indicators</span>
            <span class="ind-overall" style="color:${sigColor(ind.overall)}">${overallIcon} ${ind.overall || 'N/A'} (${ind.tech_score || 50}%)</span>
        </div>
        <div class="ind-grid">
            <div class="ind-card">
                <div class="ind-name">RSI (14)</div>
                <div class="ind-val">${ind.rsi != null ? ind.rsi : 'N/A'}</div>
                <div class="ind-sig" style="color:${sigColor(ind.rsi_signal)}">${ind.rsi_signal || 'N/A'}</div>
                <div class="ind-bar"><div class="ind-fill" style="width:${ind.rsi != null ? ind.rsi : 50}%;background:${ind.rsi > 70 ? 'var(--red)' : ind.rsi < 30 ? 'var(--green)' : 'var(--yellow)'}"></div></div>
            </div>
            <div class="ind-card">
                <div class="ind-name">Bollinger Bands</div>
                <div class="ind-val">${ind.bb_upper != null ? '₹' + fmt(ind.bb_lower) + ' — ₹' + fmt(ind.bb_upper) : 'N/A'}</div>
                <div class="ind-sig" style="color:${sigColor(ind.bb_signal)}">${ind.bb_signal || 'N/A'}</div>
                <div class="ind-detail">Mid: ${ind.bb_middle != null ? '₹' + fmt(ind.bb_middle) : 'N/A'}</div>
            </div>
            <div class="ind-card">
                <div class="ind-name">EMA Cross</div>
                <div class="ind-val">EMA9: ₹${fmt(ind.ema9)} | EMA21: ₹${fmt(ind.ema21)}</div>
                <div class="ind-sig" style="color:${sigColor(ind.ema_signal)}">${ind.ema_signal || 'N/A'}</div>
                <div class="ind-detail">${ind.ema_signal === 'Bullish' ? 'EMA9 > EMA21 ↑' : ind.ema_signal === 'Bearish' ? 'EMA9 < EMA21 ↓' : 'Flat'}</div>
            </div>
            <div class="ind-card">
                <div class="ind-name">MACD (12,26,9)</div>
                <div class="ind-val">MACD: ${ind.macd} | Signal: ${ind.macd_signal_line}</div>
                <div class="ind-sig" style="color:${sigColor(ind.macd_signal)}">${ind.macd_signal || 'N/A'}</div>
                <div class="ind-detail">Histogram: <b style="color:${ind.macd_histogram >= 0 ? 'var(--green)':'var(--red)'}">${ind.macd_histogram >= 0 ? '+' : ''}${ind.macd_histogram}</b></div>
            </div>
            <div class="ind-card">
                <div class="ind-name">SuperTrend</div>
                <div class="ind-val">${ind.st_upper != null ? '₹' + fmt(ind.st_lower) + ' — ₹' + fmt(ind.st_upper) : 'N/A'}</div>
                <div class="ind-sig" style="color:${sigColor(ind.supertrend)}">${ind.supertrend || 'N/A'}</div>
            </div>
            <div class="ind-card">
                <div class="ind-name">Stochastic (14,3)</div>
                <div class="ind-val">%K: ${ind.stoch_k != null ? ind.stoch_k : 'N/A'} | %D: ${ind.stoch_d != null ? ind.stoch_d : 'N/A'}</div>
                <div class="ind-sig" style="color:${sigColor(ind.stoch_signal)}">${ind.stoch_signal || 'N/A'}</div>
                <div class="ind-bar"><div class="ind-fill" style="width:${ind.stoch_k != null ? ind.stoch_k : 50}%;background:${ind.stoch_k > 80 ? 'var(--red)' : ind.stoch_k < 20 ? 'var(--green)' : 'var(--yellow)'}"></div></div>
            </div>
            <div class="ind-card">
                <div class="ind-name">Williams %R (14)</div>
                <div class="ind-val">${ind.williams_r != null ? ind.williams_r : 'N/A'}</div>
                <div class="ind-sig" style="color:${sigColor(ind.williams_signal)}">${ind.williams_signal || 'N/A'}</div>
            </div>
            <div class="ind-card">
                <div class="ind-name">CCI (20)</div>
                <div class="ind-val">${ind.cci != null ? ind.cci : 'N/A'}</div>
                <div class="ind-sig" style="color:${sigColor(ind.cci_signal)}">${ind.cci_signal || 'N/A'}</div>
            </div>
            <div class="ind-card">
                <div class="ind-name">ADX (14)</div>
                <div class="ind-val">${ind.adx != null ? ind.adx : 'N/A'}</div>
                <div class="ind-sig" style="color:${sigColor(ind.adx_signal)}">${ind.adx_signal || 'N/A'}</div>
            </div>
            <div class="ind-card">
                <div class="ind-name">Pivot Points</div>
                <div class="ind-val">${ind.pivot != null ? 'P: ₹'+fmt(ind.pivot) : 'N/A'}</div>
                <div class="ind-sig" style="color:${sigColor(ind.pivot_signal)}">${ind.pivot_signal || 'N/A'}</div>
                <div class="ind-detail">${ind.s1 != null ? 'S1: ₹'+fmt(ind.s1)+' R1: ₹'+fmt(ind.r1) : ''}</div>
            </div>
        </div>
    `;

    // Future predictions comparison table (all models side by side)
    const trendFut = data.trend_future || [];
    const momFut = data.future_prices || [];
    const rfFut = data.rf_future || [];
    const gbFut = data.gb_future || [];
    const ensFut = data.ensemble_future || [];
    if (momFut.length > 0) {
        const futEl = document.getElementById('chartFuture');
        futEl.style.display = 'block';
        const polyAcc = data.poly_accuracy || 0;
        const momAcc = data.momentum_accuracy || 0;
        const rfAcc = data.rf_accuracy || 0;
        const gbAcc = data.gb_accuracy || 0;
        const best = data.better_model || 'momentum';
        let futHtml = `<div class="future-header">Future Predictions — Model Comparison</div>`;
        futHtml += `<div class="accuracy-bar">
            <span class="acc-chip" style="border-color:${best==='poly'?'var(--green)':'var(--border)'}">
                <span class="acc-dot" style="background:var(--yellow)"></span>
                Poly: <b>${polyAcc}%</b> ${best==='poly'?'⭐':''}
            </span>
            <span class="acc-chip" style="border-color:${best==='momentum'?'var(--green)':'var(--border)'}">
                <span class="acc-dot" style="background:var(--green)"></span>
                Mom: <b>${momAcc}%</b> ${best==='momentum'?'⭐':''}
            </span>
            <span class="acc-chip" style="border-color:${best==='rf'?'var(--green)':'var(--border)'}">
                <span class="acc-dot" style="background:#f97316"></span>
                RF: <b>${rfAcc}%</b> ${best==='rf'?'⭐':''}
            </span>
            <span class="acc-chip" style="border-color:${best==='gb'?'var(--green)':'var(--border)'}">
                <span class="acc-dot" style="background:#ec4899"></span>
                GB: <b>${gbAcc}%</b> ${best==='gb'?'⭐':''}
            </span>
            <span class="acc-chip" style="border-color:var(--accent)">
                <span class="acc-dot" style="background:var(--accent)"></span>
                Ensemble: weighted avg
            </span>
        </div>`;
        futHtml += '<table class="future-table"><thead><tr><th>Step</th><th>Poly (₹)</th><th>Mom (₹)</th><th>RF (₹)</th><th>GB (₹)</th><th>Ensemble (₹)</th><th>Change</th></tr></thead><tbody>';
        for (let i = 0; i < momFut.length; i++) {
            const tp = trendFut[i] || '-';
            const mp = momFut[i];
            const rp = rfFut[i] || '-';
            const gp = gbFut[i] || '-';
            const ep = ensFut[i] || '-';
            const ed = typeof ep === 'number' ? ((ep - data.current_price) / data.current_price * 100).toFixed(2) : '-';
            const ec = typeof ep === 'number' ? (ep >= data.current_price ? 'var(--green)' : 'var(--red)') : '';
            futHtml += `<tr>
                <td>+${i+1}</td>
                <td>₹${typeof tp === 'number' ? fmt(tp) : '-'}</td>
                <td>₹${fmt(mp)}</td>
                <td>₹${typeof rp === 'number' ? fmt(rp) : '-'}</td>
                <td>₹${typeof gp === 'number' ? fmt(gp) : '-'}</td>
                <td style="font-weight:700">₹${typeof ep === 'number' ? fmt(ep) : '-'}</td>
                <td style="color:${ec}">${typeof ed === 'string' && ed !== '-' ? (parseFloat(ed)>=0?'+':'') + ed + '%' : '-'}</td>
            </tr>`;
        }
        futHtml += '</tbody></table>';
        futEl.innerHTML = futHtml;
    }

    // Backtest Proof Table — shows predicted vs actual for last N known prices
    const bt = data.backtest || [];
    if (bt.length > 0) {
        const btEl = document.getElementById('chartBacktest');
        btEl.style.display = 'block';
        const polyAcc3 = data.poly_accuracy || 0;
        const momAcc3 = data.momentum_accuracy || 0;
        const rfAcc3 = data.rf_accuracy || 0;
        const gbAcc3 = data.gb_accuracy || 0;
        const best3 = data.better_model || 'momentum';
        const bestLabel = {poly:'Poly Trend', momentum:'Momentum', rf:'Random Forest', gb:'Gradient Boost'}[best3] || best3;
        let btHtml = `<div class="bt-header">
            <span class="bt-title">🔍 Backtest Proof — Predicted vs Actual (Last ${bt.length} Points)</span>
            <span class="bt-verdict" style="color:var(--green)">
                Winner: ${bestLabel}
            </span>
        </div>`;
        btHtml += `<div class="bt-desc">Model was trained on earlier data only, then asked to predict these prices. Compare predicted vs what actually happened:</div>`;
        btHtml += '<table class="future-table"><thead><tr><th>Date</th><th>Actual (₹)</th><th>Poly</th><th>Err%</th><th>Mom.</th><th>Err%</th><th>RF</th><th>Err%</th><th>GB</th><th>Err%</th></tr></thead><tbody>';
        for (const row of bt) {
            const tShort = row.time.length > 10 ? row.time.substring(5) : row.time;
            const pColor = row.poly_err <= 1 ? 'var(--green)' : row.poly_err <= 3 ? 'var(--yellow)' : 'var(--red)';
            const mColor = row.mom_err <= 1 ? 'var(--green)' : row.mom_err <= 3 ? 'var(--yellow)' : 'var(--red)';
            const rColor = (row.rf_err != null && row.rf_err <= 1) ? 'var(--green)' : (row.rf_err != null && row.rf_err <= 3) ? 'var(--yellow)' : 'var(--red)';
            const gColor = (row.gb_err != null && row.gb_err <= 1) ? 'var(--green)' : (row.gb_err != null && row.gb_err <= 3) ? 'var(--yellow)' : 'var(--red)';
            btHtml += `<tr>
                <td>${tShort}</td>
                <td style="font-weight:700">₹${fmt(row.actual)}</td>
                <td>₹${fmt(row.poly_pred)}</td>
                <td style="color:${pColor};font-weight:700">${row.poly_err}%</td>
                <td>₹${fmt(row.mom_pred)}</td>
                <td style="color:${mColor};font-weight:700">${row.mom_err}%</td>
                <td>${row.rf_pred != null ? '₹'+fmt(row.rf_pred) : '-'}</td>
                <td style="color:${rColor};font-weight:700">${row.rf_err != null ? row.rf_err+'%' : '-'}</td>
                <td>${row.gb_pred != null ? '₹'+fmt(row.gb_pred) : '-'}</td>
                <td style="color:${gColor};font-weight:700">${row.gb_err != null ? row.gb_err+'%' : '-'}</td>
            </tr>`;
        }
        btHtml += '</tbody></table>';
        btHtml += `<div class="bt-summary">
            <span>Poly: <b style="color:var(--yellow)">${polyAcc3}%</b></span>
            <span>Mom: <b style="color:var(--green)">${momAcc3}%</b></span>
            <span>RF: <b style="color:#f97316">${rfAcc3}%</b></span>
            <span>GB: <b style="color:#ec4899">${gbAcc3}%</b></span>
            <span class="bt-legend">Error: <span style="color:var(--green)">●</span>&lt;1% <span style="color:var(--yellow)">●</span>1-3% <span style="color:var(--red)">●</span>&gt;3%</span>
        </div>`;
        btEl.innerHTML = btHtml;
    }

    // Model explanation card
    const explEl = document.getElementById('chartExplain');
    explEl.style.display = 'block';
    const polyAcc2 = data.poly_accuracy || 0;
    const momAcc2 = data.momentum_accuracy || 0;
    const rfAcc2 = data.rf_accuracy || 0;
    const gbAcc2 = data.gb_accuracy || 0;
    const bestModel = data.better_model || 'momentum';
    const bestName = {poly:'Poly Trend', momentum:'Momentum', rf:'Random Forest', gb:'Gradient Boost'}[bestModel] || bestModel;
    explEl.innerHTML = `
        <div class="explain-title">How These Predictions Work</div>
        <div class="explain-grid">
            <div class="explain-item">
                <div class="explain-icon" style="color:var(--accent)">●</div>
                <div><b>Actual Price</b> (Blue Line)<br>Raw market price from Yahoo Finance.</div>
            </div>
            <div class="explain-item">
                <div class="explain-icon" style="color:#c084fc">●</div>
                <div><b>Smoothed (EMA)</b> (Purple Line)<br>Exponential Moving Average — reduces noise to show the true trend.</div>
            </div>
            <div class="explain-item">
                <div class="explain-icon" style="color:var(--yellow)">◆</div>
                <div><b>Poly Trend</b> — ${polyAcc2}%<br>Polynomial Regression (degree 3) on all data. Captures overall curve. Good for long-term trend.</div>
            </div>
            <div class="explain-item">
                <div class="explain-icon" style="color:var(--green)">■</div>
                <div><b>Momentum</b> — ${momAcc2}%<br>Weighted Linear Regression on last 10 points. Recent prices get more weight. Good for short-term direction.</div>
            </div>
            <div class="explain-item">
                <div class="explain-icon" style="color:#f97316">▲</div>
                <div><b>Random Forest</b> — ${rfAcc2}%<br>Ensemble of 100 decision trees using 3-lag features. Captures non-linear patterns and local structure.</div>
            </div>
            <div class="explain-item">
                <div class="explain-icon" style="color:#ec4899">◇</div>
                <div><b>Gradient Boost</b> — ${gbAcc2}%<br>Boosted trees (100 estimators) using 3-lag features. Learns from errors iteratively — strong on complex patterns.</div>
            </div>
            <div class="explain-item">
                <div class="explain-icon" style="color:var(--accent)">★</div>
                <div><b>Ensemble</b><br>Accuracy-weighted average of all 4 models. The best model gets the highest weight. Most robust prediction.</div>
            </div>
        </div>
        <div class="explain-verdict">
            ⭐ <b>${bestName}</b> was most accurate on recent data (backtested on last 5 price points).<br>
            📊 Predictions are <b>adjusted</b> using 10 technical indicators (RSI, BB, EMA, MACD, SuperTrend, Stochastic, Williams %R, CCI, ADX, Pivot Points).
        </div>
    `;

    // Live updated time
    if (data.last_updated) {
        document.getElementById('chartLiveUpdated').textContent = `Last data: ${data.last_updated}`;
    }

    renderStockChart(data);
    showMsg('chartMsg', '', '');
}

function renderStockChart(data) {
    const ctx = document.getElementById('stockChart').getContext('2d');
    if (_stockChart) _stockChart.destroy();

    const isDark = html.getAttribute('data-theme') === 'dark';
    const gridColor = isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)';
    const textColor = isDark ? '#a0a5b5' : '#5a6170';
    const futureCount = data.future_prices ? data.future_prices.length : 0;
    const totalLen = data.labels.length;
    const histLen = totalLen - futureCount;

    // Labels
    const shortLabels = data.labels.map((l, i) => {
        if (l.startsWith('Future')) return l;
        const parts = l.split(' ');
        return (parts[0] || '').slice(5) + ' ' + (parts[1] ? parts[1].slice(0, 5) : '');
    });

    // Point sizes
    const n = histLen;
    const ptR = n > 30 ? 2 : n > 15 ? 3 : 5;
    const ptH = n > 30 ? 5 : n > 15 ? 6 : 8;

    // Raw actual prices — matches the Current Price shown in the info bar
    const actualData = data.actual_prices;

    // EMA smoothed prices
    const smoothedData = data.smoothed_prices || data.actual_prices;

    // ML Poly Trend — full range (historical poly curve + poly extrapolation)
    const predData = data.predicted_prices;

    // Momentum Forecast — separate model, only future portion
    const momentumFuture = data.future_prices || [];
    const futureZone = new Array(histLen).fill(null).concat(momentumFuture);

    _stockChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: shortLabels,
            datasets: [
                {
                    label: 'Actual Price (₹)',
                    data: actualData,
                    borderColor: isDark ? '#6b8aff' : '#4f6ef7',
                    backgroundColor: isDark ? 'rgba(107,138,255,0.05)' : 'rgba(79,110,247,0.03)',
                    borderWidth: 1.5,
                    pointRadius: ptR,
                    pointHoverRadius: ptH,
                    pointBackgroundColor: isDark ? '#6b8aff' : '#4f6ef7',
                    fill: true,
                    tension: 0,
                    spanGaps: false
                },
                {
                    label: 'Smoothed (EMA) (₹)',
                    data: smoothedData,
                    borderColor: isDark ? '#c084fc' : '#9333ea',
                    backgroundColor: 'transparent',
                    borderWidth: 2.5,
                    pointRadius: 0,
                    pointHoverRadius: ptH - 1,
                    pointBackgroundColor: isDark ? '#c084fc' : '#9333ea',
                    fill: false,
                    tension: 0.4,
                    spanGaps: false
                },
                {
                    label: 'Poly Trend (₹)',
                    data: predData,
                    borderColor: isDark ? '#facc15' : '#ca8a04',
                    backgroundColor: 'transparent',
                    borderWidth: 2.5,
                    borderDash: [6, 3],
                    pointRadius: ptR - 1,
                    pointHoverRadius: ptH - 1,
                    pointBackgroundColor: isDark ? '#facc15' : '#ca8a04',
                    fill: false,
                    tension: 0.3
                },
                {
                    label: 'Momentum (₹)',
                    data: futureZone,
                    borderColor: isDark ? '#4ade80' : '#16a34a',
                    backgroundColor: isDark ? 'rgba(74,222,128,0.15)' : 'rgba(22,163,74,0.1)',
                    borderWidth: 3,
                    borderDash: [4, 2],
                    pointRadius: 6,
                    pointHoverRadius: 9,
                    pointBackgroundColor: isDark ? '#4ade80' : '#16a34a',
                    pointStyle: 'rectRounded',
                    fill: true,
                    tension: 0,
                    spanGaps: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: {
                    labels: { color: textColor, font: { size: 13, weight: '600' }, usePointStyle: true }
                },
                tooltip: {
                    backgroundColor: isDark ? '#1c1f2b' : '#fff',
                    titleColor: isDark ? '#e4e6eb' : '#1a1d23',
                    bodyColor: isDark ? '#a0a5b5' : '#5a6170',
                    borderColor: isDark ? '#2a2e3c' : '#e0e0e0',
                    borderWidth: 1, padding: 12,
                    callbacks: {
                        title: function(items) { return data.labels[items[0].dataIndex] || items[0].label; },
                        label: function(c) {
                            if (c.raw === null) return '';
                            return c.dataset.label + ': ₹' + Number(c.raw).toLocaleString('en-IN');
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: gridColor, display: false },
                    ticks: { color: textColor, font: { size: 10 }, maxRotation: 50, maxTicksLimit: 14, autoSkip: true }
                },
                y: {
                    grid: { color: gridColor },
                    ticks: { color: textColor, font: { size: 12 }, callback: v => '₹' + Number(v).toLocaleString('en-IN') }
                }
            }
        }
    });
}
