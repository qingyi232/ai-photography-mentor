"""
AI摄影导师 - 构图分析模块
使用OpenCV实现三分法分析和对称性分析，提供精美可视化叠加
"""
import cv2
import numpy as np
import json


class CompositionAnalyzer:
    """构图分析器：提供三分法和对称性两种构图规则分析"""

    def __init__(self):
        self.results = {}

    def analyze(self, image_path: str, rules: list = None, roi: tuple = None) -> dict:
        """
        对图像执行构图分析
        :param image_path: 图像文件路径
        :param rules: 要分析的规则列表
        :param roi: 可选的主体框选区域 (x, y, w, h)，用于聚焦分析
        :return: 结构化JSON分析结果
        """
        if rules is None:
            rules = ["rule_of_thirds", "symmetry"]

        # 使用numpy解决中文路径问题
        img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return {"error": f"无法读取图像: {image_path}"}

        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        self.results = {
            "image_path": image_path,
            "image_size": {"width": w, "height": h},
            "roi": None,
            "analyses": {}
        }

        # 如果有ROI框选，记录并用于分析
        if roi and len(roi) == 4:
            rx, ry, rw, rh = roi
            rx = max(0, min(rx, w - 1))
            ry = max(0, min(ry, h - 1))
            rw = max(1, min(rw, w - rx))
            rh = max(1, min(rh, h - ry))
            self.results["roi"] = {"x": rx, "y": ry, "width": rw, "height": rh}

        if "rule_of_thirds" in rules:
            self.results["analyses"]["rule_of_thirds"] = self._analyze_rule_of_thirds(gray, w, h, roi)

        if "symmetry" in rules:
            self.results["analyses"]["symmetry"] = self._analyze_symmetry(gray, w, h, roi)

        # 始终提取额外的客观视觉特征，供LLM引用
        self.results["analyses"]["visual_features"] = self._extract_visual_features(img, gray, w, h, roi)

        return self.results

    def _analyze_rule_of_thirds(self, gray: np.ndarray, w: int, h: int, roi: tuple = None) -> dict:
        third_points = [
            (w // 3, h // 3),
            (2 * w // 3, h // 3),
            (w // 3, 2 * h // 3),
            (2 * w // 3, 2 * h // 3),
        ]

        # 如果有ROI，在ROI区域内检测兴趣点
        if roi and len(roi) == 4:
            rx, ry, rw, rh = roi
            roi_gray = gray[ry:ry+rh, rx:rx+rw]
            corners = cv2.goodFeaturesToTrack(roi_gray, maxCorners=50, qualityLevel=0.01, minDistance=20)
            if corners is not None:
                corners = corners.reshape(-1, 2)
                # 将ROI内坐标转换为全图坐标
                corners[:, 0] += rx
                corners[:, 1] += ry
            # 同时计算主体中心到三分交点的距离
            subject_center = (rx + rw // 2, ry + rh // 2)
        else:
            corners = cv2.goodFeaturesToTrack(gray, maxCorners=50, qualityLevel=0.01, minDistance=30)
            if corners is not None:
                corners = corners.reshape(-1, 2)
            subject_center = None

        if corners is None or len(corners) == 0:
            return {
                "third_points": [{"x": p[0], "y": p[1]} for p in third_points],
                "interest_points": [],
                "min_distances": [],
                "avg_min_distance": -1,
                "avg_normalized_distance": 0,
                "score": 0,
                "description": "未检测到兴趣点"
            }

        corners = corners.reshape(-1, 2)

        min_distances = []
        for corner in corners:
            dists = [np.sqrt((corner[0] - tp[0]) ** 2 + (corner[1] - tp[1]) ** 2) for tp in third_points]
            min_distances.append(float(min(dists)))

        diag = np.sqrt(w ** 2 + h ** 2)
        norm_distances = [d / diag for d in min_distances]

        top_k = min(10, len(norm_distances))
        sorted_dists = sorted(norm_distances)[:top_k]
        avg_dist = float(np.mean(sorted_dists))

        score = max(0, min(100, int((1 - avg_dist * 5) * 100)))

        result = {
            "third_points": [{"x": int(p[0]), "y": int(p[1])} for p in third_points],
            "interest_points": [{"x": float(c[0]), "y": float(c[1])} for c in corners[:20]],
            "top_min_distances": [round(d, 4) for d in sorted_dists],
            "avg_normalized_distance": round(avg_dist, 4),
            "score": score,
            "description": self._thirds_description(score)
        }
        if subject_center:
            # 计算主体中心到最近三分交点的距离
            center_dists = [np.sqrt((subject_center[0] - tp[0]) ** 2 + (subject_center[1] - tp[1]) ** 2) for tp in third_points]
            min_center_dist = min(center_dists) / diag
            result["subject_center"] = {"x": subject_center[0], "y": subject_center[1]}
            result["subject_to_thirds_distance"] = round(min_center_dist, 4)
        return result

    def _thirds_description(self, score: int) -> str:
        if score >= 80:
            return "兴趣点非常接近三分线交点，构图优秀"
        elif score >= 60:
            return "兴趣点较接近三分线交点，构图良好"
        elif score >= 40:
            return "兴趣点与三分线交点有一定距离，构图一般"
        else:
            return "兴趣点远离三分线交点，三分法构图较弱"

    def _analyze_symmetry(self, gray: np.ndarray, w: int, h: int, roi: tuple = None) -> dict:
        # 如果有ROI，在ROI区域内分析对称性
        if roi and len(roi) == 4:
            rx, ry, rw, rh = roi
            analyze_region = gray[ry:ry+rh, rx:rx+rw]
            aw, ah = rw, rh
        else:
            analyze_region = gray
            aw, ah = w, h

        half_w = aw // 2
        left = analyze_region[:, :half_w]
        right = analyze_region[:, half_w:2 * half_w]
        right_flipped = cv2.flip(right, 1)

        h_diff = cv2.absdiff(left, right_flipped)
        h_score_raw = float(np.mean(h_diff))
        h_symmetry = max(0, min(100, int((1 - h_score_raw / 128) * 100)))

        half_h = ah // 2
        top = analyze_region[:half_h, :]
        bottom = analyze_region[half_h:2 * half_h, :]
        bottom_flipped = cv2.flip(bottom, 0)

        v_diff = cv2.absdiff(top, bottom_flipped)
        v_score_raw = float(np.mean(v_diff))
        v_symmetry = max(0, min(100, int((1 - v_score_raw / 128) * 100)))

        overall = max(h_symmetry, v_symmetry)

        return {
            "horizontal_symmetry": {
                "pixel_diff_mean": round(h_score_raw, 2),
                "score": h_symmetry
            },
            "vertical_symmetry": {
                "pixel_diff_mean": round(v_score_raw, 2),
                "score": v_symmetry
            },
            "overall_score": overall,
            "best_axis": "horizontal" if h_symmetry >= v_symmetry else "vertical",
            "description": self._symmetry_description(overall)
        }

    def _symmetry_description(self, score: int) -> str:
        if score >= 80:
            return "图像具有很强的对称性，构图工整"
        elif score >= 60:
            return "图像有一定对称性，构图较为均衡"
        elif score >= 40:
            return "图像对称性一般"
        else:
            return "图像对称性较弱，构图偏向非对称风格"

    def draw_analysis_overlay(self, image_path: str, analysis_result: dict) -> np.ndarray:
        """在图像上绘制精美的分析可视化叠加层"""
        img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return None

        h, w = img.shape[:2]
        overlay = img.copy()
        analyses = analysis_result.get("analyses", {})

        # 绘制三分法
        if "rule_of_thirds" in analyses:
            rot = analyses["rule_of_thirds"]
            # 三分线 - 使用半透明白色虚线效果
            line_color = (255, 255, 255)
            # 竖线
            for x in [w // 3, 2 * w // 3]:
                self._draw_dashed_line(overlay, (x, 0), (x, h), line_color, 1, 15, 10)
            # 横线
            for y in [h // 3, 2 * h // 3]:
                self._draw_dashed_line(overlay, (0, y), (w, y), line_color, 1, 15, 10)

            # 交点 - 使用精致的十字标记
            for tp in rot.get("third_points", []):
                cx, cy = tp["x"], tp["y"]
                # 外圈
                cv2.circle(overlay, (cx, cy), 12, (80, 200, 120), 2, cv2.LINE_AA)
                # 十字
                cv2.line(overlay, (cx - 8, cy), (cx + 8, cy), (80, 200, 120), 1, cv2.LINE_AA)
                cv2.line(overlay, (cx, cy - 8), (cx, cy + 8), (80, 200, 120), 1, cv2.LINE_AA)

            # 兴趣点 - 使用蓝色小圆点+连线到最近三分交点
            third_pts = [(tp["x"], tp["y"]) for tp in rot.get("third_points", [])]
            for ip in rot.get("interest_points", [])[:15]:
                ix, iy = int(ip["x"]), int(ip["y"])
                # 蓝色圆点 (BGR: B=255, G=140, R=50)
                cv2.circle(overlay, (ix, iy), 4, (255, 140, 50), -1, cv2.LINE_AA)
                cv2.circle(overlay, (ix, iy), 6, (255, 140, 50), 1, cv2.LINE_AA)
                # 连线到最近的三分交点
                if third_pts:
                    dists = [((ix - tx) ** 2 + (iy - ty) ** 2, (tx, ty)) for tx, ty in third_pts]
                    _, nearest = min(dists, key=lambda d: d[0])
                    cv2.line(overlay, (ix, iy), nearest, (255, 140, 50), 1, cv2.LINE_AA)

        # 绘制对称轴
        if "symmetry" in analyses:
            sym = analyses["symmetry"]
            axis_color = (0, 220, 220)
            if sym.get("best_axis") == "horizontal":
                self._draw_dashed_line(overlay, (w // 2, 0), (w // 2, h), axis_color, 2, 20, 8)
                # 标注
                cv2.putText(overlay, "Symmetry Axis", (w // 2 + 10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, axis_color, 1, cv2.LINE_AA)
            else:
                self._draw_dashed_line(overlay, (0, h // 2), (w, h // 2), axis_color, 2, 20, 8)
                cv2.putText(overlay, "Symmetry Axis", (10, h // 2 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, axis_color, 1, cv2.LINE_AA)

        # 绘制ROI框选区域
        roi_data = analysis_result.get("roi")
        if roi_data:
            rx, ry = roi_data["x"], roi_data["y"]
            rw, rh = roi_data["width"], roi_data["height"]
            # 半透明遮罩（ROI外部变暗）
            mask = np.zeros_like(overlay, dtype=np.uint8)
            mask[:] = (0, 0, 0)
            mask[ry:ry+rh, rx:rx+rw] = overlay[ry:ry+rh, rx:rx+rw]
            dark = cv2.addWeighted(overlay, 0.4, mask, 0.6, 0)
            dark[ry:ry+rh, rx:rx+rw] = overlay[ry:ry+rh, rx:rx+rw]
            overlay = dark
            # ROI边框
            cv2.rectangle(overlay, (rx, ry), (rx+rw, ry+rh), (80, 200, 120), 2, cv2.LINE_AA)
            cv2.putText(overlay, "Subject ROI", (rx + 4, ry - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (80, 200, 120), 1, cv2.LINE_AA)

        # 左上角信息面板
        self._draw_info_panel(overlay, analyses, w, h)

        # 半透明混合
        result = cv2.addWeighted(overlay, 0.75, img, 0.25, 0)
        return result

    def _draw_dashed_line(self, img, pt1, pt2, color, thickness, dash_len, gap_len):
        """绘制虚线"""
        x1, y1 = pt1
        x2, y2 = pt2
        dist = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if dist == 0:
            return
        dx = (x2 - x1) / dist
        dy = (y2 - y1) / dist
        pos = 0
        while pos < dist:
            start = (int(x1 + dx * pos), int(y1 + dy * pos))
            end_pos = min(pos + dash_len, dist)
            end = (int(x1 + dx * end_pos), int(y1 + dy * end_pos))
            cv2.line(img, start, end, color, thickness, cv2.LINE_AA)
            pos += dash_len + gap_len

    def _draw_info_panel(self, img, analyses, w, h):
        """在图像左上角绘制半透明信息面板"""
        panel_h = 80
        panel_w = 280
        # 半透明黑色背景
        sub = img[8:8 + panel_h, 8:8 + panel_w]
        black = np.zeros_like(sub)
        blended = cv2.addWeighted(sub, 0.4, black, 0.6, 0)
        img[8:8 + panel_h, 8:8 + panel_w] = blended

        y_offset = 28
        font = cv2.FONT_HERSHEY_SIMPLEX
        if "rule_of_thirds" in analyses:
            score = analyses["rule_of_thirds"].get("score", 0)
            cv2.putText(img, f"Thirds Score: {score}/100", (18, y_offset),
                        font, 0.5, (80, 200, 120), 1, cv2.LINE_AA)
            y_offset += 22

        if "symmetry" in analyses:
            score = analyses["symmetry"].get("overall_score", 0)
            cv2.putText(img, f"Symmetry Score: {score}/100", (18, y_offset),
                        font, 0.5, (0, 220, 220), 1, cv2.LINE_AA)
            y_offset += 22

        cv2.putText(img, f"Size: {w}x{h}", (18, y_offset),
                    font, 0.4, (200, 200, 200), 1, cv2.LINE_AA)

    def _extract_visual_features(self, img, gray, w, h, roi=None):
        """提取额外的客观视觉特征，为LLM提供更丰富的事实数据"""
        if roi and len(roi) == 4:
            rx, ry, rw, rh = roi
            region_gray = gray[ry:ry+rh, rx:rx+rw]
            region_color = img[ry:ry+rh, rx:rx+rw]
        else:
            region_gray = gray
            region_color = img

        features = {}

        # 1. 亮度分布分析
        mean_brightness = float(np.mean(region_gray))
        std_brightness = float(np.std(region_gray))
        # 将图像分为9宫格，计算每格亮度
        rh_g, rw_g = region_gray.shape[:2]
        grid_brightness = []
        grid_names = ["左上", "中上", "右上", "左中", "正中", "右中", "左下", "中下", "右下"]
        for gy in range(3):
            for gx in range(3):
                y1 = gy * rh_g // 3
                y2 = (gy + 1) * rh_g // 3
                x1 = gx * rw_g // 3
                x2 = (gx + 1) * rw_g // 3
                grid_brightness.append({
                    "position": grid_names[gy * 3 + gx],
                    "mean_brightness": round(float(np.mean(region_gray[y1:y2, x1:x2])), 1)
                })
        # 找出最亮和最暗区域
        sorted_grids = sorted(grid_brightness, key=lambda x: x["mean_brightness"])
        features["brightness"] = {
            "overall_mean": round(mean_brightness, 1),
            "overall_std": round(std_brightness, 1),
            "brightest_region": sorted_grids[-1]["position"],
            "brightest_value": sorted_grids[-1]["mean_brightness"],
            "darkest_region": sorted_grids[0]["position"],
            "darkest_value": sorted_grids[0]["mean_brightness"],
            "contrast_level": "高" if std_brightness > 60 else ("中" if std_brightness > 30 else "低"),
            "exposure_judgment": "偏亮" if mean_brightness > 170 else ("偏暗" if mean_brightness < 85 else "适中")
        }

        # 2. 主要线条方向检测（Hough变换）
        edges = cv2.Canny(region_gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50,
                                minLineLength=min(rw_g, rh_g) // 8, maxLineGap=10)
        h_lines = 0  # 水平线
        v_lines = 0  # 垂直线
        d_lines = 0  # 斜线
        line_angles = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.degrees(np.arctan2(abs(y2 - y1), abs(x2 - x1)))
                line_angles.append(angle)
                if angle < 15:
                    h_lines += 1
                elif angle > 75:
                    v_lines += 1
                else:
                    d_lines += 1
        total_lines = h_lines + v_lines + d_lines
        if total_lines > 0:
            dominant = "水平线条为主" if h_lines >= v_lines and h_lines >= d_lines else \
                       ("垂直线条为主" if v_lines >= h_lines and v_lines >= d_lines else "斜线条为主")
        else:
            dominant = "未检测到明显线条"
        features["lines"] = {
            "total_detected": total_lines,
            "horizontal_count": h_lines,
            "vertical_count": v_lines,
            "diagonal_count": d_lines,
            "dominant_direction": dominant
        }

        # 3. 视觉重心（质心）位置
        # 使用边缘图的质心来估算视觉重心
        moments = cv2.moments(edges)
        if moments["m00"] > 0:
            cx = int(moments["m10"] / moments["m00"])
            cy = int(moments["m01"] / moments["m00"])
            # 归一化到0-1范围
            norm_cx = round(cx / rw_g, 3)
            norm_cy = round(cy / rh_g, 3)
            # 判断重心偏向
            h_pos = "偏左" if norm_cx < 0.4 else ("偏右" if norm_cx > 0.6 else "居中")
            v_pos = "偏上" if norm_cy < 0.4 else ("偏下" if norm_cy > 0.6 else "居中")
        else:
            norm_cx, norm_cy = 0.5, 0.5
            h_pos, v_pos = "居中", "居中"
        features["visual_center"] = {
            "normalized_x": norm_cx,
            "normalized_y": norm_cy,
            "horizontal_position": h_pos,
            "vertical_position": v_pos,
            "description": f"视觉重心{h_pos}{v_pos}"
        }

        # 4. 边缘密度（复杂度指标）
        edge_density = round(float(np.sum(edges > 0)) / (rw_g * rh_g) * 100, 1)
        features["complexity"] = {
            "edge_density_percent": edge_density,
            "level": "高（细节丰富）" if edge_density > 15 else ("中" if edge_density > 5 else "低（画面简洁）")
        }

        # 5. 色彩分布（HSV空间）
        hsv = cv2.cvtColor(region_color, cv2.COLOR_BGR2HSV)
        mean_h = float(np.mean(hsv[:, :, 0]))
        mean_s = float(np.mean(hsv[:, :, 1]))
        mean_v = float(np.mean(hsv[:, :, 2]))
        # 判断主色调
        if mean_s < 30:
            color_tone = "接近黑白/灰色调"
        elif mean_h < 15 or mean_h > 165:
            color_tone = "暖色调（红/橙）"
        elif mean_h < 45:
            color_tone = "暖色调（黄/橙）"
        elif mean_h < 75:
            color_tone = "自然色调（绿）"
        elif mean_h < 105:
            color_tone = "冷色调（青/蓝绿）"
        elif mean_h < 135:
            color_tone = "冷色调（蓝）"
        else:
            color_tone = "冷色调（紫）"
        features["color"] = {
            "dominant_tone": color_tone,
            "saturation_mean": round(mean_s, 1),
            "saturation_level": "高饱和" if mean_s > 120 else ("中饱和" if mean_s > 60 else "低饱和"),
        }

        return features

    def to_json(self) -> str:
        return json.dumps(self.results, ensure_ascii=False, indent=2)
