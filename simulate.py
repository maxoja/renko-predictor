'''
    INput: 
        Filename
        Pattern length
        Recursion depth
    Output: 
        Total profit
        Phase count
        Avg profit per phase
'''

from sys import argv

from config import Config as conf, WindowShape
from decision import getStateBestActionAndUtility, getPositionReward
from renko import loadSequence, RenkoBoxType, RenkoSnapMode
from stats import KnowledgeBook, PositionType, ActionType, Action, State

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
    totalProfit = 0
    phaseCount = 0
    shiftIfLargeSnap = 1 if conf.renkoSnapMode == RenkoSnapMode.LARGE else 0

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
            phaseCount += 1
            totalProfit += getPositionReward(oldPosition, sequenceSinceOpen)
            openIndex = None
        elif action.type in [ActionType.BULL, ActionType.BEAR]:
            openIndex = i+conf.window.past

        currentPosition = newPosition

    print("Total profit", totalProfit)
    print("Phase count", phaseCount)
    print("Average Profit", totalProfit/phaseCount)








