from enum import Enum
from collections import Counter
from typing import List


class PositionType(Enum):
    NONE = "POS_NONE"
    BULL = "POS_BULL"
    BEAR = "POS_BEAR"
    INVALID = "POS_INVALID"


class ActionType(Enum):
    NONE = "ACT_NONE"
    BULL = "ACT_BULL"
    BEAR = "ACT_BEAR"
    CLOSE = "ACT_CLOSE"

    @staticmethod
    def getAll():
        return [ActionType.NONE, ActionType.BULL, ActionType.BEAR, ActionType.CLOSE]

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

        for actionType in ActionType.getAll():
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
        if actionType == ActionType.NONE:
            return currentPosition

        if (actionType, currentPosition) == (ActionType.BULL, PositionType.NONE):
            return PositionType.BULL

        if (actionType, currentPosition) == (ActionType.BEAR, PositionType.NONE):
            return PositionType.BEAR

        if actionType == ActionType.CLOSE and currentPosition in [PositionType.BULL, PositionType.BEAR]:
            return PositionType.NONE

        return PositionType.INVALID

    @staticmethod
    def create(book:KnowledgeBook, currentState:State, actionType:ActionType):
        if Action._checkCache(currentState, actionType):
            return Action._getCache(currentState, actionType)
        
        currentPattern = currentState.pattern
        currentPosition = currentState.position
        newPosition = Action.getResultPositionStatus(currentPosition, actionType)

        if newPosition == PositionType.INVALID:
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