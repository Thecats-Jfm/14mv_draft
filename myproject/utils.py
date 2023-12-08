from collections import defaultdict
import cv2
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QFileDialog, QListWidget, QHBoxLayout,
                             QSizePolicy, QSplitter, QAction, QLabel, QMenuBar, QSplitterHandle)

# 配置日志记录器
logging.basicConfig(level=logging.DEBUG,  # 设置日志级别为DEBUG
                    format='%(asctime)s [%(levelname)s] %(message)s',  # 设置日志格式
                    datefmt='%Y-%m-%d %H:%M:%S')  # 设置日期格式

class MySplitterHandle(QSplitterHandle):
    def __init__(self, orientation, splitter):
        super(MySplitterHandle, self).__init__(orientation, splitter)

    def mouseMoveEvent(self, event):
        pass

    def mousePressEvent(self, event):
        pass

class MySplitter(QSplitter):
    def __init__(self, orientation):
        super(MySplitter, self).__init__(orientation)

    def createHandle(self):
        return MySplitterHandle(self.orientation(), self)

def logprint(message, level="info"):
    """
    打印日志信息
    :param message: 日志信息内容
    :param level: 日志级别 ("debug", "info", "warning", "error", "critical")
    """
    if level.lower() == "debug":
        logging.debug(message)
    elif level.lower() == "info":
        logging.info(message)
    elif level.lower() == "warning":
        logging.warning(message)
    elif level.lower() == "error":
        logging.error(message)
    elif level.lower() == "critical":
        logging.critical(message)
    else:
        logging.info(message)


def argmax(dic):
    return max(dic, key=dic.get)

def detect_squares(image):
    # 转换为灰度图像
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #二值化

    # #默认配色
    # _, binary_image = cv2.threshold(
    #     gray_image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

    # 粉白配色
    _, binary_image = cv2.threshold(
        gray_image, 210, 255, cv2.THRESH_BINARY)
    
    if __name__ == "__main__":
        # 显示图像
        cv2.imshow('gray_image', gray_image)

        # 等待按键然后关闭窗口
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        # 显示图像
        cv2.imshow('binary image', binary_image)

        # 等待按键然后关闭窗口
        cv2.waitKey(0)
        cv2.destroyAllWindows() 

    # 查找轮廓
    contours, _ = cv2.findContours(
        binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 找到最大的正方形
    max_area = 0
    largest_square_contour = None

    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        approx_polygon = cv2.approxPolyDP(contour, 0.04 * perimeter, True)

        if len(approx_polygon) == 4:
            x, y, w, h = cv2.boundingRect(contour)
            if x < 1 or y < 1 or x + w > image.shape[1] - 1 or y + h > image.shape[0] - 1:
                continue

            area = w * h
            if area > max_area:
                max_area = area
                largest_square_contour = approx_polygon

    # 计算大正方形的位置和大小
    x, y, w, h = cv2.boundingRect(largest_square_contour)
    large_square_position = (x + 1, y + 1, w - 2, h - 2)

    # 收集正方形区域
    square_areas = []
    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        approx_polygon = cv2.approxPolyDP(contour, 0.04 * perimeter, True)

        if len(approx_polygon) == 4:
            x, y, w, h = cv2.boundingRect(contour)

            if large_square_position[0] < x and large_square_position[1] < y and large_square_position[0] + large_square_position[2] > x + w and large_square_position[1] + large_square_position[3] > y + h:
                area = w * h
                if area < 100:
                    continue
                square_areas.append(area)

    # 估计n的值
    test_n_scores = defaultdict(int)
    large_square_area = large_square_position[2] * large_square_position[3]

    for n in range(5, 9):
        mean_area = large_square_area / (n ** 2)
        score = 0
        for area in square_areas:
            score -= abs(area - mean_area) / (area + mean_area)
        test_n_scores[n] = score

    estimated_n = argmax(test_n_scores)

    return large_square_position, estimated_n, test_n_scores

if __name__ == "__main__":
    app=QApplication([])
    # 加载图像
    image_path = QFileDialog.getOpenFileName(QMainWindow(), 'Open file', r'D:\github\14mv_draft\img')[0]
    image = cv2.imread(image_path)

    # 检测正方形
    large_square_position, estimated_n, test_n_scores = detect_squares(image)

    # 输出结果
    print("Large Square Position:", large_square_position)
    print("Estimated n:", estimated_n)
    print("n scores:", test_n_scores)

    # 可视化结果
    x, y, w, h = large_square_position
    small_square_width = w // estimated_n
    small_square_height = h // estimated_n

    for row in range(estimated_n):
        for col in range(estimated_n):
            top_left_x = x + col * small_square_width
            top_left_y = y + row * small_square_height
            bottom_right_x = top_left_x + small_square_width
            bottom_right_y = top_left_y + small_square_height

            cv2.rectangle(image, (top_left_x, top_left_y),
                        (bottom_right_x, bottom_right_y), (0, 255, 255), 2)
            cv2.putText(image, f"({row},{col})", (top_left_x, top_left_y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # 显示图像
    cv2.imshow('Detected Squares', image)

    # 等待按键然后关闭窗口
    cv2.waitKey(0)
    cv2.destroyAllWindows()
