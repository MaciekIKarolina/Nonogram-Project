import Nonogram
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk


if __name__ == '__main__':
    root = tk.Tk()
    ex = Nonogram.Nono_Main(root)
    root.geometry("300x250+300+300")
    root.mainloop()
