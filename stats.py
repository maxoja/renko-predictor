from collections import Counter

class KnowledgeBook:
    def __init__(self):
        self.counterOf = dict()
        
    def includeSample(self, pattern, next):
        if not pattern in self.counterOf:
            self.counterOf[pattern] = Counter({next:1})
        else:
            self.counterOf[pattern] += Counter({next:1})
    
    def getProbOfNextPattern(self, pattern, next):
        counter = self.counterOf[pattern]
        return counter[next]/sum(counter.values())

    def getPatternOccurrence(self, pattern):
        counter = self.counterOf[pattern]
        return sum(counter.values())

    def showAllInfo(self):
        for pattern, counter in self.counterOf.items():
            strFigures = []
            for nextPattern in counter:
                prob = self.getProbOfNextPattern(pattern, nextPattern)
                strFigures.append(f'{nextPattern}({prob:.0%})')
            print(pattern, *sorted(strFigures), self.getPatternOccurrence(pattern))

POSITION_NONE = 0
POSITION_BULL = 1
POSITION_BEAR = -1
POSITION_INVALID = 2

class State:
    cached = dict()

    def __init__(self, pattern, position, actions):
        self.pattern = pattern
        self.position = position
        self.actions = actions

    def __hash__(self):
        return hash((self.pattern, self.position))

    def __eq__(self, other):
        return self.pattern == other.pattern and self.position == other.position

    def __str__(self):
        return f'[{self.pattern},{self.position}]'

    @staticmethod
    def create(book, pattern, position):
        if State._checkCache(pattern, position):
            return State._getCache(pattern, position)
            
        actions = []
        state = State(pattern, position, actions)
        State._updateCache(pattern, position, state)

        for actionType in ALL_ACTIONS:
            newAction = Action.create(book, state, actionType)
            if not newAction is None:
                actions.append(newAction)

        return state

    @staticmethod
    def _checkCache(pattern, position):
        return (pattern, position) in State.cached

    @staticmethod
    def _getCache(pattern, position):
        return State.cached[(pattern,position)]

    @staticmethod
    def _updateCache(pattern, position, state):
        State.cached[(pattern, position)] = state


ACTION_NONE = 0
ACTION_BULL = 1
ACTION_BEAR = -1
ACTION_CLOSE = 2
ALL_ACTIONS = [ACTION_NONE, ACTION_BULL, ACTION_BEAR, ACTION_CLOSE]

class Action:
    cached = dict()

    def __init__(self, currentState, actionType, outcomes:dict):
        self.fromState = currentState
        self.type = actionType
        self.outcomes = outcomes
    
    @staticmethod
    def getResultPositionStatus(currentPosition, actionType):
        if actionType == ACTION_NONE:
            return currentPosition

        if actionType == ACTION_BULL and currentPosition == POSITION_NONE:
            return POSITION_BULL

        if actionType == ACTION_BEAR and currentPosition == POSITION_NONE:
            return POSITION_BEAR

        if actionType == ACTION_CLOSE and currentPosition == (POSITION_BULL or currentPosition == POSITION_BEAR):
            return POSITION_NONE

        return POSITION_INVALID

    @staticmethod
    def create(book, currentState:State, actionType):
        if Action._checkCache(currentState, actionType):
            return Action._getCache(currentState, actionType)
        
        currentPattern = currentState.pattern
        currentPosition = currentState.position
        newPosition = Action.getResultPositionStatus(currentPosition, actionType)

        if newPosition == POSITION_INVALID:
            return None

        outcomes = {}
        result = Action(currentState, actionType, outcomes)
        Action._updateCache(currentState, actionType, result)

        nextPatterns = book.counterOf[currentPattern].keys()
        for nextPattern in nextPatterns:
            prob = book.getProbOfNextPattern(currentPattern, nextPattern)
            newPattern = currentPattern[len(nextPattern):] + nextPattern
            newState = State.create(book, newPattern, newPosition)
            outcomes[newState] = prob

        return result

    @staticmethod
    def _checkCache(state:State, actionType):
        return (state, actionType) in Action.cached

    @staticmethod
    def _getCache(state:State, actionType):
        return Action.cached[(state,actionType)]

    @staticmethod
    def _updateCache(state:State, actionType, action):
        Action.cached[(state, actionType)] = action

    def __eq__(self, other):
        return self.fromState == other.fromState and self.type == other.type

    def __hash__(self):
        return hash((self.fromState, self.type))