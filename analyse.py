from renko import UP_BOX, DOWN_BOX, loadSequence
from labeling import Criteria, LABEL_UP, LABEL_DOWN, LABEL_SIDE
from stats import PatternStats, KnowledgeBook

if __name__ == '__main__':
    criteria = Criteria(tp=2,sl=1)
    labelWinSize = 8
    predWinSize = int(input())
    renko = loadSequence('eurgbp',50)
    book = KnowledgeBook()
    
    for i in range(len(renko)):
        if i >= len(renko) - labelWinSize - predWinSize : break

        featureHead = i
        featureTail = featureHead + predWinSize
        featurePattern = renko[featureHead:featureTail]

        labelHead = featureTail
        labelTail = labelHead + labelWinSize
        labelingPattern = renko[labelHead:labelTail]
        label = criteria.getLabel(labelingPattern)
        
        book.updateKnowledge(featurePattern, label)

    book.showStatsAll(criteria.getProfitableThreshold(), skip=True)

    print(f'{book.total_up} {book.total_down} {book.total_up/(book.total_up+book.total_down):.0%} threshold {criteria.getProfitableThreshold():.0%}')

    while True:
        book.showStats(input(), criteria.getProfitableThreshold())
