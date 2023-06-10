import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint


class DrawingWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 加载背景图片
        self.background = QPixmap("img/5x5.png")

        # 创建一个 QLabel 来展示背景图片
        self.label = QLabel(self)
        self.label.setPixmap(self.background)
        self.setCentralWidget(self.label)

        # 设置画笔
        self.pen = QPen(Qt.red)
        self.last_point = None

    def mouseMoveEvent(self, event):
        # 在鼠标移动时进行绘图
        if event.buttons() & Qt.LeftButton and self.last_point is not None:
            painter = QPainter(self.background)
            painter.setPen(self.pen)
            painter.drawLine(self.last_point, event.pos())
            painter.end()

            # 更新 QLabel
            self.label.setPixmap(self.background)

            # 更新最后一个点的位置
            self.last_point = event.pos()

    def mousePressEvent(self, event):
        # 记录鼠标按下时的位置
        if event.button() == Qt.LeftButton:
            self.last_point = event.pos()

    def mouseReleaseEvent(self, event):
        # 清除最后一个点的位置
        self.last_point = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DrawingWindow()
    window.show()
    sys.exit(app.exec_())
