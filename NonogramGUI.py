import numpy as np
import tkinter as tk
from tkinter import Button
from random import choice


### In[2]:
##
##rows = [[6],[10],[14],[5,2,5],[4,2,4],[3,2,3],[3,2,3],[3,2,3],[3,2,3],[3,2,3],[3,2,3],[3,4,3],[3,6,3],[3,8,3],
##[3,3,2,3,3],[3,3,2,3,3],[5,2,5],[4,2,4],[5,2,5],[14],[10],[6]]
##columns = [[6],[10],[14],[5,5],[4,4],[3,5],[3,3,3],[3,3,3],[3,3,3],[3,3,3],[22],[22],[3,3,3],[3,3,3],[3,3,3],[3,3,3],
##[3,5],[4,4],[5,5],[14],[10],[6]]
##
##
### In[106]:
##
##rows = [[1, 1], [1], [3], [2], [0]]
##columns = [[3], [2], [2], [1], [0]]
##mat = np.array([[1, -1, -1, 1, -1], [1, -1, -1, -1, -1], [1, 1, 1, -1, -1], [-1, 1, 1, -1, -1], [-1, -1, -1, -1, -1]])
##first_step = [-1, -1]


# In[107]:

class ShowNono(tk.Frame):
    # Creates user interface to solve and show nonograms. 
    # The size of a window depends of a certain nonogram.
    # The user can fill the cell or mark it as an empty
    # with the mouse.
    
    def __init__(self, parent, rows, columns, nonoMatrix, firstStep = [-1, -1]):
        tk.Frame.__init__(self, parent, background="gray")
        self.parent = parent
        self.rows = rows
        self.columns = columns
        self.N = len(columns)
        self.M = len(rows)
        self.parent.title('[ %d x %d]' % (self.M, self.N))
        self.rclues = np.max([len(row) for row in rows])
        self.cclues = np.max([len(col) for col in columns])
        self.firstStep = firstStep
        self.create_cells(parent, self.M + self.cclues, self.N + self.rclues)
        self.width = (self.N + self.rclues) * 10
        self.height = (self.M + self.cclues) * 10
        self.parent.geometry('%dx%d' % (self.width * 2, self.height * 2 + 20))
        self.pack(side = "top", fill = "x")
        self.nonoMatrix = nonoMatrix


    def create_cells(self, parent, rows = 5, columns = 5):
        # Sets labels into a certain number of rows and columns 
        
        self.gameMatrix = np.zeros((self.M, self.N))
        self.widgets = []
        for row in range(rows):
            current_row = []
            for column in range(columns):
                label = tk.Label(self, borderwidth = 0, width = 5, text = ' ')
                label.grid(row = row, column = column, sticky = "nsew", padx = 1, pady = 1)
                current_row.append(label)
            self.widgets.append(current_row)    
        for column in range(columns):
            self.grid_columnconfigure(column, weight = 1)
            
        self.defaultbg = label.cget('bg')
        
        for i in range(self.M):
            for j in range(self.N):
                self.widgets[i + self.cclues][j + self.rclues].bind("<Button-1>", self.fill_cell)
                self.widgets[i + self.cclues][j + self.rclues].bind("<Button-3>", self.empty_cell)
                self.widgets[i + self.cclues][j + self.rclues].bind("<Button-2>", self.reset_cell)
            
        self.buttonReset = Button(self, text = 'Reset', command = self.reset_game)
        self.buttonReset.grid(columnspan = int((self.N + self.rclues)/2), 
                              column = (self.N + self.rclues) % 2)#self.N/3)
        self.buttonHint = Button(self, text = ' Hint ', command = self.get_hint)
        self.buttonHint.grid(columnspan = int((self.N + self.rclues)/2), 
                             column = int((self.N + self.rclues + 1)/2), 
                             row = self.M + self.cclues)#int(self.N/3)*2 + self.rclues
        self.create_clues()
        if self.firstStep != [-1, -1]:
            self.set_cell(self.firstStep)
        #print(self.gameMatrix)
        
    def create_clues(self):
        for i in range(self.M):
            for j in range(len(self.rows[i])):
                self.widgets[self.cclues + i][-j - self.N - 1].configure(text = str(self.rows[i][j]))
                self.widgets[self.cclues + i][-j - self.N - 1].bind("<Button-1>", self.cross_clue)

        for i in range(self.N):
            for j in range(len(self.columns[i])):
                self.widgets[self.cclues - j - 1][i + self.rclues].configure(text = str(self.columns[i][j]))
                self.widgets[self.cclues - j - 1][i + self.rclues].bind("<Button-1>", self.cross_clue)
                
        for i in range(self.rclues):
            for j in range(self.M + self.cclues):
                self.widgets[j][i].configure(bg = 'old lace')
                
        for i in range(self.cclues):
            for j in range(self.rclues + self.N):
                self.widgets[i][j].configure(bg = 'old lace')

    def set_cell(self, position):
        self.widgets[position[0] 
                     + self.cclues][position[1] 
                                    + self.rclues].configure(bg = 'black', state = 'disabled')
        self.gameMatrix[position[0]][position[1]] = 1
#        print(self.gameMatrix)

    def cut_cell(self, position):
        self.widgets[position[0] 
                     + self.cclues][position[1] 
                                    + self.rclues].configure(bg = self.defaultbg, 
                                                             text = 'x', state = 'disabled')
        self.gameMatrix[position[0]][position[1]] = 0
    
    def cross_clue(self, event):
        if event.widget.cget('fg') == 'red':
            event.widget.config(fg = 'black')
        else:
            event.widget.config(fg = 'red')
            
    def fill_cell(self, event):
#        print((int(event.widget.winfo_y()/18) - self.cclues,int(event.widget.winfo_x()/20) - self.rclues))
 
        if event.widget.cget('state') != 'disabled':
            event.widget.configure(bg = 'black')
            self.gameMatrix[int(event.widget.winfo_y()/18) 
                            - self.cclues][int(event.widget.winfo_x()/20) 
                                           - self.rclues] = 1
#        print(self.gameMatrix)
        if self.is_game_over():
            self.end_game()

    def empty_cell(self, event):
        if event.widget.cget('state') != 'disabled':
            event.widget.configure(text = 'x', bg = self.defaultbg)
            self.gameMatrix[int(event.widget.winfo_y()/19) 
                            - self.cclues][int(event.widget.winfo_x()/20) 
                                           - self.rclues] = 0
        if self.is_game_over():
            self.end_game()
        
    def reset_cell(self, event):
        if event.widget.cget('state') != 'disabled':
            event.widget.configure(bg = self.defaultbg, text = '  ')
            self.gameMatrix[int(event.widget.winfo_y()/18) 
                            - self.cclues][int(event.widget.winfo_x()/20) 
                                           - self.rclues] = 0
        if self.is_game_over():
            self.end_game()
    
    def reset_game(self):
        self.gameMatrix = np.zeros((self.M, self.N))
        for i in range(self.M + self.cclues):
            for j in range(self.N + self.rclues):
                self.widgets[i][j].configure(bg = self.defaultbg, text = '  ', fg = 'black', state = 'normal')
        self.create_clues()
        if self.firstStep != [-1, -1]:
            self.set_cell(self.firstStep)
    
    def get_hint(self):
        if not self.is_game_over():
            diff = self.gameMatrix - self.nonoMatrix
            if len(np.where(diff == -1)[0]):
                hint = choice(list(zip(np.where(diff == -1)[0],np.where(diff == -1)[1])))
                self.set_cell(hint)
#        print(hint)
            else:
                #print(np.where(diff == 2))
                hint = choice(list(zip(np.where(diff == 2)[0],np.where(diff == 2)[1])))
                self.cut_cell(hint)
                #print(self.gameMatrix)
            
            
            if self.is_game_over():
                self.end_game()
    
    def is_game_over(self):
        return(((self.gameMatrix * 2) - 1 == self.nonoMatrix).all())
        
    def end_game(self):
        for i in range(self.M + self.cclues):
            for j in range(self.N + self.rclues):
                self.widgets[i][j].configure(text = '  ', state = 'disabled')
                if self.widgets[i][j].cget('bg') != 'black':
                    self.widgets[i][j].configure(bg = 'gray')

##master = tk.Tk()
##app = ShowNono(master, rows, columns, mat, first_step)
###app.seti(1, 5)
###app.seti(1, 6)
##app.mainloop()
##
##
### In[163]:
##
##root = tk.Tk()
##root.title("Timer")
##root.geometry("100x100")
##
##def countdown(count):
##    label = tk.Label(root, text= count)
##    label.place(x=35, y=15)
##
##for i in range(5,0,-1):
##    countdown(i)
##    time.sleep(1)
##
##
##root.mainloop()

