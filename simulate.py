from sys import argv
from typing import List

from config import Config as conf, WindowShape
from renko import loadSequence, RenkoBoxType, RenkoSnapMode
from stats import KnowledgeBook
from decision import getStateBestActionAndUtility, getPositionReward, \
                        PositionType, ActionType, Action, State


class PhaseInfo:
    def __init__(self, pattern:str, position:PositionType, profit:float):
        self.pattern = pattern if conf.renkoSnapMode is RenkoSnapMode.SMALL else pattern[1:]
        self.position = position
        self.profit = profit

    def __str__(self):
        return f' [{format(self.pattern,f">{conf.utilDepth}s")}]  {self.position.name:5s} {self.profit:6.2f}'


class SimulationResult:
    def __init__(self):
        self.phases:List[PhaseInfo] = []

    def addPhase(self, phase:PhaseInfo):
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


class HoldingPosition:
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
        phase = PhaseInfo(self._jointSeq(), self.type, profit)
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
    holdingPos = HoldingPosition(conf.renkoSnapMode)

    for ib in range(conf.window.past, len(testDataset)):
        ia = ib - conf.window.past
        newBox = testDataset[ib-1]
        pastWin = testDataset[ia:ib]

        # adding new box
        holdingPos.update(newBox)

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
            holdingPos.openBull(newBox)

        elif action.type == ActionType.BEAR:
            holdingPos.openBear(newBox)

    result.printPhases()
    result.printResult()
