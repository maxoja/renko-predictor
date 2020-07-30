from renko import loadSequence
from stats import KnowledgeBook

def craftBook(sequence, pastLen, futureLen, showTable=True):
    blockLen = pastLen + futureLen
    renko = sequence
    book = KnowledgeBook()

    for i in range(len(renko) - blockLen):
        pastHead = i
        pastTail = pastHead + pastLen
        featurePattern = renko[pastHead: pastTail]

        futureHead = pastTail
        futureTail = futureHead + futureLen
        futurePattern = renko[futureHead:futureTail]

        book.includeSample(featurePattern, futurePattern)

    if showTable:
        book.showAllInfo()
        print()

    return book


def argmaxDict(d:dict):
    return max(d.keys(), key=lambda k: d[k])