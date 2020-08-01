class RenkoBoxType(str):
    pass


class RenkoBoxEnum:
    UP = RenkoBoxType("+")
    DOWN = RenkoBoxType("-")
    SIDE = RenkoBoxType(".")


class RenkoSnapMode(str):
    pass


class RenkoSnapEnum:
    SMALL = RenkoSnapMode("small")
    LARGE = RenkoSnapMode("large")


def loadSequence(snapMode: RenkoSnapMode, filename: str):
    with open(f'./data/{snapMode}/{filename}', "rb") as file:
        _ = file.read(2)
        content = file.read().decode('utf-16-le').split('\n')[2].strip()
        return content
