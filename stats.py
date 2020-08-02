from collections import Counter
from typing import List

from config import WindowShape

class KnowledgeBook:
    def __init__(self):
        self.counterOf = dict()
        
    def includeSample(self, pattern:str, next:str):
        if not pattern in self.counterOf:
            self.counterOf[pattern] = Counter({next:1})
        else:
            self.counterOf[pattern] += Counter({next:1})
    
    def getProbOfNextPattern(self, pattern:str, next:str):
        counter = self.counterOf[pattern]
        return counter[next]/sum(counter.values())

    def getPatternOccurrence(self, pattern:str):
        counter = self.counterOf[pattern]
        return sum(counter.values())

    def showAllInfo(self):
        for pattern, counter in self.counterOf.items():
            strFigures = []
            for nextPattern in counter:
                prob = self.getProbOfNextPattern(pattern, nextPattern)
                strFigures.append(f'{nextPattern}({prob:.0%})')
            print(pattern, *sorted(strFigures), self.getPatternOccurrence(pattern))

    @staticmethod 
    def craft(sequence, windowShape:WindowShape, showTable=True):
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


