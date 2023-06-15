from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QFileDialog, QListWidget, QHBoxLayout,
                             QSizePolicy, QSplitter, QAction, QLabel, QMenuBar, QSplitterHandle)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
import sys
from .problem import Problem
from .utils import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.problem = None
        self.init_ui()

    def init_ui(self):
        self.initialize_window()
        self.create_central_widget()
        self.create_menu_bar()
        self.setWindowIcon(QIcon('img/icon.png'))

    def initialize_window(self):
        # 设置窗口的标题和大小
        self.setWindowTitle('小文の14mv草稿')
        self.setGeometry(300, 300, 1920, 1080)

    def create_central_widget(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout()
        self.splitter = MySplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)
        self.splitter.setHandleWidth(4)
        self.splitter.setStyleSheet(
            "QSplitter::handle { background-color: pink }")

        self.branch_list = QListWidget()
        self.splitter.addWidget(self.branch_list)
        self.branch_list.itemClicked.connect(self.on_branch_selected)

        self.default_background_label = QLabel(self)
        pixmap = QPixmap('img/bg.png')
        self.default_background_label.setPixmap(pixmap)
        self.default_background_label.setScaledContents(True)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.default_background_label.setSizePolicy(sizePolicy)

        self.splitter.addWidget(self.default_background_label)
        self.splitter.setSizes([20, 1100])

        self.central_widget.setLayout(self.main_layout)

    def create_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        import_action = QAction('Import', self)
        import_action.triggered.connect(self.on_import_clicked)
        file_menu.addAction(import_action)

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.on_exit_clicked)
        file_menu.addAction(exit_action)

    def replace_canvas(self, new_canvas):
        if hasattr(self, 'canvas'):
            self.canvas.setParent(None)
        if hasattr(self, 'default_background_label'):
            self.default_background_label.setParent(None)
        self.canvas = new_canvas
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.splitter.insertWidget(1, self.canvas)
        self.splitter.setSizes([50, 1100])


    def on_import_clicked(self):
        image_path = QFileDialog.getOpenFileName(self, 'Open file', '')[0]
        if image_path:
            self.problem = Problem(self)
            self.problem.load_from_image(image_path)
            self.branch_list.addItem(self.problem.branches[0].name)
            self.replace_canvas(self.problem.branches[0].canvas)

    def on_branch_selected(self, item):
        selected_branch_name = item.text()
        for branch in self.problem.branches:
            if branch.name == selected_branch_name:
                self.replace_canvas(branch.canvas)
                break

    def on_exit_clicked(self):
        QApplication.quit()

    def update_branch_list(self):
        self.branch_list.clear()
        for branch in self.problem.branches:
            self.branch_list.addItem(branch.name)
        self.branch_list.setCurrentRow(0)
        self.replace_canvas(self.problem.branches[0].canvas)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
