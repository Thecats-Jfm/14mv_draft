from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QWidget, QFileDialog, QListWidget, QHBoxLayout,
                             QMenuBar, QAction, QLabel, QSlider, QToolBar, QSizePolicy, QSplitter)
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
        # 设置窗口的标题和大小
        self.setWindowTitle('小文の14mv草稿')
        self.setGeometry(300, 300, 1920, 1080)

        # 创建一个QWidget作为窗口的中心小部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 创建主布局
        self.main_layout = QHBoxLayout()

        # 创建QSplitter控件
        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)
        self.splitter.setHandleWidth(4)  # 设置分隔线的宽度
        self.splitter.setStyleSheet("QSplitter::handle { background-color: pink }")  # 设置分隔线的颜色

        # 创建左侧列表
        self.branch_list = QListWidget()
        self.splitter.addWidget(self.branch_list)
        # 连接列表项点击事件到槽函数
        self.branch_list.itemClicked.connect(self.on_branch_selected)

        # 创建中间的Canvas部分的默认背景
        self.default_background_label = QLabel(self)
        pixmap = QPixmap('img/bg.png')
        self.default_background_label.setPixmap(pixmap)
        self.default_background_label.setScaledContents(True)  # 使图像缩放以填充整个标签

        # 设置QLabel的尺寸策略
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.default_background_label.setSizePolicy(sizePolicy)

        self.splitter.addWidget(self.default_background_label)

        # 设置splitter初始大小
        self.splitter.setSizes([200, 1000])

        # 设置中心小部件的布局为刚刚创建的布局
        self.central_widget.setLayout(self.main_layout)

        # 创建菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        # 添加Import和Exit动作到文件菜单
        import_action = QAction('Import', self)
        import_action.triggered.connect(self.on_import_clicked)
        file_menu.addAction(import_action)

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.on_exit_clicked)
        file_menu.addAction(exit_action)

        # 设置窗口图标（你需要准备一个符合要求的图标文件）
        self.setWindowIcon(QIcon('img/icon.png'))

    def on_import_clicked(self):
        # 可以使用一个文件对话框来让用户选择一个图片文件
        image_path = QFileDialog.getOpenFileName(self, 'Open file', '')[0]
        if image_path:
            self.problem = Problem(self)
            self.problem.load_from_image(image_path)

            # 移除默认背景标签
            self.default_background_label.setParent(None)

            # 创建并设置新的canvas
            self.canvas = self.problem.branches[0].canvas
            self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.branch_list.addItem(self.problem.branches[0].name)

            # 在splitter的正确位置添加新的canvas
            self.splitter.insertWidget(1, self.canvas)



    def on_branch_selected(self, item):
        selected_branch_name = item.text()
        # 查找与选中项对应的branch
        for branch in self.problem.branches:
            if branch.name == selected_branch_name:
                # 移除旧的canvas
                self.canvas.setParent(None)

                # 设置当前canvas为选中branch的canvas
                self.canvas = branch.canvas
                self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

                # 在splitter的正确位置添加新的canvas
                self.splitter.insertWidget(1, self.canvas)
                break


    def on_exit_clicked(self):
        QApplication.quit()


    def update_branch_list(self):
        self.branch_list.clear()
        for branch in self.problem.branches:
            self.branch_list.addItem(branch.name)
        self.branch_list.setCurrentRow(0)
        
        self.canvas.setParent(None)

        self.canvas = self.problem.branches[0].canvas
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.splitter.insertWidget(1, self.canvas)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
