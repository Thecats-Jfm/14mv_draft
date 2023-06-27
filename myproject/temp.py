from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QColor

app = QApplication([])
window = QWidget()

label = QLabel('This text has <font color="red">red</font> and <font color="blue">blue</font> words.')
label.show()

app.exec_()