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

from renko import loadSequence
from utils import craftBook
from decision import getStateBestActionAndUtility, calculateRewardFromPattern
from stats import PositionEnum, ActionEnum, Action, State
from config import Config as conf

if __name__ == "__main__":
    filename, conf.patternLength, conf.utilDepth = argv[1], int(argv[2]), int(argv[3])

    trainRatio = 0.8
    testRatio = 1 - trainRatio

    dataset = loadSequence(filename)
    trainLength = int(len(dataset) * trainRatio)

    trainDataset = dataset[:trainLength]
    testDataset = dataset[trainLength:]

    book = craftBook(trainDataset, conf.patternLength, conf.futureLength, True)

    currentPosition = PositionEnum.NONE
    openIndex = None
    totalProfit = 0
    phaseCount = 0
    for i in range(len(testDataset) - conf.patternLength):
        oldPosition = currentPosition
        pattern = testDataset[i:i+conf.patternLength]

        currentState = State.create(book, pattern, oldPosition)
        action, util = getStateBestActionAndUtility(currentState, '', conf.utilDepth)
        newPosition = Action.getResultPositionStatus(currentPosition, action.type)

        # sum up result
        if action.type == ActionEnum.CLOSE:
            sequenceSinceOpen = testDataset[openIndex:i+conf.patternLength]
            phaseCount += 1
            totalProfit += calculateRewardFromPattern(oldPosition, sequenceSinceOpen)
            openIndex = None
        elif action.type in [ActionEnum.BULL, ActionEnum.BEAR]:
            openIndex = i+conf.patternLength

        currentPosition = newPosition

    print("Total profit", totalProfit)
    print("Phase count", phaseCount)
    print("Average Profit", totalProfit/phaseCount)
        







