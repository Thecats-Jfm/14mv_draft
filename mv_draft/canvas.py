from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QColorDialog,
    QPushButton,
    QSplitter,
    QHBoxLayout,
    QCheckBox,
)
from PyQt5.QtGui import (
    QPixmap,
    QPainter,
    QPen,
    QColor,
    QCursor,
    QIcon,
    QFontMetrics,
    QFont,
    QPalette,
)
from PyQt5.QtCore import Qt, QPoint, QSize, QRectF
from .utils import logprint, MySplitter
import numpy as np
from copy import deepcopy


class Canvas(QWidget):
    is_drawing = False
    color_index = 3
    pen = QPen(Qt.red, 5)
    eraser = QPen(Qt.transparent, 20)
    last_point = None
    other_color = None

    # 添加颜色选择按钮
    color_buttons_info = [
        ("cyan", "#00FFFF"),
        ("orange", "#FFA600"),
        ("lime", "#00FF00"),
        ("myYellow", "#E1E100"),
        ("red", "#FF0000"),
        ("blue", "#0000FF"),
        ("purple", "#A121F0"),
        ("white", "#FFFFFF"),
    ]

    def __init__(self, branch):
        super().__init__()
        # Initialize Canvas Attributes
        self.branch = branch
        self.canvas_height = 800
        self.canvas_width = 1200
        self.grided = True

        background_pixmap = self.branch.problem.background_pixmap
        self.background_pixmap = background_pixmap.scaled(
            self.canvas_width, self.canvas_height
        )
        self.image_height = background_pixmap.height()
        self.image_width = background_pixmap.width()

        self.question_board_positions = []
        self.question_board_sizes = self.branch.question_board_sizes

        # logprint(f"Image Size: {self.image_width} x {self.image_height}")
        # logprint(f"Canvas Size: {self.canvas_width} x {self.canvas_height}")
        for position in self.branch.question_board_positions:
            self.question_board_positions.append(
                [
                    round(position[0] * self.canvas_width / self.image_width),
                    round(position[1] * self.canvas_height / self.image_height),
                    round(position[2] * self.canvas_width / self.image_width),
                    round(position[3] * self.canvas_height / self.image_height),
                ]
            )
            self.safe_icon = QIcon("img/safe.png").pixmap(QSize(100, 100))
            self.mine_icon = QIcon("img/mine.png").pixmap(QSize(100, 100))
            self.choose_icon = QIcon("img/choose.png").pixmap(QSize(100, 100))
            self.circle_icon = QIcon("img/circle.svg").pixmap(QSize(100, 100))
            self.cross_icon = QIcon("img/cross.svg").pixmap(QSize(100, 100))

        self.init_ui()

    def keyPressEvent(self, event):
        # logprint(f'{event.key()}',level='debug')
        if event.key() == Qt.Key_D:
            self.toggle_drawing()
        elif event.key() == Qt.Key_X:
            self.clear_drawing_layer()
        elif event.key() == Qt.Key_Space:
            self.check_branch()
        elif event.key() == Qt.Key_C:
            self.copy_branch()
        elif event.key() == Qt.Key_Delete or event.key() == Qt.Key_Escape:
            self.delete_branch()
        elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.on_toggle_button_state_changed(not self.branch.finished)
        elif event.key() == Qt.Key_N:
            self.reset_status()
        elif event.key() == Qt.Key_Up:
            self.move_to_previous_branch()
        elif event.key() == Qt.Key_Down:
            self.move_to_next_branch()

    def move_to_previous_branch(self):
        new_idx = self.branch.problem.main_window.branch_list.currentRow() - 1
        if new_idx == -1:
            new_idx = len(self.branch.problem.main_window.branch_list) - 1
        self.branch.problem.main_window.update_branch_list(new_idx)

    def move_to_next_branch(self):
        new_idx = self.branch.problem.main_window.branch_list.currentRow() + 1
        if new_idx == len(self.branch.problem.main_window.branch_list):
            new_idx = 0
        self.branch.problem.main_window.update_branch_list(new_idx)

    def init_ui(self):
        # Initialize Layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create QSplitter
        splitter = MySplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Set Drawing Area
        self.label = QLabel(self)
        self.label.setScaledContents(True)
        self.label.setMinimumSize(self.canvas_width, self.canvas_height)
        splitter.addWidget(self.label)

        # Create Drawing Layers
        self.drawing_layer = QPixmap(self.background_pixmap.size())
        self.drawing_layer.fill(Qt.transparent)

        self.mine_layer = QPixmap(self.background_pixmap.size())
        self.mine_layer.fill(Qt.transparent)

        # Create Button Container
        button_container = QWidget()
        button_layout = QVBoxLayout()
        button_container.setLayout(button_layout)
        splitter.addWidget(button_container)

        # Create Color Label
        self.color_label = QLabel()
        button_layout.addWidget(self.color_label)
        self.color_label.setMinimumHeight(150)
        self.color_label.setAutoFillBackground(True)

        # Set color label color as current pen color
        palette = self.color_label.palette()
        palette.setColor(QPalette.Background, Canvas.pen.color())
        self.color_label.setPalette(palette)

        # Create Count Label
        self.count_label = QLabel()
        button_layout.addWidget(self.count_label)
        default_font = self.count_label.font()
        font_metrics = QFontMetrics(default_font)
        new_font_size = 1 * font_metrics.height()  # 若干倍的默认字号，后续可以调整
        new_font = QFont(default_font.family(), new_font_size)
        self.count_label.setFont(new_font)

        # 创建一个QCheckBox
        self.toggle_button = QCheckBox("未完成", self)

        # 将状态切换的槽函数连接到QCheckBox的状态变化信号
        self.toggle_button.stateChanged.connect(self.on_toggle_button_state_changed)

        button_layout.addWidget(self.toggle_button)

        # Create Buttons
        buttons_info = [
            ("Reset Status", self.reset_status),
            ("Toggle Drawing", self.toggle_drawing),
            ("Choose Other Color", self.choose_color),
            ("Delete Branch", self.delete_branch),
            ("Copy Branch", self.copy_branch),
            ("Check Branch", self.check_branch),
        ]

        for text, callback in buttons_info:
            button = QPushButton(text, self)
            button_layout.addWidget(button)
            button.clicked.connect(callback)

        # 创建颜色选择按钮
        for i in range(len(Canvas.color_buttons_info)):
            color_name, color_code = Canvas.color_buttons_info[i]
            color_button = QPushButton(self)
            color_button.setStyleSheet(f"background-color: {color_code};")
            # color_button.setMaximumWidth(20)  # 设置按钮宽度
            # color_button.setMaximumHeight(20) # 设置按钮高度
            button_layout.addWidget(color_button)
            color_button.clicked.connect(
                lambda _, color_index=i: self.set_color(color_index)
            )

        # Get Cursor Size
        cursor_bitmap = QCursor().bitmap()
        if cursor_bitmap:
            self.cursor_size = cursor_bitmap.size()
        else:
            self.cursor_size = QSize(16, 16)
        self.cursor_size = self.cursor_size.width()

        splitter.setSizes([1000, 100])

        self.init_grid()
        self.refresh_display()

    def refresh_display(self):
        # 将绘图图层叠加在背景图像上并显示
        combined_pixmap = self.background_pixmap.copy()
        painter = QPainter(combined_pixmap)
        painter.drawPixmap(0, 0, self.mine_layer)
        painter.drawPixmap(0, 0, self.drawing_layer)
        painter.end()
        self.label.setPixmap(combined_pixmap)
        self.count_label.setText(
            f'🚩  <font color="red">{self.branch.cnt_flags():02}</font>    <font color="green">?  {self.branch.cnt_safes():02}</font>'
        )

    def on_toggle_button_state_changed(self, state):
        # 根据QCheckBox的状态更新显示的文本
        if state:
            self.toggle_button.setText("已完成")
            self.toggle_button.setChecked(True)
            self.branch.finished = True
        else:
            self.branch.finished = False
            self.toggle_button.setText("未完成")
            self.toggle_button.setChecked(False)
        self.branch.problem.main_window.update_branch_list(-2)

    # 设置画笔颜色的函数
    def set_color(self, color_index):
        Canvas.color_index = color_index
        if color_index == -1:
            color_code = Canvas.other_color
        else:
            color_code = Canvas.color_buttons_info[color_index][1]
        Canvas.color_index = color_index
        color = QColor(color_code)
        Canvas.pen.setColor(color)
        palette = self.color_label.palette()
        palette.setColor(QPalette.Background, Canvas.pen.color())
        self.color_label.setPalette(palette)

    def mouseMoveEvent(self, event):
        now_pos = self.get_scaled_position(event)
        painter = QPainter(self.drawing_layer)

        if Canvas.is_drawing:
            if event.buttons() & Qt.LeftButton and Canvas.last_point is not None:
                painter.setPen(Canvas.pen)
                painter.drawLine(Canvas.last_point, now_pos)
            elif (
                event.buttons() & Qt.RightButton and Canvas.last_point is not None
            ):  # 检测是否按下右键
                painter.setCompositionMode(
                    QPainter.CompositionMode_Clear
                )  # 设置为擦除模式
                painter.setPen(Canvas.eraser)
                painter.drawLine(Canvas.last_point, now_pos)

        Canvas.last_point = now_pos
        painter.end()

        self.refresh_display()

    def wheelEvent(self, event):
        # 换鼠标之后具体数值可能会改变

        # 左右方向
        times = abs(event.angleDelta().x()) // 480
        if event.angleDelta().x() > 0:
            # 鼠标向左滚动
            for i in range(times):
                self.move_to_previous_branch()
        else:
            # 鼠标向右滚动
            for i in range(times):
                self.move_to_next_branch()

        # 上下方向
        if not Canvas.is_drawing:
            return
        if Canvas.color_index == -1:
            return

        times = abs(event.angleDelta().y()) // 120
        if event.angleDelta().y() > 0:
            # 鼠标向上滚动
            for i in range(times):
                Canvas.color_index -= 1
                if Canvas.color_index == -1:
                    Canvas.color_index = len(Canvas.color_buttons_info) - 1
        else:
            # 鼠标向下滚动
            for i in range(times):
                Canvas.color_index += 1
                if Canvas.color_index == len(Canvas.color_buttons_info):
                    Canvas.color_index = 0
        self.set_color(Canvas.color_index)

    def init_grid(self):
        if self.grided == False:
            return
        for i, position in enumerate(self.question_board_positions):
            print(i, position)
            # Calculate grid dimensions
            width = position[2]
            height = position[3]
            x1 = position[0]
            y1 = position[1]
            x2 = x1 + width
            y2 = y1 + height

            # logprint(f"width: {width}, height: {height}", level="debug")

            # Set the number of rows and columns for the n*n grid
            n = self.question_board_sizes[i]

            # Create QPixmap object
            pixmap = self.background_pixmap

            # Create QPainter object
            painter = QPainter(pixmap)

            # Create and set QPen object
            pen = QPen(Qt.cyan)  # Set pen color
            pen.setWidth(3)  # Set line width
            pen.setStyle(Qt.DashLine)  # Set dash line style
            painter.setPen(pen)

            # Calculate cell width and height
            cell_width = width / n
            cell_height = height / n

            # logprint(f"cell_width: {cell_width}, cell_height: {cell_height}", level="debug")

            # Draw grid
            for i in range(n + 1):
                # Draw horizontal lines
                painter.drawLine(x1, y1 + i * cell_height, x2, y1 + i * cell_height)
                # Draw vertical lines
                painter.drawLine(x1 + i * cell_width, y1, x1 + i * cell_width, y2)

            # End drawing
            painter.end()

    def mousePressEvent(self, event):
        # Record mouse position when pressed
        # logprint(message=f"Mouse press event: {event.button()}", level="debug")
        if event.button() in (Qt.LeftButton, Qt.RightButton):
            scale_w = self.background_pixmap.width() / self.label.width()
            scale_h = self.background_pixmap.height() / self.label.height()
            Canvas.last_point = QPoint(
                event.pos().x() * scale_w - self.cursor_size // 2,
                event.pos().y() * scale_h - self.cursor_size // 2,
            )

    def mouseReleaseEvent(self, event):

        # Clear the last point position
        if event.button() in (Qt.LeftButton, Qt.RightButton, Qt.MiddleButton):

            Canvas.last_point = None
            if not Canvas.is_drawing and self.grided:
                now_pos = self.get_scaled_position(event)

                for i, position in enumerate(self.question_board_positions):
                    size = self.question_board_sizes[i]
                    x1, y1, x2, y2 = (
                        position[0],
                        position[1],
                        position[0] + position[2],
                        position[1] + position[3],
                    )
                    if x1 <= now_pos.x() < x2 and y1 <= now_pos.y() < y2:

                        # 计算每个单元格的宽度和高度
                        cell_width = (x2 - x1) / size
                        cell_height = (y2 - y1) / size

                        # 计算now_pos坐标相对于矩形(x1, y1, x2, y2)的位置
                        relative_x = now_pos.x() - x1
                        relative_y = now_pos.y() - y1

                        # 计算now_pos坐标落在哪个单元格内
                        cell_x = int(relative_x // cell_width)
                        cell_y = int(relative_y // cell_height)

                        if event.button() == Qt.LeftButton:
                            self.branch.mark_safe(i, cell_x, cell_y)
                        elif event.button() == Qt.RightButton:
                            self.branch.mark_mine(i, cell_x, cell_y)
                        elif event.button() == Qt.MiddleButton:
                            self.branch.middle_click(i, cell_x, cell_y)

    def draw_icon_in_cell(self, idx, cell_x, cell_y, icon):
        if self.grided:
            # 计算每个单元格的宽度和高度
            position = self.question_board_positions[idx]
            size = self.question_board_sizes[idx]
            cell_width = position[2] / size
            cell_height = position[3] / size

            # 计算icon的中心坐标
            icon_x = position[0] + cell_x * cell_width + cell_width / 2
            icon_y = position[1] + cell_y * cell_height + cell_height / 2

            # 创建一个 QPainter 对象
            painter = QPainter(self.mine_layer)

            # 将icon绘制到中心位置
            icon_size = min(cell_width, cell_height) * 1.2  # 调整图标的大小以适应单元格
            icon_width = icon.width()
            icon_height = icon.height()
            icon = icon.scaled(
                icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )  # 调整图标大小

            # 将icon绘制到中心位置
            painter.drawPixmap(
                icon_x - icon.width() // 2, icon_y - icon.height() // 2, icon
            )
            painter.end()
            self.refresh_display()

    def clear_icon_in_cell(self, idx, cell_x, cell_y):
        if self.grided:
            position = self.question_board_positions[idx]
            size = self.question_board_sizes[idx]
            cell_width = position[2] / size
            cell_height = position[3] / size

            painter = QPainter(self.mine_layer)
            painter.setCompositionMode(QPainter.CompositionMode_Clear)

            icon_x = position[0] + cell_x * cell_width
            icon_y = position[1] + cell_y * cell_height

            painter.eraseRect(QRectF(icon_x, icon_y, cell_width, cell_height))
            painter.end()
            self.refresh_display()

    def get_scaled_position(self, event):
        """
        根据背景图像的大小和label的大小，获取缩放后的位置
        """
        scale_width = self.background_pixmap.width() / self.label.width()
        scale_height = self.background_pixmap.height() / self.label.height()
        scaled_x = event.pos().x() * scale_width - self.cursor_size // 2
        scaled_y = event.pos().y() * scale_height - self.cursor_size // 2
        return QPoint(scaled_x, scaled_y)

    def choose_color(self):
        # Launch color dialog for user to choose color
        color = QColorDialog.getColor()
        if color.isValid():
            Canvas.pen.setColor(color)
            Canvas.color_index = -1
            Canvas.other_color = color
            # Set border color as current pen color
            palette = self.color_label.palette()
            palette.setColor(QPalette.Background, Canvas.pen.color())
            self.color_label.setPalette(palette)

    def delete_branch(self):
        self.branch.delete_branch()

    def copy_branch(self):
        self.branch.copy_branch()

    def check_branch(self):
        self.branch.check_branch()

    def toggle_drawing(self):
        Canvas.is_drawing = not Canvas.is_drawing
        if Canvas.is_drawing:
            self.label.setCursor(Qt.CrossCursor)
        else:
            self.label.setCursor(Qt.ArrowCursor)

    def reset_status(self):
        self.branch.problem.reset_finished()

    def copy_from(self, other_canvas):  ###
        self.drawing_layer = other_canvas.drawing_layer.copy()
        self.mine_layer = other_canvas.mine_layer.copy()
        palette = self.color_label.palette()
        palette.setColor(QPalette.Background, Canvas.pen.color())
        self.color_label.setPalette(palette)
        if other_canvas.branch.finished:
            self.on_toggle_button_state_changed(True)
        self.refresh_display()

    def clear_drawing_layer(self):
        self.drawing_layer.fill(Qt.transparent)
        self.refresh_display()
