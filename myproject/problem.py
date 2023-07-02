import cv2
from .utils import logprint, detect_squares
from .branch import Branch
import numpy as np
from PyQt5.QtGui import QPixmap


class Problem:
    def __init__(self, main_window):
        self.columns = None
        self.rows = None
        self.branches = []
        self.name_branches = {}
        self.image_path = None
        self.main_window = main_window
        self.branch_count = 0

    def load_from_image(self, image_path):
        self.image_path = image_path
        self.background_pixmap=QPixmap(image_path)

        # Log loading image
        logprint("从图片中加载题目", "info")
        logprint(f"图片路径: {image_path}", "debug")

        # Read image and detect squares
        with open(image_path, 'rb') as f:
            file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)

        # 使用OpenCV的imdecode函数从字节解码图像
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        self.large_square_position, self.estimated_n, self.test_n_scores = detect_squares(
            image)

        # Log details
        # logprint(f"Large Square Position: {self.large_square_position}", "debug")
        logprint(f"Estimated n: {self.estimated_n}", "debug")
        logprint(f"n scores: {self.test_n_scores}", "debug")
        logprint(
            message=f"加载题目完成，尺寸={self.estimated_n}x{self.estimated_n}", level="info")

        # Initialize main branch
        self.columns = self.estimated_n
        self.rows = self.estimated_n
        logprint("初始化主分支", "info")
        self._create_new_branch()

    def update_mainwindow(self, new_idx=-1):
        self.main_window.update_branch_list(new_idx)

    def delete_branch(self, branch):
        # Ensure there is more than one branch before deletion
        if len(self.branches) <= 1:
            logprint("不能删除最后一个分支", "warning")
            return

        branch_idx = self.branches.index(branch)
        branch_name = branch.name
        self.branches.remove(branch)
        del self.name_branches[branch_name]

        branch_idx = min(branch_idx, len(self.branches)-1)

        # Update main window and log deletion
        self.update_mainwindow(branch_idx)
        logprint(f"删除分支{branch_name}", "info")

    def copy_branch(self, branch):
        # Create a new branch and copy data from the existing branch
        # Not create new branch to the bottom, but right below
        new_branch = self._create_new_branch(branch.index_in_list()+1)
        new_branch.copy_from(branch)

        branch_idx = self.branches.index(branch)
        # Update main window and log the copy
        self.update_mainwindow(branch_idx)
        logprint(f"复制分支{branch.name}为{new_branch.name}", "info")


    def _create_new_branch(self,idx=-1):
        # Private method to create a new branch and add to the lists
        branch_name = f"{self.branch_count:02}"
        branch = Branch(self, name=branch_name)
        self.branch_count += 1
        if idx == -1:
            self.branches.append(branch)
        else:
            self.branches.insert(idx, branch)
        self.name_branches[branch_name] = branch
        return branch

    def middle_click(self, branch, col, row):
        branch.canvas.copy_branch()
        branch.canvas.copy_branch()
        idx=branch.index_in_list()
        branch_mine = self.branches[idx+1]
        branch_safe = self.branches[idx+2]
        branch_mine.mark_mine(col, row)
        branch_safe.mark_safe(col, row)
        branch.canvas.delete_branch()
        self.update_mainwindow(idx)

    def reset_finished(self):
        for branch in self.branches:
            if branch.canvas.finished:
                branch.canvas.on_toggle_button_state_changed(False)