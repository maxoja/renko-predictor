from time import time

from config import WindowShape
from renko import loadSequence
from stats import KnowledgeBook

def craftBook(sequence, windowShape:WindowShape, showTable=True):
    renko = sequence
    book = KnowledgeBook()

    for i in range(len(renko) - windowShape.combinedSize):
        pastHead = i
        pastTail = pastHead + windowShape.past
        featurePattern = renko[pastHead: pastTail]

        futureHead = pastTail
        futureTail = futureHead + windowShape.future
        futurePattern = renko[futureHead:futureTail]

        book.includeSample(featurePattern, futurePattern)

    if showTable:
        book.showAllInfo()
        print()

    return book


def argmaxDict(d:dict):
    return max(d.keys(), key=lambda k: d[k])


def startTimer() -> None:
    global _startTime
    _startTime = time()


def timeSinceStart() -> float:
    global _startTime
    return time() - _startTime