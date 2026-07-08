import math
import random


class Capitalist:
    """负责资本家的报价、评估与还价决策"""

    def __init__(self, risk_aversion=0.3):
        self.risk_aversion = risk_aversion

    def _compute_statistics(self, remaining_amounts):
        if not remaining_amounts:
            return 0, 0
        n = len(remaining_amounts)
        mean = sum(remaining_amounts) / n
        variance = sum((x - mean) ** 2 for x in remaining_amounts) / n
        std = math.sqrt(variance)
        return mean, std

    def make_offer(self, remaining_amounts):
        """
        生成报价，精确到百位。
        策略：
        - 基础报价为剩余金额的期望值乘以一个动态系数。
        - 系数根据金额分布决定：高价值(>=75000)占比越高，系数越接近1；
          低价值(<1000)占比越高，系数越低。
        """
        mean, std = self._compute_statistics(remaining_amounts)
        if std == 0:
            return self._round_to_hundred(mean)

        n = len(remaining_amounts)
        high_count = sum(1 for a in remaining_amounts if a >= 75000)
        low_count = sum(1 for a in remaining_amounts if a < 1000)

        high_ratio = high_count / n
        low_ratio = low_count / n

        # 基础折扣系数：风险厌恶扣减
        cv = std / mean if mean > 0 else 0
        base_discount = 1 - self.risk_aversion * cv

        # 动态系数：高价值多时提高，低价值多时降低
        # 调节参数：当全部为高价值时，系数接近1.0；当全部为低价值时，系数降至0.7左右
        dynamic_factor = 0.7 + 0.3 * (high_ratio - low_ratio * 0.5)
        dynamic_factor = max(0.65, min(1.0, dynamic_factor))

        # 最终系数 = 基础折扣 * 动态系数，再略作压低（资本家总会尽量压价）
        final_factor = base_discount * dynamic_factor * 0.92
        offer = mean * final_factor

        # 确保报价不低于最低金额
        min_amount = min(remaining_amounts)
        offer = max(min_amount, offer)

        return self._round_to_hundred(offer)

    def _round_to_hundred(self, value):
        """向下取整到百位"""
        return int(value // 100) * 100

    def evaluate_counter_offer(self, counter_offer, remaining_amounts):
        """
        资本家决定是否接受梦想家的还价。
        """
        mean, _ = self._compute_statistics(remaining_amounts)
        if counter_offer <= mean:
            ratio = counter_offer / mean if mean > 0 else 1
            accept_prob = 0.6 + 0.3 * (1 - ratio)
            if random.random() < accept_prob:
                return True, "资本家接受了你的还价。"
            else:
                return False, "资本家拒绝了你的还价。"
        else:
            return False, "还价高于期望值，资本家拒绝了。"