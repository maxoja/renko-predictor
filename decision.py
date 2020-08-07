from enum import Enum
from math import inf

from config import Config as conf
from renko import RenkoBoxType, RenkoSnapMode
from stats import KnowledgeBook


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

        for actionType in ActionType:
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


REWARD_OF = {
    RenkoSnapMode.SMALL: {
        (PositionType.BULL, RenkoBoxType.UP): 1,
        (PositionType.BULL, RenkoBoxType.DOWN): -1,
        (PositionType.BEAR, RenkoBoxType.UP): -1,
        (PositionType.BEAR, RenkoBoxType.DOWN): 1
    },
    RenkoSnapMode.LARGE: {
        (PositionType.BULL, RenkoBoxType.UP+RenkoBoxType.UP): 1,
        (PositionType.BULL, RenkoBoxType.DOWN+RenkoBoxType.UP): 2,
        (PositionType.BULL, RenkoBoxType.DOWN+RenkoBoxType.DOWN): -1,
        (PositionType.BULL, RenkoBoxType.UP+RenkoBoxType.DOWN): -2,
        (PositionType.BEAR, RenkoBoxType.UP+RenkoBoxType.UP): -1,
        (PositionType.BEAR, RenkoBoxType.DOWN+RenkoBoxType.UP): -2,
        (PositionType.BEAR, RenkoBoxType.DOWN+RenkoBoxType.DOWN): 1,
        (PositionType.BEAR, RenkoBoxType.UP+RenkoBoxType.DOWN): 2,
    }
}


def getPositionReward(position:PositionType, patternSinceOpen: str) -> float:
    reward = 0
    # print(type(conf.renkoSnapMode))
    # print(type(RenkoSnapMode.SMALL))
    rewardDict = REWARD_OF[conf.renkoSnapMode]

    for i, box in enumerate(patternSinceOpen):
        if conf.renkoSnapMode == RenkoSnapMode.SMALL:
            reward += rewardDict[(position, box)]
        elif conf.renkoSnapMode == RenkoSnapMode.LARGE:
            if i == 0: continue
            reward += rewardDict[(position, patternSinceOpen[i-1:i+1])]

    return reward


def getStateBestActionAndUtility(state: State, patternSinceOpen: str, remainingDepth: int) -> (Action, float):
    bestUtil = -inf
    bestAction = None

    for action in state.actions:
        if conf.renkoSnapMode == RenkoSnapMode.SMALL:
            newAccPattern = patternSinceOpen+state.pattern[-conf.window.future:]
        elif conf.renkoSnapMode == RenkoSnapMode.LARGE:
            newAccPattern = patternSinceOpen+state.pattern[-conf.window.future-(1 if len(patternSinceOpen) == 0 else 0):]
        newRemaindingDepth = remainingDepth-1

        if action.type == ActionType.CLOSE:
            newRemaindingDepth = 0

        if state.position == PositionType.NONE:
            newAccPattern = ''

        utility = getActionUtility(action, newAccPattern, newRemaindingDepth)

        if utility > bestUtil:
            bestUtil = utility
            bestAction = action

        if conf.debug:
            print('\t'*(conf.utilDepth - remainingDepth), action.type, f'{utility:.3f}')

    return bestAction, bestUtil


def getActionUtility(action: Action, patternSinceOpen: str, remainingDepth: int, cacheTable = {}) -> float:
    if (action, patternSinceOpen, remainingDepth) in cacheTable:
        return cacheTable[(action, patternSinceOpen, remainingDepth)]

    currentPosition = action.fromState.position

    if remainingDepth == 0:
        return getPositionReward(currentPosition, patternSinceOpen)

    utility = 0
    for outcome in action.validOutcomes.items():
        newState, prob = outcome
        bestAction, bestUtil = getStateBestActionAndUtility(newState, patternSinceOpen, remainingDepth)
        utility += prob * bestUtil

        if conf.debug:
            reverseDepth = conf.utilDepth - remainingDepth
            print('\t'*reverseDepth, f'{newState.pattern[-1]} (choose {bestAction.type}) {bestUtil:.3f} * {prob:.3f}')
            if reverseDepth == 0:
                print("="*20)

    cacheTable[(action, patternSinceOpen, remainingDepth)] = utility
    return utility


