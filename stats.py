from collections import Counter

class KnowledgeBook:
    def __init__(self):
        self.counterOfPattern = dict()
        
    def includeSample(self, pattern, nextPattern):
        if not pattern in self.counterOfPattern:
            self.counterOfPattern[pattern] = Counter({nextPattern:1})
        else:
            self.counterOfPattern[pattern] += Counter({nextPattern:1})
    
    def getProbOfNextPattern(self, pattern, nextPattern):
        counter = self.counterOfPattern[pattern]
        return counter[nextPattern]/sum(counter.values())

    def getPatternOccurrence(self, pattern):
        counter = self.counterOfPattern[pattern]
        return sum(counter.values())

    def showAllInfo(self):
        for pattern, counter in self.counterOfPattern.items():
            line = pattern + ' '
            for nextPattern in counter:
                prob = self.getProbOfNextPattern(pattern, nextPattern)
                line += f'{nextPattern}({prob:.0%}) '
            print(line)