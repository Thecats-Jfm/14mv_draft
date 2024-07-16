from .canvas import Canvas
from .utils import logprint
import numpy as np
from copy import deepcopy


class QuestionBoard:
    def __init__(self, idx, n, branch):
        self.n = n
        self.mines = [[False for _ in range(n)] for _ in range(n)]
        self.safe = [[False for _ in range(n)] for _ in range(n)]
        self.idx = idx
        self.branch = branch

    def mark_mine(self, row, col):
        # 在指定位置标记雷
        if self.safe[row][col] == True:
            logprint(f"({row},{col})已经标记为非雷，不能标记为雷", "warning")
            return
        if self.mines[row][col] == True:
            self.mines[row][col] = False
            self.branch.clear_icon_in_cell(self.idx, row, col)
            # logprint(f"({row},{col})已经标记为雷，取消标记","debug")
            return
        if self.mines[row][col] == False:
            self.mines[row][col] = True
            self.branch.draw_icon_in_cell(self.idx, row, col, "mine")
            # logprint(f"({row},{col})标记为雷","debug")
            return

    def mark_safe(self, row, col):
        # 在指定位置标记非雷
        if self.mines[row][col] == True:
            logprint(f"({row},{col})已经标记为雷，不能标记为非雷", "warning")
            return
        if self.safe[row][col] == True:
            self.safe[row][col] = False
            self.branch.clear_icon_in_cell(self.idx, row, col)
            # logprint(f"({row},{col})已经标记为非雷，取消标记","debug")
            return
        if self.safe[row][col] == False:
            self.safe[row][col] = True
            self.branch.draw_icon_in_cell(self.idx, row, col, "safe")
            # logprint(f"({row},{col})标记为非雷","debug")
            return

    def middle_click(self, row, col):
        if self.mines[row][col] or self.safe[row][col]:
            logprint(f"({row},{col})已被标记，无法创建分支", "warning")
            return
        self.branch.problem.middle_click(self.branch, self.idx, row, col)

    def copy_from(self, qb):
        self.mines = deepcopy(qb.mines)
        self.safe = deepcopy(qb.safe)


class Branch:
    def __init__(self, problem, name: str):
        self.problem = problem
        self.question_board_cnt = problem.question_board_cnt
        self.name = name
        self.question_board_positions = problem.question_board_positions
        self.question_board_sizes = problem.question_board_sizes
        self.question_boards = [
            QuestionBoard(i, n, self) for i, n in enumerate(self.question_board_sizes)
        ]
        self.finished = False

        self.canvas = Canvas(self)

    def draw_icon_in_cell(self, idx, cell_x, cell_y, icon):
        if idx == 0:
            if icon == "mine":
                icon = self.canvas.mine_icon
            elif icon == "safe":
                icon = self.canvas.safe_icon
        elif idx == 1:
            if icon == "mine":
                icon = self.canvas.circle_icon
            elif icon == "safe":
                icon = self.canvas.cross_icon
        self.canvas.draw_icon_in_cell(idx, cell_x, cell_y, icon)

    def clear_icon_in_cell(self, idx, cell_x, cell_y):
        self.canvas.clear_icon_in_cell(idx, cell_x, cell_y)

    def cnt_flags(self):
        return np.count_nonzero(self.question_boards[0].mines)

    def cnt_safes(self):
        return np.count_nonzero(self.question_boards[0].safe)

    def mark_mine(self, idx, row, col):
        return self.question_boards[idx].mark_mine(row, col)

    def mark_safe(self, idx, row, col):
        return self.question_boards[idx].mark_safe(row, col)

    def middle_click(self, idx, row, col):
        return self.question_boards[idx].middle_click(row, col)

    def delete_branch(self):
        self.problem.delete_branch(self)

    def copy_branch(self):
        self.problem.copy_branch(self)

    def check_branch(self):
        flag = True

        for idx, qb in enumerate(self.question_boards):

            all_is_mine = [row[:] for row in qb.mines]
            all_is_safe = [row[:] for row in qb.safe]
            for branch in self.problem.branches:
                mine_temp = [row[:] for row in branch.question_boards[idx].mines]
                safe = [row[:] for row in branch.question_boards[idx].safe]
                for i in range(qb.n):
                    for j in range(qb.n):
                        all_is_mine[i][j] &= mine_temp[i][j]
                        all_is_safe[i][j] &= safe[i][j]

            for i in range(qb.n):
                for j in range(qb.n):
                    if all_is_mine[i][j]:
                        self.canvas.draw_icon_in_cell(
                            idx, i, j, self.canvas.choose_icon
                        )
                        flag = False
                        # logprint(f"({i},{j})是雷", "info")
                    elif all_is_safe[i][j]:
                        self.canvas.draw_icon_in_cell(
                            idx, i, j, self.canvas.choose_icon
                        )
                        flag = False
                        # logprint(f"({i},{j})是非雷", "info")
        if flag:
            logprint("未找到确定的解", level="info")

    def copy_from(self, branch):
        self.finished = branch.finished
        for i, qb in enumerate(self.question_boards):
            qb.copy_from(branch.question_boards[i])

        self.canvas.copy_from(branch.canvas)

    def index_in_list(self):
        for ret in range(len(self.problem.branches)):
            if self.problem.branches[ret] is self:
                return ret
        return -1  # Not in list

    def __str__(self):
        return self.name
