"""
价量关系信号分析模块 (Bidirectional)
识别机构吸筹信号 (Accumulation) 和派发信号 (Distribution)

吸筹信号:
- 放量突破横盘区 (Accumulation Breakout)
- 威科夫弹簧/震仓 (Wyckoff Spring)

派发信号:
- 高位放量滞涨 (High Volume Stagnation)
- 放量下跌 (High Volume Decline)
- 放量跌破支撑 (Break Support with Heavy Volume)
- 高位缩量上涨 (Low Volume Rise)
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class PriceVolumeSignals:
    """价量关系信号分析器"""

    def __init__(self, config):
        """
        初始化价量信号分析器

        Args:
            config: 配置模块
        """
        self.config = config
        self.params = config.PV_PARAMS

    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        执行价量关系分析 (双向)

        Args:
            df: 包含 OHLCV 和技术指标的 DataFrame

        Returns:
            包含所有信号的字典
        """
        if df.empty or len(df) < self.params['lookback_period']:
            logger.warning("数据不足，无法进行价量分析")
            return {}

        signals = {}

        # ========== 吸筹信号 (Accumulation Signals) ==========

        # 1. 放量突破横盘区
        breakout_signal = self.detect_accumulation_breakout(df)
        logger.debug(f"放量突破检测: {breakout_signal}")
        if breakout_signal['detected']:
            signals['ACCUMULATION_BREAKOUT'] = breakout_signal

        # 2. 威科夫弹簧/震仓
        spring_signal = self.detect_wyckoff_spring(df)
        logger.debug(f"威科夫弹簧检测: {spring_signal}")
        if spring_signal['detected']:
            signals['WYCKOFF_SPRING'] = spring_signal

        # ========== 派发信号 (Distribution Signals) ==========

        # 3. 高位放量滞涨
        stagnation_signal = self.detect_high_volume_stagnation(df)
        logger.debug(f"高位放量滞涨检测: {stagnation_signal}")
        if stagnation_signal['detected']:
            signals['HIGH_VOLUME_STAGNATION'] = stagnation_signal

        # 4. 放量下跌
        decline_signal = self.detect_high_volume_decline(df)
        logger.debug(f"放量下跌检测: {decline_signal}")
        if decline_signal['detected']:
            signals['HIGH_VOLUME_DECLINE'] = decline_signal

        # 5. 放量跌破支撑
        support_break_signal = self.detect_break_support(df)
        logger.debug(f"放量跌破支撑检测: {support_break_signal}")
        if support_break_signal['detected']:
            signals['BREAK_SUPPORT_HEAVY_VOLUME'] = support_break_signal

        # 6. 高位缩量上涨
        low_volume_rise = self.detect_low_volume_rise(df)
        logger.debug(f"高位缩量上涨检测: {low_volume_rise}")
        if low_volume_rise['detected']:
            signals['LOW_VOLUME_RISE'] = low_volume_rise

        return signals

    # =========================================================================
    # 吸筹信号检测 (Accumulation Signal Detection)
    # =========================================================================

    def detect_accumulation_breakout(
        self,
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        检测放量突破横盘区 (Accumulation Breakout)

        逻辑:
        1. 股价经历长期横盘整理 (至少20天)
        2. 成交量显著放大 (超过均量的vol_multiplier倍)
        3. 股价向上突破横盘区上沿
        4. 突破时收盘价接近当日最高价 (表明买方力量强劲)

        Args:
            df: 价格数据

        Returns:
            信号字典
        """
        lookback = self.params['lookback_period']
        vol_multiplier = self.params['vol_multiplier']

        if len(df) < lookback:
            return {'detected': False}

        df = df.copy()
        df['avg_volume'] = df['volume'].rolling(window=lookback).mean()

        # 检查最近5个交易日
        recent_days = 5
        recent_df = df.tail(recent_days)

        # 检查是否在横盘整理后
        # 横盘定义: 回看期内价格波动在10%以内
        price_high = df['high'].tail(lookback).max()
        price_low = df['low'].tail(lookback).min()
        price_range = (price_high - price_low) / price_low

        # 是否在横盘 (波动 < 20%)
        is_consolidating = price_range < 0.20

        # 检查近期是否放量
        avg_recent_volume = recent_df['volume'].mean()
        avg_baseline_volume = df['avg_volume'].iloc[-1]
        is_high_volume = avg_recent_volume > (avg_baseline_volume * vol_multiplier)

        # 检查是否向上突破
        # 突破定义: 当前收盘价 > 近lookback期最高价的95%
        current_close = df['close'].iloc[-1]
        previous_high = df['high'].iloc[-lookback:-recent_days].max()
        is_breakout = current_close > previous_high * 0.95

        # 检查收盘价是否接近最高价 (强势突破)
        latest_bar = recent_df.iloc[-1]
        close_near_high = (latest_bar['close'] / latest_bar['high']) > 0.98

        detected = is_consolidating and is_high_volume and is_breakout and close_near_high

        logger.debug(
            f"放量突破详情: 横盘={is_consolidating} (波动={price_range:.2%}), "
            f"放量={is_high_volume} (均量比={avg_recent_volume/avg_baseline_volume:.2f}x), "
            f"突破={is_breakout}, 强势收盘={close_near_high}, 检测结果={detected}"
        )

        signal_date = df['date'].iloc[-1] if 'date' in df.columns else None

        return {
            'detected': detected,
            'signal_date': signal_date,
            'description': f"放量突破横盘区 (成交量为均量{avg_recent_volume/avg_baseline_volume:.2f}倍，突破价位{previous_high:.2f})",
            'severity': 'high' if detected else 'none',
            'signal_type': 'accumulation',
            'details': {
                'consolidation_range': f"{price_range:.2%}",
                'volume_ratio': f"{avg_recent_volume/avg_baseline_volume:.2f}x",
                'breakout_price': previous_high,
                'current_price': current_close
            }
        }

    def detect_wyckoff_spring(
        self,
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        检测威科夫弹簧/震仓 (Wyckoff Spring)

        逻辑:
        1. 股价短暂跌破支撑位 (如20日均线或前期低点)
        2. 跌破时成交量不大 (说明卖压不强)
        3. 随后快速拉回到支撑位之上
        4. 这是机构测试市场剩余供应并清洗浮筹的典型手法

        Args:
            df: 价格数据

        Returns:
            信号字典
        """
        lookback = self.params['lookback_period']

        if len(df) < lookback or 'ma20' not in df.columns:
            return {'detected': False}

        df = df.copy()
        df['avg_volume'] = df['volume'].rolling(window=lookback).mean()

        # 检查最近10个交易日
        recent_days = 10
        recent_df = df.tail(recent_days)

        detected = False
        spring_date = None
        spring_details = {}

        # 寻找"弹簧"形态
        for i in range(1, len(recent_df) - 2):  # 至少需要前后各有数据点
            current_idx = recent_df.index[i]
            current_row = recent_df.iloc[i]
            prev_row = recent_df.iloc[i - 1]
            next_row = recent_df.iloc[i + 1]
            next2_row = recent_df.iloc[i + 2] if i + 2 < len(recent_df) else None

            # 获取在原始 df 中的位置
            df_idx = df.index.get_loc(current_idx)

            if df_idx == 0:
                continue

            # 条件1: 当日低点跌破20日均线
            ma20_value = df.loc[current_idx, 'ma20']
            broke_support = current_row['low'] < ma20_value

            # 条件2: 前一日收盘价在均线之上
            prev_above_ma = prev_row['close'] > df.iloc[df_idx - 1]['ma20']

            # 条件3: 跌破时成交量不大 (< 1.5倍均量)
            volume_ratio = current_row['volume'] / df.loc[current_idx, 'avg_volume']
            low_volume = volume_ratio < 1.5

            # 条件4: 随后1-2天快速拉回
            if next2_row is not None:
                quick_recovery = (
                    next_row['close'] > ma20_value or
                    next2_row['close'] > ma20_value
                )
            else:
                quick_recovery = next_row['close'] > ma20_value

            if broke_support and prev_above_ma and low_volume and quick_recovery:
                detected = True
                spring_date = df.loc[current_idx, 'date'] if 'date' in df.columns else None
                spring_details = {
                    'support_level': ma20_value,
                    'low_price': current_row['low'],
                    'volume_ratio': f"{volume_ratio:.2f}x",
                    'recovery_close': next_row['close']
                }
                logger.debug(f"威科夫弹簧检测到: 支撑={ma20_value:.2f}, 低点={current_row['low']:.2f}, 成交量比={volume_ratio:.2f}x")
                break

        return {
            'detected': detected,
            'signal_date': spring_date,
            'description': f"威科夫弹簧 (跌破支撑{spring_details.get('support_level', 0):.2f}后快速拉回)",
            'severity': 'high' if detected else 'none',
            'signal_type': 'accumulation',
            'details': spring_details
        }

    # =========================================================================
    # 派发信号检测 (Distribution Signal Detection)
    # =========================================================================

    def detect_high_volume_stagnation(
        self,
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        检测高位放量滞涨

        逻辑:
        1. 股价在回看期内有显著上涨 (定义为上涨趋势)
        2. 最近几个交易日成交量显著放大
        3. 但股价涨幅很小或停滞

        Args:
            df: 价格数据

        Returns:
            信号字典
        """
        lookback = self.params['lookback_period']
        vol_multiplier = self.params['vol_multiplier']
        price_threshold = self.params['price_change_threshold']

        if len(df) < lookback:
            return {'detected': False}

        # 计算平均成交量 (近60日)
        df = df.copy()
        df['avg_volume'] = df['volume'].rolling(window=lookback).mean()

        # 检查最近5个交易日
        recent_days = 5
        recent_df = df.tail(recent_days)

        # 检查是否在上涨趋势后 (近lookback期内涨幅 > 10%)
        price_change = (df['close'].iloc[-1] / df['close'].iloc[-lookback] - 1)
        in_uptrend = price_change > 0.10

        if not in_uptrend:
            logger.debug(f"高位放量滞涨: 不在上涨趋势中 (涨幅: {price_change:.2%}, 需要 > 10%)")
            return {'detected': False}

        # 检查近期是否放量
        avg_recent_volume = recent_df['volume'].mean()
        avg_baseline_volume = df['avg_volume'].iloc[-1]

        is_high_volume = avg_recent_volume > (avg_baseline_volume * vol_multiplier)

        # 检查近期价格是否滞涨
        recent_price_change = (recent_df['close'].iloc[-1] / recent_df['close'].iloc[0] - 1)
        is_stagnant = abs(recent_price_change) < price_threshold

        logger.debug(f"高位放量滞涨详情: 放量={is_high_volume} (均量比={avg_recent_volume/avg_baseline_volume:.2f}x, 需要>{vol_multiplier}x), 滞涨={is_stagnant} (涨幅={recent_price_change:.2%}, 需要<{price_threshold:.2%})")
        
        detected = is_high_volume and is_stagnant

        signal_date = df['date'].iloc[-1] if 'date' in df.columns else None

        return {
            'detected': detected,
            'signal_date': signal_date,
            'description': f"股价在上涨趋势后出现放量滞涨 (涨幅仅{recent_price_change:.2%}，成交量为均量{avg_recent_volume/avg_baseline_volume:.2f}倍)",
            'severity': 'high' if detected else 'none',
            'signal_type': 'distribution',
            'details': {
                'trend_gain': f"{price_change:.2%}",
                'recent_change': f"{recent_price_change:.2%}",
                'volume_ratio': f"{avg_recent_volume/avg_baseline_volume:.2f}x"
            }
        }

    def detect_high_volume_decline(
        self,
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        检测放量下跌

        逻辑:
        单日或连续几日成交量放大，且股价显著下跌

        Args:
            df: 价格数据

        Returns:
            信号字典
        """
        vol_multiplier = self.params['vol_multiplier']
        decline_threshold = self.params['decline_threshold']
        lookback = self.params['lookback_period']

        if len(df) < lookback:
            return {'detected': False}

        df = df.copy()
        df['avg_volume'] = df['volume'].rolling(window=lookback).mean()

        # 检查最近3个交易日
        recent_days = 3
        recent_df = df.tail(recent_days)

        detected = False
        signal_dates = []
        max_decline = 0
        max_volume_ratio = 0

        for i in range(len(recent_df)):
            row = recent_df.iloc[i]
            idx = df.index[df.index == row.name][0]

            # 计算跌幅
            if idx > 0:
                prev_close = df.loc[idx - 1, 'close']
                decline = (row['close'] - prev_close) / prev_close

                # 成交量倍数
                volume_ratio = row['volume'] / df.loc[idx, 'avg_volume']

                # 判断是否放量下跌
                if decline < -decline_threshold and volume_ratio > vol_multiplier:
                    detected = True
                    if 'date' in df.columns:
                        signal_dates.append(df.loc[idx, 'date'])
                    max_decline = min(max_decline, decline)
                    max_volume_ratio = max(max_volume_ratio, volume_ratio)
                    logger.debug(f"放量下跌检测到: 跌幅={decline:.2%}, 成交量比={volume_ratio:.2f}x")

        return {
            'detected': detected,
            'signal_date': signal_dates[-1] if signal_dates else None,
            'description': f"放量下跌 (最大跌幅{max_decline:.2%}，成交量达均量{max_volume_ratio:.2f}倍)",
            'severity': 'high' if detected else 'none',
            'signal_type': 'distribution',
            'details': {
                'max_decline': f"{max_decline:.2%}",
                'max_volume_ratio': f"{max_volume_ratio:.2f}x",
                'signal_days': len(signal_dates)
            }
        }

    def detect_break_support(
        self,
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        检测放量跌破关键支撑位

        支撑位包括:
        - 均线支撑 (20日、60日、120日均线)
        - 前期重要低点

        Args:
            df: 价格数据

        Returns:
            信号字典
        """
        vol_multiplier = self.params['vol_multiplier']
        lookback = self.params['lookback_period']
        ma_periods = self.params['support_ma_periods']

        if len(df) < max(ma_periods):
            return {'detected': False}

        df = df.copy()
        df['avg_volume'] = df['volume'].rolling(window=lookback).mean()

        # 检查最近5个交易日
        recent_days = 5
        recent_df = df.tail(recent_days)

        broken_supports = []

        for i in range(len(recent_df)):
            row = recent_df.iloc[i]
            idx = df.index[df.index == row.name][0]

            # 检查成交量是否放大
            volume_ratio = row['volume'] / df.loc[idx, 'avg_volume']
            is_high_volume = volume_ratio > vol_multiplier

            if not is_high_volume:
                continue

            # 检查是否跌破均线支撑
            for period in ma_periods:
                ma_col = f'ma{period}'
                if ma_col in df.columns:
                    ma_value = df.loc[idx, ma_col]
                    prev_close = df.loc[idx - 1, 'close'] if idx > 0 else None

                    # 前一日在均线之上，当日跌破
                    if prev_close and prev_close > ma_value and row['close'] < ma_value:
                        broken_supports.append({
                            'type': f'MA{period}',
                            'level': ma_value,
                            'volume_ratio': volume_ratio,
                            'date': df.loc[idx, 'date'] if 'date' in df.columns else None
                        })

        detected = len(broken_supports) > 0
        
        if not detected:
            logger.debug(f"放量跌破支撑: 未检测到跌破支撑位")

        return {
            'detected': detected,
            'signal_date': broken_supports[0]['date'] if broken_supports else None,
            'description': f"放量跌破{len(broken_supports)}个关键支撑位: {', '.join([s['type'] for s in broken_supports])}",
            'severity': 'critical' if detected else 'none',
            'signal_type': 'distribution',
            'details': {
                'broken_supports': broken_supports
            }
        }

    def detect_low_volume_rise(
        self,
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        检测高位缩量上涨

        逻辑:
        在上涨趋势末期，股价继续创新高但成交量萎缩

        Args:
            df: 价格数据

        Returns:
            信号字典
        """
        lookback = self.params['lookback_period']

        if len(df) < lookback:
            return {'detected': False}

        # 检查是否在上涨趋势中
        price_change = (df['close'].iloc[-1] / df['close'].iloc[-lookback] - 1)
        in_uptrend = price_change > 0.10

        if not in_uptrend:
            logger.debug(f"高位缩量上涨: 不在上涨趋势中 (涨幅: {price_change:.2%}, 需要 > 10%)")
            return {'detected': False}

        # 检查最近10个交易日的价格和成交量趋势
        recent_days = 10
        recent_df = df.tail(recent_days).copy()

        # 计算价格和成交量的线性回归斜率
        recent_df['index'] = range(len(recent_df))
        price_slope = np.polyfit(recent_df['index'], recent_df['close'], 1)[0]
        volume_slope = np.polyfit(recent_df['index'], recent_df['volume'], 1)[0]

        # 价格上涨 (斜率为正) 但成交量下降 (斜率为负)
        detected = price_slope > 0 and volume_slope < 0

        # 检查是否创新高
        is_new_high = df['close'].iloc[-1] >= df['close'].tail(lookback).max()

        # 只有在创新高的情况下才认为是有效信号
        detected = detected and is_new_high
        
        logger.debug(f"高位缩量上涨详情: 价格上涨={price_slope > 0}, 成交量下降={volume_slope < 0}, 创新高={is_new_high}, 检测结果={detected}")

        return {
            'detected': detected,
            'signal_date': df['date'].iloc[-1] if 'date' in df.columns else None,
            'description': f"高位缩量上涨 (价格创新高但成交量萎缩{abs(volume_slope):.0f})",
            'severity': 'medium' if detected else 'none',
            'signal_type': 'distribution',
            'details': {
                'trend_gain': f"{price_change:.2%}",
                'price_slope': price_slope,
                'volume_slope': volume_slope,
                'is_new_high': is_new_high
            }
        }


def analyze_price_volume(df: pd.DataFrame, config) -> Dict[str, Any]:
    """
    便捷函数：执行价量关系分析

    Args:
        df: 价格数据
        config: 配置模块

    Returns:
        信号字典
    """
    analyzer = PriceVolumeSignals(config)
    return analyzer.analyze(df)
