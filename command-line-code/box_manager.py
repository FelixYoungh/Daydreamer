import random

class BoxManager:
    """负责箱子金额分配、开箱、金额面板管理"""

    BASE_AMOUNTS = [
        0.1, 1, 5, 10, 25, 50, 75, 100, 200, 300, 400, 500, 750, 1000,
        5000, 10000, 25000, 50000, 75000, 100000, 200000, 300000, 400000,
        500000, 750000, 1000000
    ]

    def __init__(self, mode='normal'):
        self.mode = mode
        self.amounts = self._generate_amounts()  # 完整的金额配置列表（用于展示）
        self.amount_pool = self.amounts.copy()   # 当前未打开金额的多重集合
        self.boxes = {}          # 箱子编号 -> 金额
        self.dreamer_box = None  # 梦想家选中的箱子编号
        self.opened_boxes = set()
        self._assign_boxes()

    def _generate_amounts(self):
        amounts = self.BASE_AMOUNTS.copy()
        if self.mode == 'tycoon':   # 大富翁：后9个全部替换为1000000
            amounts[17:] = [1000000] * 9
        elif self.mode == 'depression':  # 大萧条：前9个全部替换为0.1
            amounts[:9] = [0.1] * 9
        return amounts

    def _assign_boxes(self):
        shuffled = self.amounts.copy()
        random.shuffle(shuffled)
        self.boxes = {i+1: shuffled[i] for i in range(26)}

    def set_dreamer_box(self, box_id):
        """梦想家选定自己的箱子（不打开）"""
        if box_id in self.boxes and box_id not in self.opened_boxes:
            self.dreamer_box = box_id
            return True
        return False

    def open_box(self, box_id):
        """打开指定箱子，返回金额；若不可打开则返回None"""
        if box_id == self.dreamer_box:
            print("你不能打开自己的箱子！")
            return None
        if box_id in self.opened_boxes:
            print("这个箱子已经被打开过了！")
            return None
        if box_id not in self.boxes:
            print("无效的箱子编号。")
            return None
        amount = self.boxes[box_id]
        self.opened_boxes.add(box_id)
        # 从金额池中移除该金额（只移除一个实例）
        self.amount_pool.remove(amount)
        return amount

    def reveal_dreamer_box(self):
        """打开梦想家的箱子，返回金额"""
        if self.dreamer_box is None:
            return None
        amount = self.boxes[self.dreamer_box]
        self.opened_boxes.add(self.dreamer_box)
        # 此时也从金额池移除（游戏结束，但保持一致性）
        if amount in self.amount_pool:
            self.amount_pool.remove(amount)
        return amount

    def get_remaining_amounts(self):
        """返回当前金额面板（未打开的所有金额，含梦想家箱子）"""
        return self.amount_pool.copy()

    def get_remaining_boxes(self):
        """返回所有未打开箱子的编号列表（含梦想家箱子）"""
        return [b for b in self.boxes if b not in self.opened_boxes]

    def get_openable_boxes(self):
        """返回可被打开的箱子编号（不含梦想家箱子）"""
        return [b for b in self.get_remaining_boxes() if b != self.dreamer_box]

    def get_all_boxes_info(self):
        """返回所有箱子（编号，金额，是否打开）的列表，用于最终展示"""
        info = []
        for box_id in range(1, 27):
            status = "已打开" if box_id in self.opened_boxes else "未打开"
            if box_id == self.dreamer_box:
                status += " (你的箱子)"
            info.append((box_id, self.boxes[box_id], status))
        return info