from Nonogram.timeout import timeout
from collections import defaultdict
from ast import literal_eval
from PIL import Image
import numpy as np
import itertools


def cell_naming(clues):
    """
    Returns cell naming scheme.

    Cells are named by labelling them with unique, non-null integer values.
    Each group is composed of consecutive, positive integers. Groups are
    separated with negative integers. Moreover, thenaming begins and ends
    with empty cells.

    This implementation contains two tricks helpful for 'immediate_successors'
    function:

     - cells are labelled counting from 1 but empty cells getting negated value
     - empty cells labels are doubled.

    For example:

    cell_naming([1,2,3]) ==> [-1, -1, 2, -3, -3, 4, 5, -6, -6]
                               ^   ^  ^   ^   ^  ^  ^   ^   ^
                               |   |  |   |   |  |  |   |   |
            empty cells        |   |  |   |   |  |  |   |   |
            at the beginning --+---+  |   |   |  |  |   |   |
                                      |   |   |  |  |   |   |
              1st cell group (of 1) --+   |   |  |  |   |   |
                                          |   |  |  |   |   |
            1st group is separated from --+---+  |  |   |   |
            next one by an empty cell            |  |   |   |
            Note: it is doubled                  |  |   |   |
                                                 |  |   |   |
                      2nd cell group (of two)  --+--+   |   |
                                                        |   |
                         naming ends with empty cells --+---+

    >>> list(cell_naming([1, 2]))
    [-1, -1, 2, -3, -3, 4, 5, -6, -6]

    >>> list(cell_naming([1, 2, 3]))
    [-1, -1, 2, -3, -3, 4, 5, -6, -6, 7, 8, 9, -10, -10]
    """
    it = 1

    for clue in clues:
        yield -it
        yield -it
        it += 1

        for _ in range(clue):
            yield it
            it += 1

    yield -it
    yield -it


def immediate_successors(naming):
    """
    Generates a list of possible immediate successors for cells.

    A list of successors is generated with assumptions that:

      - cells in a group happen in succession,
      - between a group of cells there is at least one empty cell,
      - before first and after last group, there can be empty cells.

    This function exploits the tricks in cell_naming function to generate list.

    Examples:

        cell_naming([1,2])  ==>  [-1, -1, 2, -3, -3, 4, 5, -6, -6]
                                   .   |  |   |   |  |
        after first empty cell,    o---+--+   |   |  |
        the next one can be either        .   |   |  |
        another empty cell or the         .   |   |  |
        1st cell from 1st group           .   |   |  |
                                          .   |   |  |
          after 1st cell from 1st group,  o---+   |  |
          there must be an empty cell         .   |  |
                                              .   |  |
               after this empty cell can be   o---+--+
               another empty cell or 1st cell
               from 2nd group


    >>> immediate_successors(cell_naming([1, 2])) == \
            {-1: {-1,2}, 2: {-3}, -3: {-3, 4}, 4: {5}, 5: {-6}, -6: {-6}}
    True
    >>> immediate_successors(cell_naming([1, 2, 3])) ==           \
            {-1: {-1, 2}, 2: {-3}, -3: {-3,4}, 4: {5}, 5: {-6}, \
             -6: {-6, 7}, 7: {8}, 8: {9}, 9: {-10}, -10: {-10}}
    True
    """
    naming = iter(naming)
    result = defaultdict(set)

    predecessor_name = next(naming)
    for current_name in naming:
        result[predecessor_name].add(current_name)
        predecessor_name = current_name

    return result


class Row:
    """Representation of the row."""

    def __init__(self, width, clues):
        """
        Generate one row (or column).

        A row consists of cells. Here, cells are sets of possible values.

        >>> Row(3, [1, 1]).details_str()
        '[{-5,-3,-1,2,4},{-5,-3,-1,2,4},{-5,-3,-1,2,4}]'
        """
        naming = list(cell_naming(clues))
        naming_s = set(naming)

        self.cells = [naming_s.copy() for _ in range(width)]
        self.successors = immediate_successors(naming)
        self.predecessors = immediate_successors(reversed(naming))
        self.first = {naming[0]}
        self.last = {naming[-1]}

    def __str__(self):
        return ''.join(cell_to_str(cell) for cell in self.cells)

    def details_str(self):
        """Show cells as sets."""
        return '[' + ','.join('{' +
                              ','.join(str(x) for x in sorted(cell)) + '}'
                              for cell in self.cells) + ']'

    def forward_solver(self):
        solver_pass(self)

    def backward_solver(self):
        solver_pass(RowReversedView(self))


def solver_pass(row):
    """
    Performs a single pass of solving (one direction).

    For each cell, generates a list of possible values
    (using its predecessor) and uses it to filter the current
    list.

    Example:

     - cell #1 may contain cells [-1, 2, 3]
     - cell #1 successor may contain
        * -1  - another empty cell,
        * 2   - after '-1' there can be also '2'
        * 3   - after '2' there must be '3'
        * -4  - after '3' there must be '-4'
     - cell #2 (initially) may contain cells [-1, 2, 3, -4, 5, 6]
     - taking into account previous considerations, we conclude
     that cell #2 can contain only values [-1, 2, 3, -4]

    >>> row = Row(3, [1, 1]); row.forward_solver()
    >>> row.cells == \
            [{-1, 2}, {-1, 2, -3}, {-1, 2, -3, 4}]
    True

    >>> row = Row(4, [2]); row.forward_solver()
    >>> row.cells == \
            [{-1, 2}, {-1, 2, 3}, {-1, 2, 3, -4}, {-1, 2, 3, -4}]
    True
    """
    cells = iter(row.cells)
    predecessor_cell = row.first  # set to empty cell
    for current_cell in cells:
        predecessor_successors = {
            possible_value
            for predecessor_cell_elem in predecessor_cell
            for possible_value in row.successors[predecessor_cell_elem]
        }
        current_cell.intersection_update(predecessor_successors)
        predecessor_cell = current_cell


def isCellFilled(cell):
    return all(x > 0 for x in cell)


def isCellBlank(cell):
    return all(x < 0 for x in cell)


def cell_to_str(cell):
    if isCellFilled(cell):
        return '#'
    elif isCellBlank(cell):
        return ' '
    return '/'


class RowReversedView:
    """Behaves like Row (above), but returns the "reversed view" of the Row."""
    def __init__(self, row):
        self.__row = row

    @property
    def cells(self):
        return reversed(self.__row.cells)

    @property
    def first(self):
        return self.__row.last

    @property
    def successors(self):
        return self.__row.predecessors


class nonogram:
    """
    N - width
    M - height
    Represents one nonogram picture
    """
    def __init__(self, Rows, Columns):
        """
        Generates nonogram. As input it takes:
        -list of lists with clues for rows
        -list of lists with clues for columns
        """
        N = len(Columns)
        M = len(Rows)
        if not self.checkifcorrect(N, M, Rows, Columns):
            raise ValueError
        self.pair = [-1, -1]
        self.width = N
        self.height = M
        self.Rows = Rows
        self.Columns = Columns
        self.iterRows = [Row(self.width, r) for r in self.Rows]
        self.iterCols = [Row(self.height, c) for c in self.Columns]
        self.nonogram_Matrix = np.zeros((N, M))

    def checkifcorrect(self, N, M, Rows, Columns):
        """
        checks whether clues for rows and columns are correct
        first check is if sum of clues in rows and clues in columns are equal
        second check is if clues can be applied to nonogram of size N
        third check doesn't allow negative numbers
        """
        rowssum = sum([sum(x) for x in Rows])
        colssum = sum([sum(y) for y in Columns])
        if rowssum != colssum:
            print('ERROR! Clues indicates that you have \
                   different number of filled cells in \
                   rows and columns!')
            return False
        rowsum = [sum(x) + len(x) - 1 for x in Rows]
        colsum = [sum(y) + len(y) - 1 for y in Columns]
        if any(x > N for x in rowsum) or any(y > M for y in colsum):
            print('ERROR! Clues doesn\'t match nonogram size!')
            return False
        rowmin = min([min(x) for x in Rows])
        colmin = min([min(y) for y in Columns])
        if rowmin < 0 or colmin < 0:
            print('ERROR! Clues can only contain non-negative numbers!')
            return False
        return True

    def show_me(self):
        for i in range(self.height):
            print(self.iterRows[i])

    def one_step(self, Row):
        Row2 = ""
        while Row2 != Row.details_str():
            Row2 = Row.details_str()
            Row.forward_solver()
            Row.backward_solver()

    def multi_step(self):
        for Row in self.iterRows:
            self.one_step(Row)
        for Row in self.iterCols:
            self.one_step(Row)

    def transpose_check(self):
        """
        For any given empty or filled cell in row,
        fills or empties coresponding cell in column
        """
        for erow, row in enumerate(self.iterRows):
            for ecol, cell in enumerate(row.cells):
                if isCellFilled(cell):
                    cell2 = self.iterCols[ecol].cells[erow]
                    self.iterCols[ecol].cells[erow] = {x for x in cell2
                                                       if x > 0}
                elif isCellBlank(cell):
                    cell2 = self.iterCols[ecol].cells[erow]
                    self.iterCols[ecol].cells[erow] = {x for x in cell2
                                                       if x < 0}
        for ecol, row in enumerate(self.iterCols):
            for erow, cell in enumerate(row.cells):
                if isCellFilled(cell):
                    cell2 = self.iterRows[erow].cells[ecol]
                    self.iterRows[erow].cells[ecol] = {x for x in cell2
                                                       if x > 0}
                elif isCellBlank(cell):
                    cell2 = self.iterRows[erow].cells[ecol]
                    self.iterRows[erow].cells[ecol] = {x for x in cell2
                                                       if x < 0}

    def solve(self):
        """
        for columns and rows tries to check if any cell
        must be filled or emptied by checking possible
        successors and predecessors for every cell. Then
        transfer this cellsto rows/columns and tries again,
        until there is no change, or 300 times
        """
        i = 0
        Nonog = ""
        Nonog2 = ''.join(cell.__str__()
                         for row in self.iterRows
                         for cell in row.cells)
        while Nonog != Nonog2:
            i += 1
            if i > 300:
                return
            Nonog = Nonog2
            self.multi_step()
            self.transpose_check()
            Nonog2 = ''.join(cell.__str__()
                             for row in self.iterRows
                             for cell in row.cells)
            self.nonogram_Matrix = [[1 * isCellFilled(cell) -
                                     1 * isCellBlank(cell)
                                     for cell in Row.cells]
                                    for Row in self.iterRows]

    def check_if_correct(self):
        matrixRows = [row_to_clues(x)
                      for x in np.array(self.nonogram_Matrix)]
        matrixCols = [row_to_clues(x)
                      for x in np.array(self.nonogram_Matrix).T]
        return matrixRows == self.Rows and matrixCols == self.Columns

    @timeout(45)
    def full_solve(self):
        """
        check uniqueness of solution, then it solves it, or fills
        one cell to show one possible solution.
        Also creates array filled with 1 where cell is filled
        and -1 where cell is empty.
        """
        if check_uniqueness(self.Rows, self.Columns):
            self.pair = [-1, -1]
            self.solve()
        else:
            self.pair = uniquisation(self.Rows, self.Columns)
            self.fill(self.pair[0], self.pair[1])
            self.solve()
            self.nonogram_Matrix = [[1 * isCellFilled(cell) -
                                     1 * isCellBlank(cell)
                                     for cell in Row.cells]
                                    for Row in self.iterRows]

    def fill(self, RowNumber, ColNumber):
        """
        Forces cell in given row and in given column to become filled
        """
        cell2 = self.iterRows[RowNumber].cells[ColNumber]
        self.iterRows[RowNumber].cells[ColNumber] = {x for x in cell2 if x > 0}

    def unfill(self, RowNumber, ColNumber):
        """
        Forces cell in given row and in given column to become empty
        """
        cell2 = self.iterRows[RowNumber].cells[ColNumber]
        self.iterRows[RowNumber].cells[ColNumber] = {x for x in cell2 if x < 0}

    def nonogram_to_GUI(self):
        return [self.Rows, self.Columns, self.nonogram_Matrix]


@timeout(30)
def check_uniqueness(Rows, Columns):
    """
    Check whether nonogram contains cells
    that are non-certain - these can be filled
    with more than one pattern
    for example:

    >>> check_uniqueness([[2],[1]],[[1],[2]])
    True

    >>> check_uniqueness([[1],[1]],[[1],[1]])
    False
    """
    NonoGram = nonogram(Rows, Columns)
    NonoGram.solve()
    representation = ''.join(row.__str__() for row in NonoGram.iterRows)
    return '/' not in representation and ' ' in representation \
           and '#' in representation


@timeout(30)
def uniquisation(Rows, Columns):
    """
    Returns coordinates of first cell that if
    filled grants us unique solution
    for example:

    >>> uniquisation([[1],[1]],[[1],[1]])
    [0, 0]
    >>> uniquisation([[2],[1]],[[1],[2]])
    [-1, -1]
    """
    NG = nonogram(Rows, Columns)
    NG.solve()
    representation = ''.join(row.__str__() for row in NG.iterRows)
    if '/' not in representation and ' ' in representation \
       and '#' in representation:
        return [-1, -1]
    for i in range(len(Rows)):
        for j in range(len(Columns)):
            NG = nonogram(Rows, Columns)
            NG.solve()

            if isCellFilled(NG.iterRows[i].cells[j]) \
               or isCellBlank(NG.iterRows[i].cells[j]):
                next
            NG.fill(i, j)
            NG.solve()
            representation = ''.join(row.__str__() for row in NG.iterRows)
            if '/' not in representation and ' ' in representation \
               and '#' in representation:
                return [i, j]
    return [-1, -1]


def import_from_file(file):
    """
    Checks given file if it contains nonograms schemes with
    pattern as below:
    [[5,4,3,1],[3,7],[2,1,8,6],[3,4,10],[17]] <------- first
    line is list of clues for rows - must contain number of
    lists equal to size of nonogram. Each sub-list relates toone
    row in nonogram. If there is no clue - [0] must be written
    [[5,8],[3,7],[14,3],[1,3,12]] <------- second line is list
    of clues for columns - conditions as for rows
                        <------- one line of space before new nonogram
    [[1,1],[0],[1,1]]   <-------+
    [[1,1],[0],[1,1]]   <-------+--- next nonogram
    """
    Nonograms = {'unique': [], 'nonunique': [], 'hard': []}
    for p in (x for x in open(file).read().split("\n\n") if x):
        NGInput = p.split("\n")
        if check_uniqueness(literal_eval(NGInput[0]),
                            literal_eval(NGInput[1])):
            Nonograms['unique'].append(nonogram(literal_eval(NGInput[0]),
                                                literal_eval(NGInput[1])))
        elif uniquisation(literal_eval(NGInput[0]),
                          literal_eval(NGInput[1])) != [-1, -1]:
            Nonograms['nonunique'].append(nonogram(literal_eval(NGInput[0]),
                                                   literal_eval(NGInput[1])))
        else:
            Nonograms['hard'].append(nonogram(literal_eval(NGInput[0]),
                                              literal_eval(NGInput[1])))
    return Nonograms


@timeout(15)
def import_picture(image_name, N, M):
    """
    Converts given picture to array of given size
    (actual size may differ due to keeping aspect ratio)
    with -1 as empty cells and with 1 as filled one,
    and then converts it to lists of clues
    Returns List of list of clues for rows and for columns
    """
    image_file = Image.open(image_name)  # open colour image
    image_file = image_file.convert('1')  # convert image to black and white
    image_file.thumbnail((M, N), Image.ANTIALIAS)
    image = np.array(image_file)
    image = 1 - 2 * image
    Rows = [row_to_clues(x) for x in image]
    Cols = [row_to_clues(x) for x in image.T]
    return Rows, Cols


def row_to_clues(X):
    """
    converts array with -1 (empty cell) and 1 (filled cell) to a list of clues

    >>> row_to_clues([-1,-1,1,1,-1,-1,-1,1,-1,-1,1,1,1,1,1,1,
                      -1,-1,-1,1,-1,-1,-1])
    [2, 1, 6, 1]
    """
    U = []
    j = 0
    running = False
    for x in X:
        if x == 1:
            if not running:
                U.append(0)
            running = True
            U[j] = U[j] + 1
        if x == -1:
            if running:
                j = j + 1
            running = False
    if U == []:
        U = [0]
    return U


@timeout(60)
def brutforce_unique(nono):
    """
    Check every option of filling nonogram
    if they matches cluesand writes every
    solution into list that it returns
    for example:

    >>> brutforce_unique(nonogram([[1],[1]],[[1],[1]]))
    [(1, 2), (0, 3)]

    whete each number can be written as:
    Number = x * (length of row) + y
    and that would mean that Number indicates cell
    in x-th row and in y-th column
    """
    results = []
    rowssum = sum([sum(x) for x in nono.Rows])
    S = set(itertools.combinations(range(len(nono.Rows) *
                                         len(nono.Columns)),
                                   rowssum))
    for TrySet in S:
        nonogram1 = nonogram(nono.Rows, nono.Columns)
        for x in TrySet:
            nonogram1.fill(int(x % nonogram1.width), int(x / nonogram1.width))
            nonogram1.nonogram_Matrix = np.array([[-1 + 2 * isCellFilled(cell)
                                                   for cell in R.cells]
                                                  for R in nonogram1.iterRows])
        if nonogram1.check_if_correct():
            results.append(TrySet)
    return results


if __name__ == "__main__":
    import doctest
    doctest.testmod()
