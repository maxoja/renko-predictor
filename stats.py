from collections import Counter
from typing import List


class PositionType(str):
    pass

class PositionEnum:
    NONE = PositionType("POS_NONE")
    BULL = PositionType("POS_BULL")
    BEAR = PositionType("POS_BEAR")
    INVALID = PositionType("POS_INVALID")

class ActionType(str):
    pass

class ActionEnum:
    NONE = ActionType("ACT_NONE")
    BULL = ActionType("ACT_BULL")
    BEAR = ActionType("ACT_BEAR")
    CLOSE = ActionType("ACT_CLOSE")

    @staticmethod
    def getAll() -> List[ActionType]:
        return [ActionEnum.NONE, ActionEnum.BULL, ActionEnum.BEAR, ActionEnum.CLOSE]

class KnowledgeBook:
    def __init__(self):
        self.counterOf = dict()
        
    def includeSample(self, pattern:str, next:str):
        if not pattern in self.counterOf:
            self.counterOf[pattern] = Counter({next:1})
        else:
            self.counterOf[pattern] += Counter({next:1})
    
    def getProbOfNextPattern(self, pattern:str, next:str):
        counter = self.counterOf[pattern]
        return counter[next]/sum(counter.values())

    def getPatternOccurrence(self, pattern:str):
        counter = self.counterOf[pattern]
        return sum(counter.values())

    def showAllInfo(self):
        for pattern, counter in self.counterOf.items():
            strFigures = []
            for nextPattern in counter:
                prob = self.getProbOfNextPattern(pattern, nextPattern)
                strFigures.append(f'{nextPattern}({prob:.0%})')
            print(pattern, *sorted(strFigures), self.getPatternOccurrence(pattern))


class State:
    cached = dict()

    def __init__(self, pattern:str, position:PositionType, actions: list):
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
    def create(book:KnowledgeBook, pattern:str, position:PositionType):
        if State._checkCache(pattern, position):
            return State._getCache(pattern, position)
            
        actions = []
        state = State(pattern, position, actions)
        State._updateCache(pattern, position, state)

        for actionType in ActionEnum.getAll():
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


class Action:
    cached = dict()

    def __init__(self, currentState:State, actionType:ActionType, validOutcomes:dict):
        self.fromState = currentState
        self.type = actionType
        self.validOutcomes = validOutcomes
    
    @staticmethod
    def getResultPositionStatus(currentPosition:PositionType, actionType:ActionType):
        if actionType == ActionEnum.NONE:
            return currentPosition

        if (actionType, currentPosition) == (ActionEnum.BULL, PositionEnum.NONE):
            return PositionEnum.BULL

        if (actionType, currentPosition) == (ActionEnum.BEAR, PositionEnum.NONE):
            return PositionEnum.BEAR

        if actionType == ActionEnum.CLOSE and currentPosition in [PositionEnum.BULL, PositionEnum.BEAR]:
            return PositionEnum.NONE

        return PositionEnum.INVALID

    @staticmethod
    def create(book:KnowledgeBook, currentState:State, actionType:ActionType):
        if Action._checkCache(currentState, actionType):
            return Action._getCache(currentState, actionType)
        
        currentPattern = currentState.pattern
        currentPosition = currentState.position
        newPosition = Action.getResultPositionStatus(currentPosition, actionType)

        if newPosition == PositionEnum.INVALID:
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

    def __str__(self):
        return f'[{self.fromState},{self.type}]'