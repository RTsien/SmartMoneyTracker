// SmartMoneyTracker Web Interface JavaScript

// API Base URL
const API_BASE = window.location.origin;

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

// Event Listeners
analyzeBtn.addEventListener('click', analyzeSingleStock);
batchAnalyzeBtn.addEventListener('click', analyzeBatchStocks);
clearBtn.addEventListener('click', clearResults);
tickerInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') analyzeSingleStock();
});

// Analyze Single Stock
async function analyzeSingleStock() {
    const ticker = tickerInput.value.trim().toUpperCase();
    const period = parseInt(periodSelect.value);
    const analyzeStructure = analyzeStructureCheckbox.checked;

    if (!ticker) {
        showError('请输入股票代码');
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
            throw new Error(data.error || '分析失败');
        }

        displaySingleResult(data);

    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || '分析过程中发生错误');
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
        showError('请输入至少一个股票代码');
        return;
    }

    // Parse tickers
    const tickers = tickersText
        .split('\n')
        .map(t => t.trim().toUpperCase())
        .filter(t => t.length > 0);

    if (tickers.length === 0) {
        showError('请输入有效的股票代码');
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
            throw new Error(data.error || '批量分析失败');
        }

        displayBatchResults(data);

    } catch (error) {
        console.error('Batch analysis error:', error);
        showError(error.message || '批量分析过程中发生错误');
    } finally {
        hideLoading();
    }
}

// Display Single Result
function displaySingleResult(data) {
    // Show results section
    resultsSection.style.display = 'block';
    singleResult.style.display = 'block';
    batchResults.style.display = 'none';

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // Update ticker and timestamp with Chinese name from API
    const displayName = data.stock_name || data.ticker;
    document.getElementById('resultTicker').textContent = 
        displayName !== data.ticker ? `${displayName} (${data.ticker})` : data.ticker;
    document.getElementById('resultTimestamp').textContent = 
        `分析时间: ${formatTimestamp(data.timestamp)}`;

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
    document.getElementById('recommendationText').textContent = data.recommendation;

    // Update full report
    document.getElementById('fullReport').textContent = data.report;
}

// Display Batch Results
function displayBatchResults(data) {
    // Show results section
    resultsSection.style.display = 'block';
    singleResult.style.display = 'none';
    batchResults.style.display = 'block';

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

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
    const displayName = result.stock_name || result.ticker;
    const titleText = displayName !== result.ticker ? 
        `${displayName} (${result.ticker})` : result.ticker;

    if (result.error) {
        div.innerHTML = `
            <div class="batch-item-info">
                <h4>${titleText}</h4>
                <p style="color: var(--danger-color);">❌ ${result.error}</p>
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
            <h4>${titleText}</h4>
            <p>
                信号: ${result.signal_count} 个 
                (进场: ${result.inflow_count}, 离场: ${result.outflow_count})
            </p>
            <p style="margin-top: 5px; font-size: 0.875rem;">
                ${result.recommendation}
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
        container.innerHTML = '<div class="no-signals">未检测到信号</div>';
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

    div.innerHTML = `
        <div class="signal-header">
            <span class="signal-name">${formatSignalName(signal.name)}</span>
            <span class="signal-score ${scoreClass}">${scoreText}</span>
        </div>
        <div class="signal-description">${signal.description || '无描述'}</div>
        ${signal.date ? `<div class="signal-date">日期: ${signal.date}</div>` : ''}
    `;

    return div;
}

// Format Signal Name
function formatSignalName(name) {
    const nameMap = {
        'ACCUMULATION_BREAKOUT': '放量突破横盘区',
        'WYCKOFF_SPRING': '威科夫弹簧',
        'OBV_BULLISH_DIVERGENCE': 'OBV看涨背离',
        'MFI_OVERSOLD': 'MFI超卖',
        'MFI_BULLISH_DIVERGENCE': 'MFI看涨背离',
        'NEW_INSTITUTION': '新机构进入',
        'INSTITUTIONAL_BUY_IN': '机构增持',
        'SHAREHOLDER_COUNT_DECREASE': '股东户数减少',
        'BID_WALL_SUPPORT': '买单墙支撑',
        'RSP_STRONG': '相对强势',
        'HIGH_VOLUME_STAGNATION': '高位放量滞涨',
        'HIGH_VOLUME_DECLINE': '放量下跌',
        'BREAK_SUPPORT_HEAVY_VOLUME': '放量跌破支撑',
        'LOW_VOLUME_RISE': '高位缩量上涨',
        'OBV_BEARISH_DIVERGENCE': 'OBV看跌背离',
        'MFI_OVERBOUGHT': 'MFI超买',
        'MFI_BEARISH_DIVERGENCE': 'MFI看跌背离',
        'RSI_BEARISH_DIVERGENCE': 'RSI看跌背离',
        'MACD_BEARISH_DIVERGENCE': 'MACD看跌背离',
        'INSTITUTIONAL_SELL_OFF': '机构减持',
        'SHAREHOLDER_COUNT_INCREASE': '股东户数增加',
        'INSIDER_SELLING': '董监高减持',
        'ASK_WALL_PRESSURE': '卖盘压单',
        'RSP_WEAK': '相对疲弱',
        'SECTOR_UNDERPERFORMANCE': '跑输行业'
    };

    return nameMap[name] || name;
}

// Get Rating Text
function getRatingText(rating) {
    const ratingMap = {
        'STRONG_BUY': '🚀🚀 强烈买入',
        'BUY': '🚀 买入',
        'NEUTRAL': '⚪ 中性',
        'SELL': '⚠️ 卖出',
        'STRONG_SELL': '🛑🛑 强烈卖出'
    };

    return ratingMap[rating] || rating;
}

// Format Timestamp
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// Clear Results
function clearResults() {
    resultsSection.style.display = 'none';
    singleResult.style.display = 'none';
    batchResults.style.display = 'none';
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
    
    // 自动批量分析预设股票
    autoAnalyzeBatch();
});

// 股票代码到中文名称的映射
const tickerNameMap = {
    // 港股
    '0700.HK': '腾讯控股',
    '9988.HK': '阿里巴巴',
    '9618.HK': '京东集团',
    '3690.HK': '美团',
    '2097.HK': '蜜雪冰城',
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

// 获取股票中文名称
function getTickerName(ticker) {
    return tickerNameMap[ticker] || ticker;
}

// 自动批量分析函数
async function autoAnalyzeBatch() {
    // 预设股票列表
    const defaultTickers = [
        '0700.HK',    // 腾讯控股
        '9988.HK',    // 阿里巴巴
        '9618.HK',    // 京东集团
        '3690.HK',    // 美团
        'PDD',        // 拼多多
        'NVDA',       // 英伟达
        '2097.HK',    // 蜜雪冰城
        'AMD',        // AMD
        'GOOGL'       // 谷歌
    ];
    
    // 填充到批量分析文本框
    batchTickersTextarea.value = defaultTickers.join('\n');
    
    // 显示提示信息
    console.log('自动开始批量分析...');
    
    // 延迟1秒后自动开始分析
    setTimeout(() => {
        analyzeBatchStocks();
    }, 1000);
}
