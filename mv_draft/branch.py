from .canvas import Canvas
from .utils import logprint


class Branch:
    def __init__(self, problem, name: str):
        self.problem = problem
        self.mines = [[False] * problem.columns for _ in range(problem.rows)]
        self.safe = [[False] * problem.columns for _ in range(problem.rows)]
        self.name = name
        self.canvas = Canvas(self)

    def mark_mine(self, row, col):
        # 在指定位置标记雷
        if self.safe[row][col] == True:
            logprint(f"({row},{col})已经标记为非雷，不能标记为雷", "warning")
            return
        if self.mines[row][col] == True:
            self.mines[row][col] = False
            self.canvas.clear_icon_in_cell(row, col)
            # logprint(f"({row},{col})已经标记为雷，取消标记","debug")
            return
        if self.mines[row][col] == False:
            self.mines[row][col] = True
            self.canvas.draw_icon_in_cell(row, col, self.canvas.mine_icon)
            # logprint(f"({row},{col})标记为雷","debug")
            return

    def mark_safe(self, row, col):
        # 在指定位置标记非雷
        if self.mines[row][col] == True:
            logprint(f"({row},{col})已经标记为雷，不能标记为非雷", "warning")
            return
        if self.safe[row][col] == True:
            self.safe[row][col] = False
            self.canvas.clear_icon_in_cell(row, col)
            # logprint(f"({row},{col})已经标记为非雷，取消标记","debug")
            return
        if self.safe[row][col] == False:
            self.safe[row][col] = True
            self.canvas.draw_icon_in_cell(row, col, self.canvas.safe_icon)
            # logprint(f"({row},{col})标记为非雷","debug")
            return

    def delete_branch(self):
        self.problem.delete_branch(self)

    def copy_branch(self):
        self.problem.copy_branch(self)

    def check_branch(self):
        all_is_mine = [row[:] for row in self.mines]
        all_is_safe = [row[:] for row in self.safe]
        for branch in self.problem.branches:
            mine_temp = [row[:] for row in branch.mines]
            safe = [row[:] for row in branch.safe]
            for i in range(self.problem.rows):
                for j in range(self.problem.columns):
                    all_is_mine[i][j] &= mine_temp[i][j]
                    all_is_safe[i][j] &= safe[i][j]
        flag = True
        for i in range(self.problem.rows):
            for j in range(self.problem.columns):
                if all_is_mine[i][j]:
                    self.canvas.draw_icon_in_cell(i, j, self.canvas.choose_icon)
                    flag = False
                    logprint(f"({i},{j})是雷", "info")
                elif all_is_safe[i][j]:
                    self.canvas.draw_icon_in_cell(i, j, self.canvas.choose_icon)
                    flag = False
                    logprint(f"({i},{j})是非雷", "info")
        if flag:
            logprint("未找到确定的解", level="info")

    def middle_click(self, row, col):
        if self.mines[row][col] or self.safe[row][col]:
            logprint(f"({row},{col})已被标记，无法创建分支", "warning")
            return
        self.problem.middle_click(self, row, col)

    def copy_from(self, branch):
        self.mines = [row[:] for row in branch.mines]
        self.safe = [row[:] for row in branch.safe]
        self.canvas.copy_from(branch.canvas)

    def index_in_list(self):
        for ret in range(len(self.problem.branches)):
            if self.problem.branches[ret] is self:
                return ret
        return -1  # Not in list
