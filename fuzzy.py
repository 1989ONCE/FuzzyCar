import numpy as np
import matplotlib.pyplot as plt
COUNT = 0
# 定義歸屬度函數
def front_near(x):
    if x <= 6:      
        return 1.0
    elif 6 < x <= 9:
        return (9 - x) / 3
    else:
        return 0.0

def front_middle(x):
    if 6 < x <= 9:
        return (x - 6) / 3
    elif 9 < x <= 12:
        return (12 - x) / 3
    else:
        return 0.0

def front_far(x):
    if x <= 9:
        return 0.0
    elif 9 < x <= 12:
        return (x - 9) / 3
    else:
        return 1.0

def diff_small(x):
    if x <= -17:
        return 1.0
    elif -17 < x <= 0:
        return (0 - x) / 17
    else:
        return 0.0

def diff_middle(x):
    if -2 < x <= 0:
        return (x + 2) / 2
    elif 0 < x <= 2:
        return (2 - x) / 2
    else:
        return 0.0

def diff_large(x):
    if x <= 0:
        return 0.0
    elif 0 < x <= 17:
        return (x - 0) / 17
    else:
        return 1.0

# 定義模糊規則
def compute_rule_strengths(μ_front_near, μ_front_middle, μ_front_far, μ_diff_small, μ_diff_middle, μ_diff_large):
    strengths = []

    # R1: 前方近 且 差距小 → 向右大轉 (30°)
    # R2: 前方近 且 差距中 → 不轉 (0°)
    # R3: 前方近 且 差距大 → 向左大轉 (-30°)
    strengths.append((min(μ_front_near, μ_diff_small), 30))
    strengths.append((min(μ_front_near, μ_diff_middle), 0))
    strengths.append((min(μ_front_near, μ_diff_large), -30))


    # R4: 前方中 且 差距小 → 向右小轉 (20°)
    # R5: 前方中 且 差距中 → 不轉 (0°)
    # R6: 前方中 且 差距大 → 向左小轉 (-20°)
    strengths.append((min(μ_front_middle, μ_diff_small), 20))
    strengths.append((min(μ_front_middle, μ_diff_middle), 0))
    strengths.append((min(μ_front_middle, μ_diff_large), -20))


    # R7: 前方遠 且 差距小 → 向右微轉 (15°)
    # R8: 前方遠 且 差距中 → 不轉 (0°)
    # R9: 前方遠 且 差距大 → 向左微轉 (-15°)
    strengths.append((min(μ_front_far, μ_diff_small), 15))
    strengths.append((min(μ_front_far, μ_diff_middle), 0))
    strengths.append((min(μ_front_far, μ_diff_large), -15))

    return strengths

# 去模糊化：中心平均法
def defuzzify(strengths):
    # Calculate the weighted sum of（strength * angles）
    weighted_sum = sum(strength * angle for strength, angle in strengths)
    
    # Calculate the sum of the strength
    total_weight = sum(strength for strength, _ in strengths)
    
    # Avoid division by zero and return the defuzzified value
    if total_weight == 0:
        return 0
    return weighted_sum / total_weight

# 實作 fuzzy_steering 函數
def fuzzy_steering(front, left, right):
    diff = left - right

    # 模糊化
    μ_front_near = front_near(front)
    μ_front_middle = front_middle(front)
    μ_front_far = front_far(front)

    μ_diff_small = diff_small(diff)
    μ_diff_middle = diff_middle(diff)
    μ_diff_large = diff_large(diff)
    global COUNT
    COUNT += 1
    
    # 模糊規則
    strengths = compute_rule_strengths(μ_front_near, μ_front_middle, μ_front_far, μ_diff_small, μ_diff_middle, μ_diff_large)
    print(f"COUNT: {COUNT}, strengths: {strengths}")
    # 去模糊化
    return defuzzify(strengths)
    
# For Testing
def simple_control(left, right):
    diff = right - left

    if abs(diff) < 2:
        # 感測器差異很小，保持直行
        return 0
    elif diff > 0:
        # 右邊比較遠，右轉
        if diff > 17:
            return 20
        else:
            return 10
    else:
        # 左邊比較遠，左轉
        if diff < -17:
            return -20
        else:
            return -10

def draw_mfGraph():
    # Create a new figure for the fuzzy membership functions
    figure = plt.Figure(figsize=(15, 12), dpi=100)
    
    # Create subplots
    ax1 = figure.add_subplot(211)  # First subplot
    ax2 = figure.add_subplot(212)  # Second subplot

    # Adjust spacing between subplots
    figure.subplots_adjust(hspace=0.5)

    # Plot front sensor membership functions (from draw_front_mf)
    x_front = np.linspace(0, 20, 500)
    y_near = [front_near(x) for x in x_front]
    y_middle = [front_middle(x) for x in x_front]
    y_far = [front_far(x) for x in x_front]
    ax1.plot(x_front, y_near, label="Near", color="red")
    ax1.plot(x_front, y_middle, label="Middle", color="blue")
    ax1.plot(x_front, y_far, label="Far", color="green")
    ax1.set_title("Front Sensor Membership Functions")
    ax1.set_xlabel("Front Distance")
    ax1.set_ylabel("Membership Degree")
    ax1.legend()
    ax1.grid(True)

    # Plot left-right difference membership functions (from draw_diff_mf)
    x_diff = np.linspace(-20, 20, 500)
    y_small = [diff_small(x) for x in x_diff]
    y_mid = [diff_middle(x) for x in x_diff]
    y_large = [diff_large(x) for x in x_diff]
    ax2.plot(x_diff, y_small, label="Small", color="red")
    ax2.plot(x_diff, y_mid, label="Middle", color="blue")
    ax2.plot(x_diff, y_large, label="Large", color="green")
    ax2.set_title("Left-Right Difference Membership Functions")
    ax2.set_xlabel("Difference (x)")
    ax2.set_ylabel("Membership Degree")
    ax2.legend()
    ax2.grid(True)

    return figure