import random
from capitalist import Capitalist
from box_manager import BoxManager
from dreamer import Dreamer

def get_round_opens(round_number):
    if round_number <= 5:
        return 7 - round_number
    else:
        return 1

def select_mode():
    print("请选择游戏模式：")
    print("1. 标准模式")
    print("2. 大富翁模式")
    print("3. 大萧条模式")
    while True:
        choice = input("输入数字(1/2/3)：").strip()
        if choice == '1':
            return 'normal'
        elif choice == '2':
            return 'tycoon'
        elif choice == '3':
            return 'depression'
        print("无效选择，请重新输入。")

def play_game():
    mode = select_mode()
    box_manager = BoxManager(mode)
    capitalist = Capitalist()
    dreamer = Dreamer()

    print("\n26个箱子已就绪，编号1-26。")
    while True:
        try:
            choice = int(input("请选择一个箱子作为你的箱子（输入编号1-26）："))
            if box_manager.set_dreamer_box(choice):
                break
            print("无效编号，请重试。")
        except ValueError:
            print("请输入数字。")
    print(f"你选择了 {choice} 号箱子，里面的金额未知。\n")

    round_num = 1
    game_over = False

    while not game_over:
        opens_needed = get_round_opens(round_num)
        openable_boxes = box_manager.get_openable_boxes()

        if opens_needed > len(openable_boxes):
            opens_needed = len(openable_boxes)

        if opens_needed == 0:
            prize = box_manager.reveal_dreamer_box()
            print(f"\n所有箱子已开完！你的箱子 {box_manager.dreamer_box} 号中有 {prize} 元。")
            dreamer.final_prize = prize
            break

        print(f"--- 第 {round_num} 轮：你需要打开 {opens_needed} 个箱子 ---")
        for i in range(opens_needed):
            print(f"可打开的箱子编号：{openable_boxes}")
            while True:
                try:
                    box_id = int(input(f"请选择第 {i+1}/{opens_needed} 个要打开的箱子编号："))
                    if box_id not in openable_boxes:
                        print("编号错误或该箱子已被打开，请重新选择。")
                        continue
                    amount = box_manager.open_box(box_id)
                    if amount is not None:
                        print(f"箱子 {box_id} 打开了，金额为 {amount} 元。")
                        openable_boxes.remove(box_id)
                        break
                except ValueError:
                    print("请输入有效数字。")

        remaining_amounts = box_manager.get_remaining_amounts()
        print(f"\n当前金额面板剩余金额：{sorted(remaining_amounts)}")

        offer = capitalist.make_offer(remaining_amounts)
        action, price = dreamer.choose_action(offer, capitalist, remaining_amounts)

        if action == 'deal':
            dreamer.final_prize = price
            print(f"你以 {price} 元成交！")
            game_over = True
        else:
            print("你选择继续开箱。\n")
            round_num += 1

        if len(box_manager.get_openable_boxes()) == 0:
            prize = box_manager.reveal_dreamer_box()
            print(f"\n其他箱子全部打开！你的箱子 {box_manager.dreamer_box} 号中有 {prize} 元。")
            dreamer.final_prize = prize
            game_over = True

    # 游戏结束，计算得分
    prize = dreamer.final_prize
    actual = box_manager.boxes[box_manager.dreamer_box]
    profit = prize - actual  # 交易盈亏

    score1 = Dreamer.calculate_score_stage1(prize)
    score2 = Dreamer.calculate_score_stage2(profit)
    total_score = score1 + score2

    print(f"\n===== 游戏结束 =====")
    print(f"你的箱子实际金额：{actual} 元")
    print(f"最终获得奖金：{prize} 元")
    if profit >= 0:
        print(f"本次交易梦想家多赚：{profit} 元")
    else:
        print(f"本次交易梦想家少赚（资本家赚）：{-profit} 元")

    print(f"\n--- 积分明细 ---")
    print(f"第一段积分（奖金金额）：{score1} / 500")
    print(f"第二段积分（交易盈亏）：{score2} / 500")
    print(f"总积分：{total_score} / 1000")

    view = input("\n是否查看所有箱子的金额？(yes/no)：").strip().lower()
    if view == 'yes':
        print("\n所有箱子详情：")
        for box_id, amount, status in box_manager.get_all_boxes_info():
            print(f"箱子 {box_id:2d}: {amount:>10} 元  [{status}]")

if __name__ == "__main__":
    play_game()



    #  spin_chars = ["🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚", "🕛"]
    #         idx = 0
    #
    #         def update_spin():
    #             nonlocal idx
    #             spin_label.config(text=spin_chars[idx % 12])