from typing import List, Sequence, Iterator, Iterable, Mapping, Set
from collections import defaultdict, namedtuple
from ast import literal_eval
from PIL import Image
import numpy as np

def cell_naming(clues: Iterable[int]) -> Iterator[int]:
    """
    Returns cell naming scheme.

    Cells are named by labelling them with unique, non-null integer values. Each group is composed
    of consecutive, positive integers. Groups are separated with negative integers. Moreover, the
    naming begins and ends with empty cells.
    
    This implementation contains two tricks helpful for 'immediate_successors' function:

      - cells are labelled counting from 1 with empty cells getting the negated value,
      - empty cells labels are doubled.

    For example:

        cell_naming([1,2,3]) ==> [-1, -1, 2, -3, -3, 4, 5, -6, -6, 7, 8, 9, -10, -10]
                                   ^   ^  ^   ^   ^  ^  ^                     ^    ^
                                   |   |  |   |   |  |  |                     |    |
                empty cells        |   |  |   |   |  |  |                     |    |
                at the beginning --+---+  |   |   |  |  |                     |    |
                                          |   |   |  |  |                     |    |
                  1st cell group (of 1) --+   |   |  |  |                     |    |
                                              |   |  |  |                     |    |
                1st group is separated from --+---+  |  |                     |    |
                next one by an empty cell            |  |                     |    |
                Note: it is doubled                  |  |                     |    |
                                                     |  |                     |    |
                          2nd cell group (of two)  --+--+                     |    |
                                                                              |    |
                                               naming ends with empty cells --+----+

    >>> list(cell_naming([1,2]))
    [-1, -1, 2, -3, -3, 4, 5, -6, -6]

    >>> list(cell_naming([1,2,3]))
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

def immediate_successors(naming: Iterable[int]) -> Mapping[int, Set[int]]:
    """
    Generates a list of possible immediate successors for cells.
    
    A list of successors is generated with assumptions that:

      - cells in a group happen in succession,
      - between a group of cells there is at least one empty cell,
      - before first and after last group, there can be empty cells.

    This function exploits the tricks in cell_naming function to generate such list.

    Examples:

        cell_naming([1,2,3]) ==> [-1, -1, 2, -3, -3, 4, 5, -6, -6, 7, 8, 9, -10, -10]
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


    >>> immediate_successors(cell_naming([1,2])) == \
            {-1: {-1,2}, 2: {-3}, -3: {-3, 4}, 4: {5}, 5: {-6}, -6: {-6}}
    True
    >>> immediate_successors(cell_naming([1,2,3])) ==           \
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

    def __init__(self, width: int, clues: List[int]):
        """
        Generate one row (or column).

        A row consists of cells. Here, cells are sets of possible values.

        >>> Row(3, [1,1]).details_str()
        '[{-5,-3,-1,2,4},{-5,-3,-1,2,4},{-5,-3,-1,2,4}]'
        """
        naming = list(cell_naming(clues))
        naming_s = set(naming)

        self.cells=[naming_s.copy() for _ in range(width)]
        self.successors=immediate_successors(naming)
        self.predecessors=immediate_successors(reversed(naming))
        self.first={naming[0]}
        self.last={naming[-1]}

    def __str__(self):
        return ''.join(cell_to_str(cell) for cell in self.cells)

    def details_str(self) -> str:
        """Show cells as sets."""
        return '[' + \
                ','.join('{' + \
                    ','.join(str(x) for x in sorted(cell)) + \
                    '}' \
                    for cell in self.cells) +\
                ']'

    def forward_solver(self):
        solver_pass(self)

    def backward_solver(self):
        solver_pass(RowReversedView(self))

def solver_pass(row):
    """
    Performs a single pass of solving (one direction).

    For each cell, generates a list of possible values (using its predecessor) and uses it to
    filter the current list.

    Example:

     - cell #1 may contain cells [-1,2,3]
     - cell #1 successor may contain
        * -1  - another empty cell,
        * 2   - after '-1' there can be also '2'
        * 3   - after '2' there must be '3'
        * -4  - after '3' there must be '-4'
     - cell #2 (initially) may contain cells [-1,2,3,-4,5,6]
     - taking into account previous considerations, we conclude that cell #2 can contain only
       values [-1,2,3,-4]

    >>> row = Row(3, [1,1]); row.forward_solver()
    >>> row.cells == \
            [{-1,2},{-1,2,-3},{-1,2,-3,4}]
    True

    >>> row = Row(4, [2]); row.forward_solver()
    >>> row.cells == \
            [{-1,2},{-1,2,3},{-1,2,3,-4},{-1,2,3,-4}]
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
    
def cell_to_str(cell: Set[int]) -> str:
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
    Represents one nonogram picture, with function to solve it,
    if there is only one solution
    """
    def __init__(self, N: int, Rows: [list], Columns: [list]):
        """
        Generwates nonogram. As input it takes:
        -dimension N,
        -list of lists with clues for rows
        -list of lists with clues for columns


        """
        if not self.checkifcorrect(N, Rows, Columns):
            raise ValueError
        self.N = N
        self.Rows = Rows
        self.Columns = Columns
        self.iterRows = [Row(self.N, r) for r in self.Rows]
        self.iterCols = [Row(self.N, c) for c in self.Columns]

    def checkifcorrect(self, N: int, Rows: [list], Columns: [list]) -> bool: 
        """
        checks whether clues for rows and columns are correct
        first check is if sum of clues in rows and clues in columns are equal
        second check is if clues can be applied to nonogram of size N
        third check doesn't allow negative numbers 
        """
        rowssum = sum([sum(x) for x in Rows])
        colssum = sum([sum(y) for y in Columns])
        if rowssum!=colssum:
            print('ERROR! Clues indicates that you have different number of filled cells in rows and columns!')
            return False
        rowsum = [sum(x)+len(x)-1 for x in Rows]
        colsum = [sum(y)+len(y)-1 for y in Columns]
        if any(x> N for x in rowsum) or any(y>N for y in colsum):
            print('ERROR! Clues doesn\'t match nonogram size!')
            return False
        rowmin = min([min(x) for x in Rows])
        colmin = min([min(y) for y in Columns])        
        if rowmin < 0 or colmin < 0:
            print('ERROR! Clues can only contain non-negative numbers!')
            return False
        return True
        
    def show_me(self):
        for i in range(self.N):
            print(self.iterRows[i])
        
    def one_step(self, Row):
        Row2=""
        while Row2!=Row.details_str():
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
        For any given empty or filled cell in row, fills or empties coresponding cell in column
        """
        for enumrow, row in enumerate(self.iterRows): #returns row as list of cells in row
            for enumcol, cell in enumerate(row.cells): #returns cell as single cell in row
                if isCellFilled(cell):
                    cell2 = self.iterCols[enumcol].cells[enumrow]
                    self.iterCols[enumcol].cells[enumrow] = {x for x in cell2 if x > 0}
                elif isCellBlank(cell):
                    cell2 = self.iterCols[enumcol].cells[enumrow]
                    self.iterCols[enumcol].cells[enumrow] = {x for x in cell2 if x < 0}
        for enumrow, row in enumerate(self.iterCols): #returns row as list of cells in column
            for enumcol, cell in enumerate(row.cells): #returns cell as single cell in column
                if isCellFilled(cell):
                    cell2 = self.iterRows[enumcol].cells[enumrow]
                    self.iterRows[enumcol].cells[enumrow] = {x for x in cell2 if x > 0}
                elif isCellBlank(cell):
                    cell2 = self.iterRows[enumcol].cells[enumrow]
                    self.iterRows[enumcol].cells[enumrow] = {x for x in cell2 if x < 0}

    def solve(self):
        """
        for columns and rows tries to check if any cell must be filled or emptied
        by checking possible successors and predecessors for every cell. Then
        transfer this cellsto rows/columns and tries again, until there is no change,
        or 100 times
        """
        i=0
        Nonog=""
        Nonog2=''.join(cell.__str__() for row in self.iterRows for cell in row.cells)
        while Nonog!=Nonog2:
            i+=1
            if i>100:
                return
            Nonog=Nonog2
            self.multi_step()
            self.transpose_check()
            Nonog2=''.join(cell.__str__() for row in self.iterRows for cell in row.cells)

    def full_solve(self):
        """
        check uniqueness of solution, then it solves it, or fills one cell
        to show one possible solution
        Also creates array filled with 1 where cell is filled and -1 where cell is empty
        """
        if check_uniqueness(self.N,self.Rows,self.Columns):
            self.solve()
        else:
            pair = uniquisation(self.N,self.Rows,self.Columns)
            self.fill(pair[0],pair[1])
            self.solve()
        self.Nonogram_Matrix = [[1*isCellFilled(cell)-1*isCellBlank(cell) for cell in Row.cells] for Row in self.iterRows]

        
    def fill(self, RowNumber: int, ColNumber: int):
        """
        Forces cell in given row and in given column to become filled
        """
        cell2 = self.iterRows[RowNumber].cells[ColNumber]
        self.iterRows[RowNumber].cells[ColNumber] = {x for x in cell2 if x > 0}
        
    def unfill(self, Rows: [list], Columns: [list]):
        """
        Forces cell in given row and in given column to become empty
        """
        cell2 = self.iterRows[RowNumber].cells[ColNumber]
        self.iterRows[RowNumber].cells[ColNumber] = {x for x in cell2 if x < 0}


        

def check_uniqueness(N: int, Rows: [list], Columns: [list]):
    """
    Check whether nonogram contains cells that are non-certain - these can be filled with more than one pattern
    """
    NonoGram = nonogram(N, Rows, Columns)
    NonoGram.solve()
    representation = ''.join(row.__str__() for row in NonoGram.iterRows)
    return not '/' in representation

def uniquisation(N: int, Rows: [list], Columns: [list]) -> List[int]:
    """
    Returns coordinates of first cell that if filled grants us unique solution
    """
    for i in range(N):
        for j in range(N):
            NG = nonogram(N, Rows, Columns)
            NG.solve()
            if isCellFilled(NG.iterRows[i].cells[j]) or isCellBlank(NG.iterRows[i].cells[j]):
                next
            NG.fill(i,j)
            NG.solve()
            representation = ''.join(row.__str__() for row in NG.iterRows)            
            if not '/' in representation and ' ' in representation and '#' in representation:
                return [i,j]



def import_from_file(file: str) -> list:
    """
    Checks given file if it contains nonograms schemes with pattern as below:
    20  <------- size of nonogram
    [[5,4,3,1],[3,7],...,[2,1,8,6],[3,4,10],[17]] <------- list of clues for rows - must contain number of lists equal to size of nonogram.
    Each sub-list relates to one row in nonogram. If there is no clue - [0] must be written 
    [[5,8],[3,7],...,[14,3],[1,3,12]] <------- list of clues for columns - conditions as for rows 
     <------- one line of space before new nonogram
    3                   <-------|  
    [[1,1],[1],[1,1]]   <-------|--- next nonogram
    [[1,1],[1],[1,1]]   <-------| 
    
    """
    Nonograms = []
    for p in (x for x in open(file).read().split("\n\n") if x):
        NGInput=p.split("\n")
        Nonograms.append(nonogram(int(NGInput[0]),literal_eval(NGInput[1]),
                                  literal_eval(NGInput[2])))
    return Nonograms


def import_picture(image_name: str, N: int) ->List[list]:
    """
    Converts given picture to array of given size with -1 as empty cells and with 1 as filled one, and then converts it to lists of clues
    Returns List of list of clues for rows and for columns
    Works only with square pictures.
    """
    image_file = Image.open(image_name) # open colour image
    image_file = image_file.convert('1') # convert image to black and white
    image_file.thumbnail((N, N), Image.ANTIALIAS)
    image = np.array(image_file)
    image = 1-2* image
    Rows = [row_to_clues(x) for x in image]
    Cols = [row_to_clues(x) for x in image.T]
    return [Rows, Cols]



def row_to_clues(X: List[int])->List[int]:
    """
    converts array with -1 (empty cell) and 1 (filled cell) to a list of clues
    >>> row_to_clues([-1,-1,1,1,-1,-1,-1,1,-1,-1,1,1,1,1,1,1,-1,-1,-1,1,-1,-1,-1])
    [2, 1, 6, 1]
    """
    U=[]
    j=0
    running=False
    for i in range(len(X)):
        if X[i]==1:
            if not running:
                U.append(0)
            running=True
            U[j]=U[j]+1
        if X[i]==-1:
            if running:
                j=j+1
            running=False
    if U==[]:
        U=[0]
    return U



X=import_from_file("Nonogram testing — kopia.txt")


Nono=X[-1]
Nono.full_solve()
Nono.show_me()
