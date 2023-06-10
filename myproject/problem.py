import cv2
from .utils import logprint
from .branch import Branch


class Problem:
    def __init__(self,main_window):
        self.board = None
        self.columns = None
        self.rows = None
        self.branches = []
        self.name_branches = {}
        self.image_path = None
        self.main_window = main_window
        self.branchcnt = 0

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
        name = "main_branch_{:0>2d}".format(self.branchcnt)
        main_branch = Branch(self,name=name)
        self.branchcnt += 1
        self.branches.append(main_branch)
        self.name_branches[name] = main_branch

    def update_mainwindow(self):
        self.main_window.update_branch_list()

    def delete_branch(self, branch):
        if len(self.branches) == 1:
            logprint(message="不能删除最后一个分支", level="warning")
            return
        branch_name = branch.name
        self.branches.remove(branch)
        del self.name_branches[branch_name]
        self.update_mainwindow()
        logprint(message="删除分支{}".format(branch_name), level="info")

    def copy_branch(self, branch):
        branch_name = branch.name
        new_branch_name = '{}_copy_{:0>2d}'.format(branch_name,self.branchcnt)
        self.branchcnt += 1
        new_branch = Branch(self,name=new_branch_name)
        new_branch.copy_from(branch)
        self.branches.append(new_branch)
        self.name_branches[new_branch_name] = new_branch
        self.update_mainwindow()
        logprint(message="复制分支{}为{}".format(branch_name,new_branch_name), level="info")




    def exclude_branch(self, branch):
        # 排除分支的逻辑
        pass