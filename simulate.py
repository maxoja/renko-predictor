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
from renko import loadSequence, RenkoSnapEnum
from stats import PositionEnum, ActionEnum, Action, State
from utils import craftBook

if __name__ == "__main__":
    filename = argv[1]
    conf.window = WindowShape(*map(int, argv[2:4]))

    trainRatio = 0.8
    testRatio = 1 - trainRatio

    dataset = loadSequence(RenkoSnapEnum.SMALL, filename)
    trainLength = int(len(dataset) * trainRatio)

    trainDataset = dataset[:trainLength]
    testDataset = dataset[trainLength:]

    book = craftBook(trainDataset, conf.window, True)

    currentPosition = PositionEnum.NONE
    openIndex = None
    totalProfit = 0
    phaseCount = 0
    for i in range(len(testDataset) - conf.window.past):
        oldPosition = currentPosition
        pattern = testDataset[i:i+conf.window.past]

        currentState = State.create(book, pattern, oldPosition)
        action, util = getStateBestActionAndUtility(currentState, '', conf.utilDepth)
        newPosition = Action.getResultPositionStatus(currentPosition, action.type)

        # sum up result
        if action.type == ActionEnum.CLOSE:
            sequenceSinceOpen = testDataset[openIndex:i+conf.window.past]
            phaseCount += 1
            totalProfit += getPositionReward(oldPosition, sequenceSinceOpen)
            openIndex = None
        elif action.type in [ActionEnum.BULL, ActionEnum.BEAR]:
            openIndex = i+conf.window.past

        currentPosition = newPosition

    print("Total profit", totalProfit)
    print("Phase count", phaseCount)
    print("Average Profit", totalProfit/phaseCount)
        







