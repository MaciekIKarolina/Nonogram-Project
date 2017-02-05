from Nonogram import Solver
import unittest


class funcTestCase(unittest.TestCase):

    def setUp(self):
        self.clues = [3, 1]
        self.succ = Solver.immediate_successors(Solver.cell_naming(self.clues))
        self.cell = {1, 5, 19, 23, 19}
        self.cell2 = {-1, -5, -19, -23, -19}
        self.cell3 = {1, -5, -19, -23, -19}
        self.Nonogram = Solver.nonogram([[1], [2]], [[2], [1]])

    def test_naming(self):
        self.assertEqual(self.succ, {-1: {-1, 2}, 2: {3}, 3: {4}, 4: {-5},
                                     -5: {-5, 6}, 6: {-7}, -7: {-7}})

    def test_isCellFilled(self):
        self.assertEqual(Solver.cell_to_str(self.cell), '#')
        self.assertEqual(Solver.cell_to_str(self.cell2), ' ')
        self.assertEqual(Solver.cell_to_str(self.cell3), '/')

    def test_fill(self):
        self.assertRaises(TypeError,  self.Nonogram.fill,  -1, 'a')

    def test_row_to_clues(self):
        self.assertEqual(Solver.row_to_clues([-1, 1, 1, -1, -1, 1, -1, -1, -1,
                                              1, 1, 1]), [2, 1, 3])
        self.assertEqual(Solver.row_to_clues([-1, -1, -1, -1, -1, -1, -1, -1,
                                              -1, -1]), [0])


suite = unittest.TestLoader().loadTestsFromTestCase(funcTestCase)
print(unittest.TextTestRunner(verbosity=3).run(suite))
