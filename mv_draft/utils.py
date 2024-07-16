from collections import defaultdict
import cv2
import logging
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFileDialog,
    QListWidget,
    QHBoxLayout,
    QSizePolicy,
    QSplitter,
    QAction,
    QLabel,
    QMenuBar,
    QSplitterHandle,
)

# 配置日志记录器
logging.basicConfig(
    level=logging.DEBUG,  # 设置日志级别为DEBUG
    format="%(asctime)s [%(levelname)s] %(message)s",  # 设置日志格式
    datefmt="%Y-%m-%d %H:%M:%S",
)  # 设置日期格式


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


def find_grids(binary_image):
    # 查找轮廓
    contours, _ = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 初始化存储两个最大正方形的面积和轮廓
    max_areas = [0, 0]
    largest_square_contours = [None, None]

    for contour in contours:
        # 计算轮廓的周长
        perimeter = cv2.arcLength(contour, True)
        # 将轮廓近似为多边形
        approx_polygon = cv2.approxPolyDP(contour, 0.04 * perimeter, True)

        # 检查多边形是否有4个顶点（是否为正方形或矩形）
        if len(approx_polygon) == 4:
            # 获取边界矩形的位置和大小
            x, y, w, h = cv2.boundingRect(contour)
            # 排除位于图像边缘的轮廓
            if x < 10 or y < 10 or x + w > binary_image.shape[1] - 10 or y + h > binary_image.shape[0] - 10:
                continue

            area = w * h
            # 更新最大正方形
            if area > max_areas[0]:
                max_areas[1] = max_areas[0]
                largest_square_contours[1] = largest_square_contours[0]
                max_areas[0] = area
                largest_square_contours[0] = approx_polygon
            elif area > max_areas[1]:
                max_areas[1] = area
                largest_square_contours[1] = approx_polygon

    # 如果只找到一个正方形，则删除第二个空元素
    if largest_square_contours[1] is None or max_areas[1] < 0.2 * max_areas[0]:
        largest_square_contours.pop()

    # 计算每个正方形的边界框
    large_square_positions = [cv2.boundingRect(contour) for contour in largest_square_contours]

    # 确保左侧的网格为1号网格，根据x坐标进行排序
    large_square_positions.sort(key=lambda pos: pos[0])

    #绘制并展示
    # for pos in large_square_positions:
        # x, y, w, h = pos
        # cv2.rectangle(binary_image, (x, y), (x + w, y + h), 200, 10)
    # cv2.imshow("binary_image", binary_image)
    # cv2.waitKey(0)

    # 返回每个网格的位置和大小
    return large_square_positions

def estimate_n(large_square_position, contours, image_shape):
    # 解压大正方形的位置和大小
    x, y, w, h = large_square_position
    # 调整大正方形的位置和大小以避开边缘
    large_square_position = (x + 1, y + 1, w - 2, h - 2)

    # 收集所有内部正方形区域的面积
    square_areas = []
    for contour in contours:
        # 计算轮廓的周长
        perimeter = cv2.arcLength(contour, True)
        # 将轮廓近似为多边形
        approx_polygon = cv2.approxPolyDP(contour, 0.04 * perimeter, True)

        # 检查多边形是否有4个顶点（是否为正方形或矩形）
        if len(approx_polygon) == 4:
            # 获取边界矩形的位置和大小
            x, y, w, h = cv2.boundingRect(contour)

            # 检查这个矩形是否在大正方形内部
            if large_square_position[0] < x and large_square_position[1] < y and \
               large_square_position[0] + large_square_position[2] > x + w and \
               large_square_position[1] + large_square_position[3] > y + h:
                area = w * h
                # 过滤掉面积小于100的区域
                if area < 100:
                    continue
                # 添加符合条件的正方形区域面积到列表
                square_areas.append(area)

    # 初始化测试不同网格大小的得分
    test_n_scores = defaultdict(int)
    # 计算大正方形的面积
    large_square_area = large_square_position[2] * large_square_position[3]

    # 遍历可能的网格大小
    for n in range(3, 9):
        # 计算每个小正方形的平均面积
        mean_area = large_square_area / (n**2)
        score = 0
        # 计算当前网格大小的得分
        for area in square_areas:
            score -= abs(area - mean_area) / (area + mean_area)
        # 存储当前网格大小的得分
        test_n_scores[n] = score

    # 选择得分最高的网格大小作为估计值
    estimated_n = max(test_n_scores, key=test_n_scores.get)

    # 返回估计的网格大小和得分
    return estimated_n, test_n_scores

def detect_squares(image, DEBUG = False):
    # DEBUG = True
    """目前只支持预设配色1与粉白配色,参见img/pink_white.png与img/set1.png"""

    # 转换为灰度图像
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    avg_gray = gray_image.mean()
    logprint(f"平均灰度值: {avg_gray}", "debug")

    if avg_gray < 100:
        # 黑底
        _, binary_image = cv2.threshold(
            gray_image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
        )
    else:
        # 白底
        _, binary_image = cv2.threshold(
            gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU
        )


    large_square_positions = find_grids(binary_image)
    contours, _ = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    n_list = []
    scores_list = []
    for pos in large_square_positions:
        n, scores = estimate_n(pos, contours, binary_image.shape)
        n_list.append(n)
        scores_list.append(scores)

    if __name__ == "__main__" or DEBUG == True:
        # 显示图像
        cv2.imshow("gray_image", gray_image)
        cv2.imshow("binary_image", binary_image)
        for pos in large_square_positions:
            x, y, w, h = pos
            cv2.rectangle(image, (x, y), (x + w, y + h), 200, 10)

        cv2.imshow("Detected Squares", image)
        print("Large Square Position:", large_square_positions)
        print("Estimated n:", n_list)
        print("n scores:", scores_list)


        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return large_square_positions, n_list, scores_list


if __name__ == "__main__":
    app = QApplication([])
    # 加载图像
    image_path = QFileDialog.getOpenFileName(
        QMainWindow(), "Open file", r"D:\github\14mv_draft\img"
    )[0]
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

            cv2.rectangle(
                image,
                (top_left_x, top_left_y),
                (bottom_right_x, bottom_right_y),
                (0, 255, 255),
                2,
            )
            cv2.putText(
                image,
                f"({row},{col})",
                (top_left_x, top_left_y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 0, 0),
                2,
            )

    # 显示图像
    cv2.imshow("Detected Squares", image)

    # 等待按键然后关闭窗口
    cv2.waitKey(0)
    cv2.destroyAllWindows()
