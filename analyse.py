from renko import loadSequence
from stats import KnowledgeBook

if __name__ == '__main__':
    pastLen = int(input())
    futureLen = 1
    blockLen = pastLen + futureLen
    renko = loadSequence('eurgbp',50)
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
