from sys import argv

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
    return x


DEBUG = False
def getActionUtility(action: Action, accPattern: str, remainingDepth):
    currentPosition = action.fromState.position

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
                print('\t'*(UTIL_DEPTH - remainingDepth), ac.type, f'{utilOfActionBranches[-1]:.3f}')

        maxIndex = _argmax(utilOfActionBranches)
        maxUtil = utilOfActionBranches[maxIndex]
        bestAction = nextActions[maxIndex]
        utilOfAction += prob * maxUtil

        if DEBUG:
            print('\t'*(UTIL_DEPTH - remainingDepth), newState.pattern[-1], f'(choose {bestAction.type}) {maxUtil:.3f} * {prob:.3f}')
            if remainingDepth == UTIL_DEPTH:
                print("="*20)
    return utilOfAction


def _argmax(l:list):
    return max(range(len(l)), key=lambda x: l[x])

def _argmaxDict(d:dict):
    return max(d.keys(), key=lambda k: d[k])


def printStateUtilities(state:State, actionUtils:dict):
    bestActionType = _argmaxDict(actionUtils)
    occurrence = book.getPatternOccurrence(startPattern)
    print(f'{state.pattern} : ',end='')
    print(f'bull {actionUtils[ACTION_BULL]: 4.2f}    ',end='')
    print(f'bear {actionUtils[ACTION_BEAR]: 4.2f}    ', end='')
    print(f'none {actionUtils[ACTION_NONE]: 4.2f}    ', end='')
    print(f'({occurrence}) choose {bestActionType}')


if __name__ == '__main__':
    FILE_NAME = argv[1]
    PAST_LEN = 5
    FUTURE_LEN = 3
    UTIL_DEPTH = 4
    print(f'FILE {FILE_NAME} --- WINDOW ({PAST_LEN},{FUTURE_LEN}) --- UTIL_DEPTH {UTIL_DEPTH} --- DEBUG {DEBUG}\n')
    book = craftBook(FILE_NAME, PAST_LEN, FUTURE_LEN, True)

    for startPattern in book.counterOf.keys():
        startState = State.create(book, startPattern, POSITION_NONE)
        actionUtils = {}
        
        for actionType in [ACTION_BULL, ACTION_BEAR, ACTION_NONE]:
            actionObj = Action.create(book, startState, actionType)
            actionUtils[actionType] = getActionUtility(actionObj, '', UTIL_DEPTH)

        printStateUtilities(startState, actionUtils)
    print('-'*20)
