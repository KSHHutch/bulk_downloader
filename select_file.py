from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename

root = Tk()
this.l5 = Label(this.root, text="Boxes File:").grid(row=0, column=0)
this.filename = StringVar()
this.e3 = Entry(this.root, textvariable=this.filename)
this.button3 = Button(
    this.root, text="Select File", command=filedialog.askopenfilename()
).grid(row=0, column=7)
mainloop()
