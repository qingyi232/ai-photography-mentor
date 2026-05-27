"""
AI摄影导师 - 样式常量和自定义组件
"""
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


class Colors:
    BG = "#F7F9F4"
    CARD_BG = "#FFFFFF"
    SIDEBAR_BG = "#F0F4EC"
    PRIMARY = "#5B8C5A"
    PRIMARY_HOVER = "#4A7A49"
    PRIMARY_LIGHT = "#E8F0E6"
    ACCENT = "#D4A574"
    ACCENT_LIGHT = "#F5EDE3"
    TEXT = "#2C3E2D"
    TEXT_SEC = "#6B7F6C"
    TEXT_LIGHT = "#9BAF9C"
    BORDER = "#D8E0D4"
    BORDER_LIGHT = "#E8EDE5"
    SUCCESS = "#5B8C5A"
    WARNING = "#D4A574"
    ERROR = "#C75C5C"
    SCORE_HIGH = "#5B8C5A"
    SCORE_MID = "#D4A574"
    SCORE_LOW = "#C75C5C"


GLOBAL_STYLE = f"""
QMainWindow {{ background-color: {Colors.BG}; }}
QWidget {{ font-family: "Microsoft YaHei", "Segoe UI", sans-serif; color: {Colors.TEXT}; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{ background: {Colors.BG}; width: 8px; border-radius: 4px; }}
QScrollBar::handle:vertical {{ background: {Colors.BORDER}; border-radius: 4px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: {Colors.TEXT_LIGHT}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QToolTip {{ background-color: {Colors.TEXT}; color: white; border: none; padding: 6px 10px; border-radius: 4px; font-size: 12px; }}
"""


class ScoreRing(QWidget):
    def __init__(self, score=0, label="", size=90, parent=None):
        super().__init__(parent)
        self._score = score
        self._label = label
        self._size = size
        self.setFixedSize(size, size + 22)

    def set_score(self, score, label=""):
        self._score = score
        if label:
            self._label = label
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        s = self._size
        cx, cy = s // 2, s // 2
        r = s // 2 - 8
        pen = QPen(QColor(Colors.BORDER_LIGHT), 6)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(cx - r, cy - r, r * 2, r * 2, 0, 360 * 16)
        if self._score >= 70:
            color = QColor(Colors.SCORE_HIGH)
        elif self._score >= 40:
            color = QColor(Colors.SCORE_MID)
        else:
            color = QColor(Colors.SCORE_LOW)
        pen = QPen(color, 6)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        span = int(self._score / 100 * 360 * 16)
        painter.drawArc(cx - r, cy - r, r * 2, r * 2, 90 * 16, -span)
        painter.setPen(QColor(Colors.TEXT))
        font = QFont("Microsoft YaHei", 16, QFont.Bold)
        painter.setFont(font)
        painter.drawText(QRect(0, 0, s, s), Qt.AlignCenter, str(self._score))
        painter.setPen(QColor(Colors.TEXT_SEC))
        font2 = QFont("Microsoft YaHei", 9)
        painter.setFont(font2)
        painter.drawText(QRect(0, s, s, 22), Qt.AlignCenter, self._label)


class CardWidget(QFrame):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(14, 12, 14, 12)
        self._layout.setSpacing(8)
        if title:
            lbl = QLabel(title)
            lbl.setWordWrap(True)
            lbl.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {Colors.TEXT}; padding-bottom: 3px; border-bottom: 2px solid {Colors.PRIMARY_LIGHT};")
            self._layout.addWidget(lbl)
        self.setStyleSheet(f"CardWidget {{ background-color: {Colors.CARD_BG}; border: 1px solid {Colors.BORDER_LIGHT}; border-radius: 12px; }}")

    def add_widget(self, widget):
        self._layout.addWidget(widget)

    def add_layout(self, layout):
        self._layout.addLayout(layout)


class StyledButton(QPushButton):
    def __init__(self, text, btn_type="default", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(38)
        if btn_type == "primary":
            self.setStyleSheet(f"QPushButton {{ background-color: {Colors.PRIMARY}; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; padding: 8px 20px; }} QPushButton:hover {{ background-color: {Colors.PRIMARY_HOVER}; }} QPushButton:pressed {{ background-color: #3D6B3C; }} QPushButton:disabled {{ background-color: {Colors.BORDER}; color: {Colors.TEXT_LIGHT}; }}")
        elif btn_type == "accent":
            self.setStyleSheet(f"QPushButton {{ background-color: {Colors.ACCENT}; color: white; border: none; border-radius: 8px; font-size: 13px; font-weight: 500; padding: 8px 16px; }} QPushButton:hover {{ background-color: #C49564; }} QPushButton:disabled {{ background-color: {Colors.BORDER}; color: {Colors.TEXT_LIGHT}; }}")
        elif btn_type == "outline":
            self.setStyleSheet(f"QPushButton {{ background-color: transparent; color: {Colors.PRIMARY}; border: 1.5px solid {Colors.PRIMARY}; border-radius: 8px; font-size: 13px; padding: 8px 16px; }} QPushButton:hover {{ background-color: {Colors.PRIMARY_LIGHT}; }} QPushButton:disabled {{ border-color: {Colors.BORDER}; color: {Colors.TEXT_LIGHT}; }}")
        else:
            self.setStyleSheet(f"QPushButton {{ background-color: {Colors.CARD_BG}; color: {Colors.TEXT}; border: 1px solid {Colors.BORDER}; border-radius: 8px; font-size: 13px; padding: 8px 16px; }} QPushButton:hover {{ background-color: {Colors.PRIMARY_LIGHT}; border-color: {Colors.PRIMARY}; }} QPushButton:disabled {{ background-color: #F5F5F5; color: {Colors.TEXT_LIGHT}; }}")


class SelectableImageLabel(QLabel):
    """支持鼠标框选ROI区域的图片标签"""
    roi_selected = Signal(int, int, int, int)  # x, y, w, h (相对于原图的坐标)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap_orig = None
        self._pixmap_overlay = None
        self._showing_overlay = False
        self._img_rect = QRect()
        self._selecting = False
        self._start_pos = None
        self._current_pos = None
        self._roi_rect = None
        self._orig_size = None
        self._zoom = 1.0
        self._pan_offset = QPoint(0, 0)
        self._panning = False
        self._pan_start = None
        self._scaled_pixmap = None
        self.setMouseTracking(True)

    def set_image(self, pixmap, orig_w=0, orig_h=0):
        """设置原图并记录原图尺寸"""
        self._pixmap_orig = pixmap
        self._orig_size = (orig_w or pixmap.width(), orig_h or pixmap.height())
        self._roi_rect = None
        self._zoom = 1.0
        self._pan_offset = QPoint(0, 0)
        self._showing_overlay = False
        self._base_w = max(pixmap.width(), 600)
        self._base_h = max(pixmap.height(), 400)
        self._update_display()

    def set_overlay(self, pixmap):
        """设置叠加图（分析结果叠加层）"""
        self._pixmap_overlay = pixmap

    def show_overlay(self, show=True):
        """切换显示叠加图或原图，缩放和平移状态保持不变"""
        self._showing_overlay = show and self._pixmap_overlay is not None
        self._update_display()

    def clear_roi(self):
        self._roi_rect = None
        self._update_display()

    def get_roi_on_original(self):
        """返回相对于原图的ROI坐标 (x, y, w, h)，无选区返回None"""
        if self._roi_rect is None or self._pixmap_orig is None or self._orig_size is None:
            return None
        if self._img_rect.width() <= 0 or self._img_rect.height() <= 0:
            return None
        # label坐标 → 原图坐标
        sx = self._orig_size[0] / self._img_rect.width()
        sy = self._orig_size[1] / self._img_rect.height()
        rx = int((self._roi_rect.x() - self._img_rect.x()) * sx)
        ry = int((self._roi_rect.y() - self._img_rect.y()) * sy)
        rw = int(self._roi_rect.width() * sx)
        rh = int(self._roi_rect.height() * sy)
        # 裁剪到合法范围
        rx = max(0, rx)
        ry = max(0, ry)
        rw = min(rw, self._orig_size[0] - rx)
        rh = min(rh, self._orig_size[1] - ry)
        if rw < 5 or rh < 5:
            return None
        return (rx, ry, rw, rh)

    def _update_display(self):
        if self._pixmap_orig is None:
            return
        source = self._pixmap_overlay if self._showing_overlay and self._pixmap_overlay else self._pixmap_orig
        src_w, src_h = source.width(), source.height()
        if src_w <= 0 or src_h <= 0:
            return

        if not hasattr(self, '_base_w'):
            self._base_w = max(src_w, 600)
            self._base_h = max(src_h, 400)

        disp_w = max(1, int(self._base_w * self._zoom))
        disp_h = max(1, int(self._base_h * self._zoom))
        scaled = source.scaled(disp_w, disp_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.setFixedSize(scaled.width(), scaled.height())
        self._img_rect = QRect(0, 0, scaled.width(), scaled.height())

        display = scaled.copy()
        if self._roi_rect is not None:
            painter = QPainter(display)
            painter.setRenderHint(QPainter.Antialiasing)
            overlay_color = QColor(0, 0, 0, 80)
            painter.fillRect(display.rect(), overlay_color)
            local_roi = QRect(
                max(0, self._roi_rect.x()),
                max(0, self._roi_rect.y()),
                min(self._roi_rect.width(), scaled.width()),
                min(self._roi_rect.height(), scaled.height())
            )
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(local_roi, Qt.transparent)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            pen = QPen(QColor(Colors.PRIMARY), 2, Qt.DashLine)
            painter.setPen(pen)
            painter.drawRect(local_roi)
            roi_orig = self.get_roi_on_original()
            if roi_orig:
                txt = f"框选区域: {roi_orig[2]}×{roi_orig[3]}"
                painter.setPen(QColor(Colors.PRIMARY))
                painter.setFont(QFont("Microsoft YaHei", 9))
                painter.drawText(local_roi.x() + 4, local_roi.y() - 4, txt)
            painter.end()
        self.setPixmap(display)

        scroll = self.parent()
        if scroll and hasattr(scroll, 'viewport'):
            scroll_parent = scroll.parent()
            if scroll_parent and hasattr(scroll_parent, 'ensureWidgetVisible'):
                scroll_parent.ensureWidgetVisible(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._pixmap_orig is not None:
            if self._img_rect.contains(event.pos()):
                self._selecting = True
                self._start_pos = event.pos()
                self._current_pos = event.pos()
                self._roi_rect = None
        elif event.button() == Qt.RightButton and self._pixmap_orig is not None:
            self._panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        elif event.button() == Qt.MiddleButton and self._pixmap_orig is not None:
            # 中键重置缩放
            self._zoom = 1.0
            self._pan_offset = QPoint(0, 0)
            self._update_display()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._panning and self._pan_start is not None:
            delta = event.pos() - self._pan_start
            self._pan_offset = self._pan_offset + delta
            self._pan_start = event.pos()
            self._update_display()
            return
        if self._selecting and self._start_pos is not None:
            self._current_pos = event.pos()
            # 限制在图片区域内
            cx = max(self._img_rect.x(), min(event.pos().x(), self._img_rect.right()))
            cy = max(self._img_rect.y(), min(event.pos().y(), self._img_rect.bottom()))
            self._current_pos = QPoint(cx, cy)
            x1 = min(self._start_pos.x(), self._current_pos.x())
            y1 = min(self._start_pos.y(), self._current_pos.y())
            x2 = max(self._start_pos.x(), self._current_pos.x())
            y2 = max(self._start_pos.y(), self._current_pos.y())
            self._roi_rect = QRect(x1, y1, x2 - x1, y2 - y1)
            self._update_display()
        if self._pixmap_orig and self._img_rect.contains(event.pos()):
            self.setCursor(Qt.CrossCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton and self._panning:
            self._panning = False
            self.setCursor(Qt.ArrowCursor)
            return
        if event.button() == Qt.LeftButton and self._selecting:
            self._selecting = False
            roi = self.get_roi_on_original()
            if roi:
                self.roi_selected.emit(*roi)
            else:
                self._roi_rect = None
                self._update_display()
        super().mouseReleaseEvent(event)

    def resizeEvent(self, event):
        self._update_display()
        super().resizeEvent(event)

    def wheelEvent(self, event):
        """滚轮缩放图片，QScrollArea 自动处理滚动"""
        if self._pixmap_orig is None:
            return
        delta = event.angleDelta().y()
        if delta > 0:
            self._zoom = min(5.0, self._zoom * 1.15)
        else:
            self._zoom = max(0.3, self._zoom / 1.15)
        self._update_display()
        event.accept()


SAMPLE_IMAGES = [
    {"name": "风光 - 山水日出", "url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80", "desc": "壮丽山脉日出风光"},
    {"name": "建筑 - 对称走廊", "url": "https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=800&q=80", "desc": "经典对称建筑构图"},
    {"name": "人像 - 三分法", "url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=800&q=80", "desc": "人像三分法构图示例"},
    {"name": "自然 - 花卉微距", "url": "https://images.unsplash.com/photo-1490750967868-88aa4f44baee?w=800&q=80", "desc": "花卉微距摄影"},
]
