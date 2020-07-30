from sys import argv
from time import time
from math import inf

from renko import *
from stats import *
from utils import craftBook
from config import Config as conf


def calculateRewardFromPattern(positionType, accPattern: str):
    if positionType == POSITION_NONE:
        return NO_EFFECT
    x = sum([GET_MONEYZ if x == UP_BOX else LOSE_MONEYZ for x in accPattern]
            ) * (-1 if positionType == POSITION_BEAR else 1)
    return x


def getStateBestActionAndUtility(state: State, accPattern: str, remainingDepth):
    bestUtil = -inf
    bestAction = None

    for action in state.actions:
        newAccPattern = accPattern+state.pattern[-conf.futureLength:]
        newRemaindingDepth = remainingDepth-1

        if action.type == ACTION_CLOSE:
            newRemaindingDepth = 0

        if state.position == POSITION_NONE:
            newAccPattern = ''

        utility = getActionUtility(action, newAccPattern, newRemaindingDepth)

        if utility > bestUtil:
            bestUtil = utility
            bestAction = action

        if DEBUG:
            print('\t'*(UTIL_DEPTH - remainingDepth), action.type, f'{utility:.3f}')

    return bestAction, bestUtil

DEBUG = False
def getActionUtility(action: Action, accPattern: str, remainingDepth, cacheTable = {}):
    if (action, accPattern, remainingDepth) in cacheTable:
        return cacheTable[(action, accPattern, remainingDepth)]

    currentPosition = action.fromState.position

    if remainingDepth == 0:
        return calculateRewardFromPattern(currentPosition, accPattern)

    utility = 0
    for outcome in action.validOutcomes.items():
        newState, prob = outcome
        bestAction, bestUtil = getStateBestActionAndUtility(newState, accPattern, remainingDepth)
        utility += prob * bestUtil

        if DEBUG:
            print('\t'*(UTIL_DEPTH - remainingDepth), newState.pattern[-1], f'(choose {bestAction.type}) {bestUtil:.3f} * {prob:.3f}')
            if remainingDepth == conf.utilDepth:
                print("="*20)

    cacheTable[(action, accPattern, remainingDepth)] = utility
    return utility


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


def getStateUtilityDict(state:State):
    utilOfActionType = {}
    for action in state.actions:
        utilOfActionType[action.type] = getActionUtility(action, '', conf.utilDepth)
    return utilOfActionType


if __name__ == '__main__':
    startTime = time()
    FILE_NAME = argv[1]
    conf.patternLength = 5
    conf.futureLength = 3
    conf.utilDepth = 6
    conf.debug = False
    print(f'FILE {FILE_NAME} --- WINDOW ({conf.patternLength},{conf.futureLength}) --- UTIL_DEPTH {conf.utilDepth} --- DEBUG {conf.debug}\n')
    
    sequence = loadSequence(FILE_NAME)
    book = craftBook(sequence, conf.patternLength, conf.futureLength, True)

    for startPattern in book.counterOf.keys():

        startState = State.create(book, startPattern, POSITION_NONE)
        utilOfActionType = getStateUtilityDict(startState)

        printStateUtilities(startState, utilOfActionType)
    
    print(time() - startTime)
