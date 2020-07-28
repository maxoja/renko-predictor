from renko import *
from stats import *

FILE_NAME = 'audnzd_50_small.txt'
FUTURE_LEN = 1  # this is not adjustablel for the moment


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
        # print('\t'*(STEPS - remainingDepth-1),'-')
        return _calculateRewardFromPattern(currentPosition, accPattern)

    utilOfAction = 0
    for outcome in action.validOutcomes.items():
        newState, prob = outcome
        newPattern = newState.pattern
        newPosition = newState.position

        nextActions = newState.actions
        utilOfActionBranches = []
        print('\t'*(STEPS - remainingDepth), '-'*10)
        for ac in nextActions:
            if ac.type == ACTION_CLOSE:
                utilOfActionBranches.append(getActionUtility(ac,
                                                 accPattern+newPattern[-FUTURE_LEN:], 0))
            elif newPosition == POSITION_NONE:
                utilOfActionBranches.append(getActionUtility(ac, '', remainingDepth-1))
            else:
                utilOfActionBranches.append(getActionUtility(ac, accPattern +
                                                 newPattern[-FUTURE_LEN:], remainingDepth-1))
            print('\t'*(STEPS - remainingDepth), ac.type, f'{utilOfActionBranches[-1]:.3f}')
        maxUtil = max(utilOfActionBranches)
        maxIndex = utilOfActionBranches.index(maxUtil)
        utilOfAction += prob * maxUtil


        print('\t'*(STEPS - remainingDepth), f'(choose {nextActions[maxIndex].type}) {maxUtil:.3f}')
        if remainingDepth == STEPS:
            print("xxxxx")
        # print('\t'*(STEPS - remainingDepth), nextActions[maxIndex].type, f'{maxUtil:.3f}')
    # print(len(action.validOutcomes.items()))
    return utilOfAction


STEPS = 5
if __name__ == '__main__':
    print('file', FILE_NAME)
    # while True:
    PAST_LEN = 2# int(input())
    book = craftBook(FILE_NAME, PAST_LEN, FUTURE_LEN, True)
    for startPattern in ["+"*PAST_LEN]: #book.counterOf.keys():
        startState = State.create(book, startPattern, POSITION_NONE)
        # u = getActionUtility(Action.create(
        #     book, startState, ACTION_BULL), '', STEPS)
        # print()
        # d = getActionUtility(Action.create(
        #     book, startState, ACTION_BEAR), '', STEPS)
        # print()
        n = getActionUtility(Action.create(
            book, startState, ACTION_NONE), '', STEPS)
        print()
        o = book.getPatternOccurrence(startPattern)
        # print(
        #     f'{startPattern} : bull {u: 4.2f}    bear {d: 4.2f}    none {n: 4.2f}    ({o})')
        # print(f'{startPattern} : none {n: 4.2f}')
    print('-'*20)
