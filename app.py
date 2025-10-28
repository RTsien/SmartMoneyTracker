"""
SmartMoneyTracker Web Application
Flask-based web interface for stock analysis
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import json
import numpy as np

from main import SmartMoneyScanner
import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)

# 初始化扫描器
scanner = SmartMoneyScanner()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_stock():
    """
    分析单个股票
    
    Request JSON:
    {
        "ticker": "600519.SH",
        "period": 250,
        "analyze_structure": true
    }
    """
    try:
        data = request.get_json()
        ticker = data.get('ticker', '').strip().upper()
        period = data.get('period', 250)
        analyze_structure = data.get('analyze_structure', True)
        
        if not ticker:
            return jsonify({
                'success': False,
                'error': '请输入股票代码'
            }), 400
        
        logger.info(f"Web API: 开始分析 {ticker}")
        
        # 获取股票名称
        stock_name = scanner.data_fetcher.get_stock_name(ticker)
        
        # 执行分析
        result = scanner.scan_stock(
            ticker=ticker,
            period=period,
            analyze_structure=analyze_structure
        )
        
        if not result['success']:
            return jsonify(result), 400
        
        # 准备返回数据
        response = {
            'success': True,
            'ticker': result['ticker'],
            'stock_name': stock_name,
            'score': result['score'],
            'rating': result['rating'],
            'signal_count': result['signal_count'],
            'inflow_count': result.get('inflow_count', 0),
            'outflow_count': result.get('outflow_count', 0),
            'inflow_signals': format_signals(result.get('inflow_signals', {})),
            'outflow_signals': format_signals(result.get('outflow_signals', {})),
            'recommendation': result['recommendation'],
            'report': result['report'],
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Web API: {ticker} 分析完成 - 评分: {result['score']}")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Web API 错误: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/batch', methods=['POST'])
def analyze_batch():
    """
    批量分析多只股票
    
    Request JSON:
    {
        "tickers": ["600519.SH", "000858.SZ"],
        "period": 250,
        "analyze_structure": false
    }
    """
    try:
        data = request.get_json()
        tickers = data.get('tickers', [])
        period = data.get('period', 250)
        analyze_structure = data.get('analyze_structure', False)
        
        if not tickers:
            return jsonify({
                'success': False,
                'error': '请输入至少一个股票代码'
            }), 400
        
        # 清理和标准化股票代码
        tickers = [t.strip().upper() for t in tickers if t.strip()]
        
        logger.info(f"Web API: 开始批量分析 {len(tickers)} 只股票")
        
        # 执行批量分析
        results = scanner.scan_batch(
            tickers=tickers,
            period=period,
            analyze_structure=analyze_structure
        )
        
        # 准备返回数据
        response = {
            'success': True,
            'count': len(results),
            'results': []
        }
        
        for ticker, result in results.items():
            # 获取股票名称
            stock_name = scanner.data_fetcher.get_stock_name(ticker)
            
            if result['success']:
                response['results'].append({
                    'ticker': ticker,
                    'stock_name': stock_name,
                    'score': result['score'],
                    'rating': result['rating'],
                    'signal_count': result['signal_count'],
                    'inflow_count': result.get('inflow_count', 0),
                    'outflow_count': result.get('outflow_count', 0),
                    'recommendation': result['recommendation']
                })
            else:
                response['results'].append({
                    'ticker': ticker,
                    'stock_name': stock_name,
                    'error': result.get('error', '未知错误')
                })
        
        logger.info(f"Web API: 批量分析完成")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Web API 批量分析错误: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置信息"""
    try:
        return jsonify({
            'success': True,
            'stock_pool': config.STOCK_POOL,
            'markets': list(config.MARKET_BENCHMARKS.keys()),
            'data_source': config.A_STOCK_DATA_SOURCE
        })
    except Exception as e:
        logger.error(f"获取配置错误: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def convert_to_json_serializable(obj):
    """
    将对象转换为 JSON 可序列化的类型
    处理 numpy 类型、pandas 类型等
    """
    if obj is None:
        return None
    elif isinstance(obj, (bool, int, float, str)):
        return obj
    elif isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    # 处理 numpy 类型 - 先检查 tolist (array) 再检查 item (scalar)
    elif hasattr(obj, 'tolist'):  # numpy array
        return obj.tolist()
    elif hasattr(obj, 'item'):  # numpy scalar (包括 bool, int, float)
        return obj.item()
    else:
        # 对于其他类型，转换为字符串
        return str(obj)

def format_signals(signals):
    """格式化信号数据以便前端显示"""
    formatted = []
    for signal_name, signal_data in signals.items():
        # signal_data 包含 'weight' 和 'data' 两个字段
        # weight 是信号的评分权重（正数=进场，负数=离场）
        weight = signal_data.get('weight', 0)
        data = signal_data.get('data', {})
        
        # 转换所有数据为 JSON 可序列化的类型
        formatted.append({
            'name': signal_name,
            'score': convert_to_json_serializable(weight),
            'description': convert_to_json_serializable(data.get('description', '')),
            'date': convert_to_json_serializable(data.get('date', '')),
            'details': convert_to_json_serializable(data.get('details', {}))
        })
    return formatted

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'success': False,
        'error': '页面未找到'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    logger.error(f"服务器内部错误: {error}", exc_info=True)
    return jsonify({
        'success': False,
        'error': '服务器内部错误'
    }), 500

if __name__ == '__main__':
    logger.info("启动 SmartMoneyTracker Web 服务...")
    logger.info("访问 http://localhost:8001 使用 Web 界面")
    app.run(host='0.0.0.0', port=8001, debug=True)
