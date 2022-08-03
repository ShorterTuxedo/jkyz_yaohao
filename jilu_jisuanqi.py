import math

print("="*20+"健康驿站房间线上预约系统抽签抽中机率计算器"+"="*20)

log = lambda a, b: math.log(b) / math.log(a)

mode = None

while mode == None:
    try:
        mode = input("请输入计算模式 （0 为 机率 -> 等待时间，1 为 等待时间 -> 机率）：")
        if mode != "0" and mode != "1":
            print("计算模式无效。")
            mode = None
    except Exception:
        print("计算模式无效。")
        mode = None


if mode == "0":
    my_chance_get = None
    while my_chance_get == None:
        try:
            my_chance_get = float(input("请输入您可接受的的抽签机率："))
            if my_chance_get <= 0 or my_chance_get >= 100:
                if my_chance_get >= 100:
                    print("无法保证中签。")
                if my_chance_get <= 0:
                    print("数值无效。")
                my_chance_get = None
        except Exception:
            print("数值无效。")
            my_chance_get = None

    my_minge = None
    while my_minge == None:
        try:
            my_minge = int(input("请输入平均名额："))
            if my_minge < 0:
                print("数值无效。")
        except Exception:
            print("数值无效。")
            my_minge = None

    my_renshu = None
    while my_renshu == None:
        try:
            my_renshu = int(input("请输入平均报名人数："))
            if my_renshu < 0:
                print("数值无效。")
        except Exception:
            print("数值无效。")
            my_renshu = None

    my_chance = my_minge / my_renshu # 抽中机率

    if my_chance > 1: # 处理名额多于人数情况
        my_chance = 1

    my_chance = 1 - my_chance # 未抽中机率

    my_days_take = math.ceil(log(my_chance, (1 - (my_chance_get / 100)))) # 由用户所欲的抽中机率计算所需日数

    print(f"如果您欲 {my_chance_get} % 抽中机率，并且每日有平均 {my_minge} 名额与 {my_renshu} 人数，您估计需要等待 {my_days_take} 日。")
elif mode == "1":
    my_waitdays = None
    while my_waitdays == None:
        try:
            my_waitdays = int(input("请输入您可接受的等待天数："))
            if my_waitdays < 1:
                print("天数不可小于 1。")
                my_waitdays = None
        except Exception:
            print("天数无效。")
    
    my_minge = None
    while my_minge == None:
        try:
            my_minge = int(input("请输入平均名额："))
            if my_minge < 0:
                print("数值无效。")
        except Exception:
            print("数值无效。")
            my_minge = None

    my_renshu = None
    while my_renshu == None:
        try:
            my_renshu = int(input("请输入平均报名人数："))
            if my_renshu < 0:
                print("数值无效。")
        except Exception:
            print("数值无效。")
            my_renshu = None

    my_chance = my_minge / my_renshu # 抽中机率

    if my_chance > 1: # 处理名额多于人数情况
        my_chance = 1

    my_chance = 1 - my_chance # 未抽中机率

    my_chancefordays = 1 - (my_chance ** my_waitdays) # 1 减去连续 N 日未抽中机率，这是 连续 N 日抽中至少 1 次的概率。

    my_chancefordays *= 100

    print(f"如果您欲等待 {my_waitdays} 日，并且每日有平均 {my_minge} 名额与 {my_renshu} 人数，您的概率为 {my_chancefordays} %。")
else:
    print("这是非法状态。")