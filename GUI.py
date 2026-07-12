import tkinter as tk
from tkinter import messagebox, scrolledtext
import random
import math


# ===================== 第一部分：资本家模块 =====================
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
        mean, std = self._compute_statistics(remaining_amounts)
        if std == 0:
            return self._round_to_hundred(mean)

        n = len(remaining_amounts)
        high_count = sum(1 for a in remaining_amounts if a >= 75000)
        low_count = sum(1 for a in remaining_amounts if a < 1000)

        high_ratio = high_count / n
        low_ratio = low_count / n

        cv = std / mean if mean > 0 else 0
        base_discount = 1 - self.risk_aversion * cv

        dynamic_factor = 0.7 + 0.3 * (high_ratio - low_ratio * 0.5)
        dynamic_factor = max(0.65, min(1.0, dynamic_factor))

        final_factor = base_discount * dynamic_factor * 0.92
        offer = mean * final_factor

        min_amount = min(remaining_amounts)
        offer = max(min_amount, offer)

        return self._round_to_hundred(offer)

    def _round_to_hundred(self, value):
        return int(value // 100) * 100

    def evaluate_counter_offer(self, counter_offer, remaining_amounts):
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


# ===================== 第二部分：箱子管理模块 =====================
class BoxManager:
    """负责箱子金额分配、开箱、金额面板管理"""

    BASE_AMOUNTS = [
        0.1, 1, 5, 10, 25, 50, 75, 100, 200, 300, 400, 500, 750, 1000,
        5000, 10000, 25000, 50000, 75000, 100000, 200000, 300000, 400000,
        500000, 750000, 1000000
    ]

    def __init__(self, mode='normal'):
        self.mode = mode
        self.amounts = self._generate_amounts()
        self.amount_pool = self.amounts.copy()
        self.boxes = {}
        self.dreamer_box = None
        self.opened_boxes = set()
        self._assign_boxes()

    def _generate_amounts(self):
        amounts = self.BASE_AMOUNTS.copy()
        if self.mode == 'tycoon':
            amounts[17:] = [1000000] * 9
        elif self.mode == 'depression':
            amounts[:9] = [0.1] * 9
        return amounts

    def _assign_boxes(self):
        shuffled = self.amounts.copy()
        random.shuffle(shuffled)
        self.boxes = {i+1: shuffled[i] for i in range(26)}

    def set_dreamer_box(self, box_id):
        if box_id in self.boxes and box_id not in self.opened_boxes:
            self.dreamer_box = box_id
            return True
        return False

    def open_box(self, box_id):
        if box_id == self.dreamer_box:
            return None
        if box_id in self.opened_boxes:
            return None
        if box_id not in self.boxes:
            return None
        amount = self.boxes[box_id]
        self.opened_boxes.add(box_id)
        self.amount_pool.remove(amount)
        return amount

    def reveal_dreamer_box(self):
        if self.dreamer_box is None:
            return None
        amount = self.boxes[self.dreamer_box]
        self.opened_boxes.add(self.dreamer_box)
        if amount in self.amount_pool:
            self.amount_pool.remove(amount)
        return amount

    def get_remaining_amounts(self):
        return self.amount_pool.copy()

    def get_remaining_boxes(self):
        return [b for b in self.boxes if b not in self.opened_boxes]

    def get_openable_boxes(self):
        return [b for b in self.get_remaining_boxes() if b != self.dreamer_box]

    def get_all_boxes_info(self):
        info = []
        for box_id in range(1, 27):
            status = "已打开" if box_id in self.opened_boxes else "未打开"
            if box_id == self.dreamer_box:
                status += " (你的箱子)"
            info.append((box_id, self.boxes[box_id], status))
        return info


# ===================== 第三部分：梦想家模块 =====================
class Dreamer:
    """负责梦想家的属性管理以及积分计算"""

    def __init__(self):
        self.has_counter_offer = True
        self.final_prize = None

    @staticmethod
    def calculate_score_stage1(prize):
        prize = max(0.1, prize)
        ratio = math.log10(prize) / 6
        return round(500 * ratio ** 2)

    @staticmethod
    def calculate_score_stage2(profit):
        if profit >= 0:
            if profit > 0:
                score = 500 * (1 - math.exp(-profit / 80000))
            else:
                score = 0
        else:
            loss = -profit
            score = -200 * (1 - math.exp(-loss / 150000))
        return round(score)


# 调试阶段使用的上帝模式
def debug_show_boxes(box_manager):
    """上帝模式：在命令行输出 26 个箱子的编号与对应金额"""
    print("\n===== 上帝模式：箱子金额一览 =====")
    print(f"{'编号':<6}{'金额':<12}")
    print("-" * 20)
    for box_id in sorted(box_manager.boxes.keys()):
        amount = box_manager.boxes[box_id]
        print(f"{box_id:<6}{amount:<12}")
    print("=" * 30)
# ===================== 第四部分：主程序 - 图形界面交互 =====================
def get_round_opens(round_number):
    if round_number <= 5:
        return 7 - round_number
    else:
        return 1


class DealOrNoDealGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Deal or No Deal?")
        self.geometry("1750x900")
        self.resizable(False, False)

        self.box_manager = None
        self.capitalist = None
        self.dreamer = None

        self.round_num = 1
        self.current_opens = 0
        self.needed_opens = 0
        self.game_state = "select_mode"

        self.offer_var = tk.StringVar(value="等待报价...")
        self.round_var = tk.StringVar(value="请选择游戏模式开始游戏")
        self.counter_var = tk.StringVar()
        self.current_offer = 0

        self._build_widgets()
        self._show_mode_selection()

    def _build_widgets(self):
        """构建所有界面元素"""
        # 顶部信息栏
        top_frame = tk.Frame(self, pady=10)
        top_frame.pack(fill=tk.X)
        tk.Label(top_frame, textvariable=self.round_var, font=("微软雅黑", 14, "bold")).pack()

        # 主内容区：左（金额面板）、中（箱子区）、右（操作区）
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15)

        # ---------- 左侧：金额面板 ----------
        left_frame = tk.LabelFrame(main_frame, text="金额面板", font=("微软雅黑", 12),
                                   fg="white", padx=10, pady=10, bg="#963634")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        self.amount_labels = []
        for i in range(13):
            lbl1 = tk.Label(left_frame, text="", font=("Times New Roman", 12, "bold"),
                            width=8, anchor="w", bg="#963634")
            lbl1.grid(row=i, column=0, pady=2, sticky="w")
            lbl2 = tk.Label(left_frame, text="", font=("Times New Roman", 12, "bold"),
                            width=8, anchor="w", bg="#963634")
            lbl2.grid(row=i, column=1, pady=2, padx=10, sticky="w")
            self.amount_labels.append(lbl1)
            self.amount_labels.append(lbl2)

        # ---------- 中间：箱子按钮区 ----------
        mid_frame = tk.LabelFrame(main_frame, text="箱子区", font=("微软雅黑", 12),
                                  padx=8, pady=8, bg="#7f7f7f")
        mid_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        self.box_buttons = {}
        for i in range(26):
            row = i // 6
            col = i % 6
            box_id = i + 1
            btn = tk.Button(
                mid_frame, text=str(box_id), width=8, height=1,
                font=("微软雅黑", 14, "bold"),
                command=lambda bid=box_id: self._on_box_click(bid),
                state=tk.DISABLED
            )
            btn.grid(row=row, column=col, padx=4, pady=3)
            self.box_buttons[box_id] = btn

        # ---------- 右侧：操作区 ----------
        right_frame = tk.LabelFrame(main_frame, text="操作区", font=("微软雅黑", 12),
                                    padx=12, pady=10, bg="#2e4971", fg="white")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, ipadx=8)

        tk.Label(right_frame, text="当前资本家报价：", font=("微软雅黑", 11),
                 bg="#2e4971", fg="white").pack(pady=(0,5))
        tk.Label(right_frame, textvariable=self.offer_var, font=("微软雅黑", 14, "bold"),
                 fg="#ffd54f", bg="#2e4971").pack(pady=(0,18))

        # Deal / No Deal 按钮
        self.deal_btn = tk.Button(
            right_frame, text="DEAL!!", font=("微软雅黑", 12, "bold"),
            bg="#388e3c", fg="white", width=16, height=2,
            command=self._on_deal, state=tk.DISABLED
        )
        self.deal_btn.pack(pady=6)

        self.no_deal_btn = tk.Button(
            right_frame, text="NO DEAL!!", font=("微软雅黑", 12, "bold"),
            bg="#d32f2f", fg="white", width=16, height=2,
            command=self._on_no_deal, state=tk.DISABLED
        )
        self.no_deal_btn.pack(pady=6)

        # 还价区域
        counter_frame = tk.Frame(right_frame, pady=15, bg="#2e4971")
        counter_frame.pack()
        tk.Label(counter_frame, text="还价金额（元）：", font=("微软雅黑", 12, "bold"),
                 bg="#2e4971", fg="white").pack(anchor="w")
        self.counter_entry = tk.Entry(counter_frame, textvariable=self.counter_var, width=16, state=tk.DISABLED)
        self.counter_entry.pack(pady=3)
        self.counter_btn = tk.Button(
            counter_frame, text="提交还价", font=("微软雅黑", 10),
            command=self._on_counter, state=tk.DISABLED, fg="black"
        )
        self.counter_btn.pack(pady=3)
        self.counter_tip = tk.Label(counter_frame, text="仅可使用 1 次", fg="#cccccc",
                                    font=("微软雅黑", 9), bg="#2e4971")
        self.counter_tip.pack()

        # ---------- 底部：游戏日志 ----------
        log_frame = tk.LabelFrame(self, text="游戏日志", font=("微软雅黑", 12), padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, font=("微软雅黑", 12), state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _show_mode_selection(self):
        """弹出模式选择窗口，关闭窗口默认选择标准模式"""
        mode_window = tk.Toplevel(self)
        mode_window.title("选择游戏模式")
        mode_window.geometry("320x270")
        mode_window.resizable(False, False)
        mode_window.transient(self)
        mode_window.grab_set()
        mode_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - mode_window.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - mode_window.winfo_height()) // 2
        mode_window.geometry(f"+{x}+{y}")

        # 标记是否已选择模式，避免关闭窗口时重复启动
        self.mode_selected_flag = False

        def choose_mode(mode):
            self.mode_selected_flag = True
            self._start_game(mode, mode_window)

        tk.Label(mode_window, text="请选择游戏模式", font=("微软雅黑", 13, "bold")).pack(pady=22)
        tk.Button(mode_window, text="1. 标准模式", width=20,
                  command=lambda: choose_mode("normal")).pack(pady=5)
        tk.Button(mode_window, text="2. 大富翁模式", width=20,
                  command=lambda: choose_mode("tycoon")).pack(pady=5)
        tk.Button(mode_window, text="3. 大萧条模式", width=20,
                  command=lambda: choose_mode("depression")).pack(pady=5)

        # 窗口关闭事件：若未选择则默认标准模式
        mode_window.protocol("WM_DELETE_WINDOW", lambda: self._on_mode_window_close(mode_window))

    def _on_mode_window_close(self, mode_window):
        """关闭模式窗口时，若未选择模式则默认标准模式"""
        if not self.mode_selected_flag:
            # 销毁窗口并启动标准模式
            mode_window.destroy()
            self._start_game("normal", None)  # None 表示窗口已销毁，无需再销毁
        else:
            # 已通过按钮启动游戏，窗口已被销毁，无需额外操作
            pass

    def _start_game(self, mode, mode_window=None):
        """初始化新游戏，mode_window 可选，若不为 None 则销毁该窗口"""
        if mode_window is not None:
            mode_window.destroy()

        self.box_manager = BoxManager(mode)
        debug_show_boxes(self.box_manager)  # 上帝模式
        self.capitalist = Capitalist()
        self.dreamer = Dreamer()

        self.round_num = 1
        self.current_opens = 0
        self.game_state = "select_initial"

        # 重置箱子按钮
        for bid in self.box_buttons:
            self.box_buttons[bid].config(
                text=str(bid), state=tk.NORMAL,
                font=("微软雅黑", 14, "bold"), width=8,
                bg="SystemButtonFace", fg="black"
            )

        self._update_amount_panel()

        mode_name = {"normal": "标准模式", "tycoon": "大富翁模式", "depression": "大萧条模式"}[mode]
        self.round_var.set(f"【{mode_name}】请选择一个箱子作为你的专属箱子")
        self.offer_var.set("等待报价...")
        self.counter_var.set("")
        self.counter_tip.config(text="全场仅可使用 1 次")
        self.current_offer = 0

        self.deal_btn.config(state=tk.DISABLED)
        self.no_deal_btn.config(state=tk.DISABLED)
        self.counter_entry.config(state=tk.DISABLED)
        self.counter_btn.config(state=tk.DISABLED)

        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

        self._add_log(f"游戏开始，当前模式：{mode_name}")
        self._add_log("请从 26 个箱子中点击选择一个作为你的专属箱子。")

    def _update_amount_panel(self):
        all_amounts = sorted(self.box_manager.amounts)
        remaining = self.box_manager.get_remaining_amounts()
        for i, amount in enumerate(all_amounts):
            lbl = self.amount_labels[i]
            if amount in remaining:
                lbl.config(text=f"$ {amount}", fg="#c2bd96",
                           font=("Times New Roman", 14, "bold"))
            else:
                lbl.config(text=f"$ {amount}", fg="#9e9e9e",
                           font=("Times New Roman", 14, "bold", "overstrike"))

    def _on_box_click(self, box_id):
        if self.game_state == "select_initial":
            self.box_manager.set_dreamer_box(box_id)
            self.box_buttons[box_id].config(bg="#1976d2", fg="white", text="我的",
                                            font=("微软雅黑", 14, "bold"))
            self._add_log(f"你选择了 {box_id} 号箱子作为你的专属箱子。")

            self.game_state = "opening"
            self.needed_opens = get_round_opens(self.round_num)
            self.current_opens = 0
            self.round_var.set(f"第 {self.round_num} 轮：请打开 {self.needed_opens} 个箱子（已开 {self.current_opens}/{self.needed_opens}）")
            self.box_buttons[box_id].config(state=tk.DISABLED)

        elif self.game_state == "opening":
            amount = self.box_manager.open_box(box_id)
            if amount is None:
                return

            self.box_buttons[box_id].config(state=tk.DISABLED, text=f"${amount}",
                                            bg="#e0e0e0", font=("微软雅黑", 10, "bold"))
            self.current_opens += 1
            self._add_log(f"打开 {box_id} 号箱子，金额：{amount} 元")
            self._update_amount_panel()
            self.round_var.set(f"第 {self.round_num} 轮：请打开 {self.needed_opens} 个箱子（已开 {self.current_opens}/{self.needed_opens}）")

            if self.current_opens >= self.needed_opens:
                self._enter_offer_phase()

    def _enter_offer_phase(self):
        """进入报价阶段，先显示思考动画再显示报价"""
        self.game_state = "offer"
        # 禁用操作按钮，等待思考结束
        self.deal_btn.config(state=tk.DISABLED)
        self.no_deal_btn.config(state=tk.DISABLED)
        self.counter_entry.config(state=tk.DISABLED)
        self.counter_btn.config(state=tk.DISABLED)
        for bid in self.box_buttons:
            self.box_buttons[bid].config(state=tk.DISABLED)

        # 计算报价，但延迟显示
        remaining = self.box_manager.get_remaining_amounts()
        offer = self.capitalist.make_offer(remaining)
        self.current_offer = offer

        self._show_thinking("资本家正在思考报价...", self._finish_offer_phase)

    def _finish_offer_phase(self):
        """思考结束后显示报价，启用操作按钮"""
        self.offer_var.set(f"{self.current_offer} 元")
        self._add_log(f"本轮开箱结束，资本家给出报价：{self.current_offer} 元")
        self.round_var.set(f"第 {self.round_num} 轮：报价 {self.current_offer} 元，在操作区做出决定")

        self.deal_btn.config(state=tk.NORMAL)
        self.no_deal_btn.config(state=tk.NORMAL)
        if self.dreamer.has_counter_offer:
            self.counter_entry.config(state=tk.NORMAL)
            self.counter_btn.config(state=tk.NORMAL)
        else:
            self.counter_entry.config(state=tk.DISABLED)
            self.counter_btn.config(state=tk.DISABLED)

    def _on_deal(self):
        if self.game_state != "offer":
            return
        offer = self.current_offer
        self.dreamer.final_prize = offer
        self._add_log(f"你选择成交，最终获得奖金：{offer} 元")
        self._end_game()

    def _on_no_deal(self):
        if self.game_state != "offer":
            return
        self._add_log("你选择不成交，进入下一轮开箱。")
        self._next_round()

    def _on_counter(self):
        if self.game_state != "offer" or not self.dreamer.has_counter_offer:
            return

        try:
            counter = float(self.counter_var.get().strip())
            if counter <= 0:
                messagebox.showwarning("提示", "请输入大于 0 的有效金额！")
                return
        except ValueError:
            messagebox.showwarning("提示", "请输入合法的数字金额！")
            return

        if counter <= self.current_offer:
            messagebox.showwarning("提示", f"还价金额必须大于资本家的报价 ({self.current_offer} 元)！")
            return

        # 消耗还价机会，禁用控件
        self.dreamer.has_counter_offer = False
        self.counter_entry.config(state=tk.DISABLED)
        self.counter_btn.config(state=tk.DISABLED)
        self.counter_tip.config(text="还价机会已使用")
        self.deal_btn.config(state=tk.DISABLED)
        self.no_deal_btn.config(state=tk.DISABLED)
        for bid in self.box_buttons:
            self.box_buttons[bid].config(state=tk.DISABLED)

        # 显示思考动画，然后处理结果
        self._show_thinking("等待资本家回应还价...", lambda: self._finish_counter(counter))

    def _finish_counter(self, counter):
        """思考结束后处理还价结果"""
        remaining = self.box_manager.get_remaining_amounts()
        accepted, reason = self.capitalist.evaluate_counter_offer(counter, remaining)
        self._add_log(f"你提出还价：{counter} 元。{reason}")

        if accepted:
            self.dreamer.final_prize = counter
            self._add_log(f"还价成交，最终获得奖金：{counter} 元")
            self._end_game()
        else:
            self._next_round()

    def _next_round(self):
        self.round_num += 1
        self.needed_opens = get_round_opens(self.round_num)
        self.current_opens = 0
        openable = self.box_manager.get_openable_boxes()

        if len(openable) == 0:
            prize = self.box_manager.reveal_dreamer_box()
            self.dreamer.final_prize = prize
            self._add_log(f"所有箱子已开完！你的箱子实际金额为：{prize} 元")
            self._end_game()
            return

        if self.needed_opens > len(openable):
            self.needed_opens = len(openable)

        self.game_state = "opening"
        self.round_var.set(f"第 {self.round_num} 轮：请打开 {self.needed_opens} 个箱子（已开 {self.current_opens}/{self.needed_opens}）")
        self.offer_var.set("等待报价...")
        self.current_offer = 0

        for bid in openable:
            self.box_buttons[bid].config(state=tk.NORMAL)

        self.deal_btn.config(state=tk.DISABLED)
        self.no_deal_btn.config(state=tk.DISABLED)

    def _show_thinking(self, message, callback):
        """显示带旋转动画的思考窗口，3~5秒后自动关闭并执行回调"""
        wait_win = tk.Toplevel(self)
        wait_win.title("请稍候")
        wait_win.geometry("300x150")
        wait_win.resizable(False, False)
        wait_win.transient(self)
        wait_win.grab_set()
        wait_win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 300) // 2
        y = self.winfo_y() + (self.winfo_height() - 120) // 2
        wait_win.geometry(f"+{x}+{y}")

        tk.Label(wait_win, text=message, font=("微软雅黑", 12)).pack(pady=15)
        spin_label = tk.Label(wait_win, text="🕐", font=("微软雅黑", 24))
        spin_label.pack()

        spin_chars = ["🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚", "🕛"]
        idx = 0

        def update_spin():
            nonlocal idx
            spin_label.config(text=spin_chars[idx % 12])
            idx += 1
            wait_win.after(50, update_spin)

        update_spin()

        delay = random.randint(1500, 3500)
        wait_win.after(delay, lambda: [wait_win.destroy(), callback()])

    def _end_game(self):
        self.game_state = "game_over"
        prize = self.dreamer.final_prize
        actual = self.box_manager.boxes[self.box_manager.dreamer_box]
        profit = prize - actual

        score1 = Dreamer.calculate_score_stage1(prize)
        score2 = Dreamer.calculate_score_stage2(profit)
        total_score = score1 + score2

        # 彩蛋检测：奖金和实际箱子都是 1,000,000
        jackpot = (prize == 1000000 and actual == 1000000)
        if jackpot:
            total_score += 500
            easter_msg = "恭喜达成百万满贯！额外 +500 分"
        else:
            easter_msg = ""

        self.box_buttons[self.box_manager.dreamer_box].config(
            state=tk.NORMAL, text=f"${actual}", bg="#ffc107", fg="black",
            font=("微软雅黑", 10, "bold")
        )

        # 自定义结果窗口
        result_win = tk.Toplevel(self)
        result_win.title("游戏结束" if not jackpot else "🎉 百万满贯！")

        if jackpot:
            result_win.geometry("500x570")
        else:
            result_win.geometry("500x500")

        result_win.resizable(False, False)
        result_win.transient(self)
        result_win.grab_set()
        result_win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 420) // 2
        y = self.winfo_y() + (self.winfo_height() - 480) // 2
        result_win.geometry(f"+{x}+{y}")

        # 标题行
        title_text = "===== 游戏结束 =====" if not jackpot else "🎉 百万满贯 🎉"
        title_color = "#333" if not jackpot else "#b8860b"
        tk.Label(result_win, text=title_text,
                 font=("微软雅黑", 14, "bold"), fg=title_color).pack(pady=10)

        # 实际金额
        tk.Label(result_win, text=f"你的箱子实际金额：{actual} 元",
                 font=("微软雅黑", 11), fg="#1565c0").pack()
        # 最终奖金
        tk.Label(result_win, text=f"最终获得奖金：{prize} 元",
                 font=("微软雅黑", 11), fg="#2e7d32").pack(pady=2)

        # 盈亏
        if profit >= 0:
            profit_text = f"本次交易你多赚：{profit} 元"
            profit_color = "#2e7d32"
        else:
            profit_text = f"本次交易你少赚（资本家盈利）：{-profit} 元"
            profit_color = "#c62828"
        tk.Label(result_win, text=profit_text, font=("微软雅黑", 11),
                 fg=profit_color).pack(pady=2)

        # 彩蛋信息
        if jackpot:
            tk.Label(result_win, text=easter_msg, font=("微软雅黑", 12, "bold"),
                     fg="#d4af37", bg="#fffacd").pack(pady=8, ipadx=10, ipady=3)

        tk.Label(result_win, text="─" * 30, fg="gray").pack(pady=5)

        # 积分明细
        tk.Label(result_win, text="--- 积分明细 ---",
                 font=("微软雅黑", 12, "bold"), fg="#6a1b9a").pack(pady=5)
        tk.Label(result_win, text=f"奖金金额积分：{score1} / 500",
                 font=("微软雅黑", 11), fg="#0d47a1").pack()
        tk.Label(result_win, text=f"交易盈亏积分：{score2} / 500",
                 font=("微软雅黑", 11), fg="#bf360c").pack()
        if jackpot:
            tk.Label(result_win, text="彩蛋加分：+500",
                     font=("微软雅黑", 11), fg="#d4af37").pack()
        tk.Label(result_win, text=f"总积分：{total_score} / 1000" if jackpot else f"总积分：{total_score} / 1000",
                 font=("微软雅黑", 14, "bold"), fg="#d84315").pack(pady=10)

        # 按钮区域
        btn_frame = tk.Frame(result_win)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="查看全部箱子", width=14,
                  command=lambda: self._show_all_boxes(result_win)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="再来一局", width=12,
                  command=lambda: [result_win.destroy(), self._show_mode_selection()]).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="退出游戏", width=12,
                  command=lambda: [result_win.destroy(), self.destroy()]).pack(side=tk.LEFT, padx=5)

        # 日志输出
        log_lines = [
            "===== 游戏结束 =====",
            f"你的箱子实际金额：{actual} 元",
            f"最终获得奖金：{prize} 元",
            profit_text,
        ]
        if jackpot:
            log_lines.append(easter_msg)
        log_lines += [
            "--- 积分明细 ---",
            f"奖金金额积分：{score1} / 500",
            f"交易盈亏积分：{score2} / 500",
        ]
        if jackpot:
            log_lines.append("彩蛋加分：+500")
        log_lines.append(f"总积分：{total_score} / {'1500' if jackpot else '1000'}")
        self._add_log("\n" + "\n".join(log_lines))

    def _show_all_boxes(self, parent_window=None):
        """弹出窗口显示所有箱子的编号、金额和状态"""
        info = self.box_manager.get_all_boxes_info()
        view_win = tk.Toplevel(parent_window or self)
        view_win.title("全部箱子信息")
        view_win.geometry("500x800")
        view_win.resizable(False, False)
        if parent_window:
            view_win.transient(parent_window)
        view_win.grab_set()

        view_win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 500) // 2
        y = self.winfo_y() + (self.winfo_height() - 550) // 2
        view_win.geometry(f"+{x}+{y}")

        tk.Label(view_win, text="所有箱子明细", font=("微软雅黑", 14, "bold")).pack(pady=10)

        text_area = scrolledtext.ScrolledText(view_win, font=("Consolas", 11), wrap=tk.NONE)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        text_area.insert(tk.END, f"{'编号':<6}{'金额':<12}状态\n")
        text_area.insert(tk.END, "-" * 30 + "\n")

        for box_id, amount, status in info:
            amount_str = f"$ {amount}"
            if "你的箱子" in status:
                text_area.insert(tk.END, f"{box_id:<6}{amount_str:<12}{status}\n", "dreamer")
            else:
                text_area.insert(tk.END, f"{box_id:<6}{amount_str:<12}{status}\n")

        text_area.tag_config("dreamer", foreground="#1976d2", font=("Consolas", 11, "bold"))
        text_area.config(state=tk.DISABLED)

        tk.Button(view_win, text="关闭", width=10, command=view_win.destroy).pack(pady=10)

    def _add_log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    try:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except:
        pass

    app = DealOrNoDealGame()
    app.mainloop()