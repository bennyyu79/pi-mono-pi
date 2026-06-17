#!/usr/bin/env python3
"""
Skill Step 1: 请求 API 获取原始 JSON 数据，并保存到本地 raw.json

API 说明:
  使用 Fake Store API (https://fakestoreapi.com) 获取电商商品数据。
  这是一个免费、公开的 RESTful API，返回标准 JSON 格式的商品列表。

输出:
  ./raw.json  — 保存从 API 获取的原始 JSON 数据
"""

import json
import sys
import os
import urllib.request
import urllib.error

# ─── 全局配置 ─────────────────────────────────────────────────
API_URL = "https://fakestoreapi.com/products"
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw.json")


def fetch_json(url: str, timeout: int = 15) -> list | dict:
    """
    发送 HTTP GET 请求并返回解析后的 JSON 对象。
    若请求失败或返回非 200 状态码，抛出 RuntimeError。
    """
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status != 200:
                raise RuntimeError(
                    f"API 返回非 200 状态码: {response.status}"
                )
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP 请求失败: {e.code} {e.reason}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"网络错误（无法连接到服务器）: {e.reason}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"JSON 解析失败: {e}")
    return data


def save_json(data: list | dict, filepath: str) -> str:
    """将 Python 对象以格式化 JSON 写入文件，返回绝对路径。"""
    abs_path = os.path.abspath(filepath)
    with open(abs_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 数据已保存到: {abs_path}")
    return abs_path


def main():
    """主流程：获取 -> 保存"""
    print(f"🌐 正在请求 API: {API_URL}")
    products = fetch_json(API_URL)
    print(f"   ✓ 成功获取 {len(products)} 条商品记录")

    save_json(products, OUTPUT_FILE)
    print(f"   ✓ 原始数据已保存至 {OUTPUT_FILE}")


# ─── 主入口 ───────────────────────────────────────────────────
if __name__ == "__main__":
    main()

# ═══════════════════════════════════════════════════════════════
# 自动化测试断言
# ═══════════════════════════════════════════════════════════════

# 1. 确保输出文件尚不存在（先清理）
if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)

# 2. 执行主流程
main()

# 3. 断言：文件已创建
assert os.path.exists(OUTPUT_FILE), f"断言失败: {OUTPUT_FILE} 未生成"
print("✓ 断言 1: raw.json 文件已生成")

# 4. 断言：文件内容为有效 JSON 且为列表
with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)
assert isinstance(data, list), "断言失败: JSON 根元素不是列表"
assert len(data) > 0, "断言失败: 商品列表为空"
print(f"✓ 断言 2: 文件含 {len(data)} 条有效记录")

# 5. 断言：每条商品包含 e-commerce 标准字段
required_fields = {"id", "title", "price", "category", "image"}
for i, product in enumerate(data):
    missing = required_fields - set(product.keys())
    assert not missing, f"断言失败: 第 {i} 条商品缺少字段: {missing}"
print(f"✓ 断言 3: 所有商品均包含标准字段 {required_fields}")

# 6. 断言：价格字段为数值类型
for i, product in enumerate(data):
    assert isinstance(product.get("price"), (int, float)), \
        f"断言失败: 第 {i} 条商品 price 不是数值: {product.get('price')}"
print(f"✓ 断言 4: 所有商品价格字段均为数值类型")

print("\n🎉 所有断言通过！脚本运行完全成功。")
