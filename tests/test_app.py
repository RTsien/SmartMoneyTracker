"""
Flask API 单元测试
测试 Web 接口的各项功能
"""

import unittest
import json
import sys
import os
import numpy as np

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, format_signals, convert_to_json_serializable


class TestFlaskAPI(unittest.TestCase):
    """Flask API 测试类"""

    def setUp(self):
        """测试前设置"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_index_route(self):
        """测试主页路由"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_config_route(self):
        """测试配置接口"""
        response = self.client.get('/api/config')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('stock_pool', data)
        self.assertIn('markets', data)
        self.assertIn('data_source', data)

    def test_format_signals_with_positive_weight(self):
        """测试格式化进场信号（正权重）"""
        signals = {
            'OBV_BULLISH_DIVERGENCE': {
                'weight': 2,
                'data': {
                    'description': 'OBV看涨背离',
                    'date': '2025-10-15',
                    'details': {}
                }
            }
        }
        
        formatted = format_signals(signals)
        
        self.assertEqual(len(formatted), 1)
        self.assertEqual(formatted[0]['name'], 'OBV_BULLISH_DIVERGENCE')
        self.assertEqual(formatted[0]['score'], 2)  # 应该是正数
        self.assertEqual(formatted[0]['description'], 'OBV看涨背离')
        self.assertEqual(formatted[0]['date'], '2025-10-15')

    def test_format_signals_with_negative_weight(self):
        """测试格式化离场信号（负权重）"""
        signals = {
            'MACD_BEARISH_DIVERGENCE': {
                'weight': -2,
                'data': {
                    'description': 'MACD看跌背离',
                    'date': '2025-10-20',
                    'details': {}
                }
            }
        }
        
        formatted = format_signals(signals)
        
        self.assertEqual(len(formatted), 1)
        self.assertEqual(formatted[0]['name'], 'MACD_BEARISH_DIVERGENCE')
        self.assertEqual(formatted[0]['score'], -2)  # 应该是负数，不是0
        self.assertEqual(formatted[0]['description'], 'MACD看跌背离')

    def test_format_signals_with_multiple_signals(self):
        """测试格式化多个信号"""
        signals = {
            'OBV_BULLISH_DIVERGENCE': {
                'weight': 2,
                'data': {
                    'description': 'OBV看涨背离',
                    'date': '2025-10-15'
                }
            },
            'MACD_BEARISH_DIVERGENCE': {
                'weight': -2,
                'data': {
                    'description': 'MACD看跌背离',
                    'date': '2025-10-20'
                }
            },
            'NEW_INSTITUTION': {
                'weight': 3,
                'data': {
                    'description': '新机构进入',
                    'date': '2025-10-18'
                }
            }
        }
        
        formatted = format_signals(signals)
        
        self.assertEqual(len(formatted), 3)
        
        # 检查每个信号的评分
        scores = {item['name']: item['score'] for item in formatted}
        self.assertEqual(scores['OBV_BULLISH_DIVERGENCE'], 2)
        self.assertEqual(scores['MACD_BEARISH_DIVERGENCE'], -2)
        self.assertEqual(scores['NEW_INSTITUTION'], 3)

    def test_format_signals_with_empty_data(self):
        """测试格式化空数据"""
        signals = {
            'SOME_SIGNAL': {
                'weight': -1,
                'data': {}
            }
        }
        
        formatted = format_signals(signals)
        
        self.assertEqual(len(formatted), 1)
        self.assertEqual(formatted[0]['score'], -1)
        self.assertEqual(formatted[0]['description'], '')
        self.assertEqual(formatted[0]['date'], '')

    def test_format_signals_empty_input(self):
        """测试空信号输入"""
        signals = {}
        formatted = format_signals(signals)
        self.assertEqual(len(formatted), 0)

    def test_format_signals_no_weight(self):
        """测试缺少weight字段的情况"""
        signals = {
            'SOME_SIGNAL': {
                'data': {
                    'description': '测试信号'
                }
            }
        }
        
        formatted = format_signals(signals)
        
        self.assertEqual(len(formatted), 1)
        self.assertEqual(formatted[0]['score'], 0)  # 默认值应该是0

    def test_analyze_api_missing_ticker(self):
        """测试分析接口缺少股票代码"""
        response = self.client.post(
            '/api/analyze',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('error', data)

    def test_batch_api_missing_tickers(self):
        """测试批量分析接口缺少股票代码"""
        response = self.client.post(
            '/api/batch',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])


class TestSignalScoreDisplay(unittest.TestCase):
    """信号评分显示测试"""

    def test_negative_score_not_zero(self):
        """确保负分不会显示为0"""
        signals = {
            'HIGH_VOLUME_STAGNATION': {
                'weight': -2,
                'data': {'description': '高位放量滞涨'}
            },
            'INSTITUTIONAL_SELL_OFF': {
                'weight': -3,
                'data': {'description': '机构减持'}
            }
        }
        
        formatted = format_signals(signals)
        
        for signal in formatted:
            # 确保所有负权重信号的score都是负数
            if signal['name'] in ['HIGH_VOLUME_STAGNATION', 'INSTITUTIONAL_SELL_OFF']:
                self.assertLess(signal['score'], 0, 
                    f"{signal['name']} 的评分应该是负数，但得到了 {signal['score']}")

    def test_positive_score_not_zero(self):
        """确保正分不会显示为0"""
        signals = {
            'ACCUMULATION_BREAKOUT': {
                'weight': 2,
                'data': {'description': '放量突破'}
            },
            'NEW_INSTITUTION': {
                'weight': 3,
                'data': {'description': '新机构进入'}
            }
        }
        
        formatted = format_signals(signals)
        
        for signal in formatted:
            # 确保所有正权重信号的score都是正数
            if signal['name'] in ['ACCUMULATION_BREAKOUT', 'NEW_INSTITUTION']:
                self.assertGreater(signal['score'], 0,
                    f"{signal['name']} 的评分应该是正数，但得到了 {signal['score']}")


class TestJSONSerialization(unittest.TestCase):
    """JSON 序列化测试"""

    def test_convert_numpy_bool(self):
        """测试 numpy bool 类型转换"""
        self.assertEqual(convert_to_json_serializable(np.bool_(True)), True)
        self.assertEqual(convert_to_json_serializable(np.bool_(False)), False)

    def test_convert_numpy_int(self):
        """测试 numpy int 类型转换"""
        self.assertEqual(convert_to_json_serializable(np.int64(42)), 42)
        self.assertEqual(convert_to_json_serializable(np.int32(100)), 100)

    def test_convert_numpy_float(self):
        """测试 numpy float 类型转换"""
        self.assertAlmostEqual(convert_to_json_serializable(np.float64(3.14)), 3.14)
        self.assertAlmostEqual(convert_to_json_serializable(np.float32(2.5)), 2.5)

    def test_convert_numpy_array(self):
        """测试 numpy array 转换"""
        arr = np.array([1, 2, 3])
        result = convert_to_json_serializable(arr)
        self.assertEqual(result, [1, 2, 3])

    def test_convert_dict_with_numpy_values(self):
        """测试包含 numpy 类型的字典转换"""
        data = {
            'bool_val': np.bool_(True),
            'int_val': np.int64(42),
            'float_val': np.float64(3.14),
            'array_val': np.array([1, 2, 3])
        }
        result = convert_to_json_serializable(data)
        
        self.assertEqual(result['bool_val'], True)
        self.assertEqual(result['int_val'], 42)
        self.assertAlmostEqual(result['float_val'], 3.14)
        self.assertEqual(result['array_val'], [1, 2, 3])

    def test_format_signals_with_numpy_types(self):
        """测试格式化包含 numpy 类型的信号"""
        signals = {
            'TEST_SIGNAL': {
                'weight': np.int64(-2),
                'data': {
                    'description': '测试信号',
                    'date': '2025-10-20',
                    'details': {
                        'value': np.float64(3.14),
                        'flag': np.bool_(True)
                    }
                }
            }
        }
        
        formatted = format_signals(signals)
        
        # 确保可以被 JSON 序列化
        try:
            json_str = json.dumps(formatted)
            self.assertIsInstance(json_str, str)
        except TypeError as e:
            self.fail(f"格式化后的信号无法被 JSON 序列化: {e}")
        
        # 验证数据正确性
        self.assertEqual(formatted[0]['score'], -2)
        self.assertEqual(formatted[0]['details']['value'], 3.14)
        self.assertEqual(formatted[0]['details']['flag'], True)


if __name__ == '__main__':
    unittest.main()
