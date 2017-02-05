import numpy as np
from Nonogram.Solver import row_to_clues
try:
    import Tkinter as tk
    from Tkinter import Button
    import tkMessageBox as box
except ImportError:
    import tkinter as tk
    from tkinter import Button
    from tkinter import messagebox as box


class ShowNonoHard(tk.Frame):
    '''
    Creates user interface to solve and show nonograms.
    The size of a window depends of a certain nonogram.
    The user can fill the cell or mark it as an empty
    with the mouse. Also it has option to reset nonograms.
    '''
    def __init__(self, parent, rows, columns):
        tk.Frame.__init__(self, parent, background="gray")
        self.parent = parent
        self.rows = rows
        self.columns = columns
        self.N = len(columns)
        self.M = len(rows)
        self.parent.title('[ %d x %d] Hard' % (self.M, self.N))
        self.rclues = np.max([len(row) for row in rows])
        self.cclues = np.max([len(col) for col in columns])
        self.create_cells(parent, self.M + self.cclues, self.N + self.rclues)
        self.width = (self.N + self.rclues) * 10
        self.height = (self.M + self.cclues) * 10
        self.parent.geometry('%dx%d' % (self.width * 2 - 10,
                                        self.height * 2 + 15))
        self.pack(side="top", fill="x")
        self.menubar = tk.Menu(self.parent)
        self.menubar.add_command(label="Reset", command=self.reset_game)
        self.menubar.add_command(label="Quit", command=self.parent.destroy)
        self.parent.config(menu=self.menubar)
        box.showinfo('', '''                    This is a little bit harder nonogram.
                    Our algorithm couldn\'t solve it so you don\'t
                    have any hints. Maybe you will solve it without
                    our help! :)''')

    def create_cells(self, parent, rows=5, columns=5):
        '''
        Creates board where player can L-click to fill,
        R-click to cross cell, and Middle-click set cell
        empty.
        '''
        self.gameMatrix = np.zeros((self.M, self.N))
        self.widgets = []
        for row in range(rows):
            current_row = []
            for column in range(columns):
                label = tk.Label(self, borderwidth=0, width=5, text=' ')
                label.grid(row=row, column=column, sticky="nsew",
                           padx=1, pady=1)
                current_row.append(label)
            self.widgets.append(current_row)
        for column in range(columns):
            self.grid_columnconfigure(column, weight=1)

        self.defaultbg = label.cget('bg')

        for i in range(self.M):
            for j in range(self.N):
                self.widgets[i + self.cclues][j + self.rclues]\
                    .bind("<Button-1>", self.fill_cell)
                self.widgets[i + self.cclues][j + self.rclues]\
                    .bind("<Button-3>", self.empty_cell)
                self.widgets[i + self.cclues][j + self.rclues]\
                    .bind("<Button-2>", self.reset_cell)

        self.create_clues()

    def create_clues(self):
        '''
        Creates labels with clues for cokumns and rows.
        On L-Click they can be turn red or black
        '''
        for i in range(self.M):
            for j in range(len(self.rows[i])):
                self.widgets[self.cclues + i][-j - self.N - 1]\
                    .configure(text=str(self.rows[i][-j-1]))
                self.widgets[self.cclues + i][-j - self.N - 1]\
                    .bind("<Button-1>", self.cross_clue)

        for i in range(self.N):
            for j in range(len(self.columns[i])):
                self.widgets[self.cclues - j - 1][i + self.rclues]\
                    .configure(text=str(self.columns[i][-j-1]))
                self.widgets[self.cclues - j - 1][i + self.rclues]\
                    .bind("<Button-1>", self.cross_clue)

        for i in range(self.rclues):
            for j in range(self.M + self.cclues):
                self.widgets[j][i].configure(bg='old lace')

        for i in range(self.cclues):
            for j in range(self.rclues + self.N):
                self.widgets[i][j].configure(bg='old lace')

    def cross_clue(self, event):
        '''Turns clue red and black'''
        if event.widget.cget('fg') == 'red':
            event.widget.config(fg='black')
        else:
            event.widget.config(fg='red')

    def fill_cell(self, event):
        '''Fills clicked cell black'''
        if event.widget.cget('state') != 'disabled':
            event.widget.configure(bg='black')
            x = int(event.widget.winfo_y()/18) - self.cclues
            y = int(event.widget.winfo_x()/19) - self.rclues
            self.gameMatrix[min([x, len(self.gameMatrix)-1])]\
                           [min([y, len(self.gameMatrix[0])-1])] = 1
        if self.is_game_over():
            self.end_game()

    def empty_cell(self, event):
        '''Crosses clicked cell'''
        if event.widget.cget('state') != 'disabled':
            event.widget.configure(text='x', bg=self.defaultbg)
            x = int(event.widget.winfo_y()/18) - self.cclues
            y = int(event.widget.winfo_x()/19) - self.rclues
            self.gameMatrix[min([x, len(self.gameMatrix)-1])]\
                           [min([y, len(self.gameMatrix[0])-1])] = 0
        if self.is_game_over():
            self.end_game()

    def reset_cell(self, event):
        '''Empties clicked cell'''
        if event.widget.cget('state') != 'disabled':
            event.widget.configure(bg=self.defaultbg, text='  ')
            x = int(event.widget.winfo_y()/18) - self.cclues
            y = int(event.widget.winfo_x()/19) - self.rclues
            self.gameMatrix[min([x, len(self.gameMatrix)-1])]\
                           [min([y, len(self.gameMatrix[0])-1])] = 0
        if self.is_game_over():
            self.end_game()

    def reset_game(self):
        '''Resets whole board, so player can play again'''
        self.gameMatrix = np.zeros((self.M, self.N))
        for i in range(self.M + self.cclues):
            for j in range(self.N + self.rclues):
                self.widgets[i][j].configure(bg=self.defaultbg, text='  ',
                                             fg='black', state='normal')
        self.create_clues()

    def is_game_over(self):
        '''
        Checks whether picture generates same clues
        as ones given during initializing.
        '''
        gameMatrix = 2 * self.gameMatrix - 1
        matrixRows = [row_to_clues(x) for x in np.array(gameMatrix)]
        matrixCols = [row_to_clues(x) for x in np.array(gameMatrix).T]
        return matrixRows == self.rows and matrixCols == self.columns

    def end_game(self):
        '''
        Diables cells, changes color of background,
        so player can see the picture he just played
        '''
        for i in range(self.M + self.cclues):
            for j in range(self.N + self.rclues):
                self.widgets[i][j].configure(text='  ', state='disabled')
                if self.widgets[i][j].cget('bg') != 'black':
                    self.widgets[i][j].configure(bg='gray')
