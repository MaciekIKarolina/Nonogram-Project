from Nonogram.GUI import *
from Nonogram.Hard_GUI import *
import Nonogram.Solver as sol
import numpy as np
from PIL import Image
import tkinter as tk
from tkinter import BOTH, Listbox, StringVar, END, Menu
from tkinter.ttk import Frame, Label, Style


class Nono_Main(Frame):
    '''
    It is GUI for player to choose nonogram,
    or to import from text file or picture
    '''
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent
        self.initUI()

    def initUI(self):
        '''
        Loades nonograms from Nonogram base.txt file,
        fills list of nonograms and creates all widgets
        within GUI
        '''
        self.parent.title("Nonograms")
        base_nonograms = sol.import_from_file("Nonogram base.txt")
        self.all_nonograms = []
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)
        self.fl = ""
        fileMenu = tk.Menu(menubar)
        fileMenu.add_command(label="Export", command=self.export)
        fileMenu.add_command(label="Open", command=self.onOpen)
        fileMenu.add_command(label="Exit", command=self.onExit)
        menubar.add_cascade(label="File", menu=fileMenu)

        self.pack(fill=tk.BOTH, expand=1)
        nonos = []
        for n in range(len(base_nonograms['unique'])):
            nonos.append('Nonogram ' + str(len(self.all_nonograms) + n))
        self.all_nonograms += base_nonograms['unique']
        for n in range(len(base_nonograms['nonunique'])):
            nonos.append('NUS Nonogram ' + str(len(self.all_nonograms) + n))
        self.all_nonograms += base_nonograms['nonunique']
        for n in range(len(base_nonograms['hard'])):
            nonos.append('HARD Nonogram ' + str(len(self.all_nonograms) + n))
        self.all_nonograms += base_nonograms['hard']
        self.lb = tk.Listbox(self)
        for i in nonos:
            self.lb.insert(tk.END, i)

        self.lb.bind("<<ListboxSelect>>", self.onSelect)

        self.lb.place(x=20, y=40)

        info1 = Label(self, text='Select nonogram:')
        info1.place(x=30, y=10)

        info2 = Label(self, text='Or choose a file:')
        info2.place(x=180, y=10)

        self.browseButton = tk.Button(self, text='Browse...',
                                      command=self.onBrowse)
        self.browseButton.place(x=200, y=30)

        self.info3 = Label(self, text="")
        self.info3.place(x=150, y=60)

        self.xSize = tk.Entry(self, width=5)
        self.info4 = Label(self, text="Rows:")
        self.ySize = tk.Entry(self, width=5)
        self.info5 = Label(self, text="Columns:")

    def onSelect(self, val):
        '''
        When player selects nonogram from list,
        new window appears with this particular
        nonogram.
        '''
        sender = val.widget
        num = sender.curselection()[0]
        current_nonogram = self.all_nonograms[num]
        current_nonogram.solve()
        current_nonogram.full_solve()
        master = tk.Tk()
        if 'HARD' not in sender.get(sender.curselection()):
            app = ShowNono(master, current_nonogram.Rows,
                           current_nonogram.Columns,
                           current_nonogram.nonogram_Matrix,
                           current_nonogram.pair)
            app.mainloop()
        else:
            app = ShowNonoHard(master, current_nonogram.Rows,
                               current_nonogram.Columns)
            app.mainloop()

    def onBrowse(self):
        '''
        Opens filedialog window, so player can choose
        text file or picture to add nonograms. In the
        second case player is asked to give dimensions
        of picture he wants to solve.
        WARNING!
        Image size ratio cannot be changed!
        So if original picture has resolution 900x900
        and players gives X = 10, Y = 100 picture will
        be converted to X = 100 and Y = 100, to retain
        size ratio and to match Y
        '''
        if self.xSize:
            self.xSize.destroy()
        if self.ySize:
            self.ySize.destroy()
        if self.info4:
            self.info4.destroy()
        if self.info5:
            self.info5.destroy()
        ftypes = [('Text files', '*.txt'),
                  ('Pictures', '*.jpg; *.png; *.bmp')]
        dlg = tk.filedialog.Open(self, filetypes=ftypes)
        self.fl = dlg.show()
        sss = self.fl.split("/")
        self.info3.configure(text=sss[-1])
        if self.fl[-3:] == "txt":
            self.convert = tk.Button(self, text='Convert',
                                     command=self.convert)
            self.convert.place(x=200, y=160)

        elif self.fl[-3:] in ['jpg', 'png', 'bmp']:
            self.ySize = tk.Entry(self, width=5)
            self.ySize.place(x=210, y=100)

            self.info4 = Label(self, text="Rows:")
            self.info4.place(x=150, y=100)

            self.xSize = tk.Entry(self, width=5)
            self.xSize.place(x=210, y=130)

            self.info5 = Label(self, text="Columns:")
            self.info5.place(x=150, y=130)

            self.convert = tk.Button(self, text='Convert',
                                     command=self.convert)
            self.convert.place(x=200, y=160)

    def convert(self):
        '''
        imports and adds to list nonograms from file,
        or converts picture to nonogram and adds it
        to the list
        '''
        if self.fl[-3:] == "txt":
            base_nonograms = sol.import_from_file(self.fl)
            name = self.fl.split("/")[-1].split(".")[0]
            nonos = []
            for n in range(len(base_nonograms['unique'])):
                nonos.append('My ' + name + ' ' +
                             str(len(self.all_nonograms) + n))
            self.all_nonograms += base_nonograms['unique']
            for n in range(len(base_nonograms['nonunique'])):
                nonos.append('My NUS ' + name + ' ' +
                             str(len(self.all_nonograms) + n))
            self.all_nonograms += base_nonograms['nonunique']
            for n in range(len(base_nonograms['hard'])):
                nonos.append('HARD ' + name + ' ' +
                             str(len(self.all_nonograms) + n))
            self.all_nonograms += base_nonograms['hard']
            for i in nonos:
                self.lb.insert(tk.END, i)
        elif self.fl[-3:] in ['jpg', 'png', 'bmp']:
            name = self.fl.split("/")[-1].split(".")[0]
            rows, cols = sol.import_picture(self.fl,
                                            int(self.xSize.get()),
                                            int(self.ySize.get()))
            ngram = sol.nonogram(rows, cols)
            self.lb.insert(tk.END, "My " + name + ' ' +
                           str(len(self.all_nonograms)))
            self.all_nonograms.append(ngram)
            self.xSize.destroy()
            self.ySize.destroy()
            self.info4.destroy()
            self.info5.destroy()

        self.convert.destroy()
        self.info3.configure(text="")

    def onOpen(self):
        self.onBrowse()

    def onExit(self):
        self.parent.destroy()

    def export(self):
        '''
        Saves all nonograms from the list to "Nonogram base.txt" so
        they will be loaded on next opening
        '''
        text = [str(nonogram.Rows) + '\n' + str(nonogram.Columns)
                for nonogram in self.all_nonograms]
        new_text = '\n\n'.join(text)
        f = open('Nonogram base.txt', 'w')
        f.write(new_text)
        f.close
