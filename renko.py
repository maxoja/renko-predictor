from enum import Enum

class RenkoBoxType(str, Enum):
    UP = "+"
    DOWN = "-"
    SIDE = "."


class RenkoSnapMode(str, Enum):
    SMALL = "small"
    LARGE = "large"


def loadSequence(snapMode: RenkoSnapMode, filename: str):
    with open(f'./data/{snapMode}/{filename}', "rb") as file:
        _ = file.read(2)
        content = file.read().decode('utf-16-le').split('\n')[2].strip()
        return content
