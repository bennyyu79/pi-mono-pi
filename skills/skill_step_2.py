#!/usr/bin/env python3
"""
Skill Step 2: 读取本地 raw.json，清洗空值，提取价格字段，计算平均值

依赖:
  agent_workspace/raw.json  — 由 skill_step_1.py 生成的原始数据

输出:
  打印清洗结果和平均价格到控制台
"""

import json
import os
import sys

# ─── 路径配置 ─────────────────────────────────────────────────
RAW_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw.json")


def load_data(filepath: str) -> list:
    """加载本地 JSON 文件，返回列表。"""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def clean_nulls(products: list) -> list:
    """
    清洗记录：
      1. 移除 products 中所有显式为 None 的记录。
      2. 移除 price 字段缺失或为 None 的记录。
      3. 移除 price 字段不是数值类型（int/float）的记录。
      4. 移除 price <= 0 的记录（业务异常值清洗）。
    返回清洗后的列表。
    """
    original_count = len(products)
    cleaned = []

    for i, item in enumerate(products):
        # 检查记录本身是否 None
        if item is None:
            continue

        # 确保 item 是 dict
        if not isinstance(item, dict):
            continue

        # 检查 price 字段是否存在
        if "price" not in item or item["price"] is None:
            continue

        price = item["price"]

        # 检查 price 是否为数值类型
        if not isinstance(price, (int, float)):
            continue

        # 检查 price 是否为正数
        if price <= 0:
            continue

        cleaned.append(item)

    removed = original_count - len(cleaned)
    if removed > 0:
        print(f"   🧹 清洗: 移除了 {removed} 条无效记录")
    else:
        print(f"   🧹 清洗: 未发现无效记录，数据质量良好")

    return cleaned


def extract_prices(products: list) -> list:
    """从商品列表中提取所有 price 字段，返回纯数值列表。"""
    return [item["price"] for item in products]


def compute_average(prices: list) -> float:
    """计算价格列表的平均值，返回保留两位小数的浮点数。"""
    avg = sum(prices) / len(prices)
    return round(avg, 2)


def main():
    """主流程：加载 -> 清洗 -> 提取 -> 计算 -> 输出"""
    print("📂 Step 2: 读取并清洗数据")

    # 1. 加载数据
    print(f"   📖 正在读取: {RAW_JSON}")
    products = load_data(RAW_JSON)
    print(f"   ✓ 读取到 {len(products)} 条原始记录")

    # 2. 清洗空值
    products = clean_nulls(products)
    print(f"   ✓ 清洗后剩余 {len(products)} 条有效记录")

    # 3. 提取价格
    prices = extract_prices(products)
    print(f"   ✓ 提取到 {len(prices)} 个价格数据")

    # 4. 计算平均值
    average = compute_average(prices)
    print(f"   📊 =============================================")
    print(f"   📊 价格均值: ${average}")
    print(f"   📊 价格范围: ${min(prices):.2f} ~ ${max(prices):.2f}")
    print(f"   📊 价格中位数: ${sorted(prices)[len(prices) // 2]:.2f}")
    print(f"   📊 =============================================")

    return prices, average


# ═══════════════════════════════════════════════════════════════
# 自动化测试断言
# ═══════════════════════════════════════════════════════════════

# 1. 执行主流程
prices, avg = main()

# 2. 断言：至少有一条有效记录
assert len(prices) > 0, "断言失败: 有效价格记录数为 0"
print("✓ 断言 1: 存在有效价格记录")

# 3. 断言：所有价格均为正数
assert all(p > 0 for p in prices), "断言失败: 存在非正价格"
print(f"✓ 断言 2: 所有 {len(prices)} 个价格均为正数")

# 4. 断言：平均值合理（FakeStore API 数据价格通常在 0 ~ 1000 之间）
assert 0 < avg < 1000, f"断言失败: 平均价格 ${avg} 超出合理范围"
print(f"✓ 断言 3: 平均价格 ${avg} 在合理范围内 (0 < avg < 1000)")

# 5. 断言：平均值低于最高价、高于最低价
assert min(prices) <= avg <= max(prices), \
    f"断言失败: 平均值 ${avg} 不在价格范围 [${min(prices)}, ${max(prices)}] 内"
print(f"✓ 断言 4: 平均值 ${avg} 在价格范围 [${min(prices):.2f}, ${max(prices):.2f}] 内")

# 6. 断言：所有价格都已从输入清洗，无 None/NaN
assert all(isinstance(p, (int, float)) for p in prices), "断言失败: 存在非数值价格"
print(f"✓ 断言 5: 所有价格均为数值类型")

print("\n🎉 所有断言通过！步骤 2 运行完全成功。")
