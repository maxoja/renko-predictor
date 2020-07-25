from renko import loadSequence
from stats import KnowledgeBook

FILE_NAME = 'eurgbp_50.txt'
FUTURE_LEN = 1

if __name__ == '__main__':
    pastLen = int(input())
    futureLen = FUTURE_LEN
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
