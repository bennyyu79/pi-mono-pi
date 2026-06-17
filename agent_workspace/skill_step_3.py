#!/usr/bin/env python3
"""
Skill Step 3: 读取原始价格数据，使用 matplotlib 绘制趋势图并保存为 chart.png

依赖:
  ./agent_workspace/raw.json  — 由 skill_step_1.py 生成的原始商品数据

前置步骤（由技能库中的技能完成）:
  - skill_step_1: 请求 API 获取原始 JSON 数据，保存到 raw.json
  - skill_step_2: 读取 raw.json，清洗空值，提取价格字段，计算平均值

输出:
  chart.png  — 价格可视化趋势图（含柱状图 + 平均线 + 类别分析）
  stddev (控制台) — 标准差等统计信息
"""

import json
import os
import sys

# ─── 确保 matplotlib 使用非交互式后端（终端/CI 环境兼容） ───
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ─── 路径配置 ─────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)  # test36_pi 目录
RAW_JSON = os.path.join(PROJECT_ROOT, "agent_workspace", "raw.json")
CHART_OUTPUT = os.path.join(PROJECT_ROOT, "agent_workspace", "chart.png")


def load_data(filepath: str) -> list:
    """加载本地 JSON 文件，返回商品列表。"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def clean_and_extract(products: list) -> tuple[list, list, int]:
    """
    清洗数据并提取价格。
    返回 (product_names, prices, valid_count)
    """
    cleaned = []
    for item in products:
        if not isinstance(item, dict):
            continue
        if "price" not in item or item["price"] is None:
            continue
        price = item["price"]
        if not isinstance(price, (int, float)) or price <= 0:
            continue
        cleaned.append(item)

    names = []
    prices = []
    for item in cleaned:
        title = item.get("title", "Unknown")
        # 取前 25 个字符作为标签，保持图表整洁
        short = title[:25] + "..." if len(title) > 25 else title
        names.append(short)
        prices.append(item["price"])

    return names, prices, len(cleaned)


def compute_stats(prices: list) -> dict:
    """计算基本统计量。"""
    n = len(prices)
    avg = sum(prices) / n
    var = sum((p - avg) ** 2 for p in prices) / n
    std = var ** 0.5
    mid = n // 2
    sorted_p = sorted(prices)
    median = sorted_p[mid] if n % 2 == 1 else (sorted_p[mid - 1] + sorted_p[mid]) / 2
    return {
        "avg": round(avg, 2),
        "median": round(median, 2),
        "std": round(std, 2),
        "min": min(prices),
        "max": max(prices),
        "count": n,
    }


def get_category_averages(products: list) -> dict:
    """按类别计算平均价格。"""
    categories = {}
    for item in products:
        if not isinstance(item, dict):
            continue
        cat = item.get("category", "unknown")
        price = item.get("price")
        if not isinstance(price, (int, float)) or price <= 0:
            continue
        categories.setdefault(cat, []).append(price)
    return {cat: round(sum(vals) / len(vals), 2) for cat, vals in categories.items()}


def plot_price_chart(prices: list, names: list, stats: dict, cat_avgs: dict):
    """
    绘制双面板图表:
      - 左图: 各商品价格柱状图 + 平均线 + 标准差区间
      - 右图: 类别平均价格柱状图
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # ═══════════════════════════════════════════════════════
    # 左图：各商品价格柱状图
    # ═══════════════════════════════════════════════════════
    x = range(len(prices))
    colors = plt.cm.viridis([i / len(prices) for i in range(len(prices))])
    bars = ax1.bar(x, prices, color=colors, edgecolor="white", linewidth=0.5, alpha=0.85)

    # 平均线
    avg = stats["avg"]
    ax1.axhline(y=avg, color="red", linestyle="--", linewidth=1.5, label=f"Mean ${avg}")

    # 标准差区间带
    std = stats["std"]
    ax1.axhspan(avg - std, avg + std, alpha=0.08, color="red", label=f"±1σ (±${std})")

    # 最高/最低价标注
    max_price = stats["max"]
    min_price = stats["min"]
    ax1.annotate(f"Max ${max_price}", xy=(prices.index(max_price), max_price),
                 xytext=(5, 10), textcoords="offset points", fontsize=8, color="darkred")
    ax1.annotate(f"Min ${min_price}", xy=(prices.index(min_price), min_price),
                 xytext=(5, -12), textcoords="offset points", fontsize=8, color="darkgreen")

    ax1.set_xlabel("Product", fontsize=11)
    ax1.set_ylabel("Price (USD)", fontsize=11)
    ax1.set_title("Price Distribution by Product", fontsize=13, fontweight="bold")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(names, rotation=45, ha="right", fontsize=7)
    ax1.legend(loc="upper left", fontsize=9)
    ax1.grid(axis="y", alpha=0.3)
    ax1.yaxis.set_major_formatter(mticker.FormatStrFormatter("$%.2f"))

    # 在柱顶显示数值（仅显示头尾 + 最大最小，避免拥挤）
    sorted_by_price = sorted(zip(prices, x), key=lambda v: v[0])
    show_indices = {0, len(prices) - 1, sorted_by_price[0][1], sorted_by_price[-1][1]}
    for i, bar in enumerate(bars):
        if i in show_indices:
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                     f"${prices[i]:.0f}", ha="center", va="bottom", fontsize=6.5)

    # ═══════════════════════════════════════════════════════
    # 右图：类别平均价格
    # ═══════════════════════════════════════════════════════
    categories = list(cat_avgs.keys())
    cat_values = list(cat_avgs.values())
    cat_colors = plt.cm.Set2([i / len(categories) for i in range(len(categories))])
    bars2 = ax2.barh(range(len(categories)), cat_values, color=cat_colors, edgecolor="white", height=0.6)

    # 全局平均线
    ax2.axvline(x=avg, color="red", linestyle="--", linewidth=1.5, label=f"Global Mean ${avg}")

    for i, (bar, val) in enumerate(zip(bars2, cat_values)):
        ax2.text(val + 2, bar.get_y() + bar.get_height() / 2,
                 f"${val:.2f}", va="center", fontsize=9)

    ax2.set_yticks(range(len(categories)))
    ax2.set_yticklabels([c.replace("'", "") for c in categories], fontsize=10)
    ax2.set_xlabel("Avg Price (USD)", fontsize=11)
    ax2.set_title("Average Price by Category", fontsize=13, fontweight="bold")
    ax2.legend(loc="lower right", fontsize=9)
    ax2.grid(axis="x", alpha=0.3)
    ax2.xaxis.set_major_formatter(mticker.FormatStrFormatter("$%.2f"))

    # ═══════════════════════════════════════════════════════
    # 添加全局统计信息水印
    # ═══════════════════════════════════════════════════════
    stats_text = (
        f"Total: {stats['count']} products  |  Mean: ${stats['avg']}  |  "
        f"Median: ${stats['median']}  |  StdDev: ${stats['std']}  |  "
        f"Min: ${stats['min']}  |  Max: ${stats['max']}"
    )
    fig.text(
        0.5, 0.01, stats_text,
        ha="center", fontsize=10, style="italic", color="gray"
    )

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(CHART_OUTPUT, dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"📊 Chart saved: {CHART_OUTPUT}")


def main():
    """主流程：加载 → 清洗 → 统计 → 可视化"""
    print("📊 Step 3: Price Visualization")

    # 1. 加载数据
    if not os.path.exists(RAW_JSON):
        print(f"   ERROR: Data file not found: {RAW_JSON}")
        print(f"   HINT: Run skill_step_1.py first to generate raw.json.")
        sys.exit(1)

    print(f"   Reading: {RAW_JSON}")
    products = load_data(RAW_JSON)
    print(f"   Loaded {len(products)} raw records")

    # 2. 清洗并提取价格
    names, prices, valid_count = clean_and_extract(products)
    print(f"   Cleaned: {valid_count} valid records, {len(prices)} prices extracted")

    # 3. 计算统计量
    stats = compute_stats(prices)
    print(f"   Stats: mean=${stats['avg']}, median=${stats['median']}, "
          f"std=${stats['std']}, range=${stats['min']}~${stats['max']}")

    # 4. 按类别计算平均价格
    cat_avgs = get_category_averages(products)
    print(f"   Categories: {', '.join(f'{k}: ${v}' for k, v in cat_avgs.items())}")

    # 5. 绘制并保存图表
    plot_price_chart(prices, names, stats, cat_avgs)

    print(f"\n   Visualization complete. Chart saved to: {CHART_OUTPUT}")


# ═══════════════════════════════════════════════════════════════
# 自动化测试断言
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # 如果存在旧图表则清理
    if os.path.exists(CHART_OUTPUT):
        os.remove(CHART_OUTPUT)

    # 执行主流程
    main()

    # Assert 1: chart file generated
    assert os.path.exists(CHART_OUTPUT), f"Assert failed: {CHART_OUTPUT} not generated"
    chart_size = os.path.getsize(CHART_OUTPUT)
    print(f"✓ Assert 1: chart.png generated ({chart_size} bytes)")

    # Assert 2: valid PNG
    with open(CHART_OUTPUT, "rb") as f:
        header = f.read(8)
    assert header[:4] == b'\x89PNG', f"Assert failed: Not a valid PNG: {header[:4]}"
    print(f"✓ Assert 2: chart.png is a valid PNG file")

    # Assert 3: file size >= 10KB
    assert chart_size >= 10240, f"Assert failed: chart too small ({chart_size} bytes)"
    print(f"✓ Assert 3: chart file size reasonable (>= 10KB)")

    # Assert 4: data validation -- non-empty positive prices
    products_data = load_data(RAW_JSON)
    _, prices, _ = clean_and_extract(products_data)
    assert len(prices) > 0, "Assert failed: no valid price data"
    assert all(p > 0 for p in prices), "Assert failed: non-positive price found"
    print(f"✓ Assert 4: {len(prices)} valid prices, all positive")

    # Assert 5: stat consistency
    stats = compute_stats(prices)
    assert stats["min"] <= stats["avg"] <= stats["max"], \
        f"Assert failed: mean ${stats['avg']} not in [${stats['min']}, ${stats['max']}]"
    assert stats["std"] >= 0, "Assert failed: stddev should be non-negative"
    print(f"✓ Assert 5: stats self-consistent (mean=${stats['avg']}, std=${stats['std']})")

    print(f"\n🎉 All assertions passed! Step 3 completed successfully.")
