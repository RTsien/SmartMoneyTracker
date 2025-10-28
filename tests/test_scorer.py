"""
信号聚合器单元测试
测试评分和评级逻辑
"""

import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config
from aggregator.scorer import SignalAggregator


class TestSignalAggregator(unittest.TestCase):
    """信号聚合器测试类"""

    def setUp(self):
        """测试前设置"""
        self.aggregator = SignalAggregator(config)

    def test_empty_signals(self):
        """测试空信号"""
        result = self.aggregator.calculate_score({})
        
        self.assertEqual(result['score'], 0)
        self.assertEqual(result['rating'], 'NEUTRAL')
        self.assertEqual(result['signal_count'], 0)
        self.assertEqual(result['inflow_count'], 0)
        self.assertEqual(result['outflow_count'], 0)

    def test_positive_signals_only(self):
        """测试仅有进场信号"""
        signals = {
            'OBV_BULLISH_DIVERGENCE': {'description': 'OBV看涨背离'},
            'NEW_INSTITUTION': {'description': '新机构进入'}
        }
        
        result = self.aggregator.calculate_score(signals)
        
        # OBV_BULLISH_DIVERGENCE: +2, NEW_INSTITUTION: +3
        self.assertEqual(result['score'], 5)
        self.assertEqual(result['rating'], 'BUY')
        self.assertEqual(result['inflow_count'], 2)
        self.assertEqual(result['outflow_count'], 0)

    def test_negative_signals_only(self):
        """测试仅有离场信号"""
        signals = {
            'MACD_BEARISH_DIVERGENCE': {'description': 'MACD看跌背离'},
            'INSTITUTIONAL_SELL_OFF': {'description': '机构减持'}
        }
        
        result = self.aggregator.calculate_score(signals)
        
        # MACD_BEARISH_DIVERGENCE: -2, INSTITUTIONAL_SELL_OFF: -3
        self.assertEqual(result['score'], -5)
        self.assertEqual(result['rating'], 'SELL')
        self.assertEqual(result['inflow_count'], 0)
        self.assertEqual(result['outflow_count'], 2)

    def test_mixed_signals(self):
        """测试混合信号"""
        signals = {
            'OBV_BULLISH_DIVERGENCE': {'description': 'OBV看涨背离'},  # +2
            'MACD_BEARISH_DIVERGENCE': {'description': 'MACD看跌背离'}  # -2
        }
        
        result = self.aggregator.calculate_score(signals)
        
        # +2 + (-2) = 0
        self.assertEqual(result['score'], 0)
        self.assertEqual(result['rating'], 'NEUTRAL')
        self.assertEqual(result['inflow_count'], 1)
        self.assertEqual(result['outflow_count'], 1)

    def test_strong_buy_rating(self):
        """测试强烈买入评级"""
        signals = {
            'NEW_INSTITUTION': {'description': '新机构进入'},  # +3
            'INSTITUTIONAL_BUY_IN': {'description': '机构增持'},  # +3
            'OBV_BULLISH_DIVERGENCE': {'description': 'OBV看涨背离'}  # +2
        }
        
        result = self.aggregator.calculate_score(signals)
        
        # +3 + 3 + 2 = +8
        self.assertEqual(result['score'], 8)
        self.assertEqual(result['rating'], 'STRONG_BUY')

    def test_strong_sell_rating(self):
        """测试强烈卖出评级"""
        signals = {
            'INSTITUTIONAL_SELL_OFF': {'description': '机构减持'},  # -3
            'BREAK_SUPPORT_HEAVY_VOLUME': {'description': '放量跌破支撑'},  # -3
            'HIGH_VOLUME_STAGNATION': {'description': '高位放量滞涨'}  # -2
        }
        
        result = self.aggregator.calculate_score(signals)
        
        # -3 + (-3) + (-2) = -8
        self.assertEqual(result['score'], -8)
        self.assertEqual(result['rating'], 'STRONG_SELL')

    def test_score_capping_at_10(self):
        """测试评分上限为10"""
        # 创建大量正信号
        signals = {
            f'SIGNAL_{i}': {'description': f'信号{i}'}
            for i in range(10)
        }
        # 手动添加已知信号
        signals['NEW_INSTITUTION'] = {'description': '新机构进入'}  # +3
        signals['INSTITUTIONAL_BUY_IN'] = {'description': '机构增持'}  # +3
        signals['OBV_BULLISH_DIVERGENCE'] = {'description': 'OBV看涨背离'}  # +2
        signals['ACCUMULATION_BREAKOUT'] = {'description': '放量突破'}  # +2
        
        result = self.aggregator.calculate_score(signals)
        
        # 评分应该被限制在10
        self.assertLessEqual(result['score'], 10)

    def test_score_capping_at_minus_10(self):
        """测试评分下限为-10"""
        signals = {
            'INSTITUTIONAL_SELL_OFF': {'description': '机构减持'},  # -3
            'BREAK_SUPPORT_HEAVY_VOLUME': {'description': '放量跌破'},  # -3
            'HIGH_VOLUME_STAGNATION': {'description': '高位滞涨'},  # -2
            'MACD_BEARISH_DIVERGENCE': {'description': 'MACD背离'},  # -2
            'OBV_BEARISH_DIVERGENCE': {'description': 'OBV背离'}  # -2
        }
        
        result = self.aggregator.calculate_score(signals)
        
        # 评分应该被限制在-10
        self.assertGreaterEqual(result['score'], -10)

    def test_unknown_signal_ignored(self):
        """测试未知信号被忽略"""
        signals = {
            'UNKNOWN_SIGNAL': {'description': '未知信号'},
            'OBV_BULLISH_DIVERGENCE': {'description': 'OBV看涨背离'}  # +2
        }
        
        result = self.aggregator.calculate_score(signals)
        
        # 只计算已知信号
        self.assertEqual(result['score'], 2)
        self.assertEqual(result['signal_count'], 1)

    def test_signal_weight_structure(self):
        """测试信号权重结构正确性"""
        signals = {
            'OBV_BULLISH_DIVERGENCE': {'description': 'OBV看涨背离'}
        }
        
        result = self.aggregator.calculate_score(signals)
        
        # 检查返回的信号结构
        self.assertIn('OBV_BULLISH_DIVERGENCE', result['triggered_signals'])
        signal_entry = result['triggered_signals']['OBV_BULLISH_DIVERGENCE']
        
        # 确保包含weight字段
        self.assertIn('weight', signal_entry)
        self.assertEqual(signal_entry['weight'], 2)
        
        # 确保包含data字段
        self.assertIn('data', signal_entry)
        self.assertEqual(signal_entry['data']['description'], 'OBV看涨背离')

    def test_inflow_outflow_separation(self):
        """测试进场和离场信号正确分类"""
        signals = {
            'OBV_BULLISH_DIVERGENCE': {'description': 'OBV看涨背离'},  # +2
            'NEW_INSTITUTION': {'description': '新机构进入'},  # +3
            'MACD_BEARISH_DIVERGENCE': {'description': 'MACD看跌背离'},  # -2
            'INSTITUTIONAL_SELL_OFF': {'description': '机构减持'}  # -3
        }
        
        result = self.aggregator.calculate_score(signals)
        
        # 检查进场信号
        self.assertEqual(len(result['inflow_signals']), 2)
        self.assertIn('OBV_BULLISH_DIVERGENCE', result['inflow_signals'])
        self.assertIn('NEW_INSTITUTION', result['inflow_signals'])
        
        # 检查离场信号
        self.assertEqual(len(result['outflow_signals']), 2)
        self.assertIn('MACD_BEARISH_DIVERGENCE', result['outflow_signals'])
        self.assertIn('INSTITUTIONAL_SELL_OFF', result['outflow_signals'])

    def test_recommendation_text(self):
        """测试投资建议文本"""
        # 测试强烈买入建议
        recommendation = self.aggregator.get_recommendation('STRONG_BUY', 8.0)
        self.assertIn('强烈', recommendation)
        self.assertIn('吸筹', recommendation)
        
        # 测试强烈卖出建议
        recommendation = self.aggregator.get_recommendation('STRONG_SELL', -8.0)
        self.assertIn('强烈', recommendation)
        self.assertIn('派发', recommendation)
        
        # 测试中性建议
        recommendation = self.aggregator.get_recommendation('NEUTRAL', 0.0)
        self.assertIn('观察', recommendation)


class TestRatingDetermination(unittest.TestCase):
    """评级判定测试"""

    def setUp(self):
        """测试前设置"""
        self.aggregator = SignalAggregator(config)

    def test_rating_boundaries(self):
        """测试评级边界值"""
        test_cases = [
            (10, 'STRONG_BUY'),
            (6, 'STRONG_BUY'),
            (5, 'BUY'),
            (2, 'BUY'),
            (1, 'NEUTRAL'),
            (0, 'NEUTRAL'),
            (-1, 'NEUTRAL'),
            (-2, 'SELL'),
            (-5, 'SELL'),
            (-6, 'STRONG_SELL'),
            (-10, 'STRONG_SELL')
        ]
        
        for score, expected_rating in test_cases:
            rating = self.aggregator._determine_rating(score)
            self.assertEqual(rating, expected_rating,
                f"评分 {score} 应该对应评级 {expected_rating}，但得到了 {rating}")


if __name__ == '__main__':
    unittest.main()
