from collections import Counter

class KnowledgeBook:
    def __init__(self):
        self.counterOf = dict()
        
    def includeSample(self, pattern, next):
        if not pattern in self.counterOf:
            self.counterOf[pattern] = Counter({next:1})
        else:
            self.counterOf[pattern] += Counter({next:1})
    
    def getProbOfNextPattern(self, pattern, next):
        counter = self.counterOf[pattern]
        return counter[next]/sum(counter.values())

    def getPatternOccurrence(self, pattern):
        counter = self.counterOf[pattern]
        return sum(counter.values())

    def showAllInfo(self):
        for pattern, counter in self.counterOf.items():
            strFigures = []
            for nextPattern in counter:
                prob = self.getProbOfNextPattern(pattern, nextPattern)
                strFigures.append(f'{nextPattern}({prob:.0%})')
            print(pattern, *strFigures)