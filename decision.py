from math import inf

from config import Config as conf
from renko import RenkoBoxEnum
from stats import State, Action, PositionEnum, PositionType, ActionEnum


REWARD_OF = {
    (PositionEnum.BULL, RenkoBoxEnum.UP): 1,
    (PositionEnum.BULL, RenkoBoxEnum.DOWN): -1,
    (PositionEnum.BEAR, RenkoBoxEnum.UP): -1,
    (PositionEnum.BEAR, RenkoBoxEnum.DOWN): 1
}

def calculateRewardFromPattern(position:PositionType, accPattern: str) -> float:
    reward = 0
    for box in accPattern:
        reward += REWARD_OF[(position, box)]
    return reward


def getStateBestActionAndUtility(state: State, accPattern: str, remainingDepth: int) -> (Action, float):
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

        if conf.debug:
            print('\t'*(conf.utilDepth - remainingDepth), action.type, f'{utility:.3f}')

    return bestAction, bestUtil


def getActionUtility(action: Action, accPattern: str, remainingDepth: int, cacheTable = {}) -> float:
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

        if conf.debug:
            reverseDepth = conf.utilDepth - remainingDepth
            print('\t'*reverseDepth, f'{newState.pattern[-1]} (choose {bestAction.type}) {bestUtil:.3f} * {prob:.3f}')
            if reverseDepth == 0:
                print("="*20)

    cacheTable[(action, accPattern, remainingDepth)] = utility
    return utility