// SmartMoneyTracker Web Interface JavaScript

// API Base URL
const API_BASE = window.location.origin;
const LANGUAGE_STORAGE_KEY = 'smartmoneytracker-language';
const DEFAULT_LANGUAGE = 'en';

const translations = {
    en: {
        pageTitle: 'SmartMoneyTracker - Institutional Flow Analysis',
        githubAria: 'View source on GitHub',
        languageSelector: 'Language',
        subtitle: 'Track smart money across the full institutional accumulation and distribution cycle',
        stockAnalysis: 'Stock Analysis',
        tickerLabel: 'Ticker',
        tickerPlaceholder: 'e.g. 600519.SH, AAPL, 0700.HK',
        marketsHelp: 'Supports Chinese A-shares, US stocks, and Hong Kong stocks',
        lookbackDays: 'Lookback Period',
        days60: '60 days',
        days120: '120 days',
        days250: '250 days',
        days500: '500 days',
        structureAnalysis: 'Enable structural signal analysis',
        analyze: 'Analyze',
        batchAnalysis: 'Batch Analysis',
        batchTickerLabel: 'Ticker list (one per line)',
        batchPlaceholder: '600519.SH\n000858.SZ\nAAPL',
        batchAnalyze: 'Analyze Batch',
        results: 'Analysis Results',
        clear: 'Clear',
        inflowSignals: 'Inflow Signals',
        outflowSignals: 'Outflow Signals',
        totalSignals: 'Total Signals',
        accumulationSignals: 'Inflow Signals (Accumulation)',
        distributionSignals: 'Outflow Signals (Distribution)',
        recommendation: 'Recommendation',
        fullReport: 'View Full Report',
        batchCompletePrefix: 'Analysis completed for',
        batchCompleteSuffix: 'stocks',
        analyzing: 'Analyzing...',
        disclaimer: 'For educational and research purposes only. This tool does not constitute investment advice. Investing involves risk.',
        close: 'Close',
        analysisTime: 'Analysis time',
        noSignals: 'No signals detected',
        noDescription: 'No description',
        date: 'Date',
        signalSummary: 'Signals: {total} (inflow: {inflow}, outflow: {outflow})',
        tickerRequired: 'Enter a ticker symbol.',
        tickersRequired: 'Enter at least one ticker symbol.',
        validTickerRequired: 'Enter a valid ticker symbol.',
        analysisFailed: 'Analysis failed. Please try again.',
        batchAnalysisFailed: 'Batch analysis failed. Please try again.',
        dataUnavailable: 'Market data is currently unavailable. Please try again later.',
        reportTitle: 'Smart Money Tracker - Institutional Flow Analysis Report',
        ticker: 'Ticker',
        overallScore: 'Overall Score',
        rating: 'Rating',
        triggeredSignals: 'Triggered Signals',
        reportDisclaimer: 'Disclaimer: For educational and research purposes only. This report does not constitute investment advice.'
    },
    'zh-CN': {
        pageTitle: 'SmartMoneyTracker - 聪明钱追踪系统',
        githubAria: '在 GitHub 上查看源代码',
        languageSelector: '语言',
        subtitle: '追踪“聪明钱”的足迹 - 机构资金进出场全周期识别系统',
        stockAnalysis: '股票分析',
        tickerLabel: '股票代码',
        tickerPlaceholder: '例如：600519.SH、AAPL、0700.HK',
        marketsHelp: '支持 A 股、美股、港股',
        lookbackDays: '回看天数',
        days60: '60 天',
        days120: '120 天',
        days250: '250 天',
        days500: '500 天',
        structureAnalysis: '启用结构性信号分析',
        analyze: '开始分析',
        batchAnalysis: '批量分析',
        batchTickerLabel: '股票代码列表（每行一个）',
        batchPlaceholder: '600519.SH\n000858.SZ\nAAPL',
        batchAnalyze: '批量分析',
        results: '分析结果',
        clear: '清除',
        inflowSignals: '进场信号',
        outflowSignals: '离场信号',
        totalSignals: '总信号数',
        accumulationSignals: '进场信号（吸筹）',
        distributionSignals: '离场信号（派发）',
        recommendation: '投资建议',
        fullReport: '查看完整报告',
        batchCompletePrefix: '分析完成',
        batchCompleteSuffix: '只股票',
        analyzing: '正在分析中...',
        disclaimer: '本工具仅供学习和研究目的，不构成任何投资建议。投资有风险，决策需谨慎。',
        close: '关闭',
        analysisTime: '分析时间',
        noSignals: '未检测到信号',
        noDescription: '无描述',
        date: '日期',
        signalSummary: '信号：{total} 个（进场：{inflow}，离场：{outflow}）',
        tickerRequired: '请输入股票代码',
        tickersRequired: '请输入至少一个股票代码',
        validTickerRequired: '请输入有效的股票代码',
        analysisFailed: '分析失败，请稍后重试',
        batchAnalysisFailed: '批量分析失败，请稍后重试',
        dataUnavailable: '暂时无法获取行情数据，请稍后重试',
        reportTitle: 'Smart Money Tracker - 机构资金动向分析报告',
        ticker: '股票代码',
        overallScore: '综合评分',
        rating: '综合评级',
        triggeredSignals: '触发信号',
        reportDisclaimer: '免责声明：本报告仅供学习研究使用，不构成任何投资建议。'
    }
};

const signalNames = {
    en: {
        ACCUMULATION_BREAKOUT: 'Accumulation Breakout',
        WYCKOFF_SPRING: 'Wyckoff Spring',
        OBV_BULLISH_DIVERGENCE: 'Bullish OBV Divergence',
        MFI_OVERSOLD: 'MFI Oversold',
        MFI_BULLISH_DIVERGENCE: 'Bullish MFI Divergence',
        NEW_INSTITUTION: 'New Institutional Holder',
        INSTITUTIONAL_BUY_IN: 'Institutional Buying',
        SHAREHOLDER_COUNT_DECREASE: 'Shareholder Count Decrease',
        BID_WALL_SUPPORT: 'Bid-Wall Support',
        RSP_STRONG: 'Relative Strength',
        HIGH_VOLUME_STAGNATION: 'High-Volume Stagnation',
        HIGH_VOLUME_DECLINE: 'High-Volume Decline',
        BREAK_SUPPORT_HEAVY_VOLUME: 'High-Volume Support Breakdown',
        LOW_VOLUME_RISE: 'Low-Volume Rally',
        OBV_BEARISH_DIVERGENCE: 'Bearish OBV Divergence',
        MFI_OVERBOUGHT: 'MFI Overbought',
        MFI_BEARISH_DIVERGENCE: 'Bearish MFI Divergence',
        RSI_BEARISH_DIVERGENCE: 'Bearish RSI Divergence',
        MACD_BEARISH_DIVERGENCE: 'Bearish MACD Divergence',
        INSTITUTIONAL_SELL_OFF: 'Institutional Selling',
        SHAREHOLDER_COUNT_INCREASE: 'Shareholder Count Increase',
        INSIDER_SELLING: 'Insider Selling',
        ASK_WALL_PRESSURE: 'Sell-Wall Pressure',
        RSP_WEAK: 'Relative Weakness',
        SECTOR_UNDERPERFORMANCE: 'Sector Underperformance'
    },
    'zh-CN': {
        ACCUMULATION_BREAKOUT: '放量突破横盘区',
        WYCKOFF_SPRING: '威科夫弹簧',
        OBV_BULLISH_DIVERGENCE: 'OBV 看涨背离',
        MFI_OVERSOLD: 'MFI 超卖',
        MFI_BULLISH_DIVERGENCE: 'MFI 看涨背离',
        NEW_INSTITUTION: '新机构进入',
        INSTITUTIONAL_BUY_IN: '机构增持',
        SHAREHOLDER_COUNT_DECREASE: '股东户数减少',
        BID_WALL_SUPPORT: '买单墙支撑',
        RSP_STRONG: '相对强势',
        HIGH_VOLUME_STAGNATION: '高位放量滞涨',
        HIGH_VOLUME_DECLINE: '放量下跌',
        BREAK_SUPPORT_HEAVY_VOLUME: '放量跌破支撑',
        LOW_VOLUME_RISE: '高位缩量上涨',
        OBV_BEARISH_DIVERGENCE: 'OBV 看跌背离',
        MFI_OVERBOUGHT: 'MFI 超买',
        MFI_BEARISH_DIVERGENCE: 'MFI 看跌背离',
        RSI_BEARISH_DIVERGENCE: 'RSI 看跌背离',
        MACD_BEARISH_DIVERGENCE: 'MACD 看跌背离',
        INSTITUTIONAL_SELL_OFF: '机构减持',
        SHAREHOLDER_COUNT_INCREASE: '股东户数增加',
        INSIDER_SELLING: '董监高减持',
        ASK_WALL_PRESSURE: '卖盘压单',
        RSP_WEAK: '相对疲弱',
        SECTOR_UNDERPERFORMANCE: '跑输行业'
    }
};

const englishSignalDescriptions = {
    ACCUMULATION_BREAKOUT: 'Price broke above a consolidation range with expanding volume.',
    WYCKOFF_SPRING: 'Price recovered after briefly breaking support, consistent with a Wyckoff spring.',
    OBV_BULLISH_DIVERGENCE: 'Price made a lower low while OBV held a higher low.',
    MFI_OVERSOLD: 'The Money Flow Index is in oversold territory.',
    MFI_BULLISH_DIVERGENCE: 'Price made a lower low while MFI held a higher low.',
    NEW_INSTITUTION: 'A new institution appeared among the leading shareholders.',
    INSTITUTIONAL_BUY_IN: 'Institutional ownership increased.',
    SHAREHOLDER_COUNT_DECREASE: 'The shareholder count declined, indicating greater ownership concentration.',
    BID_WALL_SUPPORT: 'Persistent buy orders are supporting price.',
    RSP_STRONG: 'The stock is outperforming its benchmark.',
    HIGH_VOLUME_STAGNATION: 'Volume expanded but price stopped advancing near a high.',
    HIGH_VOLUME_DECLINE: 'Price declined on elevated volume.',
    BREAK_SUPPORT_HEAVY_VOLUME: 'Price broke below support on elevated volume.',
    LOW_VOLUME_RISE: 'Price rose on weakening volume near a high.',
    OBV_BEARISH_DIVERGENCE: 'Price made a higher high while OBV made a lower high.',
    MFI_OVERBOUGHT: 'The Money Flow Index is in overbought territory.',
    MFI_BEARISH_DIVERGENCE: 'Price made a higher high while MFI made a lower high.',
    RSI_BEARISH_DIVERGENCE: 'Price made a higher high while RSI weakened.',
    MACD_BEARISH_DIVERGENCE: 'Price made a higher high while MACD weakened.',
    INSTITUTIONAL_SELL_OFF: 'Institutional ownership decreased.',
    SHAREHOLDER_COUNT_INCREASE: 'The shareholder count increased, indicating wider distribution.',
    INSIDER_SELLING: 'Directors or senior executives reduced their holdings.',
    ASK_WALL_PRESSURE: 'Persistent sell orders are limiting price advances.',
    RSP_WEAK: 'The stock is underperforming its benchmark.',
    SECTOR_UNDERPERFORMANCE: 'The stock is underperforming its sector.'
};

let currentLanguage = localStorage.getItem(LANGUAGE_STORAGE_KEY) || DEFAULT_LANGUAGE;
if (!translations[currentLanguage]) currentLanguage = DEFAULT_LANGUAGE;
let lastSingleResult = null;
let lastBatchResult = null;

// DOM Elements
const analyzeBtn = document.getElementById('analyzeBtn');
const batchAnalyzeBtn = document.getElementById('batchAnalyzeBtn');
const clearBtn = document.getElementById('clearBtn');
const tickerInput = document.getElementById('ticker');
const periodSelect = document.getElementById('period');
const analyzeStructureCheckbox = document.getElementById('analyze_structure');
const batchTickersTextarea = document.getElementById('batch_tickers');
const resultsSection = document.getElementById('resultsSection');
const singleResult = document.getElementById('singleResult');
const batchResults = document.getElementById('batchResults');
const loadingIndicator = document.getElementById('loadingIndicator');
const errorMessage = document.getElementById('errorMessage');
const languageBtnEn = document.getElementById('languageBtnEn');
const languageBtnZh = document.getElementById('languageBtnZh');

function t(key, replacements = {}) {
    let value = translations[currentLanguage][key] || translations.en[key] || key;
    Object.entries(replacements).forEach(([name, replacement]) => {
        value = value.replace(`{${name}}`, replacement);
    });
    return value;
}

function applyLanguage(language, options = {}) {
    const { persist = true, rerender = true } = options;
    currentLanguage = translations[language] ? language : DEFAULT_LANGUAGE;

    if (persist) localStorage.setItem(LANGUAGE_STORAGE_KEY, currentLanguage);
    document.documentElement.lang = currentLanguage;
    document.title = t('pageTitle');

    document.querySelectorAll('[data-i18n]').forEach(element => {
        element.textContent = t(element.dataset.i18n);
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        element.placeholder = t(element.dataset.i18nPlaceholder);
    });
    document.querySelectorAll('[data-i18n-aria-label]').forEach(element => {
        element.setAttribute('aria-label', t(element.dataset.i18nAriaLabel));
    });

    languageBtnEn.classList.toggle('active', currentLanguage === 'en');
    languageBtnZh.classList.toggle('active', currentLanguage === 'zh-CN');
    languageBtnEn.setAttribute('aria-pressed', String(currentLanguage === 'en'));
    languageBtnZh.setAttribute('aria-pressed', String(currentLanguage === 'zh-CN'));

    if (rerender && lastSingleResult && singleResult.style.display !== 'none') {
        displaySingleResult(lastSingleResult, false);
    }
    if (rerender && lastBatchResult && batchResults.style.display !== 'none') {
        displayBatchResults(lastBatchResult, false);
    }
}

// Event Listeners
analyzeBtn.addEventListener('click', analyzeSingleStock);
batchAnalyzeBtn.addEventListener('click', analyzeBatchStocks);
clearBtn.addEventListener('click', clearResults);
languageBtnEn.addEventListener('click', () => applyLanguage('en'));
languageBtnZh.addEventListener('click', () => applyLanguage('zh-CN'));
tickerInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') analyzeSingleStock();
});

// Analyze Single Stock
async function analyzeSingleStock() {
    const ticker = tickerInput.value.trim().toUpperCase();
    const period = parseInt(periodSelect.value);
    const analyzeStructure = analyzeStructureCheckbox.checked;

    if (!ticker) {
        showError(t('tickerRequired'));
        return;
    }

    showLoading();
    hideError();

    try {
        const response = await fetch(`${API_BASE}/api/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ticker,
                period,
                analyze_structure: analyzeStructure
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(translateApiError(data.error, 'analysisFailed'));
        }

        displaySingleResult(data);

    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || t('analysisFailed'));
    } finally {
        hideLoading();
    }
}

// Analyze Batch Stocks
async function analyzeBatchStocks() {
    const tickersText = batchTickersTextarea.value.trim();
    const period = parseInt(periodSelect.value);
    const analyzeStructure = analyzeStructureCheckbox.checked;

    if (!tickersText) {
        showError(t('tickersRequired'));
        return;
    }

    // Parse tickers
    const tickers = tickersText
        .split('\n')
        .map(t => t.trim().toUpperCase())
        .filter(t => t.length > 0);

    if (tickers.length === 0) {
        showError(t('validTickerRequired'));
        return;
    }

    showLoading();
    hideError();

    try {
        const response = await fetch(`${API_BASE}/api/batch`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tickers,
                period,
                analyze_structure: analyzeStructure
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(translateApiError(data.error, 'batchAnalysisFailed'));
        }

        displayBatchResults(data);

    } catch (error) {
        console.error('Batch analysis error:', error);
        showError(error.message || t('batchAnalysisFailed'));
    } finally {
        hideLoading();
    }
}

// Display Single Result
function displaySingleResult(data, shouldScroll = true) {
    lastSingleResult = data;
    lastBatchResult = null;

    // Show results section
    resultsSection.style.display = 'block';
    singleResult.style.display = 'block';
    batchResults.style.display = 'none';

    // Scroll to results
    if (shouldScroll) {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    document.getElementById('resultTicker').textContent = getDisplayName(
        data.ticker,
        data.stock_name
    );
    document.getElementById('resultTimestamp').textContent =
        `${t('analysisTime')}: ${formatTimestamp(data.timestamp)}`;

    // Update score
    const scoreValue = document.getElementById('scoreValue');
    const scoreCircle = document.getElementById('scoreCircle');
    scoreValue.textContent = data.score >= 0 ? `+${data.score.toFixed(1)}` : data.score.toFixed(1);
    
    // Set score circle color
    scoreCircle.className = 'score-circle';
    if (data.score > 1) {
        scoreCircle.classList.add('positive');
    } else if (data.score < -1) {
        scoreCircle.classList.add('negative');
    } else {
        scoreCircle.classList.add('neutral');
    }

    // Update rating badge
    const ratingBadge = document.getElementById('ratingBadge');
    ratingBadge.textContent = getRatingText(data.rating);
    ratingBadge.className = `rating-badge ${data.rating}`;

    // Update signal counts
    document.getElementById('inflowCount').textContent = data.inflow_count;
    document.getElementById('outflowCount').textContent = data.outflow_count;
    document.getElementById('totalCount').textContent = data.signal_count;

    // Display signals
    displaySignals('inflowSignals', data.inflow_signals, 'inflow');
    displaySignals('outflowSignals', data.outflow_signals, 'outflow');

    // Update recommendation
    document.getElementById('recommendationText').textContent = getRecommendation(data);

    // Update full report
    document.getElementById('fullReport').textContent =
        currentLanguage === 'en' ? buildEnglishReport(data) : data.report;
}

// Display Batch Results
function displayBatchResults(data, shouldScroll = true) {
    lastBatchResult = data;
    lastSingleResult = null;

    // Show results section
    resultsSection.style.display = 'block';
    singleResult.style.display = 'none';
    batchResults.style.display = 'block';

    // Scroll to results
    if (shouldScroll) {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Update count
    document.getElementById('batchCount').textContent = data.count;

    // Display results list
    const batchResultsList = document.getElementById('batchResultsList');
    batchResultsList.innerHTML = '';

    data.results.forEach(result => {
        const item = createBatchResultItem(result);
        batchResultsList.appendChild(item);
    });
}

// Create Batch Result Item
function createBatchResultItem(result) {
    const div = document.createElement('div');
    div.className = 'batch-item';
    
    // Use stock name from API, fallback to ticker
    const titleText = getDisplayName(result.ticker, result.stock_name);

    if (result.error) {
        div.innerHTML = `
            <div class="batch-item-info">
                <h4>${escapeHtml(titleText)}</h4>
                <p style="color: var(--danger-color);">❌ ${escapeHtml(translateApiError(result.error, 'analysisFailed'))}</p>
            </div>
        `;
        return div;
    }

    // Determine class based on score
    if (result.score > 1) {
        div.classList.add('positive');
    } else if (result.score < -1) {
        div.classList.add('negative');
    } else {
        div.classList.add('neutral');
    }

    div.innerHTML = `
        <div class="batch-item-info">
            <h4>${escapeHtml(titleText)}</h4>
            <p>
                ${t('signalSummary', {
                    total: result.signal_count,
                    inflow: result.inflow_count,
                    outflow: result.outflow_count
                })}
            </p>
            <p style="margin-top: 5px; font-size: 0.875rem;">
                ${escapeHtml(getRecommendation(result))}
            </p>
        </div>
        <div class="batch-item-score">
            <span class="batch-score-value ${result.score > 1 ? 'positive' : result.score < -1 ? 'negative' : 'neutral'}">
                ${result.score >= 0 ? '+' : ''}${result.score.toFixed(1)}
            </span>
            <span class="batch-rating rating-badge ${result.rating}">
                ${getRatingText(result.rating)}
            </span>
        </div>
    `;

    return div;
}

// Display Signals
function displaySignals(containerId, signals, type) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';

    if (!signals || signals.length === 0) {
        container.innerHTML = `<div class="no-signals">${t('noSignals')}</div>`;
        return;
    }

    signals.forEach(signal => {
        const signalItem = createSignalItem(signal, type);
        container.appendChild(signalItem);
    });
}

// Create Signal Item
function createSignalItem(signal, type) {
    const div = document.createElement('div');
    div.className = `signal-item ${type}`;

    const scoreClass = signal.score >= 0 ? 'positive' : 'negative';
    const scoreText = signal.score >= 0 ? `+${signal.score}` : signal.score;
    const description = getSignalDescription(signal);

    div.innerHTML = `
        <div class="signal-header">
            <span class="signal-name">${escapeHtml(formatSignalName(signal.name))}</span>
            <span class="signal-score ${scoreClass}">${scoreText}</span>
        </div>
        <div class="signal-description">${escapeHtml(description)}</div>
        ${signal.date ? `<div class="signal-date">${t('date')}: ${escapeHtml(signal.date)}</div>` : ''}
    `;

    return div;
}

// Format Signal Name
function formatSignalName(name) {
    return signalNames[currentLanguage][name] || name;
}

// Get Rating Text
function getRatingText(rating) {
    const ratingMaps = {
        en: {
            STRONG_BUY: '🚀🚀 Strong Buy',
            BUY: '🚀 Buy',
            NEUTRAL: '⚪ Neutral',
            SELL: '⚠️ Sell',
            STRONG_SELL: '🛑🛑 Strong Sell'
        },
        'zh-CN': {
            STRONG_BUY: '🚀🚀 强烈买入',
            BUY: '🚀 买入',
            NEUTRAL: '⚪ 中性',
            SELL: '⚠️ 卖出',
            STRONG_SELL: '🛑🛑 强烈卖出'
        }
    };

    return ratingMaps[currentLanguage][rating] || rating;
}

// Format Timestamp
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString(currentLanguage === 'en' ? 'en-US' : 'zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

function getSignalDescription(signal) {
    if (currentLanguage === 'en') {
        return englishSignalDescriptions[signal.name] || t('noDescription');
    }
    return signal.description || t('noDescription');
}

function getDisplayName(ticker, serverName) {
    if (currentLanguage === 'zh-CN') {
        const localizedName = tickerNameMap[ticker] || serverName;
        return localizedName && localizedName !== ticker
            ? `${localizedName} (${ticker})`
            : ticker;
    }

    const hasChineseCharacters = /[\u3400-\u9fff]/.test(serverName || '');
    return serverName && serverName !== ticker && !hasChineseCharacters
        ? `${serverName} (${ticker})`
        : ticker;
}

function getRecommendation(data) {
    if (currentLanguage === 'zh-CN') {
        return data.recommendation || '';
    }

    const score = Number(data.score || 0).toFixed(1);
    const recommendations = {
        STRONG_BUY: `Strong institutional accumulation signals detected (score ${score}). Confirm the setup with price action and manage position risk carefully.`,
        BUY: `Moderate institutional accumulation signals detected (score ${score}). Monitor price and volume for confirmation.`,
        NEUTRAL: `No decisive institutional flow signal is present (score ${score}). Continue monitoring for a clearer setup.`,
        SELL: `Institutional distribution signals detected (score ${score}). Exercise caution and watch for further price-volume weakness.`,
        STRONG_SELL: `Strong institutional distribution signals detected (score ${score}). Risk is elevated; avoid relying on this signal alone.`
    };
    return recommendations[data.rating] || recommendations.NEUTRAL;
}

function buildEnglishReport(data) {
    const signals = [
        ...(data.inflow_signals || []),
        ...(data.outflow_signals || [])
    ];
    const signalLines = signals.length
        ? signals.map(signal =>
            `- ${formatSignalName(signal.name)} (${signal.score >= 0 ? '+' : ''}${signal.score}): ${getSignalDescription(signal)}`
        ).join('\n')
        : `- ${t('noSignals')}`;

    return [
        '======================================================================',
        t('reportTitle'),
        '======================================================================',
        '',
        `${t('ticker')}: ${data.ticker}`,
        `${t('analysisTime')}: ${formatTimestamp(data.timestamp)}`,
        `${t('overallScore')}: ${data.score >= 0 ? '+' : ''}${Number(data.score).toFixed(1)}/10`,
        `${t('rating')}: ${getRatingText(data.rating)}`,
        '',
        `${t('triggeredSignals')}:`,
        signalLines,
        '',
        `${t('recommendation')}:`,
        getRecommendation(data),
        '',
        t('reportDisclaimer')
    ].join('\n');
}

function translateApiError(message, fallbackKey) {
    if (currentLanguage === 'zh-CN') {
        return message || t(fallbackKey);
    }

    const normalized = String(message || '').toLowerCase();
    if (
        normalized.includes('无法获取数据') ||
        normalized.includes('too many requests') ||
        normalized.includes('rate limit') ||
        normalized.includes('market data')
    ) {
        return t('dataUnavailable');
    }
    return t(fallbackKey);
}

function escapeHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

// Clear Results
function clearResults() {
    resultsSection.style.display = 'none';
    singleResult.style.display = 'none';
    batchResults.style.display = 'none';
    lastSingleResult = null;
    lastBatchResult = null;
}

// Show Loading
function showLoading() {
    loadingIndicator.style.display = 'flex';
    analyzeBtn.disabled = true;
    batchAnalyzeBtn.disabled = true;
}

// Hide Loading
function hideLoading() {
    loadingIndicator.style.display = 'none';
    analyzeBtn.disabled = false;
    batchAnalyzeBtn.disabled = false;
}

// Show Error
function showError(message) {
    const errorText = document.getElementById('errorText');
    errorText.textContent = message;
    errorMessage.style.display = 'flex';

    // Auto hide after 5 seconds
    setTimeout(() => {
        hideError();
    }, 5000);
}

// Hide Error
function hideError() {
    errorMessage.style.display = 'none';
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('SmartMoneyTracker Web Interface initialized');

    applyLanguage(currentLanguage, { persist: false, rerender: false });

    populateDefaultTickers();
});

// 股票代码到中文名称的映射
const tickerNameMap = {
    // 港股
    '0700.HK': '腾讯控股',
    '9988.HK': '阿里巴巴',
    '9618.HK': '京东集团',
    '3690.HK': '美团',
    '2097.HK': '蜜雪冰城',
    '1810.HK': '小米集团',
    '6862.HK': '海底捞',
    '2150.HK': '奈雪的茶',
    '2555.HK': '茶百道',
    '1364.HK': '古茗',
    
    // 美股
    'PDD': '拼多多',
    'NVDA': '英伟达',
    'AMD': '超威半导体',
    'GOOGL': '谷歌',
    'AAPL': '苹果',
    'MSFT': '微软',
    'TSLA': '特斯拉',
    'META': 'Meta',
    'AMZN': '亚马逊',
    'NFLX': '奈飞',
    
    // A股
    '600519.SH': '贵州茅台',
    '000858.SZ': '五粮液',
    '000333.SZ': '美的集团',
    '600036.SH': '招商银行',
    '000001.SZ': '平安银行'
};

// 填充默认批量股票列表，由用户主动开始分析。
function populateDefaultTickers() {
    // 预设股票列表
    const defaultTickers = [
        '0700.HK',    // 腾讯控股
        '9988.HK',    // 阿里巴巴
        '9618.HK',    // 京东集团
        '3690.HK',    // 美团
        'PDD',        // 拼多多
        'NVDA',       // 英伟达
        '2097.HK',    // 蜜雪冰城
        '1810.HK',    // 小米集团
        'AAPL',       // 苹果
        'MSFT',       // 微软
        'META',       // Meta
        'AMZN',       // 亚马逊
        'TSLA',       // 特斯拉
        'AMD',        // AMD
        'GOOGL'       // 谷歌
    ];
    
    // 填充到批量分析文本框
    batchTickersTextarea.value = defaultTickers.join('\n');
}
