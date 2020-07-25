UP_BOX = '+'
DOWN_BOX = '-'

def loadSequence(quote, boxSize):
    with open(f'./data/{quote}_{boxSize}.txt', "rb") as file:
        header = file.read(2)
        content = file.read().decode('utf-16-le').split('\n')[2].strip()
        return content
