from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QColorDialog,
    QPushButton, QSplitter, QHBoxLayout, QCheckBox
)
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QCursor, QIcon
from PyQt5.QtCore import Qt, QPoint, QSize, QRectF
from .utils import logprint, MySplitter


class Canvas(QWidget):
    def __init__(self, branch):
        super().__init__()

        # Initialize Canvas Attributes
        self.branch = branch
        self.is_drawing = False
        self.last_point = None
        self.canvas_height = 800
        self.canvas_width = 1200
        self.pen = QPen(Qt.red, 5)
        self.eraser = QPen(Qt.transparent, 20)
        self.finished = False

        image_path = self.branch.problem.image_path
        background_pixmap = QPixmap(image_path)
        self.background_pixmap = background_pixmap.scaled(self.canvas_width, self.canvas_height)
        self.image_height = background_pixmap.height()
        self.image_width = background_pixmap.width()

        # logprint(f"Image Size: {self.image_width} x {self.image_height}")
        # logprint(f"Canvas Size: {self.canvas_width} x {self.canvas_height}")

        position = self.branch.problem.large_square_position
        self.large_square_position = [
            round(position[0] * self.canvas_width / self.image_width),
            round(position[1] * self.canvas_height / self.image_height),
            round(position[2] * self.canvas_width / self.image_width),
            round(position[3] * self.canvas_height / self.image_height)
        ]

        self.estimated_n = self.branch.problem.estimated_n
        self.safe_icon = QIcon("img/safe.png").pixmap(QSize(100, 100))
        self.mine_icon = QIcon("img/mine.png").pixmap(QSize(100, 100))
        self.choose_icon = QIcon("img/choose.png").pixmap(QSize(100, 100))

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
        elif event.key() == Qt.Key_Delete:
            self.delete_branch()
        elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.on_toggle_button_state_changed(not self.finished)
        elif event.key() == Qt.Key_N:
            self.reset_status()
        elif event.key() == Qt.Key_Up:
            new_idx = self.branch.problem.main_window.branch_list.currentRow()-1
            if new_idx == -1:
                new_idx = len(self.branch.problem.main_window.branch_list)-1
            self.branch.problem.main_window.update_branch_list(new_idx)
        elif event.key() == Qt.Key_Down:
            new_idx = self.branch.problem.main_window.branch_list.currentRow()+1
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


        # 创建一个QCheckBox
        self.toggle_button = QCheckBox("未完成", self)

        # 将状态切换的槽函数连接到QCheckBox的状态变化信号
        self.toggle_button.stateChanged.connect(self.on_toggle_button_state_changed)

        button_layout.addWidget(self.toggle_button)

        # 添加颜色选择按钮
        color_buttons_info = [
            ('cyan', '#00FFFF'),
            ('orange', '#FFA600'),
            ('lime', '#00FF00'),
            ('yellow', '#FFFF00'),
            ('red', '#FF0000'),
            ('blue', '#0000FF'),
            ('purple', '#A121F0'),
            ('white', '#FFFFFF')
        ]

        # 创建颜色选择按钮
        for color_name, color_code in color_buttons_info:
            color_button = QPushButton(self)
            color_button.setStyleSheet(f'background-color: {color_code}')
            # color_button.setMaximumWidth(20)  # 设置按钮宽度
            # color_button.setMaximumHeight(20) # 设置按钮高度
            button_layout.addWidget(color_button)
            color_button.clicked.connect(lambda _, color=color_code: self.set_color(color))


        # Create Buttons
        buttons_info = [
            ('Reset Status', self.reset_status),
            ('Toggle Drawing', self.toggle_drawing),
            ('Choose Other Color', self.choose_color),
            ('Delete Branch', self.delete_branch),
            ('Copy Branch', self.copy_branch),
            ('Check Branch', self.check_branch)
        ]

        for text, callback in buttons_info:
            button = QPushButton(text, self)
            button_layout.addWidget(button)
            button.clicked.connect(callback)

        # Set border color as current pen color
        self.label.setStyleSheet(f"border: 4px solid {self.pen.color().name()};")

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
        combined_pixmap= self.background_pixmap.copy()
        painter= QPainter(combined_pixmap)
        painter.drawPixmap(0, 0, self.mine_layer)
        painter.drawPixmap(0, 0, self.drawing_layer)
        painter.end()
        self.label.setPixmap(combined_pixmap)
        self.setFocus()
        # self.label.setPixmap(self.mine_layer)

    def on_toggle_button_state_changed(self, state):
        # 根据QCheckBox的状态更新显示的文本
        if state:
            self.toggle_button.setText("已完成")
            self.toggle_button.setChecked(True)
            self.finished = True
        else:
            self.finished = False
            self.toggle_button.setText("未完成")
            self.toggle_button.setChecked(False)
        self.branch.problem.main_window.update_branch_list(-2)
        self.setFocus()

    # 设置画笔颜色的函数
    def set_color(self, color_code):
        color = QColor(color_code)
        self.pen.setColor(color)
        self.label.setStyleSheet(f"border: 4px solid {color.name()};")

    def mouseMoveEvent(self, event):
        # 如果正在画图且移动的是鼠标左键
        # logprint(message=f"Canvas size: {self.label.size()}", level="debug")
        # logprint(
        #     message=f"Drawing layer size: {self.drawing_layer.size()}", level="debug")
        # logprint(
        #     message=f"background_pixmap size: {self.background_pixmap.size()}", level="debug")

        now_pos = self.get_scaled_position(event)
        painter= QPainter(self.drawing_layer)

        if self.is_drawing:
            if event.buttons() & Qt.LeftButton and self.last_point is not None:
                painter.setPen(self.pen)
                painter.drawLine(self.last_point, now_pos)
            elif event.buttons() & Qt.RightButton and self.last_point is not None:  # 检测是否按下右键
                painter.setCompositionMode(
                    QPainter.CompositionMode_Clear)  # 设置为擦除模式
                painter.setPen(self.eraser)
                painter.drawLine(self.last_point, now_pos)

        self.last_point= now_pos
        painter.end()

        self.refresh_display()

    def init_grid(self):
        # Calculate grid dimensions
        width = self.large_square_position[2]
        height = self.large_square_position[3]
        x1 = self.large_square_position[0]
        y1 = self.large_square_position[1]
        x2 = x1 + width
        y2 = y1 + height

        # logprint(f"width: {width}, height: {height}", level="debug")

        # Set the number of rows and columns for the n*n grid
        n = self.estimated_n

        # Create QPixmap object
        pixmap = self.background_pixmap

        # Create QPainter object
        painter = QPainter(pixmap)

        # Create and set QPen object
        pen = QPen(Qt.blue)  # Set color
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
            self.last_point = QPoint(
                event.pos().x() * scale_w - self.cursor_size // 2,
                event.pos().y() * scale_h - self.cursor_size // 2
            )
    def mouseReleaseEvent(self, event):

        # Clear the last point position
        if event.button() in (Qt.LeftButton, Qt.RightButton, Qt.MiddleButton):

            self.last_point = None
            if not self.is_drawing:
                now_pos = self.get_scaled_position(event)
                x1, y1, x2, y2 = self.large_square_position[0], self.large_square_position[1], self.large_square_position[0] + self.large_square_position[2], self.large_square_position[1] + self.large_square_position[3]

                if x1 <= now_pos.x() <= x2 and y1 <= now_pos.y() <= y2:

                    # 计算每个单元格的宽度和高度
                    cell_width = (x2 - x1) / self.estimated_n
                    cell_height = (y2 - y1) / self.estimated_n

                    # 计算now_pos坐标相对于矩形(x1, y1, x2, y2)的位置
                    relative_x = now_pos.x() - x1
                    relative_y = now_pos.y() - y1

                    # 计算now_pos坐标落在哪个单元格内
                    cell_x = int(relative_x // cell_width)
                    cell_y = int(relative_y // cell_height)

                    if event.button() == Qt.LeftButton:
                        self.branch.mark_safe(cell_x, cell_y)
                    elif event.button() == Qt.RightButton:
                        self.branch.mark_mine(cell_x, cell_y)
                    elif event.button() == Qt.MiddleButton:
                        self.branch.middle_click(cell_x, cell_y)

    def draw_icon_in_cell(self, cell_x, cell_y, icon):
        # 计算每个单元格的宽度和高度
        cell_width = self.large_square_position[2] / self.estimated_n
        cell_height = self.large_square_position[3] / self.estimated_n

        # 计算icon的中心坐标
        icon_x = self.large_square_position[0] + cell_x * cell_width + cell_width / 2
        icon_y = self.large_square_position[1] + cell_y * cell_height + cell_height / 2

        # 创建一个 QPainter 对象
        painter = QPainter(self.mine_layer)

        # 将icon绘制到中心位置，假设icon的大小为 icon_size x icon_size
        icon_size = min(cell_width, cell_height) * 1.3  # 调整图标的大小以适应单元格
        icon = icon.scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # 调整图标大小

        # 将icon绘制到中心位置
        painter.drawPixmap(icon_x - icon_size / 2, icon_y - icon_size / 2, icon)
        painter.end()
        self.refresh_display()

    def clear_icon_in_cell(self, cell_x, cell_y):
        # 计算每个单元格的宽度和高度
        cell_width = self.large_square_position[2] / self.estimated_n
        cell_height = self.large_square_position[3] / self.estimated_n

        # 创建一个 QPainter 对象
        painter = QPainter(self.mine_layer)

        # 设置composition mode为清除模式
        painter.setCompositionMode(QPainter.CompositionMode_Clear)

        # 计算icon的区域
        icon_x = self.large_square_position[0] + cell_x * cell_width
        icon_y = self.large_square_position[1] + cell_y * cell_height

        # 使用eraseRect删除这个区域
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
            self.pen.setColor(color)
            # Set border color as current pen color
            self.label.setStyleSheet(f"border: 4px solid {color.name()};")

    def delete_branch(self):
        self.branch.delete_branch()

    def copy_branch(self):
        self.branch.copy_branch()

    def check_branch(self):
        self.branch.check_branch()

    def toggle_drawing(self):
        self.is_drawing = not self.is_drawing
        if self.is_drawing:
            self.label.setCursor(Qt.CrossCursor)
        else:
            self.label.setCursor(Qt.ArrowCursor)

    def reset_status(self):
        self.branch.problem.reset_finished()

    def copy_from(self, other_canvas):
        self.drawing_layer = other_canvas.drawing_layer.copy()
        self.mine_layer = other_canvas.mine_layer.copy()
        self.pen = other_canvas.pen
        if other_canvas.is_drawing:
            self.toggle_drawing()
        self.eraser = other_canvas.eraser
        self.label.setStyleSheet(f"border: 4px solid {self.pen.color().name()};")
        if other_canvas.finished:
            self.on_toggle_button_state_changed(True)
        self.refresh_display()

    def clear_drawing_layer(self):
        self.drawing_layer.fill(Qt.transparent)
        self.refresh_display()