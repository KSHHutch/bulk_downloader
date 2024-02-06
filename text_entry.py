from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename


def printtext():
    global e
    words = e.get()
    print(words)


root = Tk()

root.title("Name")

e = Entry(root)
e.pack()
e.focus_set()

b = Button(root, text="okay", command=printtext)
b.pack(side="bottom")
root.mainloop()
