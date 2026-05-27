"""
提示词工程三代迭代测试脚本
用同一张图片的分析数据，分别用V1.0/V2.0/V3.0三种提示词生成评语
"""
import requests
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen2:1.5b"

# 先用CV模块分析一张示例图片，获取真实数据
from composition_analyzer import CompositionAnalyzer

# 使用已下载的示例图片
sample_dir = os.path.join(os.path.dirname(__file__), "data", "samples")
test_image = None
if os.path.exists(sample_dir):
    for f in os.listdir(sample_dir):
        if f.endswith(('.jpg', '.jpeg', '.png')):
            test_image = os.path.join(sample_dir, f)
            break

if not test_image:
    print("没有找到示例图片，请先在应用中点击'示例图片'下载一张")
    sys.exit(1)

print(f"测试图片: {os.path.basename(test_image)}")
print("正在进行CV分析...")

analyzer = CompositionAnalyzer()
result = analyzer.analyze(test_image, ["rule_of_thirds", "symmetry"])
analyses = result.get("analyses", {})
size = result.get("image_size", {})

rot = analyses.get("rule_of_thirds", {})
sym = analyses.get("symmetry", {})
vf = analyses.get("visual_features", {})

print(f"三分法得分: {rot.get('score')}, 对称性得分: {sym.get('overall_score')}")
print("=" * 60)


def call_ollama(system_prompt, user_prompt):
    """调用Ollama生成评语"""
    try:
        resp = requests.post(f"{OLLAMA_URL}/api/chat", json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {"temperature": 0.7, "top_p": 0.9, "num_predict": 512}
        }, timeout=120)
        if resp.status_code == 200:
            return resp.json()["message"]["content"]
        return f"[错误] {resp.status_code}"
    except Exception as e:
        return f"[错误] {e}"


# ============================================================
# V1.0 - 简单指令，无数据注入
# ============================================================
v1_system = "你是一个摄影评价助手。"
v1_user = "请评价这张照片的构图。"

print("\n" + "=" * 60)
print("V1.0 提示词测试")
print("=" * 60)
print(f"系统提示词: {v1_system}")
print(f"用户提示词: {v1_user}")
print("-" * 40)
print("正在生成...")
v1_result = call_ollama(v1_system, v1_user)
print(f"模型输出:\n{v1_result}")


# ============================================================
# V2.0 - 加入分析维度，但数据简略
# ============================================================
v2_system = "你是一个摄影构图分析助手，请分析照片构图的优点和不足。"
v2_user = f"分析主体位置、三分法符合度，给出优点和不足。三分法得分{rot.get('score')}分，对称性得分{sym.get('overall_score')}分。"

print("\n" + "=" * 60)
print("V2.0 提示词测试")
print("=" * 60)
print(f"系统提示词: {v2_system}")
print(f"用户提示词: {v2_user}")
print("-" * 40)
print("正在生成...")
v2_result = call_ollama(v2_system, v2_user)
print(f"模型输出:\n{v2_result}")


# ============================================================
# V3.0 - 完整角色+CV数据注入+格式要求（当前版本）
# ============================================================
v3_system = """你是一位经验丰富的摄影构图分析导师。你的工作方式如下：

【你的数据来源】
计算机视觉模块已经对照片进行了精确的像素级测量。这些数据将在用户消息中提供给你。

【严格规则】
1. 你无法看到图片，所有分析必须且只能基于提供的计算机视觉测量数据
2. 禁止描述图片具体内容，因为你看不到图片
3. 禁止编造数据中没有的信息
4. 每一句评价都必须能在数据中找到对应的数值支撑

【输出风格】
用自然流畅的段落形式输出，像一位导师在面对面指导学生。不要使用【】标题分段。
先肯定优点并引用数据，再指出不足并引用数据，最后给出具体可操作的改进建议。"""

brightness = vf.get("brightness", {})
lines_data = vf.get("lines", {})
vc = vf.get("visual_center", {})
comp = vf.get("complexity", {})
color = vf.get("color", {})

v3_user = f"""以下是计算机视觉模块对一张照片的精确量化分析结果。请严格基于这些客观测量数据生成构图评语。

图像尺寸: {size.get('width')} x {size.get('height')} 像素

═══ 三分法构图分析 ═══
  综合得分: {rot.get('score')}/100
  检测到兴趣点: {len(rot.get('interest_points', []))} 个
  兴趣点到三分线交点平均归一化距离: {rot.get('avg_normalized_distance')}
  系统判断: {rot.get('description', '')}

═══ 对称性构图分析 ═══
  水平对称得分: {sym.get('horizontal_symmetry', {}).get('score')}/100
  垂直对称得分: {sym.get('vertical_symmetry', {}).get('score')}/100
  综合对称得分: {sym.get('overall_score')}/100
  最佳对称轴: {'水平' if sym.get('best_axis') == 'horizontal' else '垂直'}

═══ 额外视觉特征 ═══
  亮度均值: {brightness.get('overall_mean')}/255 ({brightness.get('exposure_judgment')})
  对比度: {brightness.get('contrast_level')} (标准差{brightness.get('overall_std')})
  线条总数: {lines_data.get('total_detected')} 条 (水平{lines_data.get('horizontal_count')}/垂直{lines_data.get('vertical_count')}/斜线{lines_data.get('diagonal_count')})
  主导线条方向: {lines_data.get('dominant_direction')}
  视觉重心: {vc.get('description', '')}
  边缘密度: {comp.get('edge_density_percent')}% ({comp.get('level')})
  主色调: {color.get('dominant_tone')} ({color.get('saturation_level')})

请用自然段落形式输出评语，引用具体数据，给出可操作的改进建议。"""

print("\n" + "=" * 60)
print("V3.0 提示词测试")
print("=" * 60)
print(f"系统提示词: (完整角色设定+规则，共{len(v3_system)}字)")
print(f"用户提示词: (完整CV数据注入，共{len(v3_user)}字)")
print("-" * 40)
print("正在生成...")
v3_result = call_ollama(v3_system, v3_user)
print(f"模型输出:\n{v3_result}")


# ============================================================
# 保存结果到文件
# ============================================================
output_path = os.path.join(os.path.dirname(__file__), "提示词迭代测试结果.txt")
with open(output_path, "w", encoding="utf-8") as f:
    f.write("=" * 70 + "\n")
    f.write("    AI摄影导师 - 提示词工程三代迭代测试结果\n")
    f.write("=" * 70 + "\n\n")
    f.write(f"测试图片: {os.path.basename(test_image)}\n")
    f.write(f"图像尺寸: {size.get('width')} x {size.get('height')}\n")
    f.write(f"三分法得分: {rot.get('score')}/100\n")
    f.write(f"对称性得分: {sym.get('overall_score')}/100\n\n")

    f.write("=" * 70 + "\n")
    f.write("V1.0 - 简单指令（无数据注入）\n")
    f.write("=" * 70 + "\n")
    f.write(f"系统提示词: {v1_system}\n")
    f.write(f"用户提示词: {v1_user}\n")
    f.write("-" * 50 + "\n")
    f.write(f"模型输出:\n{v1_result}\n\n")

    f.write("=" * 70 + "\n")
    f.write("V2.0 - 加入分析维度（数据简略）\n")
    f.write("=" * 70 + "\n")
    f.write(f"系统提示词: {v2_system}\n")
    f.write(f"用户提示词: {v2_user}\n")
    f.write("-" * 50 + "\n")
    f.write(f"模型输出:\n{v2_result}\n\n")

    f.write("=" * 70 + "\n")
    f.write("V3.0 - 完整角色+CV数据注入+格式要求（当前版本）\n")
    f.write("=" * 70 + "\n")
    f.write(f"系统提示词: (完整角色设定+规则，共{len(v3_system)}字)\n")
    f.write(f"用户提示词: (完整CV数据注入，共{len(v3_user)}字)\n")
    f.write("-" * 50 + "\n")
    f.write(f"模型输出:\n{v3_result}\n")

print(f"\n\n结果已保存到: {output_path}")
print("完成！")
