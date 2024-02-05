from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename


# Functions
def choose_file():
    global file_name
    file_name = askopenfilename
    return file_name


def click_me():
    print(i.get())


# Window & widgets
window = Tk()
window.title("Bulk Downloader v4")
frm = ttk.Frame(window, padding=20)
quit_button = ttk.Button(frm, text="Quit", command=window.destroy)
file_select_button = ttk.Button(frm, text="Choose File", command=askopenfilename)

# Checkbutton widget
i = IntVar()
c = Checkbutton(window, text="Python", variable=i)
b = Button(window, text="Click here", command=click_me)


# Widget Geometry
frm.grid()
quit_button.grid(column=1, row=0)
file_select_button.grid(column=1, row=1)
c.grid(column=2, row=2)
b.grid(column=2, row=1)


# Run
window.mainloop()
