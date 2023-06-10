from .canvas import Canvas
from .utils import logprint

class Branch:
    def __init__(self, problem,name:str,idx=0):
        self.problem = problem
        self.mines = [[False] * problem.columns for _ in range(problem.rows)]
        self.not_mines = [[False] * problem.columns for _ in range(problem.rows)]
        self.idx = idx
        self.name = name
        self.canvas = Canvas(self)

    def mark_mine(self, row, col):
        # 在指定位置标记雷
        self.mines[row][col] = True
        self.not_mines[row][col] = False

    def mark_not_mine(self, row, col):
        # 在指定位置标记非雷
        self.not_mines[row][col] = True
        self.mines[row][col] = False

    def delete_branch(self):
        self.problem.delete_branch(self)

    def copy_branch(self):
        self.problem.copy_branch(self)

    def copy_from(self,branch):
        self.mines = [row[:] for row in branch.mines]
        self.not_mines = [row[:] for row in branch.not_mines]
        self.canvas.copy_from(branch.canvas)
        