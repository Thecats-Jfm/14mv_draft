import unittest
from myproject.problem import Problem

class TestProblem(unittest.TestCase):

    def test_load_from_image(self):
        # 创建Problem实例
        problem = Problem()

        # 加载图像
        problem.load_from_image('./img/5x5.png')

        # 检查问题是否已成功加载
        self.assertIsNotNone(problem.board, "Board should not be None")

        # 检查行数
        self.assertEqual(len(problem.board), 5, "Board should have 5 rows")

        # 检查列数
        for row in problem.board:
            self.assertEqual(len(row), 5, "Each row should have 5 columns")

        # 检查branches列表是否包含主分支
        self.assertEqual(len(problem.branches), 1, "There should be one main branch")


if __name__ == '__main__':
    unittest.main()
