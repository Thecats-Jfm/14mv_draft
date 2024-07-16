import cv2
from .utils import logprint, detect_squares
from .branch import Branch
import numpy as np
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QInputDialog
from copy import deepcopy


class Problem:
    def __init__(self, main_window):
        self.branches = []
        self.name_branches = {}
        self.image_path = None
        self.main_window = main_window
        self.branch_count = 0
        self.question_board_cnt = 0
        self.question_board_positions = []
        self.question_board_sizes = []

    def load_from_image(self, image_path, grid="auto"):
        """grid: auto; no_grid; manual"""
        self.image_path = image_path
        self.background_pixmap = QPixmap(image_path)

        # Log loading image
        logprint("从图片中加载题目", "info")
        logprint(f"图片路径: {image_path}", "debug")

        if grid == "auto":
            # Read image and detect squares
            with open(image_path, "rb") as f:
                file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)

            # 使用OpenCV的imdecode函数从字节解码图像
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            (
                self.question_board_positions,
                self.question_board_sizes,
                self.test_scores,
            ) = detect_squares(image)
            self.question_board_size0 = self.question_board_sizes[0]
            # Log details
            # logprint(f"Large Square Position: {self.large_square_position}", "debug")
            logprint(f"Estimated n: {self.question_board_size0}", "debug")
            logprint(f"n scores: {self.test_scores}", "debug")
            logprint(
                f"Number of squares: {len(self.question_board_positions)}", "debug"
            )
            logprint(
                message=f"加载题目完成，尺寸={self.question_board_size0}x{self.question_board_size0},题板数量={len(self.question_board_positions)}",
                level="info",
            )

        elif grid == "no_grid":
            self.question_board_size0 = 0
            self.test_n_scores = []
            self.large_square_position = None
            logprint("加载题目完成，无网格", "info")
        elif grid == "manual":
            logprint("暂未实现手动网格", "warning")
            # temp
            text, ok = QInputDialog.getText(None, "Input Dialog", "n:")
            self.question_board_size0 = int(text)
            self.large_square_position = (
                629,
                654,
                491 * self.question_board_size0 // 7,
                515 * self.question_board_size0 // 7,
            )

        # Initialize main branch
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

        branch_idx = min(branch_idx, len(self.branches) - 1)

        # Update main window and log deletion
        self.update_mainwindow(branch_idx)
        logprint(f"删除分支{branch_name}", "info")

    def copy_branch(self, branch):
        # Create a new branch and copy data from the existing branch
        # Not create new branch to the bottom, but right below
        # print(branch.index_in_list())
        print(branch)
        print(branch.name)
        new_branch_name = self._create_new_branch(branch.index_in_list() + 1)
        self.name_branches[new_branch_name].copy_from(branch)

        branch_idx = self.branches.index(branch)

        # Update main window and log the copy
        self.update_mainwindow(branch_idx)

        logprint(f"复制分支{branch}为{self.name_branches[new_branch_name]}", "info")

    def _create_new_branch(self, idx=-1):
        # Private method to create a new branch and add to the lists
        branch_name = f"{self.branch_count:03}"
        branch = Branch(self, name=branch_name)
        self.branch_count += 1
        if idx == -1:
            self.branches.append(branch)
        else:
            self.branches.insert(idx, branch)
        self.name_branches[branch_name] = branch
        return branch_name

    def middle_click(self, branch, board_idx, col, row, idx=0):
        self.copy_branch(branch)
        self.copy_branch(branch)
        idx = branch.index_in_list()
        branch_mine = self.branches[idx + 1]
        branch_safe = self.branches[idx + 2]
        branch_mine.mark_mine(board_idx, col, row)
        branch_safe.mark_safe(board_idx, col, row)
        self.delete_branch(branch)
        self.update_mainwindow(idx)

    def reset_finished(self):
        for branch in self.branches:
            if branch.canvas.finished:
                branch.canvas.on_toggle_button_state_changed(False)
