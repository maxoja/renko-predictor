from time import time

from config import WindowShape
from renko import loadSequence
from stats import KnowledgeBook


def argmaxDict(d:dict):
    return max(d.keys(), key=lambda k: d[k])


def startTimer() -> None:
    global _startTime
    _startTime = time()


def timeSinceStart() -> float:
    global _startTime
    return time() - _startTime