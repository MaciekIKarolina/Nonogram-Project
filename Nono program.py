import numpy as np
from NonogramGUI import *
import tkinter as tk
from tkinter import BOTH, Listbox, StringVar, END, Menu
from tkinter.ttk import Frame, Label, Style
import nonogram as nng


class Example(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
         
        self.parent = parent        
        self.initUI()
        
    def initUI(self):
      
        self.parent.title("Nonograms") 
        base_nonograms = nng.import_from_file("Nonogram base.txt")
        self.all_nonograms = base_nonograms['unique'] + base_nonograms['nonunique']
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)
        
        fileMenu = tk.Menu(menubar)
        fileMenu.add_command(label="Open", command=self.onOpen)
        fileMenu.add_command(label="Exit", command=self.onExit)
        menubar.add_cascade(label="File", menu=fileMenu)       

    
        self.pack(fill=tk.BOTH, expand=1)
        nonos=[]
        for n in range(len(base_nonograms['unique'])):
            nonos.append('Nonogram ' + str(n))
        for n in range(len(base_nonograms['nonunique'])):
            nonos.append('NUS Nonogram ' + str(n))        
        lb = tk.Listbox(self)
        for i in nonos:
            lb.insert(tk.END, i)
            
        lb.bind("<<ListboxSelect>>", self.onSelect)    
            
        lb.place(x=20, y=40)

#        self.var = tk.StringVar()
#        self.label = Label(self, text=0, textvariable=self.var)        
#        self.label.place(x=20, y=210)

        info1 = Label(self, text = 'Select nonogram:')
        info1.place(x = 30, y = 10)
        
        info2 = Label(self, text = 'Or choose a file:')
        info2.place(x = 180, y = 80)
        
        self.browseButton = tk.Button(self, text = 'Browse...', command = self.onBrowse)
        self.browseButton.place(x = 200, y = 100)

    def onSelect(self, val):
        sender = val.widget
        num = sender.curselection()[0]
        current_nonogram = self.all_nonograms[num]
        current_nonogram.solve()
        current_nonogram.full_solve()
        master = tk.Tk()
        app = ShowNono(master, current_nonogram.Rows,
                       current_nonogram.Columns,
                       current_nonogram.nonogram_Matrix,
                       current_nonogram.pair)
        app.mainloop()
    
#        sender = val.widget
#        idx = sender.curselection()
#        value = sender.get(idx)   

#        self.var.set(value)
 
    def onBrowse(self):
        ftypes = [('Text files', '*.txt'), ('Pictures', '*.jpg')]
        dlg = filedialog.Open(self, filetypes = ftypes)
        fl = dlg.show()
    
    def onOpen(self):
        pass
        
    def onExit(self):
        self.quit()

        
         

def main():
  
    root = tk.Tk()
    ex = Example(root)
    root.geometry("300x250+300+300")
    root.mainloop()  


if __name__ == '__main__':
    main()


# In[75]:

##a = [[-1, 1, -1, 1, -1, -1, -1, -1, -1], 
##     [-1, 1, 1, 1, -1, -1, -1, -1, -1], 
##     [1, 1, 1, 1, 1, -1, -1, -1, -1],
##     [1, 1, 1, 1, 1, -1, -1, -1, -1],
##     [-1, -1, 1, -1, -1, -1, -1, 1, -1],
##     [-1, -1, 1, -1, -1, -1, -1, 1, -1],
##     [-1, -1, 1, 1, -1, -1, 1, 1, -1],
##     [-1, -1, 1, 1, 1, -1, 1, -1, -1],
##     [-1, 1, 1, 1, 1, 1, 1, 1, -1]]
##
##
##rows = [[6],[10],[14],[5,2,5],[4,2,4],[3,2,3],[3,2,3],[3,2,3],[3,2,3],[3,2,3],[3,2,3],[3,4,3],[3,6,3],[3,8,3],
##[3,3,2,3,3],[3,3,2,3,3],[5,2,5],[4,2,4],[5,2,5],[14],[10],[6]]
##columns = [[6],[10],[14],[5,5],[4,4],[3,5],[3,3,3],[3,3,3],[3,3,3],[3,3,3],[22],[22],[3,3,3],[3,3,3],[3,3,3],[3,3,3],
##[3,5],[4,4],[5,5],[14],[10],[6]]

#import numpy as np
##np.max([len(row) for row in rows])


##master = tk.Tk()
##app = ShowNono(master, 9)
##for i in range(len(a)):
##    for j in range(len(a[0])):
##        if a[i][j] == 1:
##            app.seti(i, j)
##app.mainloop()

