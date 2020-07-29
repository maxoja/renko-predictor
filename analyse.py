from renko import *
from stats import *


def craftBook(filename, pastLen, futureLen, showTable=True):
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

    if showTable:
        book.showAllInfo()
        print()
    return book


def _calculateRewardFromPattern(positionType, accPattern: str):
    if positionType == POSITION_NONE:
        return NO_EFFECT
    x = sum([GET_MONEYZ if x == UP_BOX else LOSE_MONEYZ for x in accPattern]
            ) * (-1 if positionType == POSITION_BEAR else 1)
    # print(format(positionType, "4d"), accPattern, x)
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
        utilOfActionBranches = []
        for ac in nextActions:
            if ac.type == ACTION_CLOSE:
                utilOfActionBranches.append(getActionUtility(ac,
                                                 accPattern+newPattern[-FUTURE_LEN:], 0))
            elif newPosition == POSITION_NONE:
                utilOfActionBranches.append(getActionUtility(ac, '', remainingDepth-1))
            else:
                utilOfActionBranches.append(getActionUtility(ac, accPattern +
                                                 newPattern[-FUTURE_LEN:], remainingDepth-1))
            if DEBUG:
                print('\t'*(STEPS - remainingDepth), ac.type, f'{utilOfActionBranches[-1]:.3f}')
        maxUtil = max(utilOfActionBranches)
        maxIndex = utilOfActionBranches.index(maxUtil)
        utilOfAction += prob * maxUtil

        if DEBUG:
            print('\t'*(STEPS - remainingDepth), newState.pattern[-1], f'(choose {nextActions[maxIndex].type}) {maxUtil:.3f} * {prob:.3f}')
            if remainingDepth == STEPS:
                print("="*20)
    return utilOfAction

FILE_NAME = 'audnzd_100_small.txt'
FUTURE_LEN = 3  # this is not adjustablel for the moment
PAST_LEN = 5# int(input())
STEPS = 4
DEBUG = False
if __name__ == '__main__':
    print('file', FILE_NAME)
    # while True:
    book = craftBook(FILE_NAME, PAST_LEN, FUTURE_LEN, True)
    # for startPattern in ["+"*PAST_LEN]:
    for startPattern in book.counterOf.keys():
        u, d, n = 9.99, 9.99, 9.99
        startState = State.create(book, startPattern, POSITION_NONE)
        u = getActionUtility(Action.create(
            book, startState, ACTION_BULL), '', STEPS)
        d = getActionUtility(Action.create(
            book, startState, ACTION_BEAR), '', STEPS)
        n = getActionUtility(Action.create(
            book, startState, ACTION_NONE), '', STEPS)
        # print()
        o = book.getPatternOccurrence(startPattern)
        maxVal = max(u,d,n)
        winner = 'Bull' if maxVal == u else 'Bear' if maxVal == d else '-'
        print(
            f'{startPattern} : bull {u: 4.2f}    bear {d: 4.2f}    none {n: 4.2f}    ({o}) choose {winner}',)
    print('-'*20)
