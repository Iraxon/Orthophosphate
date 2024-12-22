import tkinter
import user_interface.gui

if __name__ == "__main__":

    root = tkinter.Tk()
    user_interface.gui.set_up_window(root=root)
    root.mainloop()