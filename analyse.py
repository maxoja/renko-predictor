from sys import argv

from config import Config as conf
from decision import getActionUtility
from renko import loadSequence
from stats import KnowledgeBook, State, PositionEnum, ActionEnum
from utils import craftBook, argmaxDict, startTimer, timeSinceStart


def getStateUtilityDict(state:State):
    utilOfActionType = {}
    for action in state.actions:
        utilOfActionType[action.type] = getActionUtility(action, '', conf.utilDepth)
    return utilOfActionType


def printStateUtilities(state:State, actionUtils:dict):
    bestActionType = argmaxDict(actionUtils)
    occurrence = book.getPatternOccurrence(startPattern)
    print(f'{state.pattern} : ',end='')
    print(f'bull {actionUtils[ActionEnum.BULL]: 4.2f}    ',end='')
    print(f'bear {actionUtils[ActionEnum.BEAR]: 4.2f}    ', end='')
    print(f'none {actionUtils[ActionEnum.NONE]: 4.2f}    ', end='')
    print(f'({occurrence}) choose {bestActionType}')
    print()


if __name__ == '__main__':
    FILE_NAME = argv[1]
    print('Dataset file:', FILE_NAME)
    print(conf.getStringInfo())
    
    startTimer()
    dataset = loadSequence(FILE_NAME)
    book = craftBook(dataset, conf.patternLength, conf.futureLength, True)

    for startPattern in book.counterOf.keys():
        startState = State.create(book, startPattern, PositionEnum.NONE)
        utilOfActionType = getStateUtilityDict(startState)
        printStateUtilities(startState, utilOfActionType)
    
    print(f'execution time: {timeSinceStart():.2f} s' )
