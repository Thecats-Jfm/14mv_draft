from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
import random

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'My Window'
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            self.setStyleSheet("background-color: %s" % color.name())
        elif event.button() == Qt.RightButton:
            self.close()
