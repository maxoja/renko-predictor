from sys import argv
from typing import List

from config import Config as conf, WindowShape
from renko import loadSequence, RenkoBoxType, RenkoSnapMode
from stats import KnowledgeBook
from decision import getStateBestActionAndUtility, getPositionReward, \
                        PositionType, ActionType, Action, State


class PositionRecord:
    def __init__(self, pattern:str, position:PositionType, profit:float, reknoMode:RenkoSnapMode):
        self.pattern = pattern
        self.position = position
        self.profit = profit
        self.renkoMode = reknoMode

    def __str__(self):
        if self.renkoMode == RenkoSnapMode.SMALL:
            fPattern = format(self.pattern,f"<{conf.utilDepth}s")
        else:
            fPattern = format((self.pattern[0] + '|' + self.pattern[1:]),f"<{conf.utilDepth+2}s")
        return f' [{fPattern}]  {self.position.name:5s} {self.profit:6.2f}'


class SimulationResult:
    def __init__(self):
        self.phases:List[PositionRecord] = []

    def addPhase(self, phase:PositionRecord):
        self.phases.append(phase)

    def printPhases(self):
        print('\n'.join(map(str,self.phases+[''])))

    def printResult(self):
        totalProfit = sum([p.profit for p in self.phases])
        phaseCount = len(self.phases)
        average = totalProfit/phaseCount

        print("Total profit", totalProfit)
        print("Phase count", phaseCount)
        print("Average Profit", average)


class PositionTracker:
    def __init__(self, renkoMode):
        self.renkoMode = renkoMode
        self.type = PositionType.NONE
        self.seqSinceOpen = ''
        self.preSeq = ''
    
    def _jointSeq(self):
        if self.renkoMode == RenkoSnapMode.SMALL: return self.seqSinceOpen
        return self.preSeq + self.seqSinceOpen

    def shouldCloseNow(self):
        return len(self.seqSinceOpen) >= conf.utilDepth

    def update(self, newSeq):
        if self.type != PositionType.NONE:
            self.seqSinceOpen += newSeq

    def close(self):
        profit = getPositionReward(self.type, self._jointSeq())
        phase = PositionRecord(self._jointSeq(), self.type, profit, self.renkoMode)
        self.type = PositionType.NONE
        self.seqSinceOpen = ''
        self.preSeq = ''
        return phase

    def openBull(self, preSeq):
        self.type = PositionType.BULL
        self.seqSinceOpen = ''
        self.preSeq = preSeq

    def openBear(self, preSeq):
        self.type = PositionType.BEAR
        self.seqSinceOpen = ''
        self.preSeq = preSeq

    
if __name__ == "__main__":
    folder, filename = argv[1], argv[2]
    conf.window = WindowShape(*map(int, argv[3:5]))
    conf.renkoSnapMode = folder

    trainRatio = 0.8
    testRatio = 1 - trainRatio

    dataset = loadSequence(folder, filename)
    trainLength = int(len(dataset) * trainRatio)

    trainDataset = dataset[:trainLength]
    testDataset = dataset[trainLength:]
    book = KnowledgeBook.craft(trainDataset, conf.window, True)

    result = SimulationResult()
    holdingPos = PositionTracker(conf.renkoSnapMode)

    for iEnd in range(conf.window.past, len(testDataset)):
        iBegin = iEnd - conf.window.past
        latestBox = testDataset[iEnd-1]
        pastWin = testDataset[iBegin:iEnd]

        # adding new box
        holdingPos.update(latestBox)

        # make decision after new box
        state = State.create(book, pastWin, holdingPos.type)
        if holdingPos.shouldCloseNow():
            action = Action.create(book, state, ActionType.CLOSE)
        else:
            action, _ = getStateBestActionAndUtility(state, '', conf.utilDepth)

        # perform the decided action
        if action.type == ActionType.CLOSE:
            closedPhase = holdingPos.close()
            result.addPhase(closedPhase)

        elif action.type == ActionType.BULL:
            holdingPos.openBull(latestBox)

        elif action.type == ActionType.BEAR:
            holdingPos.openBear(latestBox)

    result.printPhases()
    result.printResult()
