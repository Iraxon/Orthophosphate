from .file_utils import fileKeyPut, fileValueFromKey, USER_INPUT_PATH


def save_in(path: str) -> None:
    fileKeyPut("file_path_in", path, USER_INPUT_PATH)


def save_out(path: str) -> None:
    fileKeyPut("file_path_out", path, USER_INPUT_PATH)


def load_in() -> str:
    return fileValueFromKey("file_path_in", USER_INPUT_PATH)


def load_out() -> str:
    return fileValueFromKey("file_path_out", USER_INPUT_PATH)
