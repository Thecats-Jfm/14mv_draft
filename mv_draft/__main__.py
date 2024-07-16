from mv_draft.mainwindow import MainWindow
from PyQt5.QtWidgets import QApplication
from PIL import ImageGrab
import sys, os, datetime
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Capture and process a screenshot.")
    parser.add_argument(
        "--from_screen", action="store_true", help="Capture screenshot from screen."
    )
    parser.add_argument(
        "--grid",
        default="auto",
        choices=["auto", "no_grid", "manual"],
        help="Grid mode: auto (default), no_grid, or manual.",
    )
    parser.add_argument(
        "--from_file", nargs="?", type = str, help="Load screenshot from file.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    app = QApplication(sys.argv)

    if args.from_screen:
        now = datetime.datetime.now()
        folder_path = r"C:\Users\19000\OneDrive - 北京大学\图片\屏幕截图"
        screenshot = ImageGrab.grab()
        screenshot_file_name = rf'屏幕截图 {now.strftime("%Y-%m-%d %H%M%S")}.png'
        screenshot_path = os.path.join(folder_path, screenshot_file_name)
        screenshot.save(screenshot_path)
        latest_file = screenshot_path

        main_window = MainWindow()
        main_window.from_image_path(latest_file, args.grid)

    elif args.from_file:
        main_window = MainWindow()
        main_window.from_image_path(args.from_file, args.grid)
    else:
        main_window = MainWindow()

    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
