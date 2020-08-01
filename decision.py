from math import inf

from config import Config as conf
from renko import RenkoBoxType, RenkoSnapMode
from stats import State, Action, PositionType, ActionType


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


class PositionSnapshot:
    def __init__(self, positionType:PositionType, preSequence:str=''):
        self.type = positionType
        self.sequence:str = ''
        self.preSequence:str = preSequence

    def extendSequence(self, extension:str):
        self.sequence += extension

    def checkReward(self, renkoMode:RenkoSnapMode) -> float:
        reward = 0
        rewardDict = REWARD_OF[renkoMode]
    
        for i, box in enumerate(self.preSequence + self.sequence):
            if renkoMode == RenkoSnapMode.SMALL:
                reward += rewardDict[(self.type, box)]
            elif renkoMode == RenkoSnapMode.LARGE:
                if i == 0: continue
                reward += rewardDict[(self.type, (self.preSequence + self.sequence)[i-1:i+1])]

        return reward


class PositionIndexedSnapshot:
    def __init__(self, seq, positionType, startIndex, preSequenceIndex=None, endIndex=None):
        self.seq = seq
        self.type = positionType
        self.start = startIndex
        self.pre = startIndex if preSequenceIndex is None else preSequenceIndex
        self.end = endIndex
        
    def setEndIndex(self, endIndex):
        self.end = endIndex

    def checkReward(self, renkoMode:RenkoSnapMode) -> float:
        reward = 0
        rewardDict = REWARD_OF[renkoMode]
        sequence = self.seq[self.pre: self.end]
    
        for i, box in enumerate(sequence):
            if renkoMode == RenkoSnapMode.SMALL:
                reward += rewardDict[(self.type, box)]
            elif renkoMode == RenkoSnapMode.LARGE:
                if i == 0: continue
                reward += rewardDict[(self.type, (sequence)[i-1:i+1])]

        return reward

    @staticmethod
    def NONE():
        return PositionIndexedSnapshot('', PositionType.NONE, None)
    