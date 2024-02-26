from .mainwindow import MainWindow
from PyQt5.QtWidgets import QApplication
from PIL import ImageGrab
import sys, os, datetime

def main():
    args = parse_args()

    app = QApplication(sys.argv)

    if args.from_screen:
        grid = "auto"
        if args.no_grid:
            grid = "no_grid"
        elif args.manual:
            grid = "manual"

        now = datetime.datetime.now()
        folder_path = r'C:\Users\19000\OneDrive - 北京大学\图片\屏幕截图'
        screenshot = ImageGrab.grab()
        screenshot_file_name = rf'屏幕截图 {now.strftime("%Y-%m-%d %H%M%S")}.png'
        screenshot_path = os.path.join(folder_path, screenshot_file_name)
        screenshot.save(screenshot_path)
        latest_file = screenshot_path

        main_window = MainWindow()
        main_window.from_image_path(latest_file, grid)
    else:
        main_window = MainWindow()

    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
