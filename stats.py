from labeling import LABEL_UP, LABEL_DOWN, LABEL_SIDE

minSample = 80

class PatternStats:
    def __init__(self, pattern):
        self.pattern = pattern
        self.up = 0
        self.down = 0
        self.side = 0
        self.total = 0
        
    def countUp(self):
        self.up += 1
        self.total += 1

    def countDown(self):
        self.down += 1
        self.total += 1

    def countSide(self):
        self.side += 1
        self.total += 1

    def countLabel(self, label):
        if label == LABEL_UP:
            self.countUp()
        elif label == LABEL_DOWN:
            self.countDown()
        else:
            self.countSide()


class KnowledgeBook:
    def __init__(self):
        self.knowledge = {}
        self.total_up = 0
        self.total_down = 0

    def updateKnowledge(self, pattern, label):
        stats = self.knowledge.get(pattern)
        
        if stats is None:
            stats = PatternStats(pattern)
            self.knowledge[pattern] = stats
            
        stats.countLabel(label)
        if label == LABEL_UP:
            self.total_up += 1
        if label == LABEL_DOWN:
            self.total_down += 1

    def showStatsAll(self, profitThresh, skip=False):
        for pattern in self.knowledge:
            self.showStats(pattern, profitThresh, skip)
    
    def showStats(self, pattern, profitThresh, skip=False):
        if not pattern in self.knowledge:
            print(pattern, None)
            return

        stats = self.knowledge[pattern]
        ups = stats.up
        downs = stats.down
        others = stats.side
        all = stats.total

        ratio_up = ups/all
        ratio_down = downs/all
        pass_threshold = ratio_up > profitThresh or ratio_down > profitThresh
        if skip and (all < minSample or not pass_threshold):
            return
        
        print(f'{pattern} {ups:>4} {downs:>4} {others:>4} {all:>4}|  {ups/all:.0%}  {downs/all:.0%}  ', end='')
        if all >= minSample and pass_threshold:
            print('*')
        else:
            print()
