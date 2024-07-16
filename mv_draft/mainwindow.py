# 需求：可以放3个按钮，表示“已讨论完“

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFileDialog,
    QListWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSizePolicy,
    QSplitter,
    QAction,
    QLabel,
    QMenuBar,
    QSplitterHandle,
    QPushButton,
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
import sys
from .problem import Problem
from .utils import *
from .canvas import Canvas


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.problem = None
        self.init_ui()

    def init_ui(self):
        self.initialize_window()
        self.create_central_widget()
        self.create_menu_bar()
        self.setWindowIcon(QIcon("img/icon.png"))

    def initialize_window(self):
        # 设置窗口的标题和大小
        self.setWindowTitle("小文の14mv草稿")
        self.setGeometry(0, 0, 2560, 1500)
        self.showMaximized()

    def create_central_widget(self):
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("qproperty-focusPolicy: NoFocus;")
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout()
        self.splitter = MySplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)
        self.splitter.setHandleWidth(4)
        self.splitter.setStyleSheet("QSplitter::handle { background-color: pink }")

        self.branch_list = QListWidget()
        self.splitter.addWidget(self.branch_list)
        self.branch_list.itemClicked.connect(self.on_branch_selected)

        self.default_background_layout = QVBoxLayout()

        self.default_background_label = QLabel(self)
        pixmap = QPixmap("img/bg.png")
        self.default_background_label.setPixmap(pixmap)
        self.default_background_label.setScaledContents(True)
        self.default_background_label.setFixedSize(pixmap.size())

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.default_background_label.setSizePolicy(sizePolicy)

        self.reference_website = r"https://www.bilibili.com/opus/755321637587386404"

        self.bg_reference_label = QLabel()
        self.bg_reference_label.setText(
            f"<font size=80>图片作者：B站 @墨鱼鱼鱼鱼<br /><br />{self.reference_website} </font>"
        )

        self.reference_copy_button = QPushButton()
        self.reference_copy_button.setText("点击复制链接")
        self.reference_copy_button.setStyleSheet("font-size: 80px;")

        def on_reference_copy_clicked():
            QApplication.clipboard().setText(self.reference_website)

        self.reference_copy_button.clicked.connect(on_reference_copy_clicked)

        self.main_layout.addLayout(self.default_background_layout)
        self.splitter.setSizes([20, 1100])
        self.default_background_layout.addWidget(self.default_background_label)
        self.default_background_layout.addWidget(self.bg_reference_label)
        self.default_background_layout.addWidget(self.reference_copy_button)

        self.central_widget.setLayout(self.main_layout)

    def create_menu_bar(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("font-size: 170px;")

        file_menu = menubar.addMenu("File")

        import_action = QAction("Import", self)
        import_action.triggered.connect(self.on_import_clicked)
        file_menu.addAction(import_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.on_exit_clicked)
        file_menu.addAction(exit_action)

    def replace_canvas(self, new_canvas):
        if hasattr(self, "canvas"):
            self.canvas.setParent(None)
        if hasattr(self, "default_background_layout"):
            self.default_background_layout.setParent(None)

            self.default_background_label.setParent(None)
            self.bg_reference_label.setParent(None)
            self.reference_copy_button.setParent(None)
        self.canvas = new_canvas
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.splitter.insertWidget(1, self.canvas)
        self.splitter.setSizes([50, 1100])

        Canvas.is_drawing = not Canvas.is_drawing
        self.canvas.toggle_drawing()  # 再触发一次反转
        self.canvas.set_color(Canvas.color_index)

        self.canvas.setFocus()

    def on_import_clicked(self):
        if hasattr(self, "problem"):
            self.problem = None
            logprint("Deleted old problem", "info")

        image_path = QFileDialog.getOpenFileName(self, "Load Image")[0]
        if image_path:
            self.from_image_path(image_path)

    # puphich: on_import_no_grid_clicked

    def from_image_path(self, image_path, grid="auto"):
        self.problem = Problem(self)
        self.problem.load_from_image(image_path, grid)
        self.branch_list.addItem(self.problem.branches[0].name)
        self.replace_canvas(self.problem.branches[0].canvas)
        self.update_branch_list()

    def on_branch_selected(self, item):
        selected_branch_name = item.text()[:3]
        for branch in self.problem.branches:
            if branch.name == selected_branch_name:
                self.replace_canvas(branch.canvas)
                break

    def on_exit_clicked(self):
        QApplication.quit()

    def update_branch_list(self, new_idx=-1):
        if new_idx == -1:
            new_idx = 0
        elif new_idx == -2:
            new_idx = self.branch_list.currentRow()

        self.branch_list.clear()
        for branch in self.problem.branches:
            self.branch_list.addItem(branch.name + ("√" if branch.finished else ""))

        self.branch_list.setCurrentRow(new_idx)
        self.replace_canvas(self.problem.branches[new_idx].canvas)
