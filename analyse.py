from renko import loadSequence
from stats import KnowledgeBook

FILE_NAME = 'eurgbp_50.txt'
FUTURE_LEN = 1

def createBook(filename, pastLen, futureLen):
    blockLen = pastLen + futureLen
    renko = loadSequence(FILE_NAME)
    book = KnowledgeBook()
    
    for i in range(len(renko) - blockLen):
        pastHead = i
        pastTail = pastHead + pastLen
        featurePattern = renko[pastHead: pastTail]

        futureHead = pastTail
        futureTail = futureHead + futureLen
        futurePattern = renko[futureHead:futureTail]
        
        book.includeSample(featurePattern, futurePattern)

    book.showAllInfo()
    return book

if __name__ == '__main__':
    book = createBook(FILE_NAME, int(input()), FUTURE_LEN)
