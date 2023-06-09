import cv2
from .utils import logprint
from .branch import Branch


class Problem:
    def __init__(self):
        self.board = None
        self.columns = None
        self.rows = None
        self.branches = []
        self.image_path = None

    def load_from_image(self, image_path='./img/5x5.png'):
        self.image_path = image_path
        
        logprint(message="从图片中加载题目", level="info")
        # 1. 读取图片
        image = cv2.imread(image_path)

        logprint(message="set board size to 5x5", level="info")
        self.columns = 5
        self.rows = 5

        # 2. 使用OpenCV从图片中提取题版区域
        # board_area = image[100:500, 100:500]
        board_area = image[:, :]

        # 3. 将识别的字符串转换为二维数组
        self.board = [[0] * self.columns for _ in range(self.rows)]

        # 初始化主分支
        logprint(message="初始化主分支", level="info")
        main_branch = Branch(self)
        self.branches.append(main_branch)

    def show(self):
        logprint(message="Problem调用主分支显示", level="debug")
        self.branches[0].show()




    def exclude_branch(self, branch):
        # 排除分支的逻辑
        pass