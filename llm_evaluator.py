"""
AI摄影导师 - LLM评语生成模块
通过Ollama本地部署的Qwen2模型生成摄影构图评语
"""
import requests
import json


class LLMEvaluator:
    """LLM评语生成器：调用Ollama API，基于构图分析数据生成专业评语"""

    DEFAULT_OLLAMA_URL = "http://localhost:11434"
    DEFAULT_MODEL = "qwen2:1.5b"

    SYSTEM_PROMPTS = {
        "专业": """你是一位经验丰富的摄影构图分析导师。

【数据来源】
计算机视觉模块已对照片进行像素级测量，数据将在用户消息中提供。

【铁律】
1. 所有分析只能基于提供的测量数据，禁止描述图片内容，禁止编造
2. 每句评价必须有数值支撑

【输出格式——必须严格遵守，不可改动】
固定使用以下三段结构，每段必须以序号+加粗标题开头，段内用编号列表展开：

**1. 优点**
(1) ...（引用具体数据，如三分法得分、对称性得分等）
(2) ...
(3) ...

**2. 不足**
(1) ...（引用数据说明问题）
(2) ...

**3. 改进建议**
(1) ...（结合数据给出可操作建议）
(2) ...
(3) ...

字数要求：每段80-120字，总计300-400字。
语气：专业严谨，侧重技术分析，像资深摄影师在做专业点评。""",

        "简洁": """你是一位摄影构图分析导师，请用简洁风格输出评语。

【铁律】
1. 所有分析只能基于提供的测量数据，禁止描述图片内容，禁止编造
2. 每句评价必须有数值支撑

【输出格式——必须严格遵守，不可改动】
固定使用以下三段结构，每段一句话概括+关键数据：

**1. 优点**：一句话总结，括号内注明关键数据。
**2. 不足**：一句话指出核心问题，括号内注明数据。
**3. 改进建议**：2条简短可操作的建议，每条不超过20字。

字数要求：总计100-150字，言简意赅，不做展开分析。
语气：干练直接，重点突出。""",

        "鼓励": """你是一位温暖的摄影导师，请用鼓励风格输出评语。

【铁律】
1. 所有分析只能基于提供的测量数据，禁止描述图片内容，禁止编造
2. 每句评价必须有数值支撑

【输出格式——必须严格遵守，不可改动】
固定使用以下三段结构：

**1. 做得好的地方**
(1) ...（充分肯定，引用数据说明为什么好）
(2) ...
(3) ...

**2. 可以更好的地方**
(1) ...（温和指出，用"如果能...就更棒了"句式）

**3. 小建议**
(1) ...（鼓励性的建议，语气温暖）
(2) ...

字数要求：优点段占60%篇幅（120-150字），不足和建议各占20%（各40-60字），总计200-280字。
语气：温暖友好，先大力肯定再温和建议，像一位耐心导师在面对面指导。"""
    }

    def __init__(self, ollama_url: str = None, model: str = None):
        self.ollama_url = ollama_url or self.DEFAULT_OLLAMA_URL
        self.model = model or self.DEFAULT_MODEL
        self.api_endpoint = f"{self.ollama_url}/api/chat"

    def check_connection(self) -> dict:
        """检查Ollama服务是否可用"""
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                models = [m["name"] for m in resp.json().get("models", [])]
                has_model = any(self.model in m for m in models)
                return {
                    "connected": True,
                    "models": models,
                    "target_model_available": has_model,
                    "message": "Ollama连接正常，Qwen2模型就绪" if has_model else f"Ollama已连接，但未找到模型 {self.model}，请运行: ollama pull qwen2:1.5b"
                }
            return {"connected": False, "target_model_available": False, "message": f"Ollama返回状态码: {resp.status_code}"}
        except requests.ConnectionError:
            return {"connected": False, "target_model_available": False, "message": "无法连接到Ollama服务，请确认Ollama已启动"}
        except Exception as e:
            return {"connected": False, "target_model_available": False, "message": f"连接异常: {str(e)}"}

    def generate_comment(self, analysis_data: dict, style: str = "专业") -> dict:
        """根据构图分析数据生成评语（非流式）"""
        user_prompt = self._build_prompt(analysis_data, style)
        system_prompt = self.SYSTEM_PROMPTS.get(style, self.SYSTEM_PROMPTS["专业"])

        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.4,
                    "top_p": 0.85,
                    "num_predict": 800
                }
            }

            resp = requests.post(self.api_endpoint, json=payload, timeout=60)

            if resp.status_code == 200:
                data = resp.json()
                comment = data.get("message", {}).get("content", "")
                return {"success": True, "comment": comment.strip(), "error": ""}
            else:
                return {"success": False, "comment": "", "error": f"API返回错误: {resp.status_code} - {resp.text}"}

        except requests.Timeout:
            return {"success": False, "comment": "", "error": "请求超时，模型可能正在加载中，请稍后重试"}
        except requests.ConnectionError:
            return {"success": False, "comment": "", "error": "无法连接Ollama服务，请确认已启动"}
        except Exception as e:
            return {"success": False, "comment": "", "error": f"生成评语异常: {str(e)}"}

    def generate_comment_stream(self, analysis_data: dict, style: str = "专业"):
        """流式生成评语（逐字输出）"""
        user_prompt = self._build_prompt(analysis_data, style)
        system_prompt = self.SYSTEM_PROMPTS.get(style, self.SYSTEM_PROMPTS["专业"])
        max_tokens = 400 if style == "简洁" else 800

        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": True,
                "options": {
                    "temperature": 0.4,
                    "top_p": 0.85,
                    "num_predict": max_tokens
                }
            }

            resp = requests.post(self.api_endpoint, json=payload, timeout=120, stream=True)

            if resp.status_code == 200:
                for line in resp.iter_lines():
                    if line:
                        data = json.loads(line)
                        content = data.get("message", {}).get("content", "")
                        if content:
                            yield content
                        if data.get("done", False):
                            break
            else:
                yield f"[错误] API返回: {resp.status_code}"

        except Exception as e:
            yield f"[错误] {str(e)}"

    def _build_prompt(self, analysis_data: dict, style: str) -> str:
        """构建用户提示词 - 将计算机视觉模块的量化数据结构化传递给LLM"""
        analyses = analysis_data.get("analyses", {})
        size = analysis_data.get("image_size", {})
        roi = analysis_data.get("roi")

        prompt_parts = []
        prompt_parts.append("以下是计算机视觉模块对一张照片的精确量化分析结果，请严格基于这些数据生成评语。")
        prompt_parts.append(f"\n图像基本信息：尺寸 {size.get('width', '未知')} x {size.get('height', '未知')} 像素")

        if roi:
            prompt_parts.append(f"用户手动框选的主体区域：起点({roi['x']}, {roi['y']})，大小 {roi['width']}x{roi['height']} 像素")
            prompt_parts.append("（以下分析数据已聚焦于该主体区域）\n")
        else:
            prompt_parts.append("（用户未框选主体，以下为全图分析）\n")

        if "rule_of_thirds" in analyses:
            rot = analyses["rule_of_thirds"]
            prompt_parts.append("═══ 三分法构图分析（计算机视觉测量结果）═══")
            prompt_parts.append(f"  综合得分：{rot.get('score', 'N/A')}/100")
            prompt_parts.append(f"  检测到的视觉兴趣点数量：{len(rot.get('interest_points', []))} 个")
            prompt_parts.append(f"  兴趣点到三分线交点的平均归一化距离：{rot.get('avg_normalized_distance', 'N/A')}")
            prompt_parts.append(f"  （距离越小说明兴趣点越接近三分线交点，0.05以下为优秀）")
            prompt_parts.append(f"  系统初步判断：{rot.get('description', '')}")
            if rot.get('subject_center'):
                sc = rot['subject_center']
                prompt_parts.append(f"  主体中心坐标：({sc['x']}, {sc['y']})")
                prompt_parts.append(f"  主体中心到最近三分交点的归一化距离：{rot.get('subject_to_thirds_distance', 'N/A')}")
            prompt_parts.append("")

        if "symmetry" in analyses:
            sym = analyses["symmetry"]
            h_score = sym.get('horizontal_symmetry', {}).get('score', 'N/A')
            v_score = sym.get('vertical_symmetry', {}).get('score', 'N/A')
            h_diff = sym.get('horizontal_symmetry', {}).get('pixel_diff_mean', 'N/A')
            v_diff = sym.get('vertical_symmetry', {}).get('pixel_diff_mean', 'N/A')
            prompt_parts.append("═══ 对称性构图分析（计算机视觉测量结果）═══")
            prompt_parts.append(f"  水平对称得分：{h_score}/100（左右像素差异均值：{h_diff}）")
            prompt_parts.append(f"  垂直对称得分：{v_score}/100（上下像素差异均值：{v_diff}）")
            prompt_parts.append(f"  综合对称得分：{sym.get('overall_score', 'N/A')}/100")
            best = '水平（左右对称）' if sym.get('best_axis') == 'horizontal' else '垂直（上下对称）'
            prompt_parts.append(f"  最佳对称轴方向：{best}")
            prompt_parts.append(f"  系统初步判断：{sym.get('description', '')}")
            prompt_parts.append("")

        # 额外视觉特征数据
        vf = analyses.get("visual_features", {})
        if vf:
            prompt_parts.append("═══ 额外视觉特征（计算机视觉测量结果）═══")

            brightness = vf.get("brightness", {})
            if brightness:
                prompt_parts.append(f"  整体亮度均值：{brightness.get('overall_mean', 'N/A')}/255")
                prompt_parts.append(f"  亮度标准差：{brightness.get('overall_std', 'N/A')}（对比度{brightness.get('contrast_level', '')}）")
                prompt_parts.append(f"  曝光判断：{brightness.get('exposure_judgment', 'N/A')}")
                prompt_parts.append(f"  最亮区域：{brightness.get('brightest_region', '')}（亮度{brightness.get('brightest_value', '')}）")
                prompt_parts.append(f"  最暗区域：{brightness.get('darkest_region', '')}（亮度{brightness.get('darkest_value', '')}）")

            lines_data = vf.get("lines", {})
            if lines_data:
                prompt_parts.append(f"  检测到线条总数：{lines_data.get('total_detected', 0)} 条")
                prompt_parts.append(f"    水平线：{lines_data.get('horizontal_count', 0)} 条")
                prompt_parts.append(f"    垂直线：{lines_data.get('vertical_count', 0)} 条")
                prompt_parts.append(f"    斜线：{lines_data.get('diagonal_count', 0)} 条")
                prompt_parts.append(f"  主导线条方向：{lines_data.get('dominant_direction', 'N/A')}")

            vc = vf.get("visual_center", {})
            if vc:
                prompt_parts.append(f"  视觉重心位置：水平{vc.get('horizontal_position', '')}，垂直{vc.get('vertical_position', '')}")
                prompt_parts.append(f"  视觉重心归一化坐标：({vc.get('normalized_x', '')}, {vc.get('normalized_y', '')})")

            comp = vf.get("complexity", {})
            if comp:
                prompt_parts.append(f"  边缘密度：{comp.get('edge_density_percent', '')}%（画面复杂度{comp.get('level', '')}）")

            color = vf.get("color", {})
            if color:
                prompt_parts.append(f"  主色调：{color.get('dominant_tone', 'N/A')}")
                prompt_parts.append(f"  饱和度：{color.get('saturation_level', '')}（均值{color.get('saturation_mean', '')}）")

            prompt_parts.append("")

        prompt_parts.append("请严格按照系统提示中规定的输出格式生成评语，格式不可改动（段落结构、编号方式、字数限制）。")
        prompt_parts.append("禁止描述图片具体内容，只能引用上述测量数据。")

        return "\n".join(prompt_parts)
