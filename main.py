import tkinter
import user_interface.file_utils
import user_interface.gui
import datapack_directory_management

from user_interface.file_utils import fileKeyPut
from user_interface.file_utils import fileValueFromKey

def save_in(path: str) -> None:
    fileKeyPut("file_path_in", path, user_interface.file_utils.USER_INPUT_PATH)

def save_out(path: str) -> None:
    fileKeyPut("file_path_out", path, user_interface.file_utils.USER_INPUT_PATH)

def load_in() -> str:
    return fileValueFromKey("file_path_in", user_interface.file_utils.USER_INPUT_PATH)

def load_out() -> str:
    return fileValueFromKey("file_path_out", user_interface.file_utils.USER_INPUT_PATH)

if __name__ == "__main__":

    root = tkinter.Tk()
    user_interface.gui.set_up_window(root=root, save_path_in_function=save_in, save_path_out_function=save_out, load_path_in_function=load_in, load_path_out_function=load_out)
    root.mainloop()