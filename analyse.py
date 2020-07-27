from renko import *
from stats import *

FILE_NAME = 'eurgbp_50.txt'
FUTURE_LEN = 1


def craftBook(filename, pastLen, futureLen):
    blockLen = pastLen + futureLen
    renko = loadSequence(FILE_NAME)
    book = KnowledgeBook()

    for i in range(len(renko) - blockLen):
        pastHead = i
        pastTail = pastHead + pastLen
        featurePattern = renko[pastHead: pastTail]

        futureHead = pastTail
        futureTail = futureHead + futureLen
        futurePattern = renko[futureHead:futureTail]

        book.includeSample(featurePattern, futurePattern)

    book.showAllInfo()
    return book


def _calculateRewardFromPattern(positionType, accPattern: str):
    if positionType == POSITION_NONE:
        return NO_EFFECT
    x = sum([GET_MONEYZ if x == UP_BOX else LOSE_MONEYZ for x in accPattern]
            ) * (-1 if positionType == POSITION_BEAR else 1)
    print(format(positionType, "4d"), accPattern, x)
    return x


def getActionUtility(action: Action, accPattern: str, remainingDepth):
    currentPosition = action.fromState.position
    actionType = action.type

    if remainingDepth == 0:
        return _calculateRewardFromPattern(currentPosition, accPattern)

    utilOfAction = 0
    for outcome in action.validOutcomes.items():
        newState, prob = outcome
        newPattern = newState.pattern
        newPosition = newState.position

        nextActions = newState.actions
        utilOfBranches = []
        for ac in nextActions:
            if ac.type == ACTION_CLOSE:
                utilOfBranches.append(getActionUtility(ac,
                                                 accPattern+newPattern[-FUTURE_LEN:], 0))
            else:
                utilOfBranches.append(getActionUtility(ac, accPattern +
                                                 newPattern[-FUTURE_LEN:], remainingDepth-1))

        utilOfAction += prob * max(utilOfBranches)

    return utilOfAction


if __name__ == '__main__':
    book = craftBook(FILE_NAME, int(input()), FUTURE_LEN)
    startState = State.create(book, "++", POSITION_NONE)
    startAction = Action.create(book, startState, ACTION_BEAR)
    print(getActionUtility(startAction, '', 5))
