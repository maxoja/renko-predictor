from sys import argv
from time import time
from math import inf

from config import Config as conf
from decision import getActionUtility
from renko import loadSequence
from stats import KnowledgeBook, State, PositionEnum, ActionEnum
from utils import craftBook, argmaxDict


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
