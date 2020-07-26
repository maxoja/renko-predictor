UP_BOX = '+'
DOWN_BOX = '-'

def loadSequence(filename):
    with open(f'./data/{filename}', "rb") as file:
        _ = file.read(2)
        content = file.read().decode('utf-16-le').split('\n')[2].strip()
        return content
