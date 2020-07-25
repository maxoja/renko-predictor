from renko import UP_BOX, DOWN_BOX

LABEL_UP = 1
LABEL_DOWN = -1
LABEL_SIDE = 0

class Criteria:
    def __init__(self, tp=2, sl=1):
        if tp < sl:
            raise 'tp should be more than sl'
        self.tp = tp
        self.sl = sl

    def getLabel(self, pattern):
        movement = 0
        lostBuy = False
        lostSell = False
        for c in pattern:
            movement += 1 if c == UP_BOX else -1
            reachedBuyTp = movement >= self.tp
            reachedBuySl = movement <= -self.sl
            reachedSellTp = movement <= -self.tp
            reachedSellSl = movement >= self.sl

            lostBuy = lostBuy or reachedBuySl
            lostSell = lostSell or reachedSellSl
            
            if not lostBuy and reachedBuyTp:
                return LABEL_UP
            if not lostSell and reachedSellTp:
                return LABEL_DOWN
            
        return LABEL_SIDE

    def getOneHotLabel(self, pattern):
        label = self.getLabel(pattern)
        return label==LABEL_UP, label==LABEL_DOWN, label==LABEL_SIDE

    def getProfitableThreshold(self):
        return self.sl/(self.tp+self.sl)
