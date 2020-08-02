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

    currentPosition = PositionType.NONE
    openIndex = None
    shiftIfLargeSnap = 1 if conf.renkoSnapMode == RenkoSnapMode.LARGE else 0

    result = SimulationResult()

    for i in range(shiftIfLargeSnap, len(testDataset) - conf.window.past):
        oldPosition = currentPosition
        pattern = testDataset[i:i+conf.window.past]

        currentState = State.create(book, pattern, oldPosition)
        action, util = getStateBestActionAndUtility(currentState, '', conf.utilDepth)
        if not openIndex is None and i+conf.window.past - openIndex == conf.utilDepth:
            action = Action.create(book, currentState, ActionType.CLOSE)
        newPosition = Action.getResultPositionStatus(currentPosition, action.type)

        if action.type == ActionType.CLOSE:
            sequenceSinceOpen = testDataset[openIndex-shiftIfLargeSnap:i+conf.window.past]
            profitOfPhase = getPositionReward(oldPosition, sequenceSinceOpen)
            closedPhase = PhaseInfo(sequenceSinceOpen, oldPosition, profitOfPhase)
            result.addPhase(closedPhase)
            openIndex = None
        elif action.type in [ActionType.BULL, ActionType.BEAR]:
            openIndex = i+conf.window.past

        currentPosition = newPosition

    # result.printPhases()
    result.printResult()








