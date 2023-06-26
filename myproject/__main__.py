from .mainwindow import MainWindow
from PyQt5.QtWidgets import QApplication
from PIL import ImageGrab
import sys, os, datetime

def main():
    app = QApplication(sys.argv)
    
    if 'from_screen' in sys.argv:
        now = datetime.datetime.now()
        folder_path = r'C:\Users\19000\OneDrive - 北京大学\图片\屏幕截图'
        screenshot = ImageGrab.grab()
        screenshot.save(rf'C:\Users\19000\OneDrive - 北京大学\图片\屏幕截图\屏幕截图 {now.strftime("%Y-%m-%d %H%M%S")}.png')
        files = os.listdir(folder_path)
        paths = [os.path.join(folder_path, file) for file in files]
        latest_file = max(paths, key=os.path.getctime)

        main_window = MainWindow()
        main_window.from_image_path(latest_file)
    else:
        main_window = MainWindow()

    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
