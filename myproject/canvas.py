from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QColorDialog, QPushButton, QSplitter, QVBoxLayout, QColorDialog
from PyQt5.QtGui import QPixmap, QPainter, QPen, QImage, QColor, QCursor
from PyQt5.QtCore import Qt, QPoint,QSize
from .utils import logprint


class Canvas(QWidget):
    def __init__(self, branch):
        super().__init__()

        # 初始化Canvas属性
        self.branch = branch
        self.drawing = True
        self.last_point = None
        self.height = 800
        self.width = 1000
        self.backpixmap = QPixmap(self.branch.problem.image_path).scaled(
            self.width, self.height)
        self.image = self.backpixmap.toImage()
        self.setMinimumSize(self.width, self.height)
        self.pen = QPen(Qt.red,5)
        self.eraser = QPen(Qt.transparent, 10)  # 透明的笔作为橡皮擦

        # 设置UI
        self.init_ui()

    def init_ui(self):
        # 设置布局
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 创建一个QSplitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # 设置画板标签
        self.label = QLabel(self)
        self.label.setScaledContents(True)
        self.label.setCursor(Qt.CrossCursor)  # 设置鼠标光标为十字形状
        splitter.addWidget(self.label)
        self.label.setMinimumSize(self.width, self.height)

        self.drawing_layer = QPixmap(self.label.size())
        self.drawing_layer.fill(Qt.transparent)

        # 创建一个新的QWidget作为按钮的容器
        button_container = QWidget()
        button_layout = QVBoxLayout()
        button_container.setLayout(button_layout)
        splitter.addWidget(button_container)

        # 设置颜色选择按钮
        color_button = QPushButton('Choose Color', self)
        button_layout.addWidget(color_button)
        color_button.clicked.connect(self.choose_color)

        # 设置Delete Branch按钮
        delete_branch_button = QPushButton('Delete Branch', self)
        button_layout.addWidget(delete_branch_button)
        delete_branch_button.clicked.connect(self.delete_branch)

        # 设置Copy Branch按钮
        copy_branch_button = QPushButton('Copy Branch', self)
        button_layout.addWidget(copy_branch_button)
        copy_branch_button.clicked.connect(self.copy_branch)

        # 设置Check Branch按钮
        check_branch_button = QPushButton('Check Branch', self)
        button_layout.addWidget(check_branch_button)
        check_branch_button.clicked.connect(self.check_branch)

        self.label.setStyleSheet(
            f"border: 4px solid {self.pen.color().name()};")

        cursor_bitmap = QCursor().bitmap()
        if cursor_bitmap:
            self.cursor_size = cursor_bitmap.size()
            print(
                f"Cursor size: {cursor_size.width()} x {cursor_size.height()}")
        else:
            self.cursor_size = 16
            print("Could not retrieve cursor bitmap.")

        self.refresh_display()

    def refresh_display(self):
        # 将绘图图层叠加在背景图像上并显示
        combined_pixmap = self.backpixmap.copy()
        painter = QPainter(combined_pixmap)
        painter.drawPixmap(0, 0, self.drawing_layer)
        painter.end()
        self.label.setPixmap(combined_pixmap)

    def mouseMoveEvent(self, event):
        # 如果正在画图且移动的是鼠标左键
        # logprint(message=f"Canvas size: {self.label.size()}", level="debug")
        # logprint(message=f"Drawing layer size: {self.drawing_layer.size()}", level="debug")
        # logprint(message=f"Backpixmap size: {self.backpixmap.size()}", level="debug")

        scale_w = self.backpixmap.width() / self.label.width()
        scale_h = self.backpixmap.height() / self.label.height()

        # 创建一个画家，开始在图像上绘制
        nowpos = QPoint(event.pos().x() * scale_w - self.cursor_size // 2, event.pos().y() * scale_h - self.cursor_size // 2)
        painter = QPainter(self.drawing_layer)

        if self.drawing and event.buttons() & Qt.LeftButton and self.last_point is not None:
            painter.setPen(self.pen)
            painter.drawLine(self.last_point, nowpos)
        elif event.buttons() & Qt.RightButton:  # 检测是否按下右键
            painter.setCompositionMode(QPainter.CompositionMode_Clear)  # 设置为擦除模式
            painter.setPen(self.eraser)
            painter.drawLine(self.last_point, nowpos)

        self.last_point = nowpos
        painter.end()

        self.refresh_display()

    def mousePressEvent(self, event):
        # 记录鼠标按下时的位置
        logprint(message=f"Mouse press event: {event.button()}", level="debug")
        if event.button() == Qt.LeftButton or event.button() == Qt.RightButton:
            scale_w = self.backpixmap.width() / self.label.width()
            scale_h = self.backpixmap.height() / self.label.height()
            self.last_point = QPoint(event.pos().x() * scale_w - self.cursor_size //
                                     2, event.pos().y() * scale_h - self.cursor_size // 2)

    def mouseReleaseEvent(self, event):
        # 清除最后一个点的位置
        if event.button() == Qt.LeftButton:
            self.last_point = None

    def choose_color(self):
        # 弹出颜色对话框让用户选择颜色
        color = QColorDialog.getColor()
        if color.isValid():
            self.pen.setColor(color)
            # Set border color as current pen color
            self.label.setStyleSheet(f"border: 4px solid {color.name()};")

    def delete_branch(self):
        logprint(message=f"{self.branch.name} deleted.", level="info")
        self.branch.delete_branch()
    def copy_branch(self):
        logprint(message=f"{self.branch.name} copied.", level="info")
        self.branch.copy_branch()
    def check_branch(self):
        # Logic to check branch
        pass

    def copy_from(self, canvas):
        self.drawing_layer = canvas.drawing_layer.copy()
        self.pen = canvas.pen
        self.eraser = canvas.eraser
        self.label.setStyleSheet(f"border: 4px solid {self.pen.color().name()};")
        self.refresh_display()
