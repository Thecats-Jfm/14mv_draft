from .canvas import Canvas
from .utils import logprint

class Branch:
    def __init__(self, problem,idx=0):
        self.problem = problem
        self.mines = [[False] * problem.columns for _ in range(problem.rows)]
        self.not_mines = [[False] * problem.columns for _ in range(problem.rows)]
        self.idx = idx
        self.canvas = Canvas(self)

    def mark_mine(self, row, col):
        # 在指定位置标记雷
        self.mines[row][col] = True
        self.not_mines[row][col] = False

    def mark_not_mine(self, row, col):
        # 在指定位置标记非雷
        self.not_mines[row][col] = True
        self.mines[row][col] = False

    def show(self):
        logprint(message="Branch%d调用Canvas显示"%self.idx, level="debug")
        self.canvas.show()