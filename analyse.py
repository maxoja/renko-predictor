from renko import loadSequence
from stats import KnowledgeBook, State, Action, POSITION_NONE

FILE_NAME = 'test_1.txt'
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


def recurseState(state:State, depthTillStop:int):

    print(f'state {state.pattern} {state.position}')

    if depthTillStop > 0:
        for action in state.actions:
            recurse(action, depthTillStop-1)


def recurseAction(action:Action, depthTillStop:int):

    print(f'action {action.fromState} {action.type}')

    if depthTillStop > 0:
        for state, prob in action.outcomes.items():
            recurse(state, depthTillStop-1)


def getActionUtility(stateOrAction, depthTillStop=1):

    if isinstance(stateOrAction, State):
        recurseState(stateOrAction, depthTillStop)

    if isinstance(stateOrAction, Action):
        recurseAction(stateOrAction, depthTillStop)


if __name__ == '__main__':
    book = craftBook(FILE_NAME, int(input()), FUTURE_LEN)
    startState = State.create(book, "++", POSITION_NONE)
    recurse(startState, 5)