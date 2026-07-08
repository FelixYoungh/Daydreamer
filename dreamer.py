import math

class Dreamer:
    """负责梦想家的决策、还价以及积分计算"""

    def __init__(self):
        self.has_counter_offer = True
        self.final_prize = None

    def choose_action(self, offer, capitalist, remaining_amounts):
        print(f"\n资本家报价：{offer} 元")
        options = ["deal", "no deal"]
        if self.has_counter_offer:
            options.append("counter")
            prompt = "请选择 (deal/no deal/counter)："
        else:
            prompt = "请选择 (deal/no deal)："

        while True:
            choice = input(prompt).strip().lower()
            if choice in ('deal', 'no deal'):
                if choice == 'deal':
                    return ('deal', offer)
                else:
                    return ('no deal', None)
            elif choice == 'counter' and self.has_counter_offer:
                return self._handle_counter_offer(offer, capitalist, remaining_amounts)
            else:
                print("无效输入，请重新选择。")

    def _handle_counter_offer(self, current_offer, capitalist, remaining_amounts):
        try:
            counter = float(input("请输入你的还价金额："))
        except ValueError:
            print("无效金额，视为放弃还价。")
            self.has_counter_offer = False
            return ('no deal', None)

        accepted, reason = capitalist.evaluate_counter_offer(counter, remaining_amounts)
        print(reason)
        self.has_counter_offer = False
        if accepted:
            return ('deal', counter)
        else:
            return ('no deal', None)

    @staticmethod
    def calculate_score_stage1(prize):
        """第一段积分：基于最终奖金，0-500分（原1000分的一半）"""
        # min_val = math.log10(0.1)
        # max_val = math.log10(1000000)
        prize = max(0.1, prize)
        # log_prize = math.log10(prize)
        # full_score = 1 + (log_prize - min_val) / (max_val - min_val) * 999
        ratio = math.log10(prize) / 6
        return round(500 * ratio ** 2)  # 映射到0-500
        # return round(full_score * 0.5)

    @staticmethod
    def calculate_score_stage2(profit):
        """
        第二段积分：基于交易盈亏（profit = 最终到手 - 箱子实际金额），-500~500分
        正盈利（梦想家赚）：较快逼近500，参数T=30000
        负盈利（资本家赚）：较慢逼近-500，参数U=300000
        """
        if profit >= 0:
            # 正区间：score = 500 * (1 - exp(-profit / 30000))
            if profit > 0:
                score = 500 * (1 - math.exp(-profit / 30000))
            else:
                score = 0
        else:
            # 负区间：score = -500 * (1 - exp(profit / 300000))  注意profit为负
            loss = -profit
            score = -200 * (1 - math.exp(-loss / 300000))
        return round(score)