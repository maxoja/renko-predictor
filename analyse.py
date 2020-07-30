from sys import argv
from time import time
from math import inf

from renko import RenkoBoxEnum, loadSequence
from stats import KnowledgeBook, State, Action, PositionEnum, ActionEnum, PositionType
from utils import craftBook, argmaxDict
from config import Config as conf

rewardOf = {
    (PositionEnum.BULL, RenkoBoxEnum.UP): 1,
    (PositionEnum.BULL, RenkoBoxEnum.DOWN): -1,
    (PositionEnum.BEAR, RenkoBoxEnum.UP): -1,
    (PositionEnum.BEAR, RenkoBoxEnum.DOWN): 1
}


def calculateRewardFromPattern(position:PositionType, accPattern: str) -> float:
    reward = 0
    for box in accPattern:
        reward += rewardOf[(position, box)]
    return reward


def getStateBestActionAndUtility(state: State, accPattern: str, remainingDepth) -> (Action, float):
    bestUtil = -inf
    bestAction = None

    for action in state.actions:
        newAccPattern = accPattern+state.pattern[-conf.futureLength:]
        newRemaindingDepth = remainingDepth-1

        if action.type == ActionEnum.CLOSE:
            newRemaindingDepth = 0

        if state.position == PositionEnum.NONE:
            newAccPattern = ''

        utility = getActionUtility(action, newAccPattern, newRemaindingDepth)

        if utility > bestUtil:
            bestUtil = utility
            bestAction = action

        if DEBUG:
            print('\t'*(conf.utilDepth - remainingDepth), action.type, f'{utility:.3f}')

    return bestAction, bestUtil

DEBUG = False
def getActionUtility(action: Action, accPattern: str, remainingDepth, cacheTable = {}) -> float:
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
            print('\t'*(conf.utilDepth - remainingDepth), newState.pattern[-1], f'(choose {bestAction.type}) {bestUtil:.3f} * {prob:.3f}')
            if remainingDepth == conf.utilDepth:
                print("="*20)

    cacheTable[(action, accPattern, remainingDepth)] = utility
    return utility


def printStateUtilities(state:State, actionUtils:dict):
    bestActionType = argmaxDict(actionUtils)
    occurrence = book.getPatternOccurrence(startPattern)
    print(f'{state.pattern} : ',end='')
    print(f'bull {actionUtils[ActionEnum.BULL]: 4.2f}    ',end='')
    print(f'bear {actionUtils[ActionEnum.BEAR]: 4.2f}    ', end='')
    print(f'none {actionUtils[ActionEnum.NONE]: 4.2f}    ', end='')
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

        startState = State.create(book, startPattern, PositionEnum.NONE)
        utilOfActionType = getStateUtilityDict(startState)

        printStateUtilities(startState, utilOfActionType)
    
    print(time() - startTime)
