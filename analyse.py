from sys import argv

from config import Config as conf
from decision import getActionUtility
from renko import loadSequence, RenkoSnapEnum
from stats import KnowledgeBook, State, PositionType, ActionType
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
    print(f'bull {actionUtils[ActionType.BULL]: 4.2f}    ',end='')
    print(f'bear {actionUtils[ActionType.BEAR]: 4.2f}    ', end='')
    print(f'none {actionUtils[ActionType.NONE]: 4.2f}    ', end='')
    print(f'({occurrence}) choose {bestActionType}')


if __name__ == '__main__':
    FOLDER, FILE_NAME = argv[1], argv[2]
    conf.renkoSnapMode = FOLDER
    print('Dataset file:', FOLDER, FILE_NAME)
    print(conf.getStringInfo())
    
    startTimer()
    dataset = loadSequence(FOLDER, FILE_NAME)
    book = KnowledgeBook.craft(dataset, conf.window, True)

    for startPattern in book.counterOf.keys():
        startState = State.create(book, startPattern, PositionType.NONE)
        utilOfActionType = getStateUtilityDict(startState)
        printStateUtilities(startState, utilOfActionType)
    
    print()
    print(f'execution time: {timeSinceStart():.2f} s' )
