import unittest
from PyQt5.QtWidgets import QApplication
from myproject.window import MyWindow

app = QApplication([])

class TestMyWindow(unittest.TestCase):
    def test_init(self):
        window = MyWindow()
        self.assertEqual(window.title, "My Window")

if __name__ == "__main__":
    unittest.main()
