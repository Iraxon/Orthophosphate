import tkinter
import user_interface.gui
import compiler.compiler

from user_interface.prompting import save_in, save_out, load_in, load_out

if __name__ == "__main__":

    root = tkinter.Tk()
    user_interface.gui.set_up_window(
        root=root,
        save_path_in_function=save_in,
        save_path_out_function=save_out,
        load_path_in_function=load_in,
        load_path_out_function=load_out,
        compile_function=compiler.compiler.compile,
    )
    root.mainloop()
